//! pry — static testability-surface analyzer (F1: deterministic, zero intelligence).
//!
//! Stage-1 minimal TS/JS map (F28): `pry map <path>` parses TypeScript and
//! JavaScript via tree-sitter (one TS-superset grammar — see `is_source`),
//! matches the boundary catalog, classifies seamed/welded/ambiguous
//! with the two-tier inputSimulation tag, and emits a deterministic JSON map +
//! coverage summary (the F27 lens metric on the substitution-demand subset).

use anyhow::{Context, Result};
use pry::catalog;
use pry::classify::{self, Class, Finding};
use pry::floor::{self, FloorFinding};
use pry::untested;
use clap::{Parser, Subcommand};
use serde_json::json;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[derive(Parser)]
#[command(name = "pry", version, about = "Static testability-surface analyzer (welded vs seamed boundaries).")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Emit the risk map (risk ranking, NOT a bug list) for a path of TS/JS files.
    Map {
        /// File or directory to analyze.
        path: PathBuf,
        /// Print only the coverage summary (omit per-finding rows).
        #[arg(long)]
        summary_only: bool,
        /// Exclude paths matching a glob (repeatable, positive-sense — no leading
        /// '!'; use a `.pryignore` file for gitignore-style re-include). Applied on
        /// top of `.gitignore` and a per-repo `.pryignore`. Scope is the repo's
        /// call — pry does not guess wantedness (E7, docs/spec-eval-harness.md).
        #[arg(long = "exclude", value_name = "GLOB")]
        exclude: Vec<String>,
    },
    /// Emit the CLAIM channel (swallowed boundary failures = defects to fix, NOT a
    /// ranking) for a path of TS/JS files. Physically separate from `map`
    /// (docs/spec-floor.md). FLOOR-1 = swallowed failure-capable boundary failure;
    /// FLOOR-2 = that, then control reaches a mutation/commit.
    Floor {
        /// File or directory to analyze.
        path: PathBuf,
        /// Exclude paths matching a glob (repeatable, positive-sense).
        #[arg(long = "exclude", value_name = "GLOB")]
        exclude: Vec<String>,
    },
    /// Emit the WORKLIST channel: welded, failure-capable boundaries (network/
    /// subprocess/db/fileio) at substitution demand whose FAILURE has no test that
    /// simulates it (docs/spec-untested.md). The "add a failure test" candidates —
    /// the north-star dogfood cut. "untested" = no failure-mock fingerprint (a fast
    /// static filter), NOT proven-uncovered.
    Untested {
        /// File or directory to analyze.
        path: PathBuf,
        /// Exclude paths matching a glob (repeatable, positive-sense).
        #[arg(long = "exclude", value_name = "GLOB")]
        exclude: Vec<String>,
    },
}

fn main() -> Result<()> {
    match Cli::parse().cmd {
        Cmd::Map { path, summary_only, exclude } => run_map(&path, summary_only, &exclude),
        Cmd::Floor { path, exclude } => run_floor(&path, &exclude),
        Cmd::Untested { path, exclude } => run_untested(&path, &exclude),
    }
}

