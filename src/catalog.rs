//! Boundary catalog as data (spec F21/F28). Embedded at compile time from
//! `catalog/typescript.toml`; parsed once at startup. Pure data — the matching
//! and seam-classification logic lives in `classify.rs`.

use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Catalog {
    #[allow(dead_code)]
    pub version: String,
    #[allow(dead_code)]
    pub language: String,
    pub boundary: Vec<Boundary>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Boundary {
    pub form: String,
    pub kind: String,
    #[serde(default)]
    pub leg: Vec<String>,
    #[serde(default)]
    pub demand: bool,
    #[serde(default)]
    pub ctor: Option<String>,
    #[serde(default)]
    pub callee: Option<String>,
    #[serde(default)]
    pub object: Option<String>,
    #[serde(default)]
    pub method: Option<String>,
    #[serde(default)]
    pub property: Option<String>,
    #[serde(default)]
    pub clock_ctor: bool,
    /// Comma-separated penultimate-segment allow-list (e.g. "responses,messages"
    /// to match only `*.responses.create` / `*.messages.create`).
    #[serde(default)]
    pub require_root: Option<String>,
}

impl Boundary {
    pub fn require_root_set(&self) -> Vec<String> {
        self.require_root
            .as_deref()
            .map(|s| s.split(',').map(|p| p.trim().to_string()).collect())
            .unwrap_or_default()
    }
}

pub fn load() -> Catalog {
    let raw = include_str!("../catalog/typescript.toml");
    toml::from_str(raw).expect("embedded catalog/typescript.toml must parse")
}
