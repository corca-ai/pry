"""floor_verdict.py — reconcile the 3-rater floor panel + apply the frozen go/kill.

Reads floor-votes/{raterA,raterB,raterC}.json + floor-worklist.json, reconciles
each flag by majority (no majority => AMBIGUOUS), computes FLOOR-2 precision
(GENUINE / decided), the Wilson 95% interval (reported), the linter-survival
fraction (GENUINE flags eslint `no-empty` would PASS = non-empty catch), and
applies the pre-registered go/kill from config. Writes floor-labels.json (frozen
reconciliation) + floor_result.json. No LLM, deterministic.

Usage: python3 harness/floor_verdict.py
"""

from __future__ import annotations

import json
import math
from collections import Counter

import config

VOTES = config.EVAL_DIR / "floor-votes"
WORKLIST = config.EVAL_DIR / "floor-worklist.json"
GENUINE = "GENUINE-MEANINGFUL"


def norm_id(i: str) -> str:
    return i.split("#", 1)[0]


def load_votes(name):
    arr = json.loads((VOTES / f"{name}.json").read_text())
    return {norm_id(o["id"]): o for o in arr}  # dup ids collapse (identical labels)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - half) / d, (c + half) / d)


def main():
    a, b, c = load_votes("raterA"), load_votes("raterB"), load_votes("raterC")
    wl = json.loads(WORKLIST.read_text())
    items = {norm_id(i["id"]): i for i in wl["items"]}  # dup collapses to 1

    reconciled = {}
    for iid, it in items.items():
        votes = [d[iid]["label"] for d in (a, b, c) if iid in d]
        cnt = Counter(votes)
        top, n = cnt.most_common(1)[0]
        label = top if n >= 2 else "AMBIGUOUS"
        cons = next((d[iid].get("consequence") for d in (a, b, c)
                     if iid in d and d[iid]["label"] == GENUINE and d[iid].get("consequence")), None)
        reconciled[iid] = {
            "id": iid, "rule": it["rule"], "repo": it["repo"],
            "catch_empty": it["catch_empty"], "votes": votes,
            "label": label, "consequence": cons,
        }

    def stats(rule):
        rows = [r for r in reconciled.values() if r["rule"] == rule]
        decided = [r for r in rows if r["label"] != "AMBIGUOUS"]
        genuine = [r for r in decided if r["label"] == GENUINE]
        prec = len(genuine) / len(decided) if decided else None
        lo, hi = wilson(len(genuine), len(decided))
        repos = sorted({r["repo"] for r in genuine})
        # linter-survival: GENUINE flags eslint no-empty PASSES (non-empty catch)
        surv = sum(1 for r in genuine if not r["catch_empty"])
        return {
            "n_total": len(rows), "n_decided": len(decided),
            "n_genuine": len(genuine), "precision": prec,
            "wilson95": [lo, hi], "genuine_repos": repos,
            "linter_survival": f"{surv}/{len(genuine)}",
            "benign": sum(1 for r in decided if r["label"] == "BENIGN-SWALLOW"),
            "false_flag": sum(1 for r in decided if r["label"] == "FALSE-FLAG"),
            "genuine_ids": [r["id"] for r in genuine],
        }

    f2 = stats("FLOOR-2")
    f1 = stats("FLOOR-1")

    # go/kill on FLOOR-2 (the headline), per frozen config
    total_f2 = wl["n_floor2_total"]
    go = (f2["precision"] is not None
          and f2["precision"] >= config.FLOOR_GO_PRECISION
          and f2["n_decided"] >= config.FLOOR_GO_MIN_DECIDED
          and total_f2 >= config.FLOOR_MIN_TOTAL_FLAGS
          and f2["n_genuine"] >= config.FLOOR_GO_MIN_GENUINE
          and len(f2["genuine_repos"]) >= config.FLOOR_GO_MIN_REPOS)
    kill = (f2["precision"] is not None
            and (f2["precision"] <= config.FLOOR_KILL_PRECISION or f2["n_genuine"] < 2))
    verdict = "GO" if go else ("KILL" if kill else "WEAK")

    result = {
        "verdict": verdict,
        "headline": "FLOOR-2 (swallow-then-commit)",
        "floor2": f2, "floor1": f1,
        "floor2_total_corpus": total_f2,
        "go_kill_inputs": {
            "precision": f2["precision"], "n_decided": f2["n_decided"],
            "n_genuine": f2["n_genuine"], "genuine_repos": len(f2["genuine_repos"]),
            "corpus_total": total_f2,
        },
        "thresholds": {
            "go_precision": config.FLOOR_GO_PRECISION,
            "go_min_decided": config.FLOOR_GO_MIN_DECIDED,
            "go_min_total": config.FLOOR_MIN_TOTAL_FLAGS,
            "go_min_genuine": config.FLOOR_GO_MIN_GENUINE,
            "go_min_repos": config.FLOOR_GO_MIN_REPOS,
            "kill_precision": config.FLOOR_KILL_PRECISION,
        },
        "panel": "3 fresh-eye subagent raters, majority reconciliation; same-model caveat disclosed",
        "note": "KILL scopes to THIS minimal rule set, not the floor concept",
    }
    config.FLOOR_LABELS_PATH.write_text(json.dumps(
        {"reconciled": list(reconciled.values())}, indent=2) + "\n")
    config.FLOOR_RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n")

    def line(tag, s):
        return (f"{tag}: genuine {s['n_genuine']}/{s['n_decided']} decided "
                f"(total {s['n_total']}) precision="
                f"{s['precision']:.3f} " if s['precision'] is not None else f"{tag}: n/a ") + \
            (f"Wilson95=[{s['wilson95'][0]:.2f},{s['wilson95'][1]:.2f}] "
             f"repos={len(s['genuine_repos'])} benign={s['benign']} false={s['false_flag']} "
             f"linter-survival={s['linter_survival']}" if s['precision'] is not None else "")

    print("=== FLOOR go/kill (panel-reconciled) ===")
    print(line("FLOOR-2", f2))
    print(line("FLOOR-1", f1))
    print(f"FLOOR-2 corpus total = {total_f2} (GO-eligibility >= {config.FLOOR_MIN_TOTAL_FLAGS})")
    print(f"GENUINE FLOOR-2 ids: {f2['genuine_ids']}")
    print(f"GENUINE FLOOR-1 ids: {f1['genuine_ids']}")
    print(f"\nVERDICT: {verdict}  (GO needs precision>={config.FLOOR_GO_PRECISION} "
          f"over >={config.FLOOR_GO_MIN_DECIDED} decided + >={config.FLOOR_GO_MIN_GENUINE} "
          f"genuine/>={config.FLOOR_GO_MIN_REPOS} repos; KILL if precision<="
          f"{config.FLOOR_KILL_PRECISION} or <2 genuine)")
    print(f"wrote {config.FLOOR_LABELS_PATH.name}, {config.FLOOR_RESULT_PATH.name}")


if __name__ == "__main__":
    main()
