"""enrichment.py — Tier-1 matched enrichment + dev/heldout (E9 S3 + S4).

Reads the per-repo sweep records (harness/fixtures/eval/sweep/*.json) and computes
the PRE-REGISTERED verdict metric (preregistration.md / config E9 block). It only
*aggregates* — every threshold, arm, denominator, and CI was frozen earlier and is
read from config, so this script cannot move the goalposts.

Metric (signal = welded-at-demand "wd"; PRIMARY control = "rest"):
  * matched ratio = direct standardization over (file-churn tercile × site-size
    tercile) strata, strata with < ENRICHMENT_MIN_STRATUM findings in EITHER arm
    dropped + logged (R-D);
  * 95% CI via a repo-cluster bootstrap (B/seed from config), tercile cut points
    FIXED from the analysis set (stratification on full data, inference by cluster
    bootstrap — standard);
  * raw pooled ratio reported alongside (confound R-B visibility);
  * per-repo distribution (Simpson guard);
  * SECONDARY breakdowns vs seamed-only and welded-not-demand-only;
  * dev vs heldout reported separately (쟁점 2); any tuning is dev-only (none here).

Usage:
    python3 harness/enrichment.py                 # compute + write results json
    python3 harness/enrichment.py --markdown      # also print the eval-gate section
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import config


def load_records() -> dict[str, dict]:
    recs = {}
    for p in sorted(config.SWEEP_DIR.glob("*.json")):
        if p.name.endswith(".minets.json"):
            continue
        r = json.loads(p.read_text())
        rid = p.stem                       # the file is named <id>.json
        r["id"] = rid
        recs[rid] = r
    return recs


def _tercile_cuts(values: list[int]) -> tuple[float, float]:
    s = sorted(values)
    if not s:
        return (0.0, 0.0)
    n = len(s)
    return (s[n // 3], s[2 * n // 3])


def _bucket(v: float, cuts: tuple[float, float]) -> int:
    return 0 if v <= cuts[0] else (1 if v <= cuts[1] else 2)


def _control_pred(control: str):
    """Return a predicate selecting the control findings."""
    if control == "rest":
        return lambda f: f["arm"] == "rest"
    if control == "seamed":
        return lambda f: f.get("subarm") == "seamed"
    if control == "wnd":
        return lambda f: f.get("subarm") == "wnd"
    raise ValueError(control)


def matched_ratio(findings: list[dict], churn_cuts, size_cuts, control: str,
                  min_stratum: int) -> dict:
    is_ctrl = _control_pred(control)
    strata: dict[tuple[int, int], dict] = {}
    wd_tot = wd_bug = ct_tot = ct_bug = 0
    for f in findings:
        if f["arm"] == "wd":
            grp = "wd"
        elif is_ctrl(f):
            grp = "ct"
        else:
            continue
        key = (_bucket(f["file_churn"], churn_cuts),
               _bucket(f["site_size"], size_cuts))
        s = strata.setdefault(key, {"wd": 0, "wd_bug": 0, "ct": 0, "ct_bug": 0})
        s[grp] += 1
        if f["bugfix_touched"]:
            s[grp + "_bug"] += 1
        if grp == "wd":
            wd_tot += 1
            wd_bug += f["bugfix_touched"]
        else:
            ct_tot += 1
            ct_bug += f["bugfix_touched"]

    num = den = 0.0
    used, dropped = [], []
    for key in sorted(strata):
        s = strata[key]
        if s["wd"] >= min_stratum and s["ct"] >= min_stratum:
            w = s["wd"] + s["ct"]
            num += w * (s["wd_bug"] / s["wd"])
            den += w * (s["ct_bug"] / s["ct"])
            used.append({"stratum": key, **s})
        else:
            dropped.append({"stratum": key, **s})
    matched = (num / den) if den else None
    raw = ((wd_bug / wd_tot) / (ct_bug / ct_tot)
           if wd_tot and ct_tot and ct_bug else None)
    return {
        "control": control,
        "matched_ratio": matched,
        "raw_ratio": raw,
        "wd_n": wd_tot, "wd_bugfix": wd_bug,
        "ctrl_n": ct_tot, "ctrl_bugfix": ct_bug,
        "wd_rate": wd_bug / wd_tot if wd_tot else None,
        "ctrl_rate": ct_bug / ct_tot if ct_tot else None,
        "strata_used": len(used), "strata_dropped": len(dropped),
        "dropped_detail": dropped,
    }


def _matched_point(findings, churn_cuts, size_cuts, control, min_stratum):
    return matched_ratio(findings, churn_cuts, size_cuts, control,
                         min_stratum)["matched_ratio"]


def bootstrap_ci(by_repo: dict[str, list[dict]], churn_cuts, size_cuts,
                 control: str) -> tuple[float | None, float | None]:
    ids = list(by_repo)
    if len(ids) < 2:
        return (None, None)
    rng = random.Random(config.ENRICHMENT_BOOTSTRAP_SEED)
    vals = []
    for _ in range(config.ENRICHMENT_BOOTSTRAP_B):
        sample = [rng.choice(ids) for _ in ids]
        pool = [f for rid in sample for f in by_repo[rid]]
        r = _matched_point(pool, churn_cuts, size_cuts, control,
                           config.ENRICHMENT_MIN_STRATUM)
        if r is not None:
            vals.append(r)
    if not vals:
        return (None, None)
    vals.sort()
    alpha = (1 - config.ENRICHMENT_BOOTSTRAP_CI) / 2
    lo = vals[int(alpha * len(vals))]
    hi = vals[min(len(vals) - 1, int((1 - alpha) * len(vals)))]
    return (lo, hi)


def per_repo_distribution(by_repo: dict[str, list[dict]], control: str) -> dict:
    is_ctrl = _control_pred(control)
    rows, eligible, gt1 = [], 0, 0
    for rid in sorted(by_repo):
        fs = by_repo[rid]
        wd = [f for f in fs if f["arm"] == "wd"]
        ct = [f for f in fs if is_ctrl(f)]
        if len(wd) >= config.ENRICHMENT_PERREPO_MIN_FINDINGS and \
           len(ct) >= config.ENRICHMENT_PERREPO_MIN_FINDINGS:
            wr = sum(f["bugfix_touched"] for f in wd) / len(wd)
            cr = sum(f["bugfix_touched"] for f in ct) / len(ct)
            ratio = (wr / cr) if cr else None
            eligible += 1
            if ratio and ratio > 1.0:
                gt1 += 1
            rows.append({"id": rid, "wd_n": len(wd), "ctrl_n": len(ct),
                         "ratio": round(ratio, 3) if ratio else None})
    frac = (gt1 / eligible) if eligible else None
    return {"eligible_repos": eligible, "repos_ratio_gt1": gt1,
            "fraction_gt1": frac,
            "passes_simpson_guard": (frac is not None and
                                     frac >= config.ENRICHMENT_PERREPO_MAJORITY),
            "rows": rows}


def verdict(point, ci_lo) -> str:
    if point is None:
        return "UNDERPOWERED (no usable strata)"
    if point <= config.ENRICHMENT_FALSIFIER or (ci_lo is not None and
                                                ci_lo <= config.ENRICHMENT_GO_CI_LOWER_MIN):
        return "FALSIFIED"
    if point >= config.ENRICHMENT_GO_FLOOR and ci_lo is not None and \
       ci_lo > config.ENRICHMENT_GO_CI_LOWER_MIN:
        return "GO (signal real)"
    return "WEAK / inconclusive"


def analyze(records: dict[str, dict], label: str, control: str = "rest") -> dict:
    by_repo = {rid: r["findings"] for rid, r in records.items()}
    allf = [f for fs in by_repo.values() for f in fs if f["arm"] in ("wd", "rest")]
    churn_cuts = _tercile_cuts([f["file_churn"] for f in allf])
    size_cuts = _tercile_cuts([f["site_size"] for f in allf])
    m = matched_ratio(allf if control == "rest"
                      else [f for fs in by_repo.values() for f in fs],
                      churn_cuts, size_cuts, control, config.ENRICHMENT_MIN_STRATUM)
    lo, hi = bootstrap_ci(by_repo, churn_cuts, size_cuts, control)
    m["ci95"] = [lo, hi]
    m["verdict"] = verdict(m["matched_ratio"], lo)
    m["label"] = label
    m["n_repos"] = len(records)
    m["churn_cuts"] = list(churn_cuts)
    m["size_cuts"] = list(size_cuts)
    if control == "rest":
        m["per_repo"] = per_repo_distribution(by_repo, control)
    return m


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out", type=Path,
                    default=config.EVAL_DIR / "enrichment_result.json")
    args = ap.parse_args()

    records = load_records()
    if not records:
        raise SystemExit(f"no sweep records in {config.SWEEP_DIR}")
    dev = {k: v for k, v in records.items() if v["split"] == "dev"}
    held = {k: v for k, v in records.items() if v["split"] == "heldout"}

    result = {
        "n_repos": len(records),
        "primary": {
            "corpus": analyze(records, "corpus", "rest"),
            "dev": analyze(dev, "dev", "rest") if dev else None,
            "heldout": analyze(held, "heldout", "rest") if held else None,
        },
        "secondary": {
            "vs_seamed": analyze(records, "corpus", "seamed"),
            "vs_welded_not_demand": analyze(records, "corpus", "wnd"),
        },
        "config": {
            "go_floor": config.ENRICHMENT_GO_FLOOR,
            "falsifier": config.ENRICHMENT_FALSIFIER,
            "min_stratum": config.ENRICHMENT_MIN_STRATUM,
            "bootstrap_B": config.ENRICHMENT_BOOTSTRAP_B,
        },
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    def line(m):
        return (f"{m['label']:<9} n_repos={m['n_repos']:<3} "
                f"wd {m['wd_bugfix']}/{m['wd_n']}={_pct(m['wd_rate'])} "
                f"ctrl {m['ctrl_bugfix']}/{m['ctrl_n']}={_pct(m['ctrl_rate'])} "
                f"raw={_r(m['raw_ratio'])} matched={_r(m['matched_ratio'])} "
                f"CI95=[{_r(m['ci95'][0])},{_r(m['ci95'][1])}] "
                f"strata {m['strata_used']}u/{m['strata_dropped']}d -> {m['verdict']}")
    print("=== Tier-1 enrichment (primary: wd vs rest) ===")
    for k in ("corpus", "dev", "heldout"):
        if result["primary"][k]:
            print(" ", line(result["primary"][k]))
    pr = result["primary"]["corpus"]["per_repo"]
    print(f"  Simpson guard: {pr['repos_ratio_gt1']}/{pr['eligible_repos']} "
          f"repos ratio>1 (frac={_r(pr['fraction_gt1'])}, "
          f"pass={pr['passes_simpson_guard']})")
    print("=== Secondary controls (corpus) ===")
    for k in ("vs_seamed", "vs_welded_not_demand"):
        print(" ", line(result["secondary"][k]))
    print(f"\nwrote {args.out}")
    if args.markdown:
        print("\n" + render_markdown(result))


def _pct(x):
    return f"{x*100:.1f}%" if x is not None else "n/a"


def _r(x):
    return f"{x:.2f}" if isinstance(x, (int, float)) else "n/a"


def render_markdown(result: dict) -> str:
    out = ["## Tier-1 enrichment (E9 쟁점 4 + 쟁점 2) — welded-at-demand vs rest",
           "",
           "Pre-registered (preregistration.md, committed before this number): "
           "signal = welded-at-demand (class=welded AND demand); PRIMARY control = "
           "rest (seamed | welded-not-demand). Matched on (file-churn × site-size) "
           "terciles, direct standardization; 95% CI = repo-cluster bootstrap "
           f"(B={result['config']['bootstrap_B']}). GO: matched≥"
           f"{result['config']['go_floor']} AND CI-lower>1.0. FALSIFIED: matched≤"
           f"{result['config']['falsifier']} OR CI-lower≤1.0.", "",
           "| arm set | repos | wd rate | ctrl rate | raw | matched | 95% CI | strata u/d | verdict |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in ("corpus", "dev", "heldout"):
        m = result["primary"].get(k)
        if m:
            out.append(f"| **{m['label']}** | {m['n_repos']} | {_pct(m['wd_rate'])} "
                       f"| {_pct(m['ctrl_rate'])} | {_r(m['raw_ratio'])} | "
                       f"**{_r(m['matched_ratio'])}** | "
                       f"[{_r(m['ci95'][0])}, {_r(m['ci95'][1])}] | "
                       f"{m['strata_used']}/{m['strata_dropped']} | {m['verdict']} |")
    pr = result["primary"]["corpus"]["per_repo"]
    out += ["", f"**Simpson guard:** {pr['repos_ratio_gt1']}/{pr['eligible_repos']} "
            f"eligible repos (≥{config.ENRICHMENT_PERREPO_MIN_FINDINGS}/arm) have "
            f"per-repo ratio>1 (fraction {_r(pr['fraction_gt1'])}; "
            f"pass={pr['passes_simpson_guard']}).", "",
            "**Secondary controls (corpus):**"]
    for k in ("vs_seamed", "vs_welded_not_demand"):
        m = result["secondary"][k]
        out.append(f"- {m['control']}: matched {_r(m['matched_ratio'])} "
                   f"(wd {_pct(m['wd_rate'])} vs {_pct(m['ctrl_rate'])}, "
                   f"strata {m['strata_used']}u/{m['strata_dropped']}d) — "
                   f"{m['verdict']}")
    return "\n".join(out)


if __name__ == "__main__":
    main()
