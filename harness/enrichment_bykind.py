"""enrichment_bykind.py — EXPLORATORY post-hoc per-kind re-cut of the E9 sweep.

NOT a pre-registered verdict. The pre-registered headline (pooled matched 1.05 ->
FALSIFIED) stands; this is a hypothesis-generating diagnostic over the SAME frozen
sweep records (zero new mining), asking: is a sharper bug-prediction signal hiding
in the GENUINE boundary kinds (network + subprocess, the H3 100%-precision ones)
that the cosmetic tail (clock/fileio/env/random) washes out of the pooled number?

Because this is post-hoc and multiple-comparison territory, it is labeled
EXPLORATORY everywhere and never writes a verdict token into the gate docs.

Usage:
    python3 harness/enrichment_bykind.py
"""

from __future__ import annotations

import json

import config
import enrichment

# The "genuine substitution-demand" boundary kinds (H3: network+subprocess were
# 100% precision) vs the cosmetic tail that dragged the pooled number to ~1.0.
GENUINE = {"network", "subprocess"}
COSMETIC = {"clock", "fileio", "env", "random"}


def _rate(n, b):
    return (b / n) if n else None


def _r(x):
    return f"{x:.2f}" if isinstance(x, (int, float)) else "n/a"


def _pct(x):
    return f"{x*100:.1f}%" if x is not None else "n/a"


def per_kind_raw(records):
    """Kind-matched raw rates: wd-of-kind vs rest-of-kind (same kind)."""
    agg = {}
    for r in records.values():
        for f in r["findings"]:
            k = f.get("kind") or "?"
            a = agg.setdefault(k, {"wd_n": 0, "wd_b": 0, "rest_n": 0, "rest_b": 0})
            if f["arm"] == "wd":
                a["wd_n"] += 1
                a["wd_b"] += f["bugfix_touched"]
            elif f["arm"] == "rest":
                a["rest_n"] += 1
                a["rest_b"] += f["bugfix_touched"]
    return agg


def subset_matched(records, kinds, label):
    """Matched enrichment (wd vs rest) restricted to `kinds`, with bootstrap CI.

    Reuses enrichment.py machinery; tercile cuts recomputed WITHIN the subset so
    the churn/size matching is meaningful for that subset.
    """
    by_repo = {rid: [f for f in r["findings"] if (f.get("kind") in kinds)
                     and f["arm"] in ("wd", "rest")]
               for rid, r in records.items()}
    allf = [f for fs in by_repo.values() for f in fs]
    if not allf:
        return None
    churn_cuts = enrichment._tercile_cuts([f["file_churn"] for f in allf])
    size_cuts = enrichment._tercile_cuts([f["site_size"] for f in allf])
    m = enrichment.matched_ratio(allf, churn_cuts, size_cuts, "rest",
                                 config.ENRICHMENT_MIN_STRATUM)
    lo, hi = enrichment.bootstrap_ci(by_repo, churn_cuts, size_cuts, "rest")
    m["ci95"] = [lo, hi]
    m["label"] = label
    return m


def main():
    records = enrichment.load_records()
    print("=== EXPLORATORY post-hoc per-kind re-cut (NOT a pre-registered verdict) ===")
    print("pooled headline stays FALSIFIED (matched 1.05); this asks if a narrow\n"
          "genuine-boundary signal hides under the cosmetic tail.\n")

    agg = per_kind_raw(records)
    print(f"{'kind':<11} {'wd rate':>10} {'rest rate':>10} {'ratio':>6}  "
          f"{'wd n':>6} {'rest n':>7}")
    for k in sorted(agg, key=lambda k: -(agg[k]['wd_n'])):
        a = agg[k]
        wr, rr = _rate(a["wd_n"], a["wd_b"]), _rate(a["rest_n"], a["rest_b"])
        ratio = (wr / rr) if (wr and rr) else None
        print(f"{k:<11} {_pct(wr):>10} {_pct(rr):>10} {_r(ratio):>6}  "
              f"{a['wd_n']:>6} {a['rest_n']:>7}")

    print("\n=== matched enrichment by subset (wd vs rest, within subset) ===")
    out = {"exploratory": True, "headline_unchanged": "FALSIFIED (pooled 1.05)",
           "per_kind_raw": agg, "subsets": {}}
    for kinds, label in ((GENUINE, "genuine(net+subproc)"),
                         (COSMETIC, "cosmetic(clock/fileio/env/random)"),
                         (GENUINE | COSMETIC, "all-kinds(sanity)")):
        m = subset_matched(records, kinds, label)
        if not m:
            continue
        out["subsets"][label] = m
        print(f"  {label:<34} wd {m['wd_bugfix']}/{m['wd_n']}={_pct(m['wd_rate'])} "
              f"rest {m['ctrl_bugfix']}/{m['ctrl_n']}={_pct(m['ctrl_rate'])} "
              f"raw={_r(m['raw_ratio'])} matched={_r(m['matched_ratio'])} "
              f"CI95=[{_r(m['ci95'][0])},{_r(m['ci95'][1])}] "
              f"strata {m['strata_used']}u/{m['strata_dropped']}d")

    dest = config.EVAL_DIR / "enrichment_bykind_exploratory.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {dest}")
    print("\nReading guide: a GENUINE-subset matched ratio clearly >1 (CI excludes 1)\n"
          "would be a *hypothesis* that net/subproc welds predict bugs even though\n"
          "the pooled number is flat — to be confirmed by a fresh pre-registration,\n"
          "NOT treated as a verdict here. A flat genuine subset => bug-prediction is\n"
          "dead even for the high-precision boundaries => pivot to testability-debt.")


if __name__ == "__main__":
    main()