/// Accept TypeScript and JavaScript source. JS (`.mjs`/`.cjs`/`.js`) is parsed
/// with the same tree-sitter-*typescript* grammar: TS is a syntactic superset of
/// JS and node kinds are grammar-determined, so the TS-targeted classifier (e.g.
/// the `required_parameter`/`optional_parameter` default-param seam logic) keeps
/// working on JS. Genuinely TS-only signals (`implements`, `: Type` rung-3) simply
/// don't appear in JS source — expected, not a bug.
fn is_source(p: &Path) -> bool {
    let Some(name) = p.file_name().and_then(|n| n.to_str()) else {
        return false;
    };
    let is_ts = name.ends_with(".ts") && !name.ends_with(".d.ts");
    let is_js = name.ends_with(".js") || name.ends_with(".mjs") || name.ends_with(".cjs");
    if !is_ts && !is_js {
        return false;
    }
    // drop test/spec/vitest/e2e/support files across both languages. `vitest`/`e2e`
    // are conventional stems the eval-gate test-file heuristic adds (docs/eval-gate.md):
    // e.g. continue's `*.vitest.ts` suites mock-inject `fetch`, so a welded finding
    // there is a FALSE-WELD. Repo-specific harness dirs (`manual-testing-sandbox/`,
    // `*-sol.ts`) stay the repo's `.pryignore` job (E7), NOT this default heuristic.
    let is_test_stem = ["test", "spec", "vitest", "e2e"].iter().any(|s| {
        [".ts", ".tsx", ".js", ".mjs", ".cjs"]
            .iter()
            .any(|ext| name.ends_with(&format!(".{s}{ext}")))
    });
    if is_test_stem || name.ends_with("-test-support.ts") {
        return false;
    }
    let s = p.to_string_lossy();
    if s.contains("/__tests__/")
        || s.contains("/test/")
        || s.contains("/tests/")
        || s.contains("/node_modules/")
    {
        return false;
    }
    true
}

/// Is `p` a TEST file? Used by `untested` to find the test corpus to fingerprint
/// for failure-sims. Ported faithfully from the oracle's `is_test` (harness
/// coverage.py / config.py `COVERAGE_TEST_{BASENAME,DIR}_REGEX`): a test-stem
/// basename `*.{test,spec,e2e,vitest,cy}.[cm]?[jt]sx?` OR a path under a test dir
/// `{__tests__,__mocks__,test(s),e2e,cypress,spec}`. The wider net (vs `is_source`'s
/// narrower test exclusion) keeps the failure-mock index complete — a `__mocks__/`
/// manual mock or a `.mts`/Cypress test that is omitted would shrink the index and
/// inflate false "untested" alarms. node_modules and `.d.ts` are excluded.
fn is_test_file(p: &Path) -> bool {
    let Some(name) = p.file_name().and_then(|n| n.to_str()) else {
        return false;
    };
    if name.ends_with(".d.ts") {
        return false;
    }
    let s = p.to_string_lossy();
    if s.contains("/node_modules/") {
        return false;
    }
    // basename stem.ext (COVERAGE_TEST_BASENAME_REGEX: the `[cm]?[jt]sx?` ext family)
    const STEMS: &[&str] = &["test", "spec", "e2e", "vitest", "cy"];
    const EXTS: &[&str] = &["js", "jsx", "ts", "tsx", "mjs", "cjs", "mts", "cts"];
    let test_stem = STEMS
        .iter()
        .any(|st| EXTS.iter().any(|ext| name.ends_with(&format!(".{st}.{ext}"))));
    if test_stem || name.ends_with("-test-support.ts") {
        return true;
    }
    // path under a test directory (COVERAGE_TEST_DIR_REGEX)
    ["/__tests__/", "/__mocks__/", "/test/", "/tests/", "/e2e/", "/cypress/", "/spec/"]
        .iter()
        .any(|d| s.contains(d))
}

