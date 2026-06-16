"""Unit tests for step1b.py — the static failure-test detector.

Pins the frozen catalogs (preregistration-step1b.md §3/§4): the binding-precedence
module extraction, the mock + failure-sim detection families (FLAT/BRACED/bare),
and the absolute-rate verdict thresholds. Pure functions, no corpus/clone needed.

    python3 harness/test_step1b.py        (or: cd harness && python3 -m pytest test_step1b.py)
"""

from __future__ import annotations

import config
import step1b as s


# --- §3 import-binding parser -------------------------------------------------

def test_import_bindings_forms():
    b = s.import_bindings(
        'import axios from "axios";\n'
        'import { execSync, spawn } from "node:child_process";\n'
        'import * as fsp from "fs/promises";\n'
        'import Redis from "ioredis";\n'
        'import fetch from "node-fetch";\n'
        'const { exec } = require("child_process");\n'
        'import { get as g } from "got";\n'
    )
    assert b["axios"] == "axios"
    assert b["execSync"] == "child_process" and b["spawn"] == "child_process"
    assert b["fsp"] == "fs"                       # fs/promises folds to fs
    assert b["Redis"] == "ioredis"
    assert b["fetch"] == "node-fetch"             # node-fetch import, NOT global
    assert b["exec"] == "child_process"           # require destructure
    assert b["g"] == "got"                        # aliased named import


def test_import_bindings_multiline_and_relative():
    b = s.import_bindings('import {\n  a,\n  b as c,\n} from "m";\n'
                          'import { wrap } from "./local";\n')
    assert b["a"] == "m" and b["c"] == "m"
    assert b["wrap"] == "./local"                 # relative kept relative (-> UNRESOLVED later)


# --- §3 callee root + module extraction (the binding-precedence rule) ----------

def _mod(line, col, bindings):
    return s.extract_module([line], bindings, 1, col)


def test_extract_bare_global_fetch():
    # bare fetch with no binding -> __global_fetch__ (col points at the `f`)
    assert _mod("  const r = fetch(url);", 13, {}) == s.GLOBAL_FETCH


def test_extract_node_fetch_binding_wins_over_global():
    # an in-file fetch binding ALWAYS wins (prereg §3 step 2)
    assert _mod("  const r = fetch(url);", 13, {"fetch": "node-fetch"}) == "node-fetch"


def test_extract_member_call_is_not_global_fetch():
    # this.fetch(...) -> root is `this`, no binding -> UNRESOLVED, never __global_fetch__
    assert _mod("  const r = this.fetch(url);", 13, {}) == s.UNRESOLVED


def test_extract_globalthis_fetch():
    assert _mod("  globalThis.fetch(url);", 3, {}) == s.GLOBAL_FETCH


def test_extract_new_constructor_db():
    # col points at `new`; constructor identifier resolves via its import binding
    assert _mod("  const c = new Redis(opts);", 13, {"Redis": "ioredis"}) == "ioredis"


def test_extract_member_axios_get():
    # axios.get(...) -> root axios -> its module
    assert _mod("  await axios.get(u);", 9, {"axios": "axios"}) == "axios"


def test_extract_relative_wrapper_is_unresolved():
    assert _mod("  await db.query(q);", 9, {"db": "./db"}) == s.UNRESOLVED


def test_extract_subprocess_named_import():
    assert _mod("  execSync(cmd);", 3, {"execSync": "child_process"}) == "child_process"


# --- §4.1 mock-of-M detection -------------------------------------------------

def test_mocked_modules_vimock_and_nock_and_global():
    blob = ('vi.mock("axios");\n'
            'import nock from "nock";\n'
            'vi.stubGlobal("fetch", f);\n')
    mods = s.mocked_modules("a.test.ts", blob, {})
    assert "axios" in mods
    assert s.NETWORK_ANY in mods                  # nock -> network-agnostic
    assert s.GLOBAL_FETCH in mods


def test_mocked_modules_relative_vimock_ignored():
    mods = s.mocked_modules("a.test.ts", 'vi.mock("./svc");', {})
    assert mods == set()                          # relative mock targets a local file, not module M


