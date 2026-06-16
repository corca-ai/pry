//! `.pryconfig.toml` — per-repo pry configuration (docs/spec-untested.md, the
//! `.pryconfig.toml` direction). Agent-authored, committed, reviewed. The unified
//! config home the roadmap pointed at; v1 carries the two fields that pay off the
//! dogfood now:
//!
//! - `[scope].exclude` — gitignore-style globs dropped from ALL analysis
//!   (map/floor/untested). The production filter: drop `scripts/`/`bin/` tooling so
//!   `pry untested` shows production gaps only. SUPPLEMENTS `.gitignore` + `.pryignore`
//!   + `--exclude` (it does not replace them — additive, backward-compatible).
//! - `[untested].failure_capable_add` — extra boundary kinds treated as
//!   failure-capable by `pry untested`, on top of the default
//!   network/subprocess/db/fileio. The catalog ships `llm`/`slack` but they are omitted
//!   from the hardcoded default; a repo opts in here. This is the thing `.pryignore`
//!   structurally cannot express — it is why the config file earns its place.
//!
//! `deny_unknown_fields` gives section/key typo protection. Loading is best-effort:
//! a missing file yields defaults; a malformed file is a hard error (a silently
//! ignored config would be worse than a stop).

use anyhow::{Context, Result};
use serde::Deserialize;
use std::path::Path;

pub const CONFIG_FILENAME: &str = ".pryconfig.toml";

#[derive(Debug, Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct RawConfig {
    #[serde(default)]
    scope: RawScope,
    #[serde(default)]
    untested: RawUntested,
}

#[derive(Debug, Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct RawScope {
    #[serde(default)]
    exclude: Vec<String>,
}

#[derive(Debug, Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct RawUntested {
    #[serde(default)]
    failure_capable_add: Vec<String>,
}

/// The resolved per-repo configuration (defaults = empty when no file is present).
#[derive(Debug, Default, Clone)]
pub struct PryConfig {
    /// Positive-sense globs to exclude (merged with CLI `--exclude`).
    pub exclude: Vec<String>,
    /// Boundary kinds added to the `untested` failure-capable set.
    pub failure_capable_add: Vec<String>,
    /// The file it came from, for output transparency (None = defaults).
    pub loaded_from: Option<String>,
}

/// Resolve the config path for an analysis `root`: `<root>/.pryconfig.toml` when
/// `root` is a directory, else next to the single file being analyzed.
fn config_path(root: &Path) -> Option<std::path::PathBuf> {
    if root.is_dir() {
        Some(root.join(CONFIG_FILENAME))
    } else {
        root.parent().map(|p| p.join(CONFIG_FILENAME))
    }
}

/// Load `.pryconfig.toml` for `root`. Missing file -> defaults; malformed -> error.
pub fn load(root: &Path) -> Result<PryConfig> {
    let Some(path) = config_path(root) else {
        return Ok(PryConfig::default());
    };
    if !path.exists() {
        return Ok(PryConfig::default());
    }
    let text = std::fs::read_to_string(&path)
        .with_context(|| format!("reading {}", path.display()))?;
    parse(&text).with_context(|| format!("parsing {}", path.display()))
        .map(|mut c| {
            c.loaded_from = Some(path.display().to_string());
            c
        })
}

/// Parse config text (factored out for tests — no I/O).
pub fn parse(text: &str) -> Result<PryConfig> {
    let raw: RawConfig = toml::from_str(text)?;
    Ok(PryConfig {
        exclude: raw.scope.exclude,
        failure_capable_add: raw.untested.failure_capable_add,
        loaded_from: None,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_both_sections() {
        let c = parse(
            r#"
            [scope]
            exclude = ["scripts/**", "bin/**"]
            [untested]
            failure_capable_add = ["llm", "slack"]
        "#,
        )
        .unwrap();
        assert_eq!(c.exclude, vec!["scripts/**", "bin/**"]);
        assert_eq!(c.failure_capable_add, vec!["llm", "slack"]);
    }

    #[test]
    fn empty_and_partial_default_cleanly() {
        assert!(parse("").unwrap().exclude.is_empty());
        let c = parse("[scope]\nexclude = [\"x/\"]\n").unwrap();
        assert_eq!(c.exclude, vec!["x/"]);
        assert!(c.failure_capable_add.is_empty());
    }

    #[test]
    fn unknown_field_is_rejected() {
        // typo protection: a misspelled key/section is a hard error, not silently ignored
        assert!(parse("[scope]\nexcludes = [\"x/\"]\n").is_err(), "unknown key must error");
        assert!(parse("[scoop]\nexclude = [\"x/\"]\n").is_err(), "unknown section must error");
    }
}
