//! pry analysis core (library). The pure, I/O-free functional core (F26
//! self-application: pry is testable by its own standard — `analyze_source`
//! takes injected source + tree + catalog and performs no I/O). The binary
//! (`src/main.rs`) is a thin shell that does file discovery and emit.

pub mod catalog;
pub mod classify;
pub mod floor;
pub mod untested;

/// Convenience: parse a TS source string and classify it against the embedded
/// catalog. Used by the binary's smoke path and by tests (no file I/O — F26).
pub fn analyze_str(src: &str, file: &str) -> Vec<classify::Finding> {
    let cat = catalog::load();
    let language: tree_sitter::Language = tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into();
    let mut parser = tree_sitter::Parser::new();
    parser
        .set_language(&language)
        .expect("set tree-sitter-typescript language");
    let Some(tree) = parser.parse(src.as_bytes(), None) else {
        return Vec::new();
    };
    classify::analyze_source(src.as_bytes(), file, &tree, &cat)
}