def test_mocked_modules_manual_mock_path():
    mods = s.mocked_modules("__mocks__/child_process.ts", "export default {}", {})
    assert "child_process" in mods


def test_mock_hit_network_any_credits_any_network_boundary():
    assert s._mock_hit("axios", "network", {s.NETWORK_ANY})
    assert s._mock_hit(s.GLOBAL_FETCH, "network", {s.NETWORK_ANY})
    assert not s._mock_hit("axios", "db", {s.NETWORK_ANY})   # not for non-network kinds


# --- §4.2 failure-sim detection (FLAT / BRACED / bare DESCRIPTIVE-ONLY) --------

def test_failuresim_flat_mockrejected():
    assert s.has_failuresim("x.mockRejectedValue(new Error('e'));", include_bare=False)


def test_failuresim_braced_mockimplementation_throw():
    assert s.has_failuresim("x.mockImplementation(() => { throw new Error('e'); });",
                            include_bare=False)


def test_failuresim_braced_resolved_ok_false():
    assert s.has_failuresim("x.mockResolvedValue({ ok: false, status: 500 });",
                            include_bare=False)


def test_failuresim_nock_status():
    assert s.has_failuresim("nock(host).get('/').reply(500);", include_bare=False)


def test_failuresim_happy_path_not_flagged():
    # a happy-path mock with no failure marker -> NOT failure-sim
    assert not s.has_failuresim("x.mockResolvedValue({ ok: true, data: 1 });",
                                include_bare=False)
    assert not s.has_failuresim("x.mockImplementation(() => 42);", include_bare=False)


def test_bare_assertion_is_descriptive_only():
    # .rejects assertion counts ONLY when include_bare=True (POSITIVE rate), not strict
    blob = "await expect(run()).rejects.toThrow();"
    assert s.has_failuresim(blob, include_bare=True)
    assert not s.has_failuresim(blob, include_bare=False)


def test_braced_window_bound():
    # a throw marker far beyond the window must NOT be paired (frozen 600-char cap)
    far = "x.mockImplementation(() => {" + ("a;" * 400) + " throw e; });"
    assert not s.has_failuresim(far, include_bare=False)


# --- §6 verdict thresholds ----------------------------------------------------

def _wd_rates(lmod_all, limp_strict):
    mk = lambda r: {"rate_resolved": r, "tested_resolved": 0, "n_resolved": 100,
                    "rate_all": r, "tested_all": 0, "n_all": 100}
    return {"lmodule_all": mk(lmod_all), "limport_all": mk(limp_strict),
            "limport_strict": mk(limp_strict)}


def test_verdict_positive():
    assert s.verdict(_wd_rates(0.15, 0.05), 0.05).startswith("POSITIVE")


def test_verdict_overstated():
    assert s.verdict(_wd_rates(0.90, 0.45), 0.05).startswith("OVERSTATED")


def test_verdict_weak_bracket():
    # generous high (not <=0.20) AND strict low (not >=0.40) -> WEAK (the real corpus case)
    assert s.verdict(_wd_rates(0.71, 0.10), 0.04).startswith("WEAK")


def test_verdict_abort_overrides():
    # UNRESOLVED over abort -> UNCOMPUTABLE even if rates would say POSITIVE
    assert s.verdict(_wd_rates(0.10, 0.05), 0.40).startswith("UNCOMPUTABLE")


def test_thresholds_are_frozen():
    assert config.STEP1B_TESTED_LOW == 0.20
    assert config.STEP1B_TESTED_HIGH == 0.40
    assert config.STEP1B_UNRESOLVED_ABORT == 0.30
    assert config.STEP1B_FAILURE_CAPABLE_KINDS == ("network", "subprocess", "db", "fileio")


if __name__ == "__main__":
    import sys
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in fns:
        try:
            f()
            print(f"  ok  {n}")
        except Exception as e:                    # noqa: BLE001
            failed += 1
            print(f"FAIL  {n}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
