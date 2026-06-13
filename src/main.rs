//! pry — static testability-surface analyzer (F1: deterministic, zero intelligence).
//!
//! Stage-1 minimal TS map (F28): `pry map <path>` parses TypeScript via
//! tree-sitter, matches the boundary catalog, classifies seamed/welded/ambiguous
//! with the two-tier inputSimulation tag, and emits a deterministic JSON map +
//! coverage summary (the F27 lens metric on the substitution-demand subset).

use anyhow::{Context, Result};
use pry::catalog;
use pry::classify::{self, Class, Finding};
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
    /// Emit the risk map (risk ranking, NOT a bug list) for a path of .ts files.
    Map {
        /// File or directory to analyze.
        path: PathBuf,
        /// Print only the coverage summary (omit per-finding rows).
        #[arg(long)]
        summary_only: bool,
    },
}

fn main() -> Result<()> {
    match Cli::parse().cmd {
        Cmd::Map { path, summary_only } => run_map(&path, summary_only),
    }
}

fn is_ts_source(p: &Path) -> bool {
    let Some(name) = p.file_name().and_then(|n| n.to_str()) else {
        return false;
    };
    if !name.ends_with(".ts") || name.ends_with(".d.ts") {
        return false;
    }
    if name.ends_with(".test.ts")
        || name.ends_with(".spec.ts")
        || name.ends_with("-test-support.ts")
    {
        return false;
    }
    let s = p.to_string_lossy();
    if s.contains("/__tests__/") || s.contains("/test/") || s.contains("/node_modules/") {
        return false;
    }
    true
}

fn discover(root: &Path) -> Vec<PathBuf> {
    let mut files = Vec::new();
    if root.is_file() {
        if is_ts_source(root) {
            files.push(root.to_path_buf());
        }
        return files;
    }
    for entry in ignore::WalkBuilder::new(root).hidden(false).build().flatten() {
        let p = entry.path();
        if p.is_file() && is_ts_source(p) {
            files.push(p.to_path_buf());
        }
    }
    files.sort(); // determinism (SC3)
    files
}

fn run_map(root: &Path, summary_only: bool) -> Result<()> {
    let cat = catalog::load();
    let language: tree_sitter::Language = tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into();
    let mut parser = tree_sitter::Parser::new();
    parser
        .set_language(&language)
        .context("set tree-sitter-typescript language")?;

    let files = discover(root);
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
