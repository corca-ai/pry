"""test_enrichment.py — unit tests for the S3 matched-enrichment math (synthetic).

No git/pry: feeds synthetic findings to the pure aggregation functions and checks
the matched ratio, stratum-drop rule, verdict thresholds, and tercile bucketing.

Run: python3 -m pytest harness/test_enrichment.py -q
"""

from __future__ import annotations

import config
import enrichment


def _f(arm, subarm, touched, churn, size):
    return {"arm": arm, "subarm": subarm, "bugfix_touched": touched,
            "file_churn": churn, "site_size": size}


def test_tercile_and_bucket():
    cuts = enrichment._tercile_cuts(list(range(1, 10)))  # 1..9
    assert enrichment._bucket(1, cuts) == 0
    assert enrichment._bucket(9, cuts) == 2


def test_matched_ratio_neutralizes_a_pure_churn_confound():
    # Construct a case where wd and rest have IDENTICAL within-stratum rates, but
    # wd is concentrated in the high-churn (high-bug) stratum. Raw ratio inflates;
    # matched ratio must be ~1.0 (the confound is neutralized).
    findings = []
    # low-churn stratum: both arms 10% bugfix
    for i in range(50):
        findings.append(_f("wd", None, i < 5, churn=1, size=1))
        findings.append(_f("rest", "wnd", i < 5, churn=1, size=1))
    # high-churn stratum: both arms 50% bugfix, but mostly wd lives here
    for i in range(50):
        findings.append(_f("wd", None, i < 25, churn=100, size=1))
    for i in range(10):
        findings.append(_f("rest", "wnd", i < 5, churn=100, size=1))
    churn_cuts = enrichment._tercile_cuts([f["file_churn"] for f in findings])
    size_cuts = enrichment._tercile_cuts([f["site_size"] for f in findings])
    m = enrichment.matched_ratio(findings, churn_cuts, size_cuts, "rest",
                                 min_stratum=5)
    assert m["raw_ratio"] > 1.2          # raw is confounded upward
    assert 0.9 <= m["matched_ratio"] <= 1.1   # matched neutralizes it


def test_understaffed_strata_dropped():
    findings = [_f("wd", None, True, 1, 1) for _ in range(3)]
    findings += [_f("rest", "wnd", False, 1, 1) for _ in range(3)]
    m = enrichment.matched_ratio(findings, (1, 1), (1, 1), "rest", min_stratum=5)
    assert m["strata_used"] == 0
    assert m["matched_ratio"] is None


def test_verdict_thresholds():
    assert enrichment.verdict(2.0, 1.4).startswith("GO")
    assert enrichment.verdict(1.05, 0.9) == "FALSIFIED"      # point below falsifier
    assert enrichment.verdict(1.8, 0.95) == "FALSIFIED"      # CI lower <= 1.0
    assert enrichment.verdict(1.3, 1.05) == "WEAK / inconclusive"
    assert enrichment.verdict(None, None).startswith("UNDERPOWERED")


def test_verdict_uses_config_floor():
    # a point exactly at the GO floor with CI above 1 is GO
    v = enrichment.verdict(config.ENRICHMENT_GO_FLOOR, 1.2)
    assert v.startswith("GO")
