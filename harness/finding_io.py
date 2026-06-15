"""finding_io.py — deterministic I/O for the AGENT-DRIVEN finding panel (no LLM).

Slice 1 (step 2) of the finding-eval harness (docs/spec-eval-harness.md). The
sibling of label_io.py, but the unit is a pry *finding* (a welded-at-demand
boundary) instead of a commit, and labeling is a **3-persona panel** that gets
**reconciled** (majority -> tie-break -> arbiter), not a single pass.

The panel is the coding agent (3 subagent personas); this script only does the
deterministic plumbing around it (E2: no harness script calls an LLM or holds a
credential):

  * `emit`      — write a BLINDED worklist from a `pry map` JSON: the
                  demand-welded findings (PQ3 sampling) + a control sample of
                  pry-SEAMED findings (E4), each as {id, file, line, kind,
                  source_context}. The worklist hides pry's verdict bit
                  (class/demand/input_sim) — weak blinding (E4). Carries one
                  rubric per persona; the neutral rubric never names pry/weld/seam.
  * `reconcile` — read the 3 persona verdict files, majority-vote (>=2/3) each
                  finding. A 1-1-1 split writes a tie-break worklist (exit 3); a
                  still-tied set after the tie-break writes an arbiter worklist
                  (exit 4); a residual tie is marked AMBIGUOUS/undecidable. On
                  full resolution writes finding_reconciled.json (exit 0).
  * `freeze`    — validate the reconciled set (pure schema/completeness check,
                  NEVER adjudicates) and write the provenance-stamped
                  finding_labels.json. Refuses (exit 1) on any incomplete or
                  malformed entry (AC1). Retains the per-finding votes (audit).

`reconcile`/`freeze` re-join to the original `pry map` by finding id to recover
the hidden group (demand-welded vs seamed-control) and report precision over the
demand-welded subset (SC2) — the blinded worklist never carried it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import config

WORKLIST_PATH = config.EVAL_DIR / "finding_worklist.json"
RECONCILED_PATH = config.EVAL_DIR / "finding_reconciled.json"
TIEBREAK_WORKLIST_PATH = config.EVAL_DIR / "finding_tiebreak_worklist.json"
ARBITER_WORKLIST_PATH = config.EVAL_DIR / "finding_arbiter_worklist.json"
LABELS_PATH = config.EVAL_DIR / "finding_labels.json"

CONFIDENCE = {"high", "medium", "low"}

# Exit codes (so the emit -> label -> reconcile -> freeze loop is scriptable).
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NEEDS_TIEBREAK = 3
EXIT_NEEDS_ARBITER = 4

# --- per-persona rubrics (PQ2) ------------------------------------------------
# Two taxonomy lenses keyed to the testability question; one NEUTRAL lens that
# never names pry/weld/seam (breaks rubric-circularity, E4). All three emit the
# same 4-way label so reconcile stays mechanical; the neutral lens's wording —
# not a separate vocabulary — is what keeps it independent.
_TAXONOMY_DEFN = (
    "GENUINE = a real failure at this boundary call that a test cannot make "
    "happen, because the call is wired straight into the logic with nothing to "
    "substitute, and the surrounding code is on a path that has to handle "
    "failure. FALSE-WELD = the failure CAN already be substituted here (the "
    "dependency arrives via a parameter, an injected client/factory/interface, "
    "or is otherwise replaceable) — so it is already testable. COSMETIC = a real "
    "un-substitutable boundary value but with no failure worth injecting (a "
    "display/record value such as a timestamp written to a field, or "
    "randomness used only for a temp name). AMBIGUOUS = the shown context cannot "
    "decide between these."
)
PERSONA_RUBRICS = {
    "pragmatic": (
        "You are reviewing whether each finding marks a real testability gap. "
        + _TAXONOMY_DEFN
        + " Judge pragmatically from the source context: would a maintainer "
        "writing a failure test actually be blocked here? Return for each id "
        "{label, confidence: high|medium|low, reason: <one short clause>}."
    ),
    "skeptic": (
        "You are a skeptic trying to DISQUALIFY each finding as a genuine "
        "testability gap. " + _TAXONOMY_DEFN + " Actively look for an existing "
        "seam (an injected dependency, a parameter, a replaceable client) that "
        "makes it FALSE-WELD, or a display/record use that makes it COSMETIC; "
        "default to the lower-severity reading when the context is borderline. "
        "Return for each id {label, confidence: high|medium|low, reason: <one "
        "short clause>}."
    ),
    # NEUTRAL: framed as plain injectability, no pry/weld/seam vocabulary, no
    # reference to a classifier's verdict. Same 4 labels, defined operationally.
    "neutral": (
        "For each code location below, answer one question: if you were writing "
        "a test, could you make this external operation FAIL on demand without "
        "editing the function under test? Use exactly these answers: GENUINE = "
        "no, you could not — the operation is called directly and there is no "
        "input/parameter/object you could swap to force a failure, and the code "
        "around it is handling or guarding against failure. FALSE-WELD = yes, "
        "you could — the thing that performs the operation is passed in or "
        "otherwise replaceable in a test. COSMETIC = the operation cannot be "
        "swapped but nothing about its failure matters here (its value is only "
        "displayed or stored, never acted on). AMBIGUOUS = you cannot tell from "
        "what is shown. Return for each id {label, confidence: high|medium|low, "
        "reason: <one short clause>}."
    ),
}
TIEBREAK_RUBRIC = (
    "These findings split three ways. Pick the single best label AMONG THE "
    "LABELS THE PANEL ALREADY USED for that id (shown as `candidate_labels`). "
    + _TAXONOMY_DEFN
    + " Return for each id {label, confidence, reason}; label MUST be one of "
    "that id's candidate_labels."
)
ARBITER_RUBRIC = (
    "Final arbitration. For each id the tie-break did not resolve, choose the "
    "single most defensible label. " + _TAXONOMY_DEFN + " Return for each id "
    "{label, confidence, reason}."
)


def _combined_rubric_hash() -> str:
    """Provenance hash over all persona rubrics + taxonomy + escalation rubrics."""
    blob = json.dumps(
        {"personas": PERSONA_RUBRICS, "tiebreak": TIEBREAK_RUBRIC,
         "arbiter": ARBITER_RUBRIC},
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def finding_id(row: dict) -> str:
    """Stable id = the map's own sort key. Hides class/demand (blinding)."""
    return f"{row['file']}:{row['line']}:{row['col']}:{row['kind']}"


