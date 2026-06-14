//! Walk-layer integration test for E7 scope control (docs/spec-eval-harness.md):
//! `.pryignore` and `--exclude <glob>` drop files the conventional test heuristic
//! in `is_source` can't catch (e.g. non-test-named `smoke-*.ts`). File I/O lives in
//! `main.rs` (F26 keeps the lib pure), so this drives the *built binary* on a real
//! fixture rather than the in-memory `analyze_str` path.
//!
//! Fixtures live under the system temp dir, NOT `CARGO_TARGET_TMPDIR`: the latter is
//! under the repo's `target/`, which the repo `.gitignore` excludes, so the `ignore`
//! crate's parent-gitignore traversal would drop every fixture file and mask the test.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const BIN: &str = env!("CARGO_BIN_EXE_pry");

/// A fresh fixture dir with two analyzable files, each a bare global `fetch`
/// (→ a welded `network` finding). The "drop" file is named like a smoke harness
/// (`smoke-*.ts`) so it is NOT caught by `is_source`'s `.test.`/`.spec.` heuristic.
fn fixture(name: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("pry-excl-{}-{name}", std::process::id()));
    let _ = fs::remove_dir_all(&dir);
    fs::create_dir_all(&dir).unwrap();
    let body = "export async function f(u: string) { return await fetch(u); }\n";
    fs::write(dir.join("keep.ts"), body).unwrap();
    fs::write(dir.join("smoke-drop.ts"), body).unwrap();
    dir
}

fn run_raw(dir: &Path, extra: &[&str]) -> std::process::Output {
    Command::new(BIN).arg("map").arg(dir).args(extra).output().expect("run pry binary")
}

fn run(dir: &Path, extra: &[&str]) -> String {
    let out = run_raw(dir, extra);
    assert!(
        out.status.success(),
        "pry map failed: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    String::from_utf8(out.stdout).unwrap()
}

#[test]
fn baseline_includes_smoke_file() {
    // Without exclusion, the smoke-named file IS analyzed — the gap E7 exists to fill.
    let dir = fixture("baseline");
    let out = run(&dir, &[]);
    assert!(out.contains("\"file\": \"keep.ts\""), "keep.ts should be analyzed:\n{out}");
    assert!(
        out.contains("\"file\": \"smoke-drop.ts\""),
        "smoke-drop.ts must be present when nothing excludes it:\n{out}"
    );
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn pryignore_excludes_path() {
    let dir = fixture("pryignore");
    fs::write(dir.join(".pryignore"), "smoke-*.ts\n").unwrap();
    let out = run(&dir, &[]);
    assert!(out.contains("\"file\": \"keep.ts\""), "keep.ts must survive .pryignore:\n{out}");
    assert!(!out.contains("smoke-drop.ts"), ".pryignore must drop smoke-drop.ts:\n{out}");
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn exclude_flag_excludes_glob() {
    let dir = fixture("flag");
    let out = run(&dir, &["--exclude", "smoke-*.ts"]);
    assert!(out.contains("\"file\": \"keep.ts\""), "keep.ts must survive --exclude:\n{out}");
    assert!(!out.contains("smoke-drop.ts"), "--exclude must drop smoke-drop.ts:\n{out}");
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn exclude_empty_glob_is_rejected() {
    // An empty glob (e.g. an unset `$VAR`) must error, not silently drop everything.
    let dir = fixture("empty");
    let out = run_raw(&dir, &["--exclude", ""]);
    assert!(!out.status.success(), "empty --exclude must exit non-zero");
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn exclude_leading_bang_is_rejected() {
    // `--exclude` is positive-sense; a gitignore-style `!re-include` must error
    // rather than become a silent `!!glob` no-op.
    let dir = fixture("bang");
    let out = run_raw(&dir, &["--exclude", "!smoke-*.ts"]);
    assert!(!out.status.success(), "leading-'!' --exclude must exit non-zero");
    assert!(
        String::from_utf8_lossy(&out.stderr).contains("positive"),
        "error should explain the positive-sense requirement"
    );
    let _ = fs::remove_dir_all(&dir);
}