/// Build the `.gitignore` + `.pryignore` + `--exclude` aware walker for `root`.
/// Scope is the repo's call: pry never guesses wantedness (E7).
fn build_walk(root: &Path, exclude: &[String]) -> Result<ignore::Walk> {
    let mut wb = ignore::WalkBuilder::new(root);
    wb.hidden(false);
    wb.add_custom_ignore_filename(".pryignore");
    if !exclude.is_empty() {
        let mut ob = ignore::overrides::OverrideBuilder::new(root);
        for g in exclude {
            let g = g.trim();
            // Guard two silent footguns: an empty glob (e.g. an unset `$VAR`) would
            // become the override line `!` = "ignore everything"; a user-leading `!`
            // would become `!!glob` = a no-op whitelist that excludes nothing. Both
            // would otherwise exit 0 with a wrong result. `--exclude` is
            // positive-sense; use a `.pryignore` file for gitignore-style re-include.
            if g.is_empty() {
                anyhow::bail!("--exclude glob is empty");
            }
            if g.starts_with('!') {
                anyhow::bail!(
                    "--exclude glob must be positive (no leading '!'): {g:?} — use a \
                     .pryignore file for gitignore-style re-include"
                );
            }
            // `!`-prefixed override = ignore this glob. With no whitelist glob in
            // the set, the `ignore` crate keeps every non-matching file, so this is
            // a pure additional ignore (not a whitelist that would drop the rest).
            ob.add(&format!("!{g}"))
                .with_context(|| format!("invalid --exclude glob: {g}"))?;
        }
        wb.overrides(ob.build().context("building --exclude override set")?);
    }
    Ok(wb.build())
}

/// Walk `root` for analyzable TS/JS source (honors `.gitignore`, a per-repo
/// `.pryignore`, and `--exclude` globs).
fn discover(root: &Path, exclude: &[String]) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    if root.is_file() {
        if is_source(root) {
            files.push(root.to_path_buf());
        }
        return Ok(files);
    }
    for entry in build_walk(root, exclude)?.flatten() {
        let p = entry.path();
        if p.is_file() && is_source(p) {
            files.push(p.to_path_buf());
        }
    }
    files.sort(); // determinism (SC3)
    Ok(files)
}

/// Walk `root` once, partitioning into (source, test) files. Used by `untested`,
/// which needs the source tree (to classify) AND the test tree (to fingerprint).
fn discover_split(root: &Path, exclude: &[String]) -> Result<(Vec<PathBuf>, Vec<PathBuf>)> {
    let mut sources = Vec::new();
    let mut tests = Vec::new();
    // Test classification wins over source: a file under `__mocks__/`/`e2e/`/`spec/`/
    // `cypress/` that `is_source` would otherwise accept belongs in the test pool (it
    // feeds the failure-mock index, and its own welds are not a production worklist).
    if root.is_file() {
        if is_test_file(root) {
            tests.push(root.to_path_buf());
        } else if is_source(root) {
            sources.push(root.to_path_buf());
        }
        return Ok((sources, tests));
    }
    for entry in build_walk(root, exclude)?.flatten() {
        let p = entry.path();
        if !p.is_file() {
            continue;
        }
        if is_test_file(p) {
            tests.push(p.to_path_buf());
        } else if is_source(p) {
            sources.push(p.to_path_buf());
        }
    }
    sources.sort(); // determinism (SC3)
    tests.sort();
    Ok((sources, tests))
}

fn run_map(root: &Path, summary_only: bool, exclude: &[String]) -> Result<()> {
    let cat = catalog::load();
    let language: tree_sitter::Language = tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into();
    let mut parser = tree_sitter::Parser::new();
    parser
        .set_language(&language)
        .context("set tree-sitter-typescript language")?;

    let files = discover(root, exclude)?;
    let mut findings: Vec<Finding> = Vec::new();
    for file in &files {
        let src = match std::fs::read(file) {
            Ok(b) => b,
            Err(_) => continue,
        };
        let Some(tree) = parser.parse(&src, None) else {
            continue;
        };
        let rel = file.strip_prefix(root).unwrap_or(file).to_string_lossy().to_string();
        findings.extend(classify::analyze_source(&src, &rel, &tree, &cat));
    }

    // determinism: stable order by (file, line, col, kind)
    findings.sort_by(|a, b| {
        (a.file.as_str(), a.line, a.col, a.kind.as_str())
            .cmp(&(b.file.as_str(), b.line, b.col, b.kind.as_str()))
    });

    let summary = summarize(&findings, files.len());
    let out = if summary_only {
        json!({
            "tool": "pry",
            "note": "risk ranking, not a bug list",
            "corpus": root.to_string_lossy(),
            "summary": summary,
        })
    } else {
        let rows: Vec<_> = findings
            .iter()
            .map(|f| {
                json!({
                    "file": f.file,
                    "line": f.line,
                    "col": f.col,
                    "kind": f.kind,
                    "class": f.class.as_str(),
                    "input_sim": f.input_sim,
                    "demand": f.demand,
                    "leg": f.leg,
                    "reason": f.reason,
                })
            })
            .collect();
        json!({
            "tool": "pry",
            "note": "risk ranking, not a bug list",
            "corpus": root.to_string_lossy(),
            "findings": rows,
            "summary": summary,
        })
    };
    println!("{}", serde_json::to_string_pretty(&out)?);
    Ok(())
}