def _source_context(repo: Path, row: dict) -> str:
    """N lines around file:line, with a '>>' marker on the boundary line.

    Reveals only location + surrounding code — never pry's verdict. Best-effort:
    a missing/unreadable file yields an explicit placeholder rather than crashing
    (the panel can still label AMBIGUOUS)."""
    path = repo / row["file"]
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"<source unavailable: {exc.strerror or exc}>"
    lines = text.splitlines()
    target = row["line"]  # 1-indexed (tree-sitter convention via main.rs)
    lo = max(1, target - config.FINDING_CONTEXT_LINES)
    hi = min(len(lines), target + config.FINDING_CONTEXT_LINES)
    out = []
    for n in range(lo, hi + 1):
        mark = ">>" if n == target else "  "
        out.append(f"{mark}{n:>5}| {lines[n - 1]}")
    ctx = "\n".join(out)
    return ctx[: config.FINDING_CONTEXT_CHAR_CAP]


def _stride_sample(rows: list[dict], fraction: float, floor: int = 0) -> list[dict]:
    """Deterministic ~`fraction` sample via a fixed stride (no RNG, so the
    worklist is byte-reproducible). `rows` must already be in a stable order."""
    n = len(rows)
    if n == 0:
        return []
    # ceil (not round) so the sample is always >= `fraction` of the pool — PQ3
    # says "clock = >=25% sample", and round() would zero a 1- or 2-item stratum.
    want = max(floor, math.ceil(n * fraction))
    want = min(want, n)
    if want <= 0:
        return []
    if want >= n:
        return list(rows)
    # even stride across the sorted list -> representative + reproducible
    step = n / want
    picked = [rows[min(n - 1, int(round(i * step)))] for i in range(want)]
    # de-dup (rounding can collide) while preserving order
    seen, uniq = set(), []
    for r in picked:
        k = finding_id(r)
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


def _load_map(map_path: Path) -> tuple[list[dict], str]:
    data = json.loads(map_path.read_text())
    rows = data.get("findings")
    if rows is None:
        sys.exit(f"{map_path} has no `findings` array — run `pry map` WITHOUT "
                 f"--summary-only.")
    corpus = data.get("corpus", str(map_path))
    return rows, corpus


