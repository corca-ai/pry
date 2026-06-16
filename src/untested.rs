//! pry untested — the welded∧untested worklist (docs/spec-untested.md).
//!
//! The product cut the north star needs: of the welded, FAILURE-CAPABLE boundaries
//! at substitution demand, which have NO test that simulates their failure. Those
//! are the "add a failure test" candidates. Ported from the validated reference
//! oracle `harness/step1b.py` (its catalogs were adversarially verified) — but only
//! the **generous L-module linkage**: a finding is `tested` iff some test anywhere
//! mocks its module AND simulates a failure. Generous-tested ⇒ conservative-untested
//! (a finding only lands on the worklist if NO test failure-sims its module) — the
//! low-false-alarm bias a worklist needs. The two-sided bracket / L-import / strict
//! catalog were eval-measurement machinery (a defensible *rate*); the product wants
//! candidate generation, not the bracket (docs/eval-gate.md closed that number WEAK).
//!
//! F1: deterministic, zero intelligence (regex = pure computation, no HTTP/LLM).
//! F26: the analysis core (`analyze_untested`) is I/O-free — injected findings +
//! source blobs + test blobs in, worklist out; the binary shell does discovery/emit.

use crate::classify::{Class, Finding};
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

const WINDOW: usize = 600; // STEP1B_BRACE_WINDOW (frozen §4.2 capped window)
const NETWORK_ANY: &str = "__NETWORK_ANY__";
const GLOBAL_FETCH: &str = "__global_fetch__";
const UNRESOLVED: &str = "UNRESOLVED";

/// One worklist row: a welded, failure-capable boundary whose failure has no test.
#[derive(Debug, Clone)]
pub struct UntestedFinding {
    pub file: String,
    pub line: usize,
    pub col: usize,
    pub kind: String,
    /// The boundary's module token (or "UNRESOLVED" for a local wrapper/alias).
    pub module: String,
    /// Provenance of the catalog entry that matched. "seed" until `.pryconfig.toml`
    /// (slice 2) adds repo-config entries — the contract this field establishes.
    pub catalog: &'static str,
    pub reason: String,
}

#[derive(Debug, Clone)]
pub struct UntestedDiag {
    pub candidates: usize, // welded ∧ demand ∧ failure-capable
    pub tested: usize,     // module in the failure-mock index (excluded from worklist)
    pub untested: usize,   // resolved, not in index — the worklist
    pub unresolved: usize, // module couldn't be linked (config target, slice 2)
    pub test_files: usize,
    pub index_modules: usize, // |idx| — diagnostic
}

// --- §3 module-token extraction (frozen binding-precedence rule) --------------

static IMPORT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"import\s+(?:type\s+)?(?P<clause>[^;]+?)\s+from\s*['"](?P<spec>[^'"]+)['"]"#).unwrap()
});
static REQUIRE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r#"(?:const|let|var)\s+(?P<pat>\{[^}]*\}|[A-Za-z_$][\w$]*)\s*=\s*require\(\s*['"](?P<spec>[^'"]+)['"]\s*\)"#,
    )
    .unwrap()
});
static STAR_AS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\*\s+as\s+([A-Za-z_$][\w$]*)").unwrap());
static BRACE_BLOCK: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\{([^}]*)\}").unwrap());
static BARE_ID: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[A-Za-z_$][\w$]*$").unwrap());
static NEW_PREFIX: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^new\s+").unwrap());
static ID_AT: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[A-Za-z_$][\w$]*").unwrap());
static MEMBER_AT: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\.\s*([A-Za-z_$][\w$]*)").unwrap());

/// Canonical module token: strip `node:`, fold `fs/*` and `fs/promises` -> `fs`.
fn canon_module(spec: &str) -> String {
    let s = spec.trim();
    let s = s.strip_prefix("node:").unwrap_or(s);
    if s == "fs" || s.starts_with("fs/") {
        return "fs".to_string();
    }
    s.to_string()
}