fn run_floor(root: &Path, exclude: &[String]) -> Result<()> {
    let cat = catalog::load();
    let language: tree_sitter::Language = tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into();
    let mut parser = tree_sitter::Parser::new();
    parser
        .set_language(&language)
        .context("set tree-sitter-typescript language")?;

    let files = discover(root, exclude)?;
    let mut findings: Vec<FloorFinding> = Vec::new();
    for file in &files {
        let src = match std::fs::read(file) {
            Ok(b) => b,
            Err(_) => continue,
        };
        let Some(tree) = parser.parse(&src, None) else {
            continue;
        };
        let rel = file.strip_prefix(root).unwrap_or(file).to_string_lossy().to_string();
        findings.extend(floor::analyze_floor(&src, &rel, &tree, &cat));
    }
    findings.sort_by(|a, b| {
        (a.file.as_str(), a.line, a.col, a.rule).cmp(&(b.file.as_str(), b.line, b.col, b.rule))
    });

    let floor1 = findings.iter().filter(|f| f.rule == "FLOOR-1").count();
    let floor2 = findings.iter().filter(|f| f.rule == "FLOOR-2").count();
    let rows: Vec<_> = findings
        .iter()
        .map(|f| {
            json!({
                "file": f.file,
                "line": f.line,
                "col": f.col,
                "rule": f.rule,
                "kind": f.kind,
                "catch_line": f.catch_line,
                "commit_line": f.commit_line,
                "catch_empty": f.catch_empty,
                "reason": f.reason,
            })
        })
        .collect();
    let out = json!({
        "tool": "pry",
        "channel": "floor",
        "note": "claim channel: swallowed boundary failures (defects to fix), NOT a ranking",
        "corpus": root.to_string_lossy(),
        "findings": rows,
        "summary": {
            "files_scanned": files.len(),
            "total": findings.len(),
            "floor1": floor1,
            "floor2": floor2,
            "floor_kinds": floor::FLOOR_KINDS,
        },
    });
    println!("{}", serde_json::to_string_pretty(&out)?);
    Ok(())
}

