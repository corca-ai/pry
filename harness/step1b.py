"""step1b.py — static FAILURE-test detection (preregistration-step1b.md).

The SHARP redo of Step-1. Step-1 asked "is the welded boundary's FILE tested at
all?" (FALSIFIED 0.95). Step-1b asks the question the testability thesis actually
makes: is the welded boundary's own FAILURE PATH simulated by a test? Measured
purely statically/offline via fingerprints — a test that (a) MOCKS the boundary's
module AND (b) SIMULATES its failure (mockRejectedValue / replyWithError / msw
error / mockImplementation(throw) / mockResolvedValue({ok:false}) / .rejects ...).
(b) is the discriminator.

Unit = a pry finding of a FAILURE-CAPABLE kind (network/subprocess/db/fileio;
clock/random/env excluded). The VERDICT (config Step-1b block, amended 2026-06-16)
is the ABSOLUTE wd failure-tested rate, two-sided: POSITIVE (<=0.20 under the
generous L-module linkage = dense untested targets) / OVERSTATED (>=0.40 under the
strict L-import linkage = untestability claim too strong) / WEAK. The welded-vs-
rest matched contrast (reuses coverage.py's machinery, keyed on failure_untested)
is REPORTED CONTEXT only — a weld/demand-specificity caveat, not a gate.

Reuses coverage.py's git plumbing + tsconfig-alias resolver + test-file detection;
net-new here are (i) per-boundary MODULE extraction (re-read the call site, resolve
the callee root identifier against the file's import map), (ii) per-test-file mock
+ failure-sim fingerprints, (iii) the L-import (test->source edges) and L-module
(per-module index) linkages. Deterministic, offline, zero new mining, no LLM.

Usage:
    python3 harness/step1b.py                # compute + write step1b_result.json
    python3 harness/step1b.py --markdown     # also print the eval-gate section
    python3 harness/step1b.py --repo continue --debug-modules   # extraction probe
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import config
import coverage
import enrichment
from coverage import (SPEC_RE, ls_tree, read_blobs, is_code, is_test,
                      is_mirror_test, base_stem, logical_stem, load_aliases,
                      resolve, _canon_dir)

FC_KINDS = set(config.STEP1B_FAILURE_CAPABLE_KINDS)   # network, subprocess, db, fileio
WINDOW = config.STEP1B_BRACE_WINDOW
NETWORK_ANY = "__NETWORK_ANY__"
GLOBAL_FETCH = "__global_fetch__"
UNRESOLVED = "UNRESOLVED"


# --- §3 module-token extraction (frozen binding-precedence rule) --------------

_ID = re.compile(r"[A-Za-z_$][\w$]*")
_IMPORT = re.compile(r"import\s+(?:type\s+)?(?P<clause>[^;]+?)\s+from\s*['\"](?P<spec>[^'\"]+)['\"]")
_REQUIRE = re.compile(
    r"(?:const|let|var)\s+(?P<pat>\{[^}]*\}|[A-Za-z_$][\w$]*)\s*=\s*"
    r"require\(\s*['\"](?P<spec>[^'\"]+)['\"]\s*\)")


def canon_module(spec: str) -> str:
    """Canonical module token: strip node:, fold fs/* and fs/promises -> fs."""
    s = spec.strip()
    if s.startswith("node:"):
        s = s[5:]
    if s == "fs" or s.startswith("fs/"):
        return "fs"
    return s


def _clause_ids(clause: str) -> list[str]:
    """Local identifiers bound by an import clause (default/namespace/named)."""
    ids: list[str] = []
    clause = clause.strip()
    for m in re.finditer(r"\*\s+as\s+([A-Za-z_$][\w$]*)", clause):
        ids.append(m.group(1))
    for block in re.findall(r"\{([^}]*)\}", clause):
        for part in block.split(","):
            part = part.strip()
            if not part:
                continue
            ids.append(part.split(" as ")[-1].strip() if " as " in part else part)
    head = clause.split("{")[0].split(",")[0].strip()
    if re.fullmatch(r"[A-Za-z_$][\w$]*", head):
        ids.append(head)
    return ids


def import_bindings(blob: str) -> dict[str, str]:
    """Map each locally-bound identifier -> its (canonical) source module spec.

    Relative specs are kept relative (caller treats them as a local wrapper ->
    UNRESOLVED). Best-effort static scan; no real scope analysis (premortem §3)."""
    b: dict[str, str] = {}
    for m in _IMPORT.finditer(blob):
        spec = m.group("spec")
        cm = spec if spec.startswith(".") else canon_module(spec)
        for i in _clause_ids(m.group("clause")):
            b[i] = cm
    for m in _REQUIRE.finditer(blob):
        spec = m.group("spec")
        cm = spec if spec.startswith(".") else canon_module(spec)
        pat = m.group("pat")
        if pat.startswith("{"):
            for part in pat.strip("{}").split(","):
                part = part.strip()
                if not part:
                    continue
                ident = part.split(":")[-1].strip() if ":" in part else part
                b[ident] = cm
        else:
            b[pat] = cm
    return b


def callee_root(line_text: str, col: int) -> tuple[str | None, str | None]:
    """Root identifier of the callee at 1-indexed `col`, and the next member.

    Handles `new X(` (skips `new`) and member chains `A.b.c(` (root=A, second=b)."""
    if col < 1 or col > len(line_text):
        return None, None
    s = line_text[col - 1:]
    nm = re.match(r"new\s+", s)
    if nm:
        s = s[nm.end():]
    m = _ID.match(s)
    if not m:
        return None, None
    root = m.group(0)
    mm = re.match(r"\.\s*([A-Za-z_$][\w$]*)", s[m.end():])
    return root, (mm.group(1) if mm else None)


def extract_module(lines: list[str], bindings: dict[str, str], line: int, col: int) -> str:
    """The boundary's module token by the frozen precedence (prereg §3)."""
    if not (0 < line <= len(lines)):
        return UNRESOLVED
    root, second = callee_root(lines[line - 1], col)
    if root is None:
        return UNRESOLVED
    if root in bindings:                       # in-file import binding ALWAYS wins
        spec = bindings[root]
        return UNRESOLVED if spec.startswith(".") else spec   # local wrapper -> UNRESOLVED
    if root == "fetch":                        # bare global fetch (no binding)
        return GLOBAL_FETCH
    if root in ("globalThis", "global") and second == "fetch":
        return GLOBAL_FETCH
    return UNRESOLVED


# --- §4.1 mock-of-M detection + §4.2 failure-sim detection (frozen catalogs) ---

_VIMOCK = re.compile(r"(?:vi|jest)\.(?:do)?[Mm]ock\(\s*['\"]([^'\"]+)['\"]")
_NOCK = re.compile(r"\bnock\b")
_MSW = re.compile(r"\b(?:setupServer|rest\.(?:get|post|put|delete|patch|all)|"
                  r"http\.(?:get|post|put|delete|patch|all)|HttpResponse)\b")
_STUBGLOBAL = re.compile(r"stubGlobal\(\s*['\"]fetch['\"]|\bglobal(?:This)?\.fetch\s*=")
_SPY = re.compile(r"(?:jest|vi)\.spyOn\(\s*([A-Za-z_$][\w$]*)|"
                  r"sinon\.(?:stub|mock)\(\s*([A-Za-z_$][\w$]*)")
_MOCKS_PATH = re.compile(r"__mocks__/(.+)$")

# failure-sim — FLAT (token presence suffices), STRICT family (counts for OVERSTATED)
_FS_FLAT = re.compile(
    r"\.mockRejectedValue(?:Once)?\(|\.replyWithError\(|HttpResponse\.error\(|"
    r"\.networkError\(|\.throws\(|\.rejects\(")
_FS_NET_STATUS = re.compile(r"\.reply\(\s*[45]\d\d|ctx\.status\(\s*[45]\d\d|"
                            r"status:\s*[45]\d\d|statusCode:\s*[45]\d\d")
# failure-sim — BRACED (anchor + a failure marker within a capped window)
_MOCKIMPL = re.compile(r"\.mockImplementation(?:Once)?\(")
_MOCKRESOLVE = re.compile(r"\.mock(?:ResolvedValue|ReturnValue)(?:Once)?\(")
_FACTORY = re.compile(r"(?:vi|jest)\.mock\([^,)]*,")
_THROW_MARK = re.compile(r"\bthrow\b|Promise\.reject|\breject\(")
# frozen §4.2 resolved-value failure markers: Promise.reject, { ok: false,
# { status: 4xx/5xx, new Error, { error:  (the BRACE on ok/error is faithful to the
# frozen `{ ok: false` / `{ error:` and avoids matching logger-mock `error: vi.fn()`)
_RESOLVE_FAIL = re.compile(r"Promise\.reject|\{\s*ok:\s*false|status(?:Code)?:\s*[45]\d\d|"
                           r"new Error|\{\s*error:")
# frozen §4.2 factory failure markers: body throws / rejecting / ok:false / 4xx-5xx
# (NO bare `error:` — a factory returning `{ error: vi.fn() }` is a logger mock, not a failure)
_FACTORY_FAIL = re.compile(r"\bthrow\b|Promise\.reject|\breject\(|\{\s*ok:\s*false|"
                           r"status(?:Code)?:\s*[45]\d\d")
# bare assertion — DESCRIPTIVE-ONLY (POSITIVE rate only; excluded from OVERSTATED)
_FS_BARE = re.compile(r"\.rejects(?![\w(])|\.toThrow(?:Error)?\(")


def _braced(blob: str, anchor: re.Pattern, marker: re.Pattern) -> bool:
    """A [BRACED] failure-sim: anchor whose capped window holds a failure marker."""
    for m in anchor.finditer(blob):
        if marker.search(blob[m.start():m.start() + WINDOW]):
            return True
    return False


def has_failuresim(blob: str, include_bare: bool) -> bool:
    if _FS_FLAT.search(blob) or _FS_NET_STATUS.search(blob):
        return True
    if _braced(blob, _MOCKIMPL, _THROW_MARK):
        return True
    if _braced(blob, _MOCKRESOLVE, _RESOLVE_FAIL):
        return True
    if _braced(blob, _FACTORY, _FACTORY_FAIL):
        return True
    return bool(include_bare and _FS_BARE.search(blob))


def mocked_modules(path: str, blob: str, bindings: dict[str, str]) -> set[str]:
    """Module tokens this test file mocks (prereg §4.1)."""
    mods: set[str] = set()
    for m in _VIMOCK.finditer(blob):
        spec = m.group(1)
        if not spec.startswith("."):
            mods.add(canon_module(spec))
    if _NOCK.search(blob) or _MSW.search(blob):
        mods.add(NETWORK_ANY)
    if _STUBGLOBAL.search(blob):
        mods.add(GLOBAL_FETCH)
    for m in _SPY.finditer(blob):
        x = m.group(1) or m.group(2)
        if x in bindings and not bindings[x].startswith("."):
            mods.add(bindings[x])
    mm = _MOCKS_PATH.search(path)               # a __mocks__/<module>.* manual mock
    if mm:
        mods.add(canon_module(mm.group(1).rsplit(".", 1)[0]))
    return mods


def _mock_hit(M: str, kind: str, mods: set[str]) -> bool:
    if M in mods:
        return True
    return kind == "network" and NETWORK_ANY in mods


# --- per-repo build -----------------------------------------------------------

def build_repo(repo: Path, commit: str, findings: list[dict]) -> tuple[list[dict], dict]:
    """Enrich each FC finding with module token + failure_tested flags (4 linkages)."""
    files = ls_tree(repo, commit)
    code = [f for f in files if is_code(f)]
    code_set = set(code)
    tests = [f for f in code if is_test(f)]
    aliases = load_aliases(repo, commit, files)
    test_blobs = read_blobs(repo, commit, tests)

    # per-test fingerprints + the L-module index (modules with a failing test anywhere)
    test_fp: dict[str, tuple[set[str], bool, bool]] = {}
    idx_all: set[str] = set()     # module -> some test mocks it AND simulates failure (incl bare)
    idx_strict: set[str] = set()  # same, strict catalog (excl bare assertion)
    for t in tests:
        blob = test_blobs.get(t, "")
        b = import_bindings(blob)
        mods = mocked_modules(t, blob, b)
        fa = has_failuresim(blob, include_bare=True)
        fs = has_failuresim(blob, include_bare=False)
        test_fp[t] = (mods, fa, fs)
        if fa:
            idx_all |= mods
        if fs:
            idx_strict |= mods

    # L-import edges: source file -> set of test files (resolved imports + mirror)
    src_tests: dict[str, set[str]] = {}
    for t in tests:
        for spec in SPEC_RE.findall(test_blobs.get(t, "")):
            r = resolve(spec, t, code_set, aliases)
            if r and not is_test(r):
                src_tests.setdefault(r, set()).add(t)
    mirror: dict[tuple, set[str]] = {}
    for t in tests:
        if is_mirror_test(t):
            mirror.setdefault((_canon_dir(t), logical_stem(t)), set()).add(t)

    def linked_tests(F: str) -> set[str]:
        return src_tests.get(F, set()) | mirror.get((_canon_dir(F), base_stem(F)), set())

    # module extraction per FC finding (read each finding's source file once)
    fc = [f for f in findings if f["kind"] in FC_KINDS]
    src_files = sorted({f["file"] for f in fc})
    src_blobs = read_blobs(repo, commit, src_files)
    bind_cache: dict[str, dict[str, str]] = {}
    line_cache: dict[str, list[str]] = {}

    out: list[dict] = []
    for f in fc:
        fp = f["file"]
        if fp not in line_cache:
            blob = src_blobs.get(fp, "")
            line_cache[fp] = blob.splitlines()
            bind_cache[fp] = import_bindings(blob)
        M = extract_module(line_cache[fp], bind_cache[fp], f["line"], f.get("col", 1))
        kind = f["kind"]
        resolved = M != UNRESOLVED

        if resolved:
            ft_mod_all = _mock_hit(M, kind, idx_all)
            ft_mod_strict = _mock_hit(M, kind, idx_strict)
            ft_imp_all = ft_imp_strict = False
            for t in linked_tests(fp):
                mods, fa, fs = test_fp[t]
                if _mock_hit(M, kind, mods):
                    ft_imp_all = ft_imp_all or fa
                    ft_imp_strict = ft_imp_strict or fs
        else:
            ft_mod_all = ft_mod_strict = ft_imp_all = ft_imp_strict = False

        g = dict(f)
        g["module"] = M
        g["resolved"] = int(resolved)
        g["ft_lmodule_all"] = int(ft_mod_all)
        g["ft_lmodule_strict"] = int(ft_mod_strict)
        g["ft_limport_all"] = int(ft_imp_all)
        g["ft_limport_strict"] = int(ft_imp_strict)
        # the outcome the reported contrast keys on (L-import, permissive catalog)
        g["failure_untested"] = int(not ft_imp_all)
        out.append(g)

    diag = {"n_test": len(tests), "n_fc": len(fc),
            "idx_all": len(idx_all), "idx_strict": len(idx_strict),
            "network_any_all": int(NETWORK_ANY in idx_all)}
    return out, diag


# --- rates + verdict ----------------------------------------------------------

def _rate(rows: list[dict], key: str, resolved_only: bool) -> tuple[float | None, int, int]:
    pool = [r for r in rows if r["resolved"]] if resolved_only else rows
    n = len(pool)
    tested = sum(r[key] for r in pool)
    return (tested / n if n else None), tested, n


def arm_rates(rows: list[dict]) -> dict:
    """failure-tested rates for one arm, both linkages, resolved-only + all."""
    d = {}
    for label, key in (("lmodule_all", "ft_lmodule_all"),
                       ("limport_all", "ft_limport_all"),
                       ("limport_strict", "ft_limport_strict")):
        r_res, t_res, n_res = _rate(rows, key, True)
        r_all, t_all, n_all = _rate(rows, key, False)
        d[label] = {"rate_resolved": r_res, "tested_resolved": t_res, "n_resolved": n_res,
                    "rate_all": r_all, "tested_all": t_all, "n_all": n_all}
    return d


def verdict(wd_rates: dict, unresolved_frac: float) -> str:
    if unresolved_frac > config.STEP1B_UNRESOLVED_ABORT:
        return (f"UNCOMPUTABLE (wd UNRESOLVED {unresolved_frac:.0%} > "
                f"{config.STEP1B_UNRESOLVED_ABORT:.0%} abort)")
    pos = wd_rates["lmodule_all"]["rate_resolved"]      # generous linkage, drop-UNRESOLVED
    ovr = wd_rates["limport_strict"]["rate_resolved"]   # strict linkage + catalog
    if pos is not None and pos <= config.STEP1B_TESTED_LOW:
        return "POSITIVE (dense untested-failure targets — recommender wedge by yield)"
    if ovr is not None and ovr >= config.STEP1B_TESTED_HIGH:
        return "OVERSTATED (untestability claim too strong)"
    return "WEAK / inconclusive"


def _perkind(rows: list[dict]) -> dict:
    out = {}
    for k in ("network", "subprocess", "db", "fileio"):
        kr = [r for r in rows if r["kind"] == k and r["resolved"]]
        if kr:
            out[k] = {"n": len(kr),
                      "tested_lmodule_all": sum(r["ft_lmodule_all"] for r in kr),
                      "tested_limport_strict": sum(r["ft_limport_strict"] for r in kr)}
    return out


# --- drive --------------------------------------------------------------------

def analyze(records: dict) -> dict:
    enriched: dict[str, dict] = {}
    diag: dict[str, dict] = {}
    for rid, r in records.items():
        rows, d = build_repo(config.CORPUS_CLONE_DIR / rid, r["pinned_commit"], r["findings"])
        enriched[rid] = {"findings": rows, "split": r["split"], "pinned_commit": r["pinned_commit"]}
        d["unresolved_wd"] = sum(1 for x in rows if x["arm"] == "wd" and not x["resolved"])
        d["n_wd"] = sum(1 for x in rows if x["arm"] == "wd")
        diag[rid] = d

    def pool(split=None, arm=None, subarm=None):
        out = []
        for rid, r in enriched.items():
            if split and r["split"] != split:
                continue
            for f in r["findings"]:
                if arm and f["arm"] != arm:
                    continue
                if subarm and f.get("subarm") != subarm:
                    continue
                out.append(f)
        return out

    wd = pool(arm="wd")
    unresolved_frac = (sum(1 for f in wd if not f["resolved"]) / len(wd)) if wd else 0.0
    wd_rates = arm_rates(wd)
    v = verdict(wd_rates, unresolved_frac)

    # reported context: matched failure_untested contrast (reuse coverage.analyze)
    contrast = {}
    for label, control, sub in (("vs_rest", "rest", None), ("vs_seamed", "seamed", "seamed"),
                                ("vs_wnd", "wnd", "wnd")):
        try:
            contrast[label] = coverage.analyze(enriched, label, control=control,
                                               key="failure_untested")
        except Exception as e:                  # underpowered arm may have no usable strata
            contrast[label] = {"error": str(e)}

    result = {
        "verdict": v,
        "thresholds": {"tested_low": config.STEP1B_TESTED_LOW,
                       "tested_high": config.STEP1B_TESTED_HIGH,
                       "unresolved_abort": config.STEP1B_UNRESOLVED_ABORT},
        "wd": {"n": len(wd), "unresolved_frac": unresolved_frac, "rates": wd_rates,
               "per_kind": _perkind(wd)},
        "wd_dev": {"rates": arm_rates(pool(split="dev", arm="wd"))},
        "wd_heldout": {"rates": arm_rates(pool(split="heldout", arm="wd"))},
        "context_arms": {
            "rest": arm_rates(pool(arm="rest")),
            "seamed": arm_rates([f for f in pool(arm="rest") if f.get("subarm") == "seamed"]),
            "wnd": arm_rates([f for f in pool(arm="rest") if f.get("subarm") == "wnd"]),
        },
        "reported_contrast": contrast,
        "diagnostics": diag,
    }
    return result


def _pct(x):
    return f"{x*100:.1f}%" if isinstance(x, (int, float)) else "n/a"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out", type=Path, default=config.STEP1B_RESULT_PATH)
    ap.add_argument("--repo", help="restrict to one repo (debug)")
    ap.add_argument("--debug-modules", action="store_true",
                    help="print module-extraction sample for --repo and exit")
    args = ap.parse_args()

    records = enrichment.load_records()
    if args.repo:
        records = {k: v for k, v in records.items() if k == args.repo}

    if args.debug_modules:
        rid = list(records)[0]
        rows, d = build_repo(config.CORPUS_CLONE_DIR / rid, records[rid]["pinned_commit"],
                             records[rid]["findings"])
        from collections import Counter
        wd = [r for r in rows if r["arm"] == "wd"]
        print(f"{rid}: {d}")
        print("module token counts (wd):", Counter(r["module"] for r in wd).most_common(15))
        print(f"wd resolved: {sum(r['resolved'] for r in wd)}/{len(wd)}")
        print("sample wd findings:")
        for r in wd[:20]:
            print(f"  {r['kind']:<10} {r['module']:<18} ft(Lmod_all={r['ft_lmodule_all']} "
                  f"Limp_strict={r['ft_limport_strict']}) {r['file'].split('/')[-1]}:{r['line']}")
        return

    result = analyze(records)
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    wr = result["wd"]["rates"]
    print("=== Step-1b: wd failure-TESTED rate (the verdict metric) ===")
    print(f"  wd n={result['wd']['n']}  UNRESOLVED={_pct(result['wd']['unresolved_frac'])}"
          f"  (abort>{_pct(config.STEP1B_UNRESOLVED_ABORT)})")
    print(f"  POSITIVE bar  : L-module/all  resolved rate = "
          f"{_pct(wr['lmodule_all']['rate_resolved'])} "
          f"({wr['lmodule_all']['tested_resolved']}/{wr['lmodule_all']['n_resolved']})  "
          f"(<= {_pct(config.STEP1B_TESTED_LOW)} => POSITIVE)")
    print(f"  OVERSTATED bar: L-import/strict resolved rate = "
          f"{_pct(wr['limport_strict']['rate_resolved'])} "
          f"({wr['limport_strict']['tested_resolved']}/{wr['limport_strict']['n_resolved']})  "
          f"(>= {_pct(config.STEP1B_TESTED_HIGH)} => OVERSTATED)")
    print(f"  per-kind (resolved): {result['wd']['per_kind']}")
    print(f"\n  VERDICT: {result['verdict']}")
    print("\n=== reported context (NOT gating) ===")
    for arm in ("rest", "seamed", "wnd"):
        a = result["context_arms"][arm]["lmodule_all"]
        print(f"  {arm:<7} L-module/all resolved rate = {_pct(a['rate_resolved'])} "
              f"({a['tested_resolved']}/{a['n_resolved']})")
    c = result["reported_contrast"].get("vs_rest", {})
    if "matched_ratio" in c:
        print(f"  wd-vs-rest matched failure_untested ratio = {c.get('matched_ratio')} "
              f"OR={c.get('odds_ratio')} CI={c.get('ci95')} -> {c.get('verdict')}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
