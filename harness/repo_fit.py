"""repo_fit.py — the analyzer-free repo-fit gate (Slice 0 verdict).

Slice 0 of the pry validation harness (docs/spec-layer0.md, P1/P1b/SC0). This is
the cheapest possible kill: it answers "does charness even HAVE this bug shape?"
from git history alone, BEFORE any Rust analyzer is written (§9 reframe, §13 A).

Two harness-only signals, both pre-registered:
  * site count vs the floor (config.REPO_FIT_SITE_FLOOR, default 30). Below the
    floor the verdict is "underpowered/inconclusive -> re-target or pull ceal",
    NOT a go/kill on the thesis.
  * P1b mining-recall: of the sampled non-matched bugfix commits, how many the
    labeler says ARE error-handling fixes the lexical miner missed. A small
    candidate set only means "no gradient" if recall is high; if recall is low,
    the miner grepped the wrong shape (§13 A.2) and the verdict is "re-tune the
    miner", not "no bug shape".

Output: fixtures/repo_fit.json + a one-line verdict for the repo-fit axis of
docs/kill-gate.md (F13). This gate does NOT decide the thesis (that needs the
map); it decides whether building the analyzer is even worthwhile.

Usage:
    python3 harness/repo_fit.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import config
from szz import BUG_SITES_PATH


def assess(site_count: int, high_conf_count: int, recall_total: int,
           recall_hits: int, floor: int) -> dict:
    """Pure decision logic (unit-testable without git or the agent).

    The floor (F17) is cleared by HIGH-CONFIDENCE sites only, so a margin-of-few
    win cannot be manufactured by low-confidence yes-votes.
    """
    recall = (recall_hits / recall_total) if recall_total else None
    tot = f"{high_conf_count} high-confidence sites (of {site_count} total)"

    if high_conf_count >= floor:
        axis = "go"
        verdict = (f"PROCEED: {tot} >= floor {floor}. charness has the bug shape; "
                   f"building the analyzer is justified.")
    else:
        axis = "inconclusive"
        if recall is not None and recall >= 0.25:
            verdict = (f"UNDERPOWERED: {tot} < floor {floor} AND the miner missed "
                       f"error-handling fixes ({recall_hits}/{recall_total} "
                       f"non-matched were real). Re-tune the miner before "
                       f"concluding 'no gradient'.")
        else:
            verdict = (f"RE-TARGET: {tot} < floor {floor} and miner recall looks "
                       f"adequate ({recall_hits}/{recall_total} missed). charness "
                       f"may not have this bug shape — pull ceal or change the "
                       f"target, don't build the analyzer.")
    return {
        "repo_fit_axis": axis,
        "site_count": site_count,
        "high_confidence_site_count": high_conf_count,
        "floor": floor,
        "mining_recall_sample": recall_total,
        "mining_recall_hits": recall_hits,
        "mining_recall": round(recall, 3) if recall is not None else None,
        "verdict": verdict,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--labels", type=Path, default=config.LABELS_PATH)
    ap.add_argument("--bug-sites", type=Path, default=BUG_SITES_PATH)
    ap.add_argument("--out", type=Path, default=config.REPO_FIT_PATH)
    ap.add_argument("--floor", type=int, default=config.REPO_FIT_SITE_FLOOR)
    args = ap.parse_args()

    for p in (args.labels, args.bug_sites):
        if not p.exists():
            sys.exit(f"{p} not found — run label.py then szz.py first")

    labels = json.loads(args.labels.read_text())["labels"]
    bug = json.loads(args.bug_sites.read_text())

    # high-confidence fix commits (F17): a site is high-confidence if any of its
    # fix commits was labeled high-confidence.
    high_conf_fix = {sha for sha, v in labels.items()
                     if v["group"] == "candidate" and v["is_error_handling_fix"]
                     and v["confidence"] == "high"}
    high_conf_count = sum(
        1 for s in bug["sites"]
        if any(fc in high_conf_fix for fc in s.get("fix_commits", []))
    )

    recall_total = sum(1 for v in labels.values() if v["group"] == "recall_sample")
    recall_hits = sum(1 for v in labels.values()
                      if v["group"] == "recall_sample" and v["is_error_handling_fix"])

    result = assess(bug["site_count"], high_conf_count, recall_total,
                    recall_hits, args.floor)
    result["corpus"] = bug["corpus"]
    result["corpus_head"] = bug["corpus_head"]

    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print("=== repo-fit gate (analyzer-free) ===")
    print(f"  sites: {result['site_count']}  high-confidence: {high_conf_count}  "
          f"floor: {result['floor']}  axis: {result['repo_fit_axis']}")
    print(f"  mining recall: {recall_hits}/{recall_total}")
    print(f"\n  {result['verdict']}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