fn run_untested(root: &Path, exclude: &[String]) -> Result<()> {
    let cat = catalog::load();
    let language: tree_sitter::Language = tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into();
    let mut parser = tree_sitter::Parser::new();
    parser
        .set_language(&language)
        .context("set tree-sitter-typescript language")?;

    let (sources, tests) = discover_split(root, exclude)?;

    // classify the source tree, keeping each file's text for the call-site re-read
    // that resolves a finding's module token.
    let mut findings: Vec<Finding> = Vec::new();
    let mut source_blobs: HashMap<String, String> = HashMap::new();
    for file in &sources {
        let bytes = match std::fs::read(file) {
            Ok(b) => b,
            Err(_) => continue,
        };
        let Some(tree) = parser.parse(&bytes, None) else {
            continue;
        };
        let rel = file.strip_prefix(root).unwrap_or(file).to_string_lossy().to_string();
        findings.extend(classify::analyze_source(&bytes, &rel, &tree, &cat));
        source_blobs.insert(rel, String::from_utf8_lossy(&bytes).into_owned());
    }

    // read the test corpus (no parse needed — fingerprints are textual).
    let mut test_files: Vec<(String, String)> = Vec::new();
    for file in &tests {
        let bytes = std::fs::read(file).unwrap_or_default();
        let rel = file.strip_prefix(root).unwrap_or(file).to_string_lossy().to_string();
        test_files.push((rel, String::from_utf8_lossy(&bytes).into_owned()));
    }

    let (worklist, unresolved, diag) =
        untested::analyze_untested(&findings, &source_blobs, &test_files);

    let row = |f: &untested::UntestedFinding| {
        json!({
            "file": f.file,
            "line": f.line,
            "col": f.col,
            "kind": f.kind,
            "module": f.module,
            "catalog": f.catalog,
            "reason": f.reason,
        })
    };
    let mut by_kind: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    for f in &worklist {
        *by_kind.entry(f.kind.clone()).or_default() += 1;
    }

    let out = json!({
        "tool": "pry",
        "channel": "untested",
        "note": "worklist: welded failure-capable boundaries whose failure has no test \
                 simulating it (static fingerprint, NOT proven uncovered)",
        "corpus": root.to_string_lossy(),
        "findings": worklist.iter().map(row).collect::<Vec<_>>(),
        "unresolved": unresolved.iter().map(row).collect::<Vec<_>>(),
        "summary": {
            "source_files": sources.len(),
            "test_files": diag.test_files,
            "failure_mock_index_modules": diag.index_modules,
            "candidates_welded_fc_demand": diag.candidates,
            "tested": diag.tested,
            "untested": diag.untested,
            "unresolved": diag.unresolved,
            "untested_by_kind": by_kind,
            "failure_capable_kinds": floor::FLOOR_KINDS,
        },
    });
    println!("{}", serde_json::to_string_pretty(&out)?);
    Ok(())
}

fn summarize(findings: &[Finding], files_scanned: usize) -> serde_json::Value {
    let count = |pred: &dyn Fn(&Finding) -> bool| findings.iter().filter(|f| pred(f)).count();

    let total = findings.len();
    let seamed = count(&|f| f.class == Class::Seamed);
    let welded = count(&|f| f.class == Class::Welded);
    let ambiguous = count(&|f| f.class == Class::Ambiguous);
    let decided = seamed + welded;

    // bare (diagnostic): fs/env-swamped, NOT the GO test (F27)
    let bare_welded_frac = ratio(welded, decided);
    let decided_frac = ratio(decided, total);

    // F27 lens: the substitution-demand subset is the GO test
    let d_seamed = count(&|f| f.demand && f.class == Class::Seamed);
    let d_welded = count(&|f| f.demand && f.class == Class::Welded);
    let d_ambiguous = count(&|f| f.demand && f.class == Class::Ambiguous);
    let d_decided = d_seamed + d_welded;
    let demand_welded_frac = ratio(d_welded, d_decided);

    // per-kind breakdown (BTreeMap -> deterministic key order)
    let mut kinds: std::collections::BTreeMap<String, [usize; 3]> = std::collections::BTreeMap::new();
    for f in findings {
        let e = kinds.entry(f.kind.clone()).or_default();
        match f.class {
            Class::Seamed => e[0] += 1,
            Class::Welded => e[1] += 1,
            Class::Ambiguous => e[2] += 1,
        }
    }
    let by_kind: serde_json::Map<String, serde_json::Value> = kinds
        .into_iter()
        .map(|(k, v)| (k, json!({ "seamed": v[0], "welded": v[1], "ambiguous": v[2] })))
        .collect();

    json!({
        "files_scanned": files_scanned,
        "total_boundaries": total,
        "seamed": seamed,
        "welded": welded,
        "ambiguous": ambiguous,
        "decided_fraction": decided_frac,
        "bare_welded_fraction_DIAGNOSTIC": bare_welded_frac,
        "substitution_demand_subset": {
            "total": d_seamed + d_welded + d_ambiguous,
            "seamed": d_seamed,
            "welded": d_welded,
            "ambiguous": d_ambiguous,
            "welded_fraction_LENS_GO_METRIC": demand_welded_frac,
            "band": [0.15, 0.85],
        },
        "by_kind": by_kind,
    })
}

