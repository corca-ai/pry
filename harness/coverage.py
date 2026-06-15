"""coverage.py — Step-1 testability join (preregistration-coverage.md).

After E9 Tier-1 FALSIFIED the bug-prediction thesis, this tests pry's remaining
honest candidate: welded-at-demand boundaries sit in LESS-tested code. It reuses
the frozen E9 sweep records (arms, file_churn, site_size) and joins a per-file
test-coverage bit from the clones at the SAME pinned commits via git plumbing
(ls-tree + cat-file) — deterministic, offline, zero new mining.

Outcome = `untested` (the finding's source file has NO test association), where a
file is test-associated iff (a) a MIRROR test file shares its stem, OR (b) it is
IMPORTED-BY-TEST (resolved relative/alias import target in a test file). The
metric is the matched untested ratio (wd vs rest) over E9's (file-churn x
site-size) terciles, repo-cluster bootstrap CI — the SAME machinery, keyed on a
different outcome. Floor reused from E9 by symmetry (config). The E9 sweep
records are NOT mutated.

Usage:
    python3 harness/coverage.py                 # compute + write coverage_result.json
    python3 harness/coverage.py --markdown      # also print the eval-gate section
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import config
import enrichment
from enrichment import _bucket, _control_pred, _tercile_cuts, verdict

CODE = re.compile(config.COVERAGE_CODE_EXT_REGEX)
TEST_BASENAME = re.compile(config.COVERAGE_TEST_BASENAME_REGEX)
TEST_DIR = re.compile(config.COVERAGE_TEST_DIR_REGEX)
FRONTEND = re.compile(config.COVERAGE_FRONTEND_REGEX)
TEST_INFIX = re.compile(r"\.(test|spec|e2e|vitest|cy)$")
EXTS = config.COVERAGE_RESOLVE_EXTS
# import / require / dynamic-import specifier (string literal target)
SPEC_RE = re.compile(r"""(?:\bfrom|\bimport|\brequire)\s*\(?\s*['"]([^'"\n]+)['"]""")


# --- file-tree + blob helpers (deterministic, at the pinned commit) -----------

def ls_tree(repo: Path, commit: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only",
                          commit], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"ls-tree failed on {repo} @ {commit[:8]}: "
                           f"{out.stderr[:160]}")
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def read_blobs(repo: Path, commit: str, paths: list[str]) -> dict[str, str]:
    """Read many blobs at `commit` via a single `git cat-file --batch` pass."""
    if not paths:
        return {}
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        input="\n".join(f"{commit}:{p}" for p in paths).encode() + b"\n",
        capture_output=True)
    data = proc.stdout
    out: dict[str, str] = {}
    i = 0
    for p in paths:
        nl = data.find(b"\n", i)
        if nl < 0:
            break
        header = data[i:nl].decode("utf-8", "replace")
        parts = header.split()
        if len(parts) >= 3 and parts[1] == "blob":
            size = int(parts[2])
            start = nl + 1
            out[p] = data[start:start + size].decode("utf-8", "replace")
            i = start + size + 1          # skip blob + trailing newline
        else:                             # missing / non-blob: header only
            i = nl + 1
    return out


# --- test-file + coverage classification --------------------------------------

def is_code(path: str) -> bool:
    return bool(CODE.search(path))


def is_test(path: str) -> bool:
    return bool(TEST_BASENAME.search(os.path.basename(path)) or TEST_DIR.search(path))


def is_mirror_test(path: str) -> bool:
    return bool(TEST_BASENAME.search(os.path.basename(path)))


def base_stem(path: str) -> str:
    """Basename with the code extension stripped (e.g. foo.tsx -> foo)."""
    b = os.path.basename(path)
    return CODE.sub("", b)


def logical_stem(path: str) -> str:
    """Mirror stem: strip code ext, then the test infix (foo.test -> foo)."""
    return TEST_INFIX.sub("", base_stem(path))


def _strip_code_ext(p: str) -> str:
    return CODE.sub("", p)


def _candidates(base: str):
    yield base
    stem = _strip_code_ext(base)
    for e in EXTS:
        yield stem + e
    for e in EXTS:
        yield base + e
    for e in EXTS:
        yield stem + "/index" + e
    for e in EXTS:
        yield base + "/index" + e


def _norm(p: str) -> str:
    return os.path.normpath(p).replace(os.sep, "/")


def load_aliases(repo: Path, commit: str, files: list[str]) -> tuple[str, dict]:
    """Best-effort tsconfig/jsconfig baseUrl + paths (root-level configs only)."""
    cfgs = [f for f in files if os.path.basename(f) in
            ("tsconfig.json", "jsconfig.json") and "/" not in f]
    if not cfgs:
        cfgs = [f for f in files if os.path.basename(f) in
                ("tsconfig.json", "jsconfig.json")][:3]
    blobs = read_blobs(repo, commit, cfgs)
    base_url, paths = ".", {}
    for f in cfgs:
        txt = blobs.get(f, "")
        # tolerant parse: strip // and /* */ comments + trailing commas
        txt = re.sub(r"//[^\n]*", "", txt)
        txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
        txt = re.sub(r",(\s*[}\]])", r"\1", txt)
        try:
            co = (json.loads(txt) or {}).get("compilerOptions", {}) or {}
        except (json.JSONDecodeError, AttributeError):
            continue
        cfg_dir = os.path.dirname(f)
        if co.get("baseUrl"):
            base_url = _norm(os.path.join(cfg_dir, co["baseUrl"]))
        for pat, targets in (co.get("paths") or {}).items():
            paths.setdefault(pat, [])
            for t in targets:
                paths[pat].append(_norm(os.path.join(base_url, t)))
    return base_url, paths


def resolve(spec: str, from_path: str, code_set: set[str], aliases: tuple) -> str | None:
    base_url, paths = aliases
    bases: list[str] = []
    if spec.startswith("."):
        bases.append(_norm(os.path.join(os.path.dirname(from_path), spec)))
    else:
        for pat, targets in paths.items():
            if "*" in pat:
                pre = pat.split("*", 1)[0]
                if spec.startswith(pre):
                    tail = spec[len(pre):]
                    for t in targets:
                        bases.append(_norm(t.replace("*", tail)))
            elif spec == pat:
                bases.extend(targets)
        if not bases:                     # bare node_modules import
            return None
    for b in bases:
        for c in _candidates(b):
            if c in code_set:
                return c
    return None


_TESTDIR_SEG = {"__tests__", "__mocks__", "test", "tests", "e2e", "cypress", "spec"}


def _canon_dir(path: str) -> str:
    """Directory of `path` with trailing test-dir segments stripped, so a test in
    `a/b/__tests__/` canonicalizes to the same dir as source `a/b/foo.ts`."""
    parts = os.path.dirname(path).split("/")
    while parts and parts[-1] in _TESTDIR_SEG:
        parts.pop()
    return "/".join(parts)


def build_coverage(repo: Path, commit: str) -> dict:
    files = ls_tree(repo, commit)
    code = [f for f in files if is_code(f)]
    code_set = set(code)
    tests = [f for f in code if is_test(f)]
    srcs = [f for f in code if not is_test(f)]
    src_set = set(srcs)

    # permissive (basename-only) mirror, and a strict path-aware mirror
    mirror_stems = {logical_stem(t) for t in tests if is_mirror_test(t)}
    covered_mirror = {s for s in srcs if base_stem(s) in mirror_stems}
    strict_by_dir: dict[str, set[str]] = {}
    for t in tests:
        if is_mirror_test(t):
            strict_by_dir.setdefault(_canon_dir(t), set()).add(logical_stem(t))
    covered_strict = {s for s in srcs
                      if base_stem(s) in strict_by_dir.get(_canon_dir(s), ())}

    blobs = read_blobs(repo, commit, tests)
    aliases = load_aliases(repo, commit, files)
    covered_import: set[str] = set()
    for t in tests:
        for spec in SPEC_RE.findall(blobs.get(t, "")):
            r = resolve(spec, t, code_set, aliases)
            if r and r in src_set:
                covered_import.add(r)
    return {
        "covered_mirror": covered_mirror,
        "covered_strict": covered_strict,
        "covered_import": covered_import,
        "covered": covered_mirror | covered_import,
        "covered_strict_or_import": covered_strict | covered_import,
        "n_src": len(srcs), "n_test": len(tests),
    }


# --- matched metric, keyed on `untested` (mirrors enrichment.matched_ratio) ----

def matched(findings: list[dict], churn_cuts, size_cuts, control: str,
            key: str = "untested") -> dict:
    is_ctrl = _control_pred(control)
    strata: dict = {}
    wd_tot = wd_e = ct_tot = ct_e = 0
    for f in findings:
        if f["arm"] == "wd":
            grp = "wd"
        elif is_ctrl(f):
            grp = "ct"
        else:
            continue
        k = (_bucket(f["file_churn"], churn_cuts), _bucket(f["site_size"], size_cuts))
        s = strata.setdefault(k, {"wd": 0, "wd_e": 0, "ct": 0, "ct_e": 0})
        s[grp] += 1
        s[grp + "_e"] += f[key]
        if grp == "wd":
            wd_tot += 1; wd_e += f[key]
        else:
            ct_tot += 1; ct_e += f[key]
    num = den = w_tot = 0.0
    used = dropped = 0
    for k in sorted(strata):
        s = strata[k]
        if s["wd"] >= config.ENRICHMENT_MIN_STRATUM and s["ct"] >= config.ENRICHMENT_MIN_STRATUM:
            w = s["wd"] + s["ct"]
            num += w * (s["wd_e"] / s["wd"])
            den += w * (s["ct_e"] / s["ct"])
            w_tot += w
            used += 1
        else:
            dropped += 1
    std_wd = (num / w_tot) if w_tot else None
    std_ct = (den / w_tot) if w_tot else None
    matched_ratio = (num / den) if den else None
    raw = ((wd_e / wd_tot) / (ct_e / ct_tot)) if wd_tot and ct_tot and ct_e else None
    odds = None
    if std_wd is not None and std_ct not in (None, 0) and std_wd < 1 and std_ct < 1:
        odds = (std_wd / (1 - std_wd)) / (std_ct / (1 - std_ct)) if std_ct else None
    return {
        "control": control,
        "matched_ratio": matched_ratio, "raw_ratio": raw,
        "odds_ratio": odds,
        "rate_diff": (std_wd - std_ct) if (std_wd is not None and std_ct is not None) else None,
        "std_wd_rate": std_wd, "std_ct_rate": std_ct,
        "wd_n": wd_tot, "wd_untested": wd_e, "ctrl_n": ct_tot, "ctrl_untested": ct_e,
        "wd_rate": wd_e / wd_tot if wd_tot else None,
        "ctrl_rate": ct_e / ct_tot if ct_tot else None,
        "strata_used": used, "strata_dropped": dropped,
        "max_ratio_ceiling": (1.0 / std_ct) if std_ct else None,
    }


def boot_ci(by_repo: dict, churn_cuts, size_cuts, control: str, key="untested"):
    import random
    ids = list(by_repo)
    if len(ids) < 2:
        return (None, None)
    rng = random.Random(config.ENRICHMENT_BOOTSTRAP_SEED)
    vals = []
    for _ in range(config.ENRICHMENT_BOOTSTRAP_B):
        sample = [rng.choice(ids) for _ in ids]
        pool = [f for rid in sample for f in by_repo[rid]]
        r = matched(pool, churn_cuts, size_cuts, control, key)["matched_ratio"]
        if r is not None:
            vals.append(r)
    if not vals:
        return (None, None)
    vals.sort()
    a = (1 - config.ENRICHMENT_BOOTSTRAP_CI) / 2
    return (vals[int(a * len(vals))],
            vals[min(len(vals) - 1, int((1 - a) * len(vals)))])


def per_repo(by_repo: dict, control: str, key="untested") -> dict:
    is_ctrl = _control_pred(control)
    rows, elig, gt1 = [], 0, 0
    for rid in sorted(by_repo):
        fs = by_repo[rid]
        wd = [f for f in fs if f["arm"] == "wd"]
        ct = [f for f in fs if is_ctrl(f)]
        if len(wd) >= config.ENRICHMENT_PERREPO_MIN_FINDINGS and \
           len(ct) >= config.ENRICHMENT_PERREPO_MIN_FINDINGS:
            wr = sum(f[key] for f in wd) / len(wd)
            cr = sum(f[key] for f in ct) / len(ct)
            ratio = (wr / cr) if cr else None
            elig += 1
            if ratio and ratio > 1.0:
                gt1 += 1
            rows.append({"id": rid, "wd_n": len(wd), "ctrl_n": len(ct),
                         "ratio": round(ratio, 3) if ratio else None})
    frac = (gt1 / elig) if elig else None
    return {"eligible_repos": elig, "repos_ratio_gt1": gt1, "fraction_gt1": frac,
            "passes_simpson_guard": frac is not None and frac >= config.ENRICHMENT_PERREPO_MAJORITY,
            "rows": rows}


def cov_verdict(point, ci_lo) -> str:
    """Same two-sided logic as enrichment.verdict but with COVERAGE_* floors."""
    if point is None:
        return "UNDERPOWERED (no usable strata)"
    if point <= config.COVERAGE_FALSIFIER or (ci_lo is not None and ci_lo <= 1.0):
        return "FALSIFIED"
    if point >= config.COVERAGE_GO_FLOOR and ci_lo is not None and ci_lo > 1.0:
        return "GO (coverage gap real)"
    return "WEAK / inconclusive"


def analyze(records: dict, label: str, control="rest", subset=None, key="untested") -> dict:
    by_repo = {rid: [f for f in r["findings"] if (subset is None or subset(f))]
               for rid, r in records.items()}
    allf = [f for fs in by_repo.values() for f in fs]
    pool = [f for f in allf if f["arm"] in ("wd", "rest")] if control == "rest" else allf
    churn_cuts = _tercile_cuts([f["file_churn"] for f in pool])
    size_cuts = _tercile_cuts([f["site_size"] for f in pool])
    m = matched(pool, churn_cuts, size_cuts, control, key)
    lo, hi = boot_ci(by_repo, churn_cuts, size_cuts, control, key)
    m["ci95"] = [lo, hi]
    m["verdict"] = cov_verdict(m["matched_ratio"], lo)
    m["label"] = label
    m["key"] = key
    m["n_repos"] = len(records)
    if control == "rest":
        m["per_repo"] = per_repo(by_repo, control, key)
    return m


# --- join + drive -------------------------------------------------------------

def join_records() -> dict:
    """Load frozen sweep records, attach untested/covered/frontend per finding."""
    records = enrichment.load_records()
    diag = {}
    for rid, r in records.items():
        cov = build_coverage(config.CORPUS_CLONE_DIR / rid, r["pinned_commit"])
        kept = []
        in_test = 0
        for f in r["findings"]:
            fp = f["file"]
            if is_test(fp):                # weld inside a test file: out of scope
                in_test += 1
                continue
            f = dict(f)
            f["covered"] = int(fp in cov["covered"])
            f["untested"] = int(fp not in cov["covered"])
            f["untested_mirror"] = int(fp not in cov["covered_mirror"])
            f["untested_import"] = int(fp not in cov["covered_import"])
            f["untested_strict"] = int(fp not in cov["covered_strict_or_import"])
            f["frontend"] = int(bool(FRONTEND.search(fp)))
            kept.append(f)
        r["findings"] = kept
        diag[rid] = {"n_src": cov["n_src"], "n_test": cov["n_test"],
                     "findings_in_test_dropped": in_test,
                     "covered_files": len(cov["covered"]),
                     "covered_mirror": len(cov["covered_mirror"]),
                     "covered_import": len(cov["covered_import"])}
    return records, diag


def _pct(x):
    return f"{x*100:.1f}%" if x is not None else "n/a"


def _r(x):
    return f"{x:.2f}" if isinstance(x, (int, float)) else "n/a"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out", type=Path, default=config.COVERAGE_RESULT_PATH)
    args = ap.parse_args()

    records, diag = join_records()
    dev = {k: v for k, v in records.items() if v["split"] == "dev"}
    held = {k: v for k, v in records.items() if v["split"] == "heldout"}
    not_frontend = lambda f: not f["frontend"]  # noqa: E731

    result = {
        "outcome": "untested (file has no test association: mirror-stem OR imported-by-test)",
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
        "robustness": {
            "backend_only": analyze(records, "corpus(backend-only)", "rest", subset=not_frontend),
            "strict_mirror_or_import": analyze(records, "corpus(strict-mirror)", "rest", key="untested_strict"),
        },
        "proxy_components": {
            "mirror_only": analyze(records, "corpus(mirror-only)", "rest", key="untested_mirror"),
            "import_only": analyze(records, "corpus(import-only)", "rest", key="untested_import"),
        },
        "config": {"go_floor": config.COVERAGE_GO_FLOOR,
                   "falsifier": config.COVERAGE_FALSIFIER,
                   "bootstrap_B": config.ENRICHMENT_BOOTSTRAP_B},
        "diagnostics": diag,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    def line(m):
        return (f"{m['label']:<20} n={m['n_repos']:<3} "
                f"wd {m['wd_untested']}/{m['wd_n']}={_pct(m['wd_rate'])} "
                f"rest {m['ctrl_untested']}/{m['ctrl_n']}={_pct(m['ctrl_rate'])} "
                f"raw={_r(m['raw_ratio'])} matched={_r(m['matched_ratio'])} "
                f"OR={_r(m['odds_ratio'])} diff={_r(m['rate_diff'])} "
                f"CI=[{_r(m['ci95'][0])},{_r(m['ci95'][1])}] "
                f"u/d={m['strata_used']}/{m['strata_dropped']} -> {m['verdict']}")
    print("=== Step-1 coverage: untested-file ratio (wd vs rest) ===")
    for k in ("corpus", "dev", "heldout"):
        if result["primary"][k]:
            print(" ", line(result["primary"][k]))
    pr = result["primary"]["corpus"]["per_repo"]
    print(f"  Simpson: {pr['repos_ratio_gt1']}/{pr['eligible_repos']} repos ratio>1 "
          f"(frac={_r(pr['fraction_gt1'])})")
    c = result["primary"]["corpus"]
    print(f"  base-rate ceiling: max achievable ratio = 1/std-rest-rate = "
          f"{_r(c['max_ratio_ceiling'])} (GO floor={config.COVERAGE_GO_FLOOR})")
    print("=== Robustness ===")
    print(" ", line(result["robustness"]["backend_only"]))
    print(" ", line(result["robustness"]["strict_mirror_or_import"]))
    print("=== Proxy components ===")
    print(" ", line(result["proxy_components"]["mirror_only"]))
    print(" ", line(result["proxy_components"]["import_only"]))
    print("=== Secondary controls ===")
    for k in ("vs_seamed", "vs_welded_not_demand"):
        print(" ", line(result["secondary"][k]))
    print(f"\nwrote {args.out}")
    if args.markdown:
        print("\n" + render_markdown(result))


def render_markdown(result: dict) -> str:
    c = result["config"]
    out = ["## Step-1 coverage (testability) — does welded-at-demand sit in LESS-tested code?",
           "",
           "Pre-registered (`preregistration-coverage.md`, committed before this "
           "number): outcome = **untested** (file has no test association: mirror-stem "
           "OR imported-by-test); signal = welded-at-demand; PRIMARY control = rest. "
           "Matched on (file-churn × site-size) terciles; 95% CI = repo-cluster "
           f"bootstrap (B={c['bootstrap_B']}). GO: matched≥{c['go_floor']} AND "
           f"CI-lower>1.0. FALSIFIED: matched≤{c['falsifier']} OR CI-lower≤1.0.", "",
           "| arm set | repos | wd untested | rest untested | raw | matched | OR | CI | verdict |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in ("corpus", "dev", "heldout"):
        m = result["primary"].get(k)
        if m:
            out.append(f"| **{m['label']}** | {m['n_repos']} | {_pct(m['wd_rate'])} | "
                       f"{_pct(m['ctrl_rate'])} | {_r(m['raw_ratio'])} | "
                       f"**{_r(m['matched_ratio'])}** | {_r(m['odds_ratio'])} | "
                       f"[{_r(m['ci95'][0])}, {_r(m['ci95'][1])}] | {m['verdict']} |")
    bo = result["robustness"]["backend_only"]
    out += ["", f"**Backend-only cut** (drop frontend, the named file-kind confound): "
            f"matched **{_r(bo['matched_ratio'])}** CI [{_r(bo['ci95'][0])}, "
            f"{_r(bo['ci95'][1])}] → {bo['verdict']}.",
            f"**Base-rate ceiling:** max achievable ratio = "
            f"{_r(result['primary']['corpus']['max_ratio_ceiling'])} "
            f"(1/standardized-rest-rate)."]
    return "\n".join(out)


if __name__ == "__main__":
    main()
