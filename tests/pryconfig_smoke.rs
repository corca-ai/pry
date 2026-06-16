//! End-to-end integration test for `.pryconfig.toml` (docs/spec-untested.md, the
//! config slice). Drives the BUILT binary on real fixtures (F26 keeps the lib pure;
//! file I/O + config loading live in `main.rs`). Two v1 capabilities + the typo
//! guards:
//!   - `[scope].exclude` drops tooling paths so `pry untested` shows production gaps.
//!   - `[untested].failure_capable_add` opts in catalog kinds (llm/slack) the default
//!     failure-capable set omits — surfacing edge gaps otherwise invisible.
//!
//! Fixtures live under the system temp dir (NOT `target/`, which the repo .gitignore
//! excludes — the `ignore` crate's parent-gitignore walk would mask them).

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const BIN: &str = env!("CARGO_BIN_EXE_pry");

fn dir(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("pry-cfg-{}-{name}", std::process::id()));
    let _ = fs::remove_dir_all(&d);
    fs::create_dir_all(&d).unwrap();
    d
}

fn untested_raw(d: &Path) -> std::process::Output {
    Command::new(BIN).arg("untested").arg(d).output().expect("run pry binary")
}

fn untested(d: &Path) -> String {
    let out = untested_raw(d);
    assert!(out.status.success(), "pry untested failed: {}", String::from_utf8_lossy(&out.stderr));
    String::from_utf8(out.stdout).unwrap()
}

const FETCH: &str = "export async function f(u: string) { return await fetch(u); }\n";

#[test]
fn scope_exclude_drops_tooling_path() {
    let d = dir("scope");
    fs::write(d.join("keep.ts"), FETCH).unwrap();
    fs::create_dir_all(d.join("scripts")).unwrap();
    fs::write(d.join("scripts/drop.ts"), FETCH).unwrap();

    // baseline: both welded fetches are on the worklist.
    let base = untested(&d);
    assert!(base.contains("keep.ts"), "keep.ts must be a candidate:\n{base}");
    assert!(base.contains("scripts/drop.ts"), "scripts/drop.ts present without config:\n{base}");

    // with [scope].exclude the tooling path is dropped (production filter).
    fs::write(d.join(".pryconfig.toml"), "[scope]\nexclude = [\"scripts/**\"]\n").unwrap();
    let filtered = untested(&d);
    assert!(filtered.contains("keep.ts"), "keep.ts must survive the filter:\n{filtered}");
    assert!(!filtered.contains("scripts/drop.ts"), "[scope].exclude must drop scripts/:\n{filtered}");
    let _ = fs::remove_dir_all(&d);
}

#[test]
fn failure_capable_add_surfaces_llm() {
    let d = dir("fcadd");
    // a welded, demand llm boundary (vercel-ai `generateText`), module resolves to "ai".
    fs::write(
        d.join("ask.ts"),
        "import { generateText } from \"ai\";\nexport async function ask(p: string) { return await generateText({ prompt: p }); }\n",
    )
    .unwrap();

    // default failure-capable set omits llm -> not on the worklist.
    let base = untested(&d);
    assert!(!base.contains("ask.ts"), "llm is omitted from the default failure-capable set:\n{base}");

    // opt in via config -> the untested llm boundary surfaces (module "ai").
    fs::write(d.join(".pryconfig.toml"), "[untested]\nfailure_capable_add = [\"llm\"]\n").unwrap();
    let opted = untested(&d);
    assert!(opted.contains("ask.ts"), "failure_capable_add = [llm] must surface the gap:\n{opted}");
    assert!(opted.contains("\"kind\": \"llm\""), "the surfaced finding is the llm boundary:\n{opted}");
    let _ = fs::remove_dir_all(&d);
}

#[test]
fn malformed_config_is_a_hard_error() {
    let d = dir("malformed");
    fs::write(d.join("keep.ts"), FETCH).unwrap();
    // unknown key (typo) must error, not be silently ignored.
    fs::write(d.join(".pryconfig.toml"), "[scope]\nexcludes = [\"x/\"]\n").unwrap();
    let out = untested_raw(&d);
    assert!(!out.status.success(), "a malformed .pryconfig.toml must exit non-zero");
    let _ = fs::remove_dir_all(&d);
}

#[test]
fn unknown_failure_capable_kind_is_rejected() {
    let d = dir("badkind");
    fs::write(d.join("keep.ts"), FETCH).unwrap();
    fs::write(d.join(".pryconfig.toml"), "[untested]\nfailure_capable_add = [\"htttp\"]\n").unwrap();
    let out = untested_raw(&d);
    assert!(!out.status.success(), "an unknown failure-capable kind (typo) must exit non-zero");
    assert!(
        String::from_utf8_lossy(&out.stderr).contains("unknown kind"),
        "the error should name the unknown kind"
    );
    let _ = fs::remove_dir_all(&d);
}
