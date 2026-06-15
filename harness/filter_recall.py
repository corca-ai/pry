"""filter_recall.py — re-derive the Slice 2 filter-recall metric from the frozen
labelsets (AC3, no LLM). Deterministic; the gate's reproduce command.

Filter-recall (E5) is the inverse of precision: did a precision filter DEMOTE a
genuine weld? Two frozen inputs, both panel-labeled once (E8) then frozen:

  * `<repo>-labels.json`          — the demand-weld pool (demand=true welded). Its
                                    GENUINE labels are welds the filters KEPT.
  * `<repo>-barepool-labels.json` — the DEMOTED pool (demand=false welded, sampled).
                                    Its GENUINE labels are welds the filters DEMOTED
                                    — i.e. filter-recall MISSES.

The gate rule (SC3): a lever ships only if dev precision rises AND held-out
filter-recall does not drop — concretely, a new lever must not push any
bare-pool finding the panel labeled GENUINE from demand=true to demand=false.
This script reports the BASELINE (the currently-shipped filters' recall); a
candidate lever is checked by re-running it after the lever and confirming the
demoted-pool GENUINE count did not rise.

Usage:  python3 harness/filter_recall.py
"""

from __future__ import annotations

import json

import config

REPOS = ("outline", "flowise", "continue", "librechat")


def _load(name: str) -> dict:
    return json.loads((config.EVAL_DIR / name).read_text())["labels"]


def main() -> None:
    # demand-weld pool: GENUINE = welds the filters KEPT (precision numerator).
    kept_genuine = kept_decided = 0
    # demoted pool: GENUINE = welds the filters DEMOTED (filter-recall misses).
    demoted_genuine = demoted_decided = 0
    by_kind_miss: dict[str, list[int]] = {}
    per_repo = []

    for repo in REPOS:
        dw = _load(f"{repo}-labels.json")
        bp = _load(f"{repo}-barepool-labels.json")

        kg = sum(1 for v in dw.values()
                 if v["group"] == "demand_weld" and v["label"] == "GENUINE")
        kd = sum(1 for v in dw.values()
                 if v["group"] == "demand_weld" and v["label"] != "AMBIGUOUS")
        kept_genuine += kg
        kept_decided += kd

        mg = sum(1 for v in bp.values()
                 if v["group"] == "demoted_weld" and v["label"] == "GENUINE")
        md = sum(1 for v in bp.values()
                 if v["group"] == "demoted_weld" and v["label"] != "AMBIGUOUS")
        demoted_genuine += mg
        demoted_decided += md
        for v in bp.values():
            if v["group"] == "demoted_weld":
                slot = by_kind_miss.setdefault(v["kind"], [0, 0])
                slot[1] += 1
                if v["label"] == "GENUINE":
                    slot[0] += 1
        per_repo.append((repo, kg, kd, mg, md))

    print("Slice 2 — filter-recall (E5), from the frozen labelsets:\n")
    print(f"  {'repo':10s}  demand-weld GENUINE/decided   demoted-pool MISSES/decided")
    for repo, kg, kd, mg, md in per_repo:
        print(f"  {repo:10s}  {kg:>3}/{kd:<3} kept{'':14}{mg:>3}/{md:<3} demoted-genuine")
    print(f"  {'POOLED':10s}  {kept_genuine}/{kept_decided} kept"
          f"{'':14}{demoted_genuine}/{demoted_decided} demoted-genuine")

    print("\n  demoted-pool misses by kind (a GENUINE here = a filter over-demoted it):")
    for kind, (g, n) in sorted(by_kind_miss.items()):
        rate = f"{g / n:.1%}" if n else "—"
        print(f"    {kind:8s}: {g}/{n} GENUINE  ({rate})")

    # filter-recall over the labeled sample (census kept + sampled demoted). The
    # demoted side is a stride sample (see config.FINDING_DEMOTED_*), so this mixes
    # a census with a sample — read it as "of the genuine welds in the labeled
    # union, the fraction NOT demoted", not an unbiased population recall.
    union_g = kept_genuine + demoted_genuine
    recall = kept_genuine / union_g if union_g else 1.0
    print(f"\n  filter-recall (labeled union, sample-weighted): "
          f"{kept_genuine}/{union_g} = {recall:.1%} of genuine welds kept")
    print("  GATE (SC3): a new lever must NOT raise the demoted-pool GENUINE count "
          "(re-run after applying the lever to confirm).")


if __name__ == "__main__":
    main()
