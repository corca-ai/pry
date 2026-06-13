"""label_io.py — deterministic I/O for AGENT-DRIVEN labeling (no LLM, no spend).

Slice 0 of the pry validation harness (docs/spec-layer0.md, F10/F16/F17). The
labeler is the coding agent, not this script. label_io.py only does the
deterministic plumbing around it:

  * `emit`  — write a BLINDED worklist (rubric + {sha, subject, diff}) the agent
              reads. No "pry"/"seam"/"welded"/thesis framing (F10 bias guard).
  * `freeze --model-id <id>` — validate the agent's verdicts (pure schema check,
              NEVER adjudicates correctness) and write the frozen labels.json in
              the exact schema szz.py/repo_fit.py consume. Refuses unless EVERY
              candidate + P1b sha is present and well-formed (completeness guard,
              so a half-labeled run cannot silently undercount the floor).

This script never calls an LLM and never spends money (Constraints). The agent
applies RUBRIC below; its hash is frozen for provenance (F16).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import config

WORKLIST_PATH = config.FIXTURES_DIR / "label_worklist.json"
VERDICTS_PATH = config.FIXTURES_DIR / "label_verdicts.json"

# Blinded, generic defect-study rubric (no pry framing). The agent applies this;
# its hash is frozen into labels.json. Keep in sync with docs/spec-layer0.md
# "Labeling rubric".
RUBRIC = (
    "Label whether each commit FIXES a bug in error-/failure-handling logic: the "
    "handling of a failure the program encountered or could encounter at a "
    "boundary (network, file/IO, subprocess, DB, clock, randomness). COUNTS: "
    "fixing a swallowed exception, a wrong/missing except clause, a missing "
    "rollback or cleanup after a failure, a broken retry/timeout, mishandling a "
    "boundary call's failure, log-and-continue on a path that should abort. Does "
    "NOT count: new features, refactors, pure business-logic fixes with no "
    "failure-handling aspect, test-only/docs/config/formatting changes, or adding "
    "error handling to brand-new code (no prior bug). For each commit return "
    "{is_error_handling_fix: bool, confidence: high|medium|low, reason: <one "
    "short clause>}. Judge only from the diff and subject; if a commit is "
    "borderline, prefer a second skeptical look arguing it does NOT count and "
    "lower the confidence accordingly."
)

CONFIDENCE = {"high", "medium", "low"}


def rubric_hash() -> str:
    return hashlib.sha256(RUBRIC.encode()).hexdigest()[:16]


def _diff(repo: Path, sha: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), "show", "--format=", "--unified=3",
         sha, "--", config.PYTHON_PATHSPEC],
        check=True, capture_output=True, text=True,
    ).stdout
    return out[: config.LABEL_DIFF_CHAR_CAP]


def _work_items(data: dict) -> list[dict]:
    """Candidates + the P1b mining-recall sample, tagged with their group."""
    cands = [{**c, "group": "candidate"} for c in data["candidates"]]
    sample = [{**c, "group": "recall_sample"}
              for c in data["non_matched_bugfix"][: config.MINING_RECALL_SAMPLE]]
    return cands + sample


def cmd_emit(args) -> None:
    data = json.loads(args.candidates.read_text())
    items = _work_items(data)
    worklist = {
        "rubric": RUBRIC,
        "rubric_hash": rubric_hash(),
        "corpus": data["corpus"],
        "corpus_head": data["corpus_head"],
        "instructions": ("Apply `rubric` to every commit in `commits`. Return a "
                         "JSON object {sha: {is_error_handling_fix, confidence, "
                         "reason}} covering ALL shas. Judge only from subject+diff."),
        "commits": [
            {"sha": it["sha"], "subject": it["subject"],
             "diff": _diff(args.repo, it["sha"])}
            for it in items
        ],
    }
    args.out.write_text(json.dumps(worklist, indent=2, sort_keys=True) + "\n")
    print(f"emitted {len(worklist['commits'])} commits "
          f"(blinded worklist, rubric {rubric_hash()}) -> {args.out}")
    print(f"agent: label every sha, write verdicts to {VERDICTS_PATH}, "
          f"then run: python3 harness/label_io.py freeze --model-id <model>")


def cmd_freeze(args) -> None:
    data = json.loads(args.candidates.read_text())
    items = _work_items(data)
    by_sha = {it["sha"]: it for it in items}

    if not args.verdicts.exists():
        sys.exit(f"verdicts file {args.verdicts} not found — agent must write it "
                 f"(emit first, then label).")
    verdicts = json.loads(args.verdicts.read_text())
    # allow either {sha: verdict} or {"verdicts": {sha: verdict}}
    if "verdicts" in verdicts and isinstance(verdicts["verdicts"], dict):
        verdicts = verdicts["verdicts"]

    # --- completeness + schema validation (pure; never adjudicates) ---------
    errors = []
    for sha in by_sha:
        v = verdicts.get(sha)
        if v is None:
            errors.append(f"missing verdict for {sha[:10]}")
            continue
        if not isinstance(v.get("is_error_handling_fix"), bool):
            errors.append(f"{sha[:10]}: is_error_handling_fix not bool")
        if v.get("confidence") not in CONFIDENCE:
            errors.append(f"{sha[:10]}: confidence not in {sorted(CONFIDENCE)}")
        if not isinstance(v.get("reason"), str) or not v.get("reason"):
            errors.append(f"{sha[:10]}: reason missing/empty")
    extra = set(verdicts) - set(by_sha)
    if extra:
        errors.append(f"{len(extra)} verdicts for unknown shas (e.g. "
                      f"{sorted(extra)[0][:10]})")
    if errors:
        print(f"FREEZE REFUSED — {len(errors)} problem(s):", file=sys.stderr)
        for e in errors[:20]:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    labels = {}
    for sha, it in by_sha.items():
        v = verdicts[sha]
        labels[sha] = {
            "subject": it["subject"],
            "date": it["date"],
            "group": it["group"],
            "is_error_handling_fix": v["is_error_handling_fix"],
            "confidence": v["confidence"],
            "reason": v["reason"][:200],
        }

    out = {
        "corpus": data["corpus"],
        "corpus_head": data["corpus_head"],
        "labeler_model": args.model_id,
        "rubric_hash": rubric_hash(),
        "labels": labels,
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

    pos = sum(1 for v in labels.values()
              if v["group"] == "candidate" and v["is_error_handling_fix"])
    hi = sum(1 for v in labels.values()
             if v["group"] == "candidate" and v["is_error_handling_fix"]
             and v["confidence"] == "high")
    recall = sum(1 for v in labels.values()
                 if v["group"] == "recall_sample" and v["is_error_handling_fix"])
    n_cand = sum(1 for it in items if it["group"] == "candidate")
    n_samp = sum(1 for it in items if it["group"] == "recall_sample")
    print(f"frozen {len(labels)} labels (model={args.model_id}, "
          f"rubric={rubric_hash()}) -> {args.out}")
    print(f"  confirmed error-handling fixes: {pos}/{n_cand}  "
          f"(high-confidence: {hi})")
    print(f"  P1b mining-recall: {recall}/{n_samp} non-matched were real misses")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("emit", help="write the blinded labeling worklist")
    e.add_argument("--candidates", type=Path, default=config.CANDIDATES_PATH)
    e.add_argument("--repo", type=Path, default=config.DEFAULT_CORPUS_REPO)
    e.add_argument("--out", type=Path, default=WORKLIST_PATH)
    e.set_defaults(func=cmd_emit)

    f = sub.add_parser("freeze", help="validate agent verdicts -> labels.json")
    f.add_argument("--model-id", required=True,
                   help="the model that drove the labeling (provenance, F10)")
    f.add_argument("--candidates", type=Path, default=config.CANDIDATES_PATH)
    f.add_argument("--verdicts", type=Path, default=VERDICTS_PATH)
    f.add_argument("--out", type=Path, default=config.LABELS_PATH)
    f.set_defaults(func=cmd_freeze)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