fn ratio(n: usize, d: usize) -> f64 {
    if d == 0 {
        0.0
    } else {
        // fixed 4-dp formatting for cross-run/machine determinism (SC3)
        ((n as f64 / d as f64) * 10000.0).round() / 10000.0
    }
}

#[cfg(test)]
mod tests {
    use super::{is_source, is_test_file};
    use std::path::PathBuf;

    fn src(p: &str) -> bool {
        is_source(&PathBuf::from(p))
    }

    fn test_f(p: &str) -> bool {
        is_test_file(&PathBuf::from(p))
    }

    #[test]
    fn test_file_detection_matches_oracle() {
        // stems × the [cm]?[jt]sx? ext family
        assert!(test_f("/r/src/a.test.ts"));
        assert!(test_f("/r/src/a.spec.tsx"));
        assert!(test_f("/r/src/a.e2e.mts"), ".mts test stem (oracle ext family)");
        assert!(test_f("/r/src/a.cy.ts"), "Cypress `cy` stem");
        assert!(test_f("/r/src/a.vitest.mjs"));
        assert!(test_f("/r/pkg/util-test-support.ts"));
        // test directories (incl. __mocks__/e2e/cypress/spec the narrow net missed)
        assert!(test_f("/r/__mocks__/fs.ts"), "__mocks__ manual mock must feed the index");
        assert!(test_f("/r/e2e/login.ts"));
        assert!(test_f("/r/cypress/support/commands.ts"));
        assert!(test_f("/r/spec/thing.ts"));
        assert!(test_f("/r/__tests__/x.ts"));
        // non-tests
        assert!(!test_f("/r/src/index.ts"));
        assert!(!test_f("/r/src/api.d.ts"), ".d.ts is not a test");
        assert!(!test_f("/r/node_modules/foo/x.test.ts"), "node_modules excluded");
        assert!(!test_f("/r/src/vitestHelpers.ts"), "'vitest' substring is not the stem");
    }

    #[test]
    fn drops_conventional_test_files() {
        // pre-existing stems
        assert!(!src("src/foo.test.ts"));
        assert!(!src("src/foo.spec.tsx"));
        assert!(!src("pkg/util-test-support.ts"));
        assert!(!src("src/foo.test.mjs"));
        // lever #2 (eval-gate test-file heuristic): conventional vitest/e2e stems
        assert!(!src("core/autocomplete/ListenableGenerator.vitest.ts"), "vitest stem must drop");
        assert!(!src("test/login.e2e.ts"), "e2e stem must drop");
        assert!(!src("a/b/thing.vitest.mjs"), "vitest on a .mjs must drop");
    }

    #[test]
    fn keeps_real_source_incl_substring_lookalikes() {
        assert!(src("src/index.ts"));
        assert!(src("src/openai.ts"));
        // substring 'vitest'/'e2e' in a non-stem position must NOT drop a real file
        assert!(src("src/vitestHelpers.ts"), "'vitest' as a name substring is not a test stem");
        assert!(src("src/core2e.ts"), "'e2e' embedded mid-name is not the `.e2e.` stem");
        // repo-specific harness files are the `.pryignore` job, NOT this heuristic —
        // is_source keeps them; only an explicit .pryignore/--exclude drops them (E7).
        assert!(src("manual-testing-sandbox/next-edit/next-edit-10-5.ts"),
            "sandbox harness stays source by default (repo .pryignore scope, not the test heuristic)");
        assert!(src("manual-testing-sandbox/next-edit/next-edit-6-3-sol.ts"),
            "`-sol.ts` stays source by default (repo .pryignore scope)");
    }
}
