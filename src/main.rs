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
use clap::{Parser, Subcommand};
use serde_json::json;
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
}

fn main() -> Result<()> {
    match Cli::parse().cmd {
        Cmd::Map { path, summary_only, exclude } => run_map(&path, summary_only, &exclude),
        Cmd::Floor { path, exclude } => run_floor(&path, &exclude),
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

/// Walk `root` for analyzable TS/JS source. Honors `.gitignore` (via the `ignore`
/// crate), a per-repo `.pryignore` (same gitignore syntax — the repo's own
/// out-of-scope set, e.g. non-conventionally-named `smoke-*.ts` harnesses the
/// `is_source` test heuristic can't catch), and any `--exclude <glob>` overrides.
/// Scope is the repo's call: pry never guesses wantedness (E7).
fn discover(root: &Path, exclude: &[String]) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    if root.is_file() {
        if is_source(root) {
            files.push(root.to_path_buf());
        }
        return Ok(files);
    }
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
    for entry in wb.build().flatten() {
        let p = entry.path();
        if p.is_file() && is_source(p) {
            files.push(p.to_path_buf());
        }
    }
    files.sort(); // determinism (SC3)
    Ok(files)
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
    use super::is_source;
    use std::path::PathBuf;

    fn src(p: &str) -> bool {
        is_source(&PathBuf::from(p))
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