def _select(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Returns (graded_demand_welds, seamed_control), both deterministically
    ordered. PQ3: non-clock demand-welds = census; clock demand-welds = stride
    sample; demand-seamed = stride control sample (E4)."""
    def key(r):
        return (r["file"], r["line"], r["col"], r["kind"])

    demand_welds = sorted(
        (r for r in rows if r.get("demand") and r.get("class") == "welded"),
        key=key,
    )
    nonclock = [r for r in demand_welds if r["kind"] != "clock"]
    clock = [r for r in demand_welds if r["kind"] == "clock"]
    graded = nonclock + _stride_sample(clock, config.FINDING_CLOCK_SAMPLE_FRACTION)
    graded.sort(key=key)

    demand_seamed = sorted(
        (r for r in rows if r.get("demand") and r.get("class") == "seamed"),
        key=key,
    )
    control = _stride_sample(
        demand_seamed,
        config.FINDING_SEAMED_CONTROL_FRACTION,
        config.FINDING_SEAMED_CONTROL_FLOOR,
    )
    return graded, control


def _select_demoted(rows: list[dict]) -> list[dict]:
    """Slice 2 (E5) filter-recall pool: the DEMOTED welded findings — class=welded,
    demand=false, in a filter-demotable kind (clock/random). These are exactly what
    the precision filters (cosmetic-clock / logsink / duration / cosmetic-random)
    pushed out of the demand subset; any panel-GENUINE here is a recall MISS. The
    fileio/env diagnostic swamp is excluded (demand=false by catalog, never demoted).
    Clock is stride-sampled heavier; random is a small known-COSMETIC control."""
    def key(r):
        return (r["file"], r["line"], r["col"], r["kind"])

    demoted = sorted(
        (r for r in rows if r.get("class") == "welded" and not r.get("demand")
         and r["kind"] in config.FINDING_DEMOTED_KINDS),
        key=key,
    )
    clock = [r for r in demoted if r["kind"] == "clock"]
    rand = [r for r in demoted if r["kind"] == "random"]
    sample = (_stride_sample(clock, config.FINDING_DEMOTED_CLOCK_FRACTION)
              + _stride_sample(rand, config.FINDING_DEMOTED_RANDOM_FRACTION))
    sample.sort(key=key)
    return sample


# --- emit ---------------------------------------------------------------------
def cmd_emit(args) -> int:
    rows, corpus = _load_map(args.map)
    if args.pool == "demoted":
        items = _select_demoted(rows)
        graded, control = items, []   # for the count message below
    else:
        graded, control = _select(rows)
        items = graded + control

    ids = [finding_id(r) for r in items]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        sys.exit(f"finding-id collision ({len(dupes)}, e.g. {dupes[0]}) — two "
                 f"findings share file:line:col:kind; cannot blind safely.")

    # blinded: NO class/demand/input_sim/reason. Sorted by id so welded and
    # seamed-control are interleaved, not grouped (the verdict bit stays hidden).
    blinded = sorted(
        ({"id": finding_id(r), "file": r["file"], "line": r["line"],
          "kind": r["kind"], "source_context": _source_context(args.repo, r)}
         for r in items),
        key=lambda d: d["id"],
    )
    worklist = {
        "harness_version": config.FINDING_HARNESS_VERSION,
        "corpus": corpus,
        "pool": args.pool,
        "rubric_hash": _combined_rubric_hash(),
        "personas": list(config.FINDING_PERSONAS),
        "persona_rubrics": PERSONA_RUBRICS,
        "instructions": (
            "Each of the 3 personas labels EVERY finding in `findings` using its "
            "own rubric in `persona_rubrics`. Write one verdicts file per persona "
            "({id: {label, confidence, reason}}) to "
            f"{config.EVAL_DIR}/finding_verdicts.<persona>.json, then run: "
            "python3 harness/finding_io.py reconcile."
        ),
        "findings": blinded,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(worklist, indent=2, sort_keys=True) + "\n")
    breakdown = (f"{len(graded)} demoted-welded (filter-recall pool)"
                 if args.pool == "demoted"
                 else f"{len(graded)} demand-welded graded + {len(control)} seamed-control")
    print(f"emitted {len(blinded)} findings ({breakdown}), "
          f"blinded, rubric {_combined_rubric_hash()} -> {args.out}")
    print(f"panel: {len(config.FINDING_PERSONAS)} personas "
          f"({', '.join(config.FINDING_PERSONAS)}) each write "
          f"finding_verdicts.<persona>.json, then run: "
          f"python3 harness/finding_io.py reconcile")
    return EXIT_OK


# --- reconcile ----------------------------------------------------------------
def _verdict_problems(ver: dict | None) -> list[str]:
    """Schema check for ONE verdict (panel OR escalation). Pure; never adjudicates.
    Escalation rounds (tie-break/arbiter) get the SAME validation as the panel —
    they are where a single vote becomes ground truth, so they need it most."""
    if ver is None:
        return ["missing verdict"]
    probs = []
    if ver.get("label") not in config.FINDING_LABELS:
        probs.append(f"label not in {list(config.FINDING_LABELS)}")
    if ver.get("confidence") not in CONFIDENCE:
        probs.append(f"confidence not in {sorted(CONFIDENCE)}")
    if not isinstance(ver.get("reason"), str) or not ver.get("reason"):
        probs.append("reason missing/empty")
    return probs


def _read_verdicts(path: Path, ids: set[str], who: str, errors: list[str]) -> dict:
    if not path.exists():
        sys.exit(f"verdicts file {path} not found — {who} must label first "
                 f"(emit, then label every finding).")
    v = json.loads(path.read_text())
    if "verdicts" in v and isinstance(v["verdicts"], dict):
        v = v["verdicts"]
    for fid in ids:
        for p in _verdict_problems(v.get(fid)):
            errors.append(f"{who}: {fid}: {p}")
    extra = set(v) - ids
    if extra:
        errors.append(f"{who}: {len(extra)} verdicts for unknown ids "
                      f"(e.g. {sorted(extra)[0]})")
    return v


def _majority(votes: list[str]) -> str | None:
    """Strict unique plurality with count>=2, else None (no majority yet)."""
    counts = {lbl: votes.count(lbl) for lbl in set(votes)}
    top = max(counts.values())
    if top < 2:
        return None
    winners = [lbl for lbl, c in counts.items() if c == top]
    return winners[0] if len(winners) == 1 else None


def cmd_reconcile(args) -> int:
    worklist = json.loads(args.worklist.read_text())
    ids = {f["id"] for f in worklist["findings"]}
    if not ids:
        sys.exit("worklist has no findings — emit first.")

    errors: list[str] = []
    persona_v = {
        p: _read_verdicts(args.eval_dir / f"finding_verdicts.{p}.json",
                          ids, p, errors)
        for p in config.FINDING_PERSONAS
    }
    if errors:
        print(f"RECONCILE REFUSED — {len(errors)} problem(s):", file=sys.stderr)
        for e in errors[:20]:
            print(f"  - {e}", file=sys.stderr)
        return EXIT_ERROR

    # optional escalation rounds (present only after the agent labels them)
    tiebreak_v = _read_optional(args.eval_dir / "finding_tiebreak_verdicts.json")
    arbiter_v = _read_optional(args.eval_dir / "finding_arbiter_verdicts.json")

    reconciled, need_tiebreak, need_arbiter = {}, [], []
    escalation_errors: list[str] = []
    for fid in sorted(ids):
        panel = [persona_v[p][fid]["label"] for p in config.FINDING_PERSONAS]
        votes = dict(zip(config.FINDING_PERSONAS, panel))
        win = _majority(panel)
        if win is not None:
            decision = "unanimous" if len(set(panel)) == 1 else "majority"
            reconciled[fid] = {"votes": votes, "label": win, "decision": decision}
            continue
        # 1-1-1 split -> tie-break. Absent = needs labeling (re-emit worklist);
        # present-but-malformed = refuse (don't let a bad vote become truth).
        tb = tiebreak_v.get(fid)
        if tb is None:
            need_tiebreak.append((fid, sorted(set(panel))))
            continue
        tb_probs = _verdict_problems(tb)
        if tb_probs:
            escalation_errors += [f"tiebreak {fid}: {p}" for p in tb_probs]
            continue
        with_tb = panel + [tb["label"]]
        win = _majority(with_tb)
        if win is not None:
            reconciled[fid] = {"votes": {**votes, "tiebreak": tb["label"]},
                               "label": win, "decision": "tiebreak"}
            continue
        # still tied (e.g. judge picked a 4th label) -> arbiter
        ab = arbiter_v.get(fid)
        if ab is None:
            need_arbiter.append((fid, sorted(set(with_tb))))
            continue
        ab_probs = _verdict_problems(ab)
        if ab_probs:
            escalation_errors += [f"arbiter {fid}: {p}" for p in ab_probs]
            continue
        reconciled[fid] = {
            "votes": {**votes, "tiebreak": tb["label"], "arbiter": ab["label"]},
            "label": ab["label"], "decision": "arbiter",
        }

    if escalation_errors:
        print(f"RECONCILE REFUSED — {len(escalation_errors)} escalation "
              f"problem(s):", file=sys.stderr)
        for e in escalation_errors[:20]:
            print(f"  - {e}", file=sys.stderr)
        return EXIT_ERROR
    if need_tiebreak:
        _write_escalation(args.eval_dir / "finding_tiebreak_worklist.json",
                          worklist, need_tiebreak, TIEBREAK_RUBRIC, "tiebreak")
        print(f"{len(need_tiebreak)} finding(s) split 1-1-1 -> wrote tie-break "
              f"worklist. Label them to finding_tiebreak_verdicts.json, then "
              f"re-run reconcile.", file=sys.stderr)
        return EXIT_NEEDS_TIEBREAK
    if need_arbiter:
        _write_escalation(args.eval_dir / "finding_arbiter_worklist.json",
                          worklist, need_arbiter, ARBITER_RUBRIC, "arbiter")
        print(f"{len(need_arbiter)} finding(s) still tied after tie-break -> "
              f"wrote arbiter worklist. Label them to "
              f"finding_arbiter_verdicts.json, then re-run reconcile.",
              file=sys.stderr)
        return EXIT_NEEDS_ARBITER

    out = {
        "harness_version": config.FINDING_HARNESS_VERSION,
        "corpus": worklist["corpus"],
        "rubric_hash": worklist["rubric_hash"],
        "reconciled": reconciled,
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    by_decision = {}
    for r in reconciled.values():
        by_decision[r["decision"]] = by_decision.get(r["decision"], 0) + 1
    print(f"reconciled {len(reconciled)} findings -> {args.out}")
    print(f"  decisions: " + ", ".join(f"{k}={v}" for k, v in
                                       sorted(by_decision.items())))
    return EXIT_OK


def _read_optional(path: Path) -> dict:
    if not path.exists():
        return {}
    v = json.loads(path.read_text())
    if "verdicts" in v and isinstance(v["verdicts"], dict):
        v = v["verdicts"]
    return v


def _write_escalation(path: Path, worklist: dict, need: list[tuple],
                      rubric: str, kind: str) -> None:
    by_id = {f["id"]: f for f in worklist["findings"]}
    items = [{**by_id[fid], "candidate_labels": cands} for fid, cands in need]
    items.sort(key=lambda d: d["id"])
    path.write_text(json.dumps({
        "harness_version": config.FINDING_HARNESS_VERSION,
        "corpus": worklist["corpus"],
        "round": kind,
        "rubric": rubric,
        "findings": items,
    }, indent=2, sort_keys=True) + "\n")


# --- freeze -------------------------------------------------------------------
def cmd_freeze(args) -> int:
    if not args.reconciled.exists():
        sys.exit(f"reconciled file {args.reconciled} not found — run reconcile "
                 f"first (it resolves the panel vote).")
    rec = json.loads(args.reconciled.read_text())["reconciled"]
    rows, corpus = _load_map(args.map)
    by_id = {finding_id(r): r for r in rows}

    worklist = json.loads(args.worklist.read_text())
    want_ids = {f["id"] for f in worklist["findings"]}

    # --- completeness + schema validation (pure; never adjudicates) ---------
    errors = []
    for fid in want_ids:
        r = rec.get(fid)
        if r is None:
            errors.append(f"missing reconciled label for {fid}")
            continue
        if r.get("label") not in config.FINDING_LABELS:
            errors.append(f"{fid}: label not in {list(config.FINDING_LABELS)}")
        if not isinstance(r.get("votes"), dict) or len(r.get("votes", {})) < 3:
            errors.append(f"{fid}: votes missing/incomplete (need >=3)")
        if fid not in by_id:
            errors.append(f"{fid}: not present in the pry map (corpus drift)")
    extra = set(rec) - want_ids
    if extra:
        errors.append(f"{len(extra)} reconciled labels for unknown ids "
                      f"(e.g. {sorted(extra)[0]})")
    if errors:
        print(f"FREEZE REFUSED — {len(errors)} problem(s):", file=sys.stderr)
        for e in errors[:20]:
            print(f"  - {e}", file=sys.stderr)
        return EXIT_ERROR

    labels = {}
    for fid in sorted(want_ids):
        r, row = rec[fid], by_id[fid]
        if row.get("class") == "welded":
            # demand=true -> precision pool; demand=false -> the DEMOTED pool a
            # filter pushed out (Slice 2 filter-recall): a GENUINE here is a miss.
            group = "demand_weld" if row.get("demand") else "demoted_weld"
        else:
            group = "seamed_control"
        labels[fid] = {
            "file": row["file"], "line": row["line"], "kind": row["kind"],
            "group": group,                # recovered from the map (was blinded)
            "pry_reason": row.get("reason", ""),  # which rule classed it (audit;
            # e.g. a demoted_weld GENUINE shows the filter that over-demoted it)
            "label": r["label"],
            "decision": r.get("decision", "majority"),
            "votes": r["votes"],
        }

    out = {
        "harness_version": config.FINDING_HARNESS_VERSION,
        "corpus": corpus,
        "labeler_model": args.model_id,
        "personas": list(config.FINDING_PERSONAS),
        "rubric_hash": _combined_rubric_hash(),
        "labels": labels,
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

    print(f"frozen {len(labels)} finding labels (model={args.model_id}, "
          f"rubric={_combined_rubric_hash()}) -> {args.out}")
    # precision is over the demand-weld group only (seamed-control is the
    # false-seam probe, not part of the precision denominator) — SC2.
    welds = [v for v in labels.values() if v["group"] == "demand_weld"]
    if welds:
        genuine = sum(1 for v in welds if v["label"] == "GENUINE")
        decided = sum(1 for v in welds if v["label"] != "AMBIGUOUS")
        prec = (genuine / decided) if decided else 0.0
        print(f"  demand-weld precision: {genuine}/{decided} = {prec:.2%} GENUINE "
              f"(of decided; {len(welds) - decided} AMBIGUOUS excluded)")
    # demoted pool (Slice 2 filter-recall): a GENUINE here is a weld a precision
    # filter wrongly demoted — a recall MISS. Zero = the filters held recall (E5).
    demoted = [v for v in labels.values() if v["group"] == "demoted_weld"]
    if demoted:
        misses = sum(1 for v in demoted if v["label"] == "GENUINE")
        d_decided = sum(1 for v in demoted if v["label"] != "AMBIGUOUS")
        print(f"  DEMOTED-pool filter-recall misses: {misses}/{d_decided} decided "
              f"labeled GENUINE (a genuine weld a filter demoted; 0 = recall held)")
    ctrl = [v for v in labels.values() if v["group"] == "seamed_control"]
    if ctrl:
        false_seam = sum(1 for v in ctrl if v["label"] == "GENUINE")
        print(f"  seamed-control false-seams: {false_seam}/{len(ctrl)} flagged "
              f"GENUINE (pry mis-classed as seamed)")
    return EXIT_OK


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("emit", help="blinded finding worklist from a pry map")
    e.add_argument("--map", type=Path, required=True,
                   help="`pry map <repo>` JSON output (NOT --summary-only)")
    e.add_argument("--repo", type=Path, required=True,
                   help="repo root the map paths are relative to (for context)")
    e.add_argument("--pool", choices=("demand", "demoted"), default="demand",
                   help="demand = demand-welds + seamed-control (Slice 1 precision); "
                        "demoted = the demand=false welded pool (Slice 2 filter-recall)")
    e.add_argument("--out", type=Path, default=WORKLIST_PATH)
    e.set_defaults(func=cmd_emit)

    r = sub.add_parser("reconcile", help="majority-vote the 3 persona verdicts")
    r.add_argument("--worklist", type=Path, default=WORKLIST_PATH)
    r.add_argument("--eval-dir", type=Path, default=config.EVAL_DIR,
                   help="dir holding finding_verdicts.<persona>.json")
    r.add_argument("--out", type=Path, default=RECONCILED_PATH)
    r.set_defaults(func=cmd_reconcile)

    f = sub.add_parser("freeze", help="validate reconciled set -> finding_labels.json")
    f.add_argument("--model-id", required=True,
                   help="the model that drove the panel (provenance, F16)")
    f.add_argument("--map", type=Path, required=True,
                   help="the SAME pry map used for emit (recovers group/precision)")
    f.add_argument("--worklist", type=Path, default=WORKLIST_PATH)
    f.add_argument("--reconciled", type=Path, default=RECONCILED_PATH)
    f.add_argument("--out", type=Path, default=LABELS_PATH)
    f.set_defaults(func=cmd_freeze)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