/// Local identifiers bound by an import clause (default/namespace/named).
fn clause_ids(clause: &str) -> Vec<String> {
    let mut ids = Vec::new();
    let clause = clause.trim();
    for c in STAR_AS.captures_iter(clause) {
        ids.push(c[1].to_string());
    }
    for block in BRACE_BLOCK.captures_iter(clause) {
        for part in block[1].split(',') {
            let part = part.trim();
            if part.is_empty() {
                continue;
            }
            // `foo as bar` -> bar; else the bare name.
            let id = match part.rsplit_once(" as ") {
                Some((_, after)) => after.trim(),
                None => part,
            };
            ids.push(id.to_string());
        }
    }
    // default import = head before any `{` and before the first `,`
    let head = clause.split('{').next().unwrap_or("");
    let head = head.split(',').next().unwrap_or("").trim();
    if BARE_ID.is_match(head) {
        ids.push(head.to_string());
    }
    ids
}

/// Map each locally-bound identifier -> its (canonical) source module spec.
/// Relative specs stay relative (caller treats them as a local wrapper -> UNRESOLVED).
/// Best-effort static scan; no real scope analysis (premortem §3).
pub fn import_bindings(blob: &str) -> HashMap<String, String> {
    let mut b = HashMap::new();
    for m in IMPORT.captures_iter(blob) {
        let spec = &m["spec"];
        let cm = if spec.starts_with('.') {
            spec.to_string()
        } else {
            canon_module(spec)
        };
        for id in clause_ids(&m["clause"]) {
            b.insert(id, cm.clone());
        }
    }
    for m in REQUIRE.captures_iter(blob) {
        let spec = &m["spec"];
        let cm = if spec.starts_with('.') {
            spec.to_string()
        } else {
            canon_module(spec)
        };
        let pat = &m["pat"];
        if pat.starts_with('{') {
            for part in pat.trim_matches(|c| c == '{' || c == '}').split(',') {
                let part = part.trim();
                if part.is_empty() {
                    continue;
                }
                // `a: b` destructure-rename -> b
                let ident = match part.rsplit_once(':') {
                    Some((_, after)) => after.trim(),
                    None => part,
                };
                b.insert(ident.to_string(), cm.clone());
            }
        } else {
            b.insert(pat.to_string(), cm.clone());
        }
    }
    b
}

/// Walk back to a UTF-8 char boundary at or below `end`.
fn clamp_end(s: &str, end: usize) -> usize {
    let mut e = end.min(s.len());
    while e > 0 && !s.is_char_boundary(e) {
        e -= 1;
    }
    e
}

/// Root identifier of the callee at 1-indexed byte `col`, and the next member.
/// Handles `new X(` (skips `new`) and member chains `A.b.c(` (root=A, second=b).
/// `col` is a tree-sitter byte column (+1), so slice by byte.
pub fn callee_root(line: &str, col: usize) -> (Option<String>, Option<String>) {
    if col < 1 || col > line.len() {
        return (None, None);
    }
    let start = col - 1;
    if !line.is_char_boundary(start) {
        return (None, None);
    }
    let mut s = &line[start..];
    if let Some(m) = NEW_PREFIX.find(s) {
        s = &s[m.end()..];
    }
    let Some(m) = ID_AT.find(s) else {
        return (None, None);
    };
    let root = m.as_str().to_string();
    let rest = &s[m.end()..];
    let second = MEMBER_AT.captures(rest).map(|c| c[1].to_string());
    (Some(root), second)
}

/// The boundary's module token by the frozen precedence (prereg §3):
/// in-file import binding ALWAYS wins (relative -> UNRESOLVED) > bare global fetch
/// > globalThis/global.fetch > UNRESOLVED.
pub fn extract_module(lines: &[&str], bindings: &HashMap<String, String>, line: usize, col: usize) -> String {
    if line == 0 || line > lines.len() {
        return UNRESOLVED.to_string();
    }
    let (root, second) = callee_root(lines[line - 1], col);
    let Some(root) = root else {
        return UNRESOLVED.to_string();
    };
    if let Some(spec) = bindings.get(&root) {
        return if spec.starts_with('.') {
            UNRESOLVED.to_string() // local wrapper -> UNRESOLVED
        } else {
            spec.clone()
        };
    }
    if root == "fetch" {
        return GLOBAL_FETCH.to_string();
    }
    if (root == "globalThis" || root == "global") && second.as_deref() == Some("fetch") {
        return GLOBAL_FETCH.to_string();
    }
    UNRESOLVED.to_string()
}

