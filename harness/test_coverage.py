"""test_coverage.py — pins the Step-1 coverage join logic (coverage.py).

Pure-function tests: test-file classification, mirror stems, the strict
path-aware mirror, import resolution (relative + tsconfig alias + index), and the
`untested`-keyed matched ratio. No git / no clones — deterministic and offline.

Run: python3 -m pytest harness/test_coverage.py -q   (or: python3 harness/test_coverage.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import coverage  # noqa: E402


def test_is_test_classification():
    assert coverage.is_test("src/foo.test.ts")
    assert coverage.is_test("src/foo.spec.tsx")
    assert coverage.is_test("e2e/login.e2e.ts")
    assert coverage.is_test("src/__tests__/helper.ts")        # test-dir, no infix
    assert coverage.is_test("packages/x/tests/run.ts")
    assert not coverage.is_test("src/foo.ts")
    assert not coverage.is_test("src/service/client.ts")
    # "spec" must be a path segment, not a substring of a filename
    assert not coverage.is_test("src/respectful.ts")


def test_mirror_stems():
    assert coverage.is_mirror_test("a/foo.test.ts")
    assert not coverage.is_mirror_test("a/__tests__/foo.ts")   # dir-only => not mirror
    assert coverage.base_stem("a/foo.ts") == "foo"
    assert coverage.base_stem("a/foo.tsx") == "foo"
    assert coverage.logical_stem("a/foo.test.ts") == "foo"
    assert coverage.logical_stem("a/foo.spec.tsx") == "foo"


def test_strict_canon_dir():
    # co-located test and a __tests__ subdir canonicalize to the source dir
    assert coverage._canon_dir("a/b/foo.test.ts") == "a/b"
    assert coverage._canon_dir("a/b/__tests__/foo.test.ts") == "a/b"
    assert coverage._canon_dir("a/b/tests/foo.test.ts") == "a/b"
    # a far-away index.test.ts does NOT canonicalize to an unrelated dir
    assert coverage._canon_dir("core/llm/index.test.ts") == "core/llm"
    assert coverage._canon_dir("core/llm/index.test.ts") != coverage._canon_dir("binary/src/index.ts")


def test_resolve_relative_and_index():
    code = {"a/b/foo.ts", "a/b/bar/index.ts", "a/c/baz.tsx"}
    al = (".", {})
    # relative, extension inferred
    assert coverage.resolve("./foo", "a/b/x.test.ts", code, al) == "a/b/foo.ts"
    # .js specifier resolving to a .ts source (TS convention)
    assert coverage.resolve("./foo.js", "a/b/x.test.ts", code, al) == "a/b/foo.ts"
    # directory -> /index
    assert coverage.resolve("./bar", "a/b/x.test.ts", code, al) == "a/b/bar/index.ts"
    # parent traversal + .tsx
    assert coverage.resolve("../c/baz", "a/b/x.test.ts", code, al) == "a/c/baz.tsx"
    # bare module (node_modules) -> unresolved
    assert coverage.resolve("react", "a/b/x.test.ts", code, al) is None


def test_resolve_tsconfig_alias():
    code = {"src/services/client.ts", "src/util/index.ts"}
    aliases = (".", {"@/*": ["src/*"], "~util": ["src/util/index.ts"]})
    assert coverage.resolve("@/services/client", "test/x.test.ts", code, aliases) == "src/services/client.ts"
    assert coverage.resolve("@/util", "test/x.test.ts", code, aliases) == "src/util/index.ts"
    assert coverage.resolve("~util", "test/x.test.ts", code, aliases) == "src/util/index.ts"
    assert coverage.resolve("@/missing", "test/x.test.ts", code, aliases) is None


def _f(arm, untested, churn, size):
    return {"arm": arm, "untested": untested, "file_churn": churn, "site_size": size,
            "subarm": "seamed" if arm == "rest" else None}


def test_matched_keyed_ratio_direction():
    # one stratum, 10 wd / 10 rest; wd untested 8/10, rest 4/10 => ratio 2.0
    findings = ([_f("wd", 1, 5, 5)] * 8 + [_f("wd", 0, 5, 5)] * 2
                + [_f("rest", 1, 5, 5)] * 4 + [_f("rest", 0, 5, 5)] * 6)
    cuts = (10, 20)  # everything in bucket 0 => single stratum
    m = coverage.matched(findings, cuts, cuts, "rest", "untested")
    assert m["wd_rate"] == 0.8 and m["ctrl_rate"] == 0.4
    assert abs(m["matched_ratio"] - 2.0) < 1e-9
    assert m["odds_ratio"] is not None and m["odds_ratio"] > 1.0   # (.8/.2)/(.4/.6)=6


def test_cov_verdict_two_sided():
    import config
    # GO: point >= 1.5 and CI lower > 1
    assert coverage.cov_verdict(1.6, 1.1).startswith("GO")
    # FALSIFIED: point <= falsifier
    assert coverage.cov_verdict(config.COVERAGE_FALSIFIER, 0.9) == "FALSIFIED"
    # FALSIFIED: CI lower <= 1 even if point high
    assert coverage.cov_verdict(1.7, 0.95) == "FALSIFIED"
    # WEAK between
    assert "WEAK" in coverage.cov_verdict(1.3, 1.05)


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:                      # noqa: BLE001
            fails += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns) - fails}/{len(fns)} passed")
    sys.exit(1 if fails else 0)
