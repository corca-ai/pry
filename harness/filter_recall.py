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

`--remap` is the CODE-REFLECTING gate (lever 3+): it re-runs the freshly-built
`pry map` on the pinned corpus and re-joins by `file:line:col:kind` to the FROZEN
panel labels (the stable oracle — "LLM once -> frozen labelset", E8). The frozen
`label` never moves; only pry's mechanical `demand`/`class` is recomputed. It then
re-derives the same metrics AND the two gate guards a precision lever must hold:
  * demoted-pool GENUINE misses must go DOWN (rescue), never up;
  * NO finding labeled COSMETIC/FALSE-WELD may flip into demand=true (precision
    damage); NO demand-pool GENUINE may flip into demand=false (lost recall).

Usage:  python3 harness/filter_recall.py            # frozen baseline
        python3 harness/filter_recall.py --remap    # re-run pry, re-derive vs oracle
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import config

REPOS = ("outline", "flowise", "continue", "librechat")

# Pinned corpus (re-clone at these SHAs if cleaned — see docs/handoff.md).
CORPUS_ROOT = Path(os.path.expanduser("~/codes/_pry-corpus"))
PRY_BIN = config.HARNESS_DIR.parent / "target" / "release" / "pry"
DEMOTABLE_KINDS = set(config.FINDING_DEMOTED_KINDS)
# The frozen Slice-2 demoted-pool GENUINE miss count (pre-lever-3 baseline). A lever
# may only LOWER this; --remap fails if it rises (see remap()'s SC3 guard).
BASELINE_MISSES = 16


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
          "(re-run `--remap` after applying the lever to confirm).")


