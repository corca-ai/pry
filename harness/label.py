"""label.py — LLM precision filter over mined candidates (PAID).

Slice 0 of the pry validation harness (docs/spec-layer0.md, F9/F10/P1b). Takes
mine.py's recall-oriented candidate set and asks the labeler whether each commit
is *actually* an error-handling bugfix, producing the frozen ground-truth labels
the kill-gate computation reads.

Spends money. Gated three ways:
  * refuses to run without an explicit --yes (prints the plan and exits),
  * resolves a credential or refuses,
  * idempotent: re-running resumes, never re-pays for an already-labeled sha.

Also labels the P1b mining-recall sample (a slice of non-matched bugfix commits)
so repo_fit.py can estimate error-handling fixes the lexical miner missed.

Determinism note: labeling is non-deterministic, so its OUTPUT is frozen and
checked in (model id + prompt hash + corpus head + per-sha verdicts). Downstream
scoring reads only the frozen file (F9).

Usage:
    python3 harness/label.py --dry-run     # build+print one prompt, no spend
    python3 harness/label.py --yes         # label all (paid), resumable
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import config

PROMPT_TEMPLATE = """\
You are labeling a git commit for a software-defect study. We are looking ONLY \
for commits that FIX a bug in *error-handling / failure-handling* logic: the \
handling of an error or failure the program has already encountered or could \
encounter at a boundary (network, file/IO, subprocess, DB, clock, randomness). \
Examples that COUNT: fixing a swallowed exception, a wrong/missing except \
clause, a missing rollback or cleanup after a failure, a broken retry/timeout, \
mishandling a boundary call's failure, log-and-continue on a path that should \
abort. Examples that do NOT count: adding a new feature, refactors, fixing \
pure business logic with no failure-handling aspect, test-only changes, docs, \
config, formatting, or adding error handling to brand-new code (no prior bug).

Commit subject: {subject}

Unified diff (Python files, may be truncated):
```diff
{diff}
```

Respond with ONLY a JSON object, no prose:
{{"is_error_handling_fix": true|false, "confidence": "high"|"medium"|"low", \
"reason": "<one short clause>"}}"""


def _prompt_hash() -> str:
    return hashlib.sha256(PROMPT_TEMPLATE.encode()).hexdigest()[:16]


def _load_credential() -> bool:
    """Ensure a credential is visible to the SDK. Loads repo-root .env if present.

    Returns True if a credential is available. Env vars set here persist for the
    current process (and thus the SDK), which is what matters.
    """
    import os

    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    env_path = config.HARNESS_DIR.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return bool(os.environ.get("ANTHROPIC_API_KEY")
                or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def _diff(repo: Path, sha: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), "show", "--format=", "--unified=3",
         sha, "--", config.PYTHON_PATHSPEC],
        check=True, capture_output=True, text=True,
    ).stdout
    return out[: config.LABEL_DIFF_CHAR_CAP]


def _build_prompt(repo: Path, commit: dict) -> str:
    return PROMPT_TEMPLATE.format(
        subject=commit["subject"], diff=_diff(repo, commit["sha"])
    )


def _parse_verdict(text: str) -> dict:
    """Pull the first JSON object out of the model's reply."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"is_error_handling_fix": None, "confidence": "low",
                "reason": "unparseable: " + text[:80]}
    try:
        obj = json.loads(text[start: end + 1])
    except json.JSONDecodeError:
        return {"is_error_handling_fix": None, "confidence": "low",
                "reason": "json error: " + text[:80]}
    return {
        "is_error_handling_fix": obj.get("is_error_handling_fix"),
        "confidence": obj.get("confidence", "low"),
        "reason": str(obj.get("reason", ""))[:200],
    }


def _label_one(client, repo: Path, commit: dict) -> dict:
    resp = client.messages.create(
        model=config.LABELER_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": _build_prompt(repo, commit)}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return _parse_verdict(text)


def _load_existing(out: Path) -> dict:
    if out.exists():
        return json.loads(out.read_text())
    return {}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", type=Path, default=config.CANDIDATES_PATH)
    ap.add_argument("--out", type=Path, default=config.LABELS_PATH)
    ap.add_argument("--repo", type=Path, default=config.DEFAULT_CORPUS_REPO)
    ap.add_argument("--dry-run", action="store_true",
                    help="build+print one prompt, make no API call, spend nothing")
    ap.add_argument("--yes", action="store_true",
                    help="required to actually spend money labeling")
    args = ap.parse_args()

    data = json.loads(args.candidates.read_text())
    candidates = [{**c, "group": "candidate"} for c in data["candidates"]]
    sample = [{**c, "group": "recall_sample"}
              for c in data["non_matched_bugfix"][: config.MINING_RECALL_SAMPLE]]
    work = candidates + sample

    if args.dry_run:
        print("=== DRY RUN (no API call, $0) ===")
        print(f"prompt hash: {_prompt_hash()}  model: {config.LABELER_MODEL}")
        print(f"would label {len(work)} commits "
              f"({len(candidates)} candidates + {len(sample)} recall sample)\n")
        print("--- example prompt (first candidate) ---")
        print(_build_prompt(args.repo, candidates[0]))
        return

    if not args.yes:
        sys.exit("refusing to spend without --yes. "
                 "Run `python3 harness/doctor.py` to see the cost, then re-run "
                 "with --yes. (Use --dry-run to preview a prompt for free.)")

    if not _load_credential():
        sys.exit("no ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN. "
                 "Put it in pry/.env (gitignored) as ANTHROPIC_API_KEY=sk-... "
                 "or export it, then re-run.")

    import anthropic

    client = anthropic.Anthropic()
    existing = _load_existing(args.out)
    results = dict(existing.get("labels", {}))

    done = sum(1 for c in work if c["sha"] in results)
    print(f"labeling {len(work)} commits with {config.LABELER_MODEL} "
          f"({done} already done, resuming)...")

    for i, commit in enumerate(work, 1):
        if commit["sha"] in results:
            continue
        verdict = _label_one(client, args.repo, commit)
        results[commit["sha"]] = {
            "subject": commit["subject"],
            "date": commit["date"],
            "group": commit["group"],
            **verdict,
        }
        # incremental freeze so a crash/rate-limit resumes without re-paying
        args.out.write_text(json.dumps({
            "corpus": data["corpus"],
            "corpus_head": data["corpus_head"],
            "labeler_model": config.LABELER_MODEL,
            "prompt_hash": _prompt_hash(),
            "labels": results,
        }, indent=2, sort_keys=True) + "\n")
        if i % 10 == 0 or i == len(work):
            print(f"  {i}/{len(work)} labeled")

    pos = sum(1 for v in results.values()
              if v["group"] == "candidate" and v["is_error_handling_fix"])
    recall_hits = sum(1 for v in results.values()
                      if v["group"] == "recall_sample" and v["is_error_handling_fix"])
    print(f"\ndone. {pos} confirmed error-handling fixes (of {len(candidates)} "
          f"candidates); P1b recall sample: {recall_hits}/{len(sample)} "
          f"non-matched commits were actually error-handling fixes the miner missed.")
    print(f"frozen -> {args.out}")


if __name__ == "__main__":
    main()