// --- §4.1 mock-of-M detection + §4.2 failure-sim detection (frozen catalogs) ---

static VIMOCK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"(?:vi|jest)\.(?:do)?[Mm]ock\(\s*['"]([^'"]+)['"]"#).unwrap());
static NOCK: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\bnock\b").unwrap());
static MSW: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\b(?:setupServer|rest\.(?:get|post|put|delete|patch|all)|http\.(?:get|post|put|delete|patch|all)|HttpResponse)\b",
    )
    .unwrap()
});
static STUBGLOBAL: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"stubGlobal\(\s*['"]fetch['"]|\bglobal(?:This)?\.fetch\s*="#).unwrap());
static SPY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?:jest|vi)\.spyOn\(\s*([A-Za-z_$][\w$]*)|sinon\.(?:stub|mock)\(\s*([A-Za-z_$][\w$]*)")
        .unwrap()
});
static MOCKS_PATH: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"__mocks__/(.+)$").unwrap());

// failure-sim — FLAT (token presence suffices)
static FS_FLAT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\.mockRejectedValue(?:Once)?\(|\.replyWithError\(|HttpResponse\.error\(|\.networkError\(|\.throws\(|\.rejects\(",
    )
    .unwrap()
});
static FS_NET_STATUS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\.reply\(\s*[45]\d\d|ctx\.status\(\s*[45]\d\d|status:\s*[45]\d\d|statusCode:\s*[45]\d\d")
        .unwrap()
});
// failure-sim — BRACED (anchor + a failure marker within the capped window)
static MOCKIMPL: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\.mockImplementation(?:Once)?\(").unwrap());
static MOCKRESOLVE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\.mock(?:ResolvedValue|ReturnValue)(?:Once)?\(").unwrap());
static FACTORY: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?:vi|jest)\.mock\([^,)]*,").unwrap());
static THROW_MARK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\bthrow\b|Promise\.reject|\breject\(").unwrap());
// frozen §4.2 resolved-value markers (the `{` on ok/error is faithful — avoids
// matching a logger-mock `error: vi.fn()`).
static RESOLVE_FAIL: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"Promise\.reject|\{\s*ok:\s*false|status(?:Code)?:\s*[45]\d\d|new Error|\{\s*error:").unwrap()
});
// frozen §4.2 factory markers (NO bare `error:` — `{ error: vi.fn() }` is a logger mock).
static FACTORY_FAIL: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\bthrow\b|Promise\.reject|\breject\(|\{\s*ok:\s*false|status(?:Code)?:\s*[45]\d\d").unwrap()
});
// bare assertion — DESCRIPTIVE-ONLY (generous index only). Frozen `\.rejects(?![\w(])`
// is refactored to the consuming-char equivalent `(?:[^\w(]|$)` (Rust regex has no
// lookaround) — faithful for boolean presence: `.rejects(` and `.rejectsFoo` stay
// excluded, `.rejects.`/`.rejects;`/EOS still hit.
static FS_BARE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\.rejects(?:[^\w(]|$)|\.toThrow(?:Error)?\(").unwrap());

/// A [BRACED] failure-sim: an anchor whose capped window holds a failure marker.
fn braced(blob: &str, anchor: &Regex, marker: &Regex) -> bool {
    for m in anchor.find_iter(blob) {
        let start = m.start();
        let end = clamp_end(blob, start + WINDOW);
        if marker.is_match(&blob[start..end]) {
            return true;
        }
    }
    false
}

/// Does this test blob simulate a boundary failure anywhere? (§4.2)
pub fn has_failuresim(blob: &str, include_bare: bool) -> bool {
    if FS_FLAT.is_match(blob) || FS_NET_STATUS.is_match(blob) {
        return true;
    }
    if braced(blob, &MOCKIMPL, &THROW_MARK) {
        return true;
    }
    if braced(blob, &MOCKRESOLVE, &RESOLVE_FAIL) {
        return true;
    }
    if braced(blob, &FACTORY, &FACTORY_FAIL) {
        return true;
    }
    include_bare && FS_BARE.is_match(blob)
}

/// Module tokens this test file mocks (§4.1).
pub fn mocked_modules(path: &str, blob: &str, bindings: &HashMap<String, String>) -> HashSet<String> {
    let mut mods = HashSet::new();
    for c in VIMOCK.captures_iter(blob) {
        let spec = &c[1];
        if !spec.starts_with('.') {
            mods.insert(canon_module(spec));
        }
    }
    if NOCK.is_match(blob) || MSW.is_match(blob) {
        mods.insert(NETWORK_ANY.to_string());
    }
    if STUBGLOBAL.is_match(blob) {
        mods.insert(GLOBAL_FETCH.to_string());
    }
    for c in SPY.captures_iter(blob) {
        let x = c.get(1).or_else(|| c.get(2)).map(|m| m.as_str());
        if let Some(x) = x {
            if let Some(spec) = bindings.get(x) {
                if !spec.starts_with('.') {
                    mods.insert(spec.clone());
                }
            }
        }
    }
    if let Some(c) = MOCKS_PATH.captures(path) {
        let rest = &c[1];
        let base = rest.rsplit_once('.').map(|(a, _)| a).unwrap_or(rest);
        mods.insert(canon_module(base));
    }
    mods
}

/// A boundary of `kind` whose module is `m` is failure-tested iff `m` is in the
/// index, or (network) the catch-all `__NETWORK_ANY__` is.
fn mock_hit(m: &str, kind: &str, idx: &HashSet<String>) -> bool {
    idx.contains(m) || (kind == "network" && idx.contains(NETWORK_ANY))
}

/// Pure analysis core (F26): no I/O.
///
/// - `findings`: all `classify` findings for the source tree.
/// - `source_blobs`: file (matching `Finding.file`) -> its source text (for the
///   re-read at the call site that resolves the module token).
/// - `test_files`: (path, blob) for every test file in the tree.
///
/// Returns `(worklist, unresolved, diag)` where `worklist` = the confident
/// untested candidates (resolved module, no failure-mock anywhere) and `unresolved`
/// = candidates whose module couldn't be linked (a `.pryconfig.toml` wrapper-alias
/// target, slice 2) — kept distinct so the worklist stays low-false-alarm.
/// `failure_capable` = the boundary kinds treated as failure-capable candidates
/// (default `floor::FLOOR_KINDS`, optionally extended by `.pryconfig.toml`'s
/// `[untested].failure_capable_add`).
pub fn analyze_untested(
    findings: &[Finding],
    source_blobs: &HashMap<String, String>,
    test_files: &[(String, String)],
    failure_capable: &[&str],
) -> (Vec<UntestedFinding>, Vec<UntestedFinding>, UntestedDiag) {
    // 1. the generous L-module failure-mock index: module -> some test mocks it AND
    //    simulates a failure (include_bare = the generous catalog).
    let mut idx: HashSet<String> = HashSet::new();
    for (path, blob) in test_files {
        if has_failuresim(blob, true) {
            let bindings = import_bindings(blob);
            for m in mocked_modules(path, blob, &bindings) {
                idx.insert(m);
            }
        }
    }

    // 2. cross each candidate against the index.
    let mut line_cache: HashMap<&str, Vec<&str>> = HashMap::new();
    let mut bind_cache: HashMap<&str, HashMap<String, String>> = HashMap::new();
    let mut worklist = Vec::new();
    let mut unresolved = Vec::new();
    let (mut candidates, mut tested) = (0usize, 0usize);

    for f in findings {
        if f.class != Class::Welded || !f.demand || !failure_capable.contains(&f.kind.as_str()) {
            continue;
        }
        candidates += 1;
        let fp = f.file.as_str();
        if !line_cache.contains_key(fp) {
            let blob: &str = source_blobs.get(fp).map(|s| s.as_str()).unwrap_or("");
            line_cache.insert(fp, blob.lines().collect());
            bind_cache.insert(fp, import_bindings(blob));
        }
        let module = extract_module(&line_cache[fp], &bind_cache[fp], f.line, f.col);

        if module == UNRESOLVED {
            unresolved.push(UntestedFinding {
                file: f.file.clone(),
                line: f.line,
                col: f.col,
                kind: f.kind.clone(),
                module: UNRESOLVED.to_string(),
                catalog: "seed",
                reason: "welded failure-capable boundary; module unresolved (local \
                         wrapper/alias — declare it in .pryconfig.toml to link)"
                    .to_string(),
            });
            continue;
        }
        if mock_hit(&module, &f.kind, &idx) {
            tested += 1;
            continue;
        }
        worklist.push(UntestedFinding {
            file: f.file.clone(),
            line: f.line,
            col: f.col,
            kind: f.kind.clone(),
            module: module.clone(),
            catalog: "seed",
            reason: format!(
                "welded failure-capable boundary; no test mocks module `{module}` and \
                 simulates its failure (static fingerprint — not proven uncovered)"
            ),
        });
    }

    // determinism (SC3): stable order by (file, line, col, kind)
    let sort_key = |a: &UntestedFinding, b: &UntestedFinding| {
        (a.file.as_str(), a.line, a.col, a.kind.as_str())
            .cmp(&(b.file.as_str(), b.line, b.col, b.kind.as_str()))
    };
    worklist.sort_by(sort_key);
    unresolved.sort_by(sort_key);

    let diag = UntestedDiag {
        candidates,
        tested,
        untested: worklist.len(),
        unresolved: unresolved.len(),
        test_files: test_files.len(),
        index_modules: idx.len(),
    };
    (worklist, unresolved, diag)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::floor::FLOOR_KINDS;

    fn binds(blob: &str) -> HashMap<String, String> {
        import_bindings(blob)
    }

    // --- import bindings -----------------------------------------------------
    #[test]
    fn import_named_default_namespace_require() {
        let b = binds(
            r#"
            import fetch from "node-fetch";
            import * as fs from "node:fs";
            import { execSync } from "child_process";
            import { Pool as PgPool } from "pg";
            const axios = require("axios");
            const { readFile } = require("fs/promises");
        "#,
        );
        assert_eq!(b.get("fetch").unwrap(), "node-fetch");
        assert_eq!(b.get("fs").unwrap(), "fs");
        assert_eq!(b.get("execSync").unwrap(), "child_process");
        assert_eq!(b.get("PgPool").unwrap(), "pg"); // named rename
        assert_eq!(b.get("axios").unwrap(), "axios");
        assert_eq!(b.get("readFile").unwrap(), "fs"); // fs/promises -> fs
    }

    #[test]
    fn relative_import_stays_relative() {
        let b = binds(r#"import { httpClient } from "./net/client";"#);
        assert_eq!(b.get("httpClient").unwrap(), "./net/client");
    }

    // --- module extraction (binding precedence) ------------------------------
    fn module_of(blob: &str, line_text: &str, col: usize) -> String {
        let b = import_bindings(blob);
        let lines = vec![line_text];
        extract_module(&lines, &b, 1, col)
    }

    #[test]
    fn bare_fetch_is_global() {
        // "  const r = fetch(url);" — `fetch` token starts at byte 13 (col 13)
        let m = module_of("", "  const r = fetch(url);", 13);
        assert_eq!(m, GLOBAL_FETCH);
    }

    #[test]
    fn node_fetch_binding_beats_global() {
        let m = module_of(
            r#"import fetch from "node-fetch";"#,
            "  const r = fetch(url);",
            13,
        );
        assert_eq!(m, "node-fetch", "in-file binding wins over the bare-fetch fallback");
    }

    #[test]
    fn member_call_resolves_root() {
        // axios.get(...) — root=axios bound to "axios"
        let m = module_of(r#"const axios = require("axios");"#, "  await axios.get(u);", 9);
        assert_eq!(m, "axios");
    }

    #[test]
    fn new_redis_resolves_constructor_root() {
        let m = module_of(r#"import Redis from "ioredis";"#, "  const c = new Redis();", 13);
        assert_eq!(m, "ioredis");
    }

    #[test]
    fn local_wrapper_is_unresolved() {
        let m = module_of(
            r#"import { httpGet } from "./util";"#,
            "  const r = httpGet(u);",
            13,
        );
        assert_eq!(m, UNRESOLVED, "relative-import callee -> UNRESOLVED (config target)");
    }

    // --- mocked modules ------------------------------------------------------
    #[test]
    fn vimock_and_network_any_and_spy() {
        let blob = r#"
            import axios from "axios";
            vi.mock("child_process");
            vi.mock("axios");
            import { setupServer } from "msw/node";
            const srv = setupServer();
            vi.spyOn(axios, "get");
        "#;
        let mods = mocked_modules("a.test.ts", blob, &import_bindings(blob));
        assert!(mods.contains("child_process"));
        assert!(mods.contains("axios"));
        assert!(mods.contains(NETWORK_ANY), "msw -> NETWORK_ANY");
    }

    #[test]
    fn stubglobal_and_mocks_dir() {
        let blob = r#"vi.stubGlobal("fetch", vi.fn());"#;
        let mods = mocked_modules("x.test.ts", blob, &import_bindings(blob));
        assert!(mods.contains(GLOBAL_FETCH));
        let mods2 = mocked_modules("__mocks__/fs.ts", "", &HashMap::new());
        assert!(mods2.contains("fs"), "__mocks__/<module> manual mock");
    }

    #[test]
    fn relative_vimock_is_ignored() {
        let blob = r#"vi.mock("./local/thing");"#;
        let mods = mocked_modules("a.test.ts", blob, &HashMap::new());
        assert!(mods.is_empty(), "relative vi.mock is a local wrapper, not a module token");
    }

    // --- failure-sim detection ----------------------------------------------
    #[test]
    fn flat_markers_hit() {
        assert!(has_failuresim(r#"vi.mocked(fetch).mockRejectedValue(new Error("x"))"#, false));
        assert!(has_failuresim(r#"nock(h).get("/").replyWithError("boom")"#, false));
        assert!(has_failuresim(r#"server.use(http.get("/x", () => HttpResponse.error()))"#, false));
        assert!(has_failuresim(r#"scope.get("/").reply(500)"#, false));
    }

    #[test]
    fn braced_mockimpl_throw_hit() {
        assert!(has_failuresim(
            r#"vi.mocked(run).mockImplementation(() => { throw new Error("nope"); })"#,
            false
        ));
    }

    #[test]
    fn braced_mockresolve_okfalse_hit() {
        assert!(has_failuresim(
            r#"vi.mocked(fetch).mockResolvedValue({ ok: false, status: 503 })"#,
            false
        ));
    }

    #[test]
    fn factory_throw_hit_but_logger_factory_misses() {
        assert!(has_failuresim(
            r#"vi.mock("child_process", () => ({ execSync: () => { throw new Error("x"); } }))"#,
            false
        ));
        // a logger-mock factory returning { error: vi.fn() } is NOT a failure sim
        assert!(
            !has_failuresim(r#"vi.mock("../logger", () => ({ error: vi.fn(), info: vi.fn() }))"#, false),
            "logger factory must not count as a failure sim"
        );
    }

    #[test]
    fn bare_assertion_only_when_generous() {
        let blob = r#"await expect(p).rejects.toThrow("x")"#;
        assert!(has_failuresim(blob, true), "bare .rejects counts in the generous catalog");
        // `.rejects.toThrow(` -> .toThrow( is itself a bare marker, so strict still false
        // only via FLAT? no: .toThrow is bare-only. strict (include_bare=false) -> false.
        assert!(!has_failuresim(r#"expect(p).rejects.toEqual(x)"#, false),
            ".rejects.toEqual without a strict marker is bare-only");
    }

    #[test]
    fn rejects_with_paren_is_flat_not_bare() {
        // sinon's `.rejects(err)` (with paren) is a FLAT marker -> strict hit
        assert!(has_failuresim(r#"stub.rejects(new Error("x"))"#, false));
    }

    // --- end-to-end cross ----------------------------------------------------
    fn finding(file: &str, line: usize, col: usize, kind: &str) -> Finding {
        Finding {
            file: file.to_string(),
            line,
            col,
            kind: kind.to_string(),
            class: Class::Welded,
            input_sim: true,
            demand: true,
            leg: vec![],
            reason: String::new(),
        }
    }

    #[test]
    fn welded_fetch_no_failuretest_is_on_worklist() {
        let src = "export async function load(u) {\n  const r = fetch(u);\n  return r.json();\n}\n";
        let mut blobs = HashMap::new();
        blobs.insert("src/load.ts".to_string(), src.to_string());
        let findings = vec![finding("src/load.ts", 2, 13, "network")];
        let (wl, unres, diag) = analyze_untested(&findings, &blobs, &[], FLOOR_KINDS);
        assert_eq!(diag.candidates, 1);
        assert_eq!(unres.len(), 0);
        assert_eq!(wl.len(), 1, "global fetch with no test -> worklist");
        assert_eq!(wl[0].module, GLOBAL_FETCH);
    }

    #[test]
    fn same_fetch_with_failuretest_drops_off() {
        let src = "export async function load(u) {\n  const r = fetch(u);\n  return r.json();\n}\n";
        let mut blobs = HashMap::new();
        blobs.insert("src/load.ts".to_string(), src.to_string());
        let findings = vec![finding("src/load.ts", 2, 13, "network")];
        // a test that stubs global fetch AND simulates a failure
        let test = (
            "src/load.test.ts".to_string(),
            r#"vi.stubGlobal("fetch", vi.fn()); vi.mocked(fetch).mockRejectedValue(new Error("net"));"#
                .to_string(),
        );
        let (wl, _unres, diag) = analyze_untested(&findings, &blobs, &[test], FLOOR_KINDS);
        assert_eq!(diag.tested, 1);
        assert_eq!(wl.len(), 0, "failure-tested -> off the worklist");
    }

    #[test]
    fn local_wrapper_goes_to_unresolved_bucket_not_worklist() {
        let src = "import { httpGet } from \"./net\";\nexport async function load(u) {\n  return httpGet(u);\n}\n";
        let mut blobs = HashMap::new();
        blobs.insert("src/load.ts".to_string(), src.to_string());
        let findings = vec![finding("src/load.ts", 3, 10, "network")];
        let (wl, unres, _diag) = analyze_untested(&findings, &blobs, &[], FLOOR_KINDS);
        assert_eq!(wl.len(), 0, "unresolved must not pollute the confident worklist");
        assert_eq!(unres.len(), 1);
        assert_eq!(unres[0].module, UNRESOLVED);
    }

    #[test]
    fn non_candidates_are_skipped() {
        let mut blobs = HashMap::new();
        blobs.insert("src/a.ts".to_string(), "const t = Date.now();\n".to_string());
        // clock kind is not failure-capable; seamed/non-demand also excluded
        let mut clk = finding("src/a.ts", 1, 11, "clock");
        clk.demand = true;
        let mut seamed = finding("src/a.ts", 1, 11, "network");
        seamed.class = Class::Seamed;
        let mut nondemand = finding("src/a.ts", 1, 11, "network");
        nondemand.demand = false;
        let (wl, unres, diag) = analyze_untested(&[clk, seamed, nondemand], &blobs, &[], FLOOR_KINDS);
        assert_eq!(diag.candidates, 0);
        assert!(wl.is_empty() && unres.is_empty());
    }
}