# --- --remap: re-run pry, re-join to the frozen oracle labels ------------------
def _run_pry(repo: str) -> dict:
    """Run the freshly-built `pry map` on the pinned corpus repo; key by
    file:line:col:kind (the frozen-label key). Fail loudly if the binary or
    corpus is absent — the gate must not silently pass on a stale map."""
    repo_path = CORPUS_ROOT / repo
    if not PRY_BIN.exists():
        sys.exit(f"pry binary not found at {PRY_BIN} — run `cargo build --release`.")
    if not repo_path.exists():
        sys.exit(f"corpus repo {repo_path} not found — re-clone at the pinned SHA "
                 f"(docs/handoff.md).")
    out = subprocess.run([str(PRY_BIN), "map", str(repo_path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"`pry map {repo_path}` failed (exit {out.returncode}):\n{out.stderr[:500]}")
    data = json.loads(out.stdout)
    return {f"{x['file']}:{x['line']}:{x['col']}:{x['kind']}": x
            for x in data["findings"]}


def remap() -> None:
    """Re-derive the Slice 2 metrics against a fresh pry map, holding the frozen
    panel labels as the oracle. Reports rescues + the two precision-damage guards."""
    misses = 0                 # GENUINE still demoted (welded, demand=false)
    rescued = 0                # GENUINE that a lever moved demoted -> demand
    precision_damage = []      # COSMETIC/FALSE-WELD a lever moved demoted -> demand
    lost_recall = []           # demand-pool GENUINE a change pushed demand -> demoted
    vanished_test = 0          # labeled key gone because lever #2 dropped a test file
    vanished_drift = []        # labeled key gone for any OTHER reason (real drift)
    miss_by_kind: dict[str, int] = {}

    # findings in test files were frozen BEFORE lever #2 (test-file heuristic) shipped;
    # they are now correctly absent from the map (out of scope, R5) — not drift.
    test_markers = (".vitest.", ".e2e.", ".test.", ".spec.", "/test/", "/tests/",
                    "__tests__", ".stories.")

    for repo in REPOS:
        fresh = _run_pry(repo)
        # union of both frozen labelsets: stable label + the OLD group snapshot.
        oracle = {}
        for name in (f"{repo}-labels.json", f"{repo}-barepool-labels.json"):
            oracle.update(_load(name))

        for key, lab in oracle.items():
            f = fresh.get(key)
            if f is None:
                path = key.split(":")[0]
                if any(m in path for m in test_markers):
                    vanished_test += 1
                else:
                    vanished_drift.append(key)
                continue
            is_demoted = (f["class"] == "welded" and not f["demand"]
                          and f["kind"] in DEMOTABLE_KINDS)
            is_demand_weld = (f["class"] == "welded" and f["demand"])
            label, old_group = lab["label"], lab["group"]

            if label == "GENUINE":
                # branch on the OLD group FIRST: a GENUINE that was KEPT (demand_weld)
                # and is now demoted is a REGRESSION (lost_recall), NOT just another
                # demoted-pool miss — must not be masked by the generic miss tally.
                if old_group == "demand_weld":
                    if is_demoted:
                        lost_recall.append((key, f["reason"]))
                    # else still demand-kept -> fine
                elif is_demand_weld:
                    rescued += 1            # was demoted, a lever promoted it -> demand
                elif is_demoted:
                    misses += 1             # was demoted, still demoted -> persistent miss
                    miss_by_kind[f["kind"]] = miss_by_kind.get(f["kind"], 0) + 1
            elif label in ("COSMETIC", "FALSE-WELD"):
                if old_group == "demoted_weld" and is_demand_weld:
                    precision_damage.append((key, label, f["reason"]))

    print("Slice 2 — filter-recall RE-DERIVED from a fresh pry map (oracle = frozen labels):\n")
    print(f"  demoted-pool GENUINE misses (recall holes):  {misses}  "
          f"(frozen baseline was {BASELINE_MISSES})")
    print(f"  rescued (demoted GENUINE -> demand by a lever): {rescued}")
    for kind, g in sorted(miss_by_kind.items()):
        print(f"    still-demoted GENUINE {kind}: {g}")

    ok = True
    print("\n  GATE GUARDS:")
    # the SC3 rule, enforced by the exit code: a lever must not RAISE the demoted-pool
    # GENUINE miss count above the frozen baseline (a non-additive lever that demotes a
    # previously-kept genuine weld would otherwise read "fewer misses elsewhere" green).
    if misses > BASELINE_MISSES:
        ok = False
        print(f"  ✗ RECALL REGRESSED: {misses} demoted-pool GENUINE misses > "
              f"baseline {BASELINE_MISSES}")
    else:
        print(f"  ✓ demoted-pool GENUINE misses {misses} ≤ baseline {BASELINE_MISSES} "
              f"(recall not regressed)")
    if precision_damage:
        ok = False
        print(f"  ✗ PRECISION DAMAGE: {len(precision_damage)} COSMETIC/FALSE-WELD "
              f"flipped demoted -> demand:")
        for k, lbl, r in precision_damage[:10]:
            print(f"      [{lbl}] {k}  ({r})")
    else:
        print("  ✓ no COSMETIC/FALSE-WELD wrongly promoted to demand (precision held)")
    if lost_recall:
        ok = False
        print(f"  ✗ LOST RECALL: {len(lost_recall)} demand-pool GENUINE pushed to "
              f"demoted:")
        for k, r in lost_recall[:10]:
            print(f"      {k}  ({r})")
    else:
        print("  ✓ no demand-pool GENUINE pushed into the demoted pool")
    if vanished_drift:
        ok = False
        print(f"  ✗ {len(vanished_drift)} labeled key(s) absent from the fresh map "
              f"(real drift): e.g. {vanished_drift[0]}")
    else:
        print("  ✓ no non-test labeled finding vanished from the fresh map (no drift)")
    if vanished_test:
        print(f"  · {vanished_test} test-file labeled finding(s) now absent — "
              f"correctly dropped by lever #2 (out of scope, R5)")

    print(f"\n  VERDICT: {'PASS' if ok else 'FAIL'} — misses {misses} "
          f"(baseline {BASELINE_MISSES}), {rescued} rescued, "
          f"{len(precision_damage)} precision-damage, {len(lost_recall)} lost-recall")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--remap", action="store_true",
                    help="re-run pry on the pinned corpus and re-derive vs the "
                         "frozen oracle labels (code-reflecting gate)")
    a = ap.parse_args()
    if a.remap:
        remap()
    else:
        main()
