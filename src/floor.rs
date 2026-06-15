//! pry floor — the syntactic CLAIM channel (docs/spec-floor.md).
//!
//! Distinct from the map (prediction). The map was falsified as a *risk
//! predictor* (E9 + Step-1); the floor makes a *fact* claim about error handling,
//! judged by precision-of-a-fact (Aspirator/Yuan lineage), and is **weld-agnostic**
//! (it does NOT consult the welded/seamed classification).
//!
//! - **FLOOR-1 (swallowed boundary failure):** a `try` whose body contains a
//!   failure-capable boundary call (network/subprocess/db/fileio), paired with a
//!   `catch` that SWALLOWS — its body has no `throw`/`return`/`break`/`continue`
//!   out and no `*.exit(` abort (empty or log-only).
//! - **FLOOR-2 (swallow-then-commit, the severe subclass):** FLOOR-1 AND, after
//!   the try/catch within the same function, control reaches a mutation/commit
//!   (a persistence/mutation call or a `x.y = …` member assignment).
//!
//! Output is physically separate from `pry map` (premortem §13.B.2).

use crate::catalog::Catalog;
use crate::classify;
use tree_sitter::Node;

/// Failure-capable boundary kinds (clock/random/env have no failure to swallow).
pub const FLOOR_KINDS: &[&str] = &["network", "subprocess", "db", "fileio"];

const FUNCTION_KINDS: &[&str] = &[
    "function_declaration",
    "function_expression",
    "arrow_function",
    "method_definition",
    "generator_function_declaration",
    "generator_function",
];

/// Persistence/mutation call methods (the "commit" half of FLOOR-2).
const COMMIT_METHODS: &[&str] = &[
    "save", "update", "updateOne", "updateMany", "commit", "create", "insert",
    "insertOne", "insertMany", "upsert", "delete", "deleteOne", "deleteMany",
    "remove", "destroy", "persist", "flush", "write", "writeFile", "writeFileSync",
    "set", "put",
];

#[derive(Debug, Clone)]
pub struct FloorFinding {
    pub file: String,
    pub rule: &'static str, // "FLOOR-1" | "FLOOR-2"
    pub kind: String,       // the swallowed boundary kind
    pub line: usize,        // boundary call line (1-based)
    pub col: usize,
    pub catch_line: usize,
    pub commit_line: Option<usize>,
    pub reason: String,
}

fn pos(n: Node) -> (usize, usize) {
    let p = n.start_position();
    (p.row + 1, p.column + 1)
}

/// Walk `root`'s subtree (named nodes) WITHOUT descending into nested functions,
/// returning the first node whose kind is in `kinds`.
fn find_kind_same_fn<'t>(root: Node<'t>, kinds: &[&str]) -> Option<Node<'t>> {
    let mut stack: Vec<(Node, bool)> = vec![(root, true)];
    while let Some((node, is_root)) = stack.pop() {
        if !is_root && FUNCTION_KINDS.contains(&node.kind()) {
            continue; // a nested fn's throw/commit is not this fn's control flow
        }
        if kinds.contains(&node.kind()) {
            return Some(node);
        }
        let mut c = node.walk();
        for ch in node.named_children(&mut c) {
            stack.push((ch, false));
        }
    }
    None
}

/// A catch clause "swallows" iff its body contains no control-exit (throw, return,
/// break, continue) at this function level and no `*.exit(` abort call.
fn catch_swallows(catch_body: Node, src: &[u8]) -> bool {
    if find_kind_same_fn(
        catch_body,
        &["throw_statement", "return_statement", "break_statement", "continue_statement"],
    )
    .is_some()
    {
        return false;
    }
    // `process.exit(...)` / `.exit(` abort: cheap text scan of the catch body.
    let txt = node_text(catch_body, src);
    if txt.contains(".exit(") || txt.contains("exit(") && txt.contains("process") {
        return false;
    }
    true
}

fn node_text<'a>(n: Node, src: &'a [u8]) -> &'a str {
    std::str::from_utf8(&src[n.byte_range()]).unwrap_or("")
}

/// Is `call` a mutation/commit? (a) member call `x.<commit-method>(...)`, or
/// (b) handled separately for assignments.
fn is_commit_call(call: Node, src: &[u8]) -> bool {
    if call.kind() != "call_expression" {
        return false;
    }
    let Some(func) = call.child_by_field_name("function") else {
        return false;
    };
    if func.kind() != "member_expression" {
        return false;
    }
    let Some(prop) = func.child_by_field_name("property") else {
        return false;
    };
    COMMIT_METHODS.contains(&node_text(prop, src))
}

/// `x.y = …` member assignment (a state mutation).
fn is_member_assignment(node: Node) -> bool {
    if node.kind() != "assignment_expression" {
        return false;
    }
    node.child_by_field_name("left")
        .map(|l| l.kind() == "member_expression" || l.kind() == "subscript_expression")
        .unwrap_or(false)
}

/// Does `root`'s subtree (same fn) contain a mutation/commit? Returns its line.
fn find_commit_same_fn(root: Node, src: &[u8]) -> Option<usize> {
    let mut stack: Vec<(Node, bool)> = vec![(root, true)];
    while let Some((node, is_root)) = stack.pop() {
        if !is_root && FUNCTION_KINDS.contains(&node.kind()) {
            continue;
        }
        if is_commit_call(node, src) || is_member_assignment(node) {
            return Some(pos(node).0);
        }
        let mut c = node.walk();
        for ch in node.named_children(&mut c) {
            stack.push((ch, false));
        }
    }
    None
}

/// Statements that lexically FOLLOW `try_node` within its enclosing function:
/// walk up to (not into) the function boundary, collecting each ancestor's
/// following named siblings. A commit in any of those subtrees = "reaches commit".
fn commit_after_in_fn(try_node: Node, src: &[u8]) -> Option<usize> {
    let mut cur = try_node;
    loop {
        // collect following siblings of `cur`
        let mut sib = cur.next_named_sibling();
        while let Some(s) = sib {
            if let Some(line) = find_commit_same_fn(s, src) {
                return Some(line);
            }
            sib = s.next_named_sibling();
        }
        let Some(parent) = cur.parent() else { return None };
        if FUNCTION_KINDS.contains(&parent.kind()) {
            return None; // reached the enclosing function; stop
        }
        cur = parent;
    }
}

/// First failure-capable boundary call in `body` (same fn), as (kind, line, col).
fn boundary_in_try(body: Node, src: &[u8], file: &str, cat: &Catalog) -> Option<(String, usize, usize)> {
    let mut stack: Vec<(Node, bool)> = vec![(body, true)];
    while let Some((node, is_root)) = stack.pop() {
        if !is_root && FUNCTION_KINDS.contains(&node.kind()) {
            continue; // a boundary inside a nested callback is not this try's call
        }
        if let Some(f) = classify::match_node(node, src, file, cat) {
            if FLOOR_KINDS.contains(&f.kind.as_str()) {
                return Some((f.kind, f.line, f.col));
            }
        }
        let mut c = node.walk();
        for ch in node.named_children(&mut c) {
            stack.push((ch, false));
        }
    }
    None
}

/// Analyze a parsed source for FLOOR-1/FLOOR-2 findings. Deterministic.
pub fn analyze_floor(src: &[u8], file: &str, tree: &tree_sitter::Tree, cat: &Catalog) -> Vec<FloorFinding> {
    let mut out = Vec::new();
    let mut stack = vec![tree.root_node()];
    while let Some(node) = stack.pop() {
        if node.kind() == "try_statement" {
            if let (Some(body), Some(handler)) = (
                node.child_by_field_name("body"),
                node.child_by_field_name("handler"),
            ) {
                let catch_body = handler.child_by_field_name("body").unwrap_or(handler);
                if let Some((kind, line, col)) = boundary_in_try(body, src, file, cat) {
                    if catch_swallows(catch_body, src) {
                        let commit_line = commit_after_in_fn(node, src);
                        let (rule, reason) = if commit_line.is_some() {
                            ("FLOOR-2", "swallowed boundary failure, then control reaches a mutation/commit")
                        } else {
                            ("FLOOR-1", "boundary failure swallowed by a catch that does not rethrow/return/exit")
                        };
                        out.push(FloorFinding {
                            file: file.to_string(),
                            rule,
                            kind,
                            line,
                            col,
                            catch_line: pos(handler).0,
                            commit_line,
                            reason: reason.to_string(),
                        });
                    }
                }
            }
        }
        let mut c = node.walk();
        for child in node.named_children(&mut c) {
            stack.push(child);
        }
    }
    // determinism: stable order by (file, line, col, rule)
    out.sort_by(|a, b| {
        (a.file.as_str(), a.line, a.col, a.rule).cmp(&(b.file.as_str(), b.line, b.col, b.rule))
    });
    out
}

#[cfg(test)]
mod tests {
    use crate::catalog;

    fn floor(src: &str) -> Vec<(&'static str, String)> {
        let cat = catalog::load();
        let lang: tree_sitter::Language = tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into();
        let mut p = tree_sitter::Parser::new();
        p.set_language(&lang).unwrap();
        let tree = p.parse(src.as_bytes(), None).unwrap();
        super::analyze_floor(src.as_bytes(), "t.ts", &tree, &cat)
            .into_iter()
            .map(|f| (f.rule, f.kind))
            .collect()
    }

    #[test]
    fn log_only_swallow_is_floor1() {
        let r = floor(r#"
            async function f(u) {
              try { await fetch("/x"); }
              catch (e) { console.log("failed", e); }
            }
        "#);
        assert_eq!(r, vec![("FLOOR-1", "network".to_string())]);
    }

    #[test]
    fn swallow_then_save_is_floor2() {
        let r = floor(r#"
            async function f(u) {
              try { await fetch("/charge"); }
              catch (e) { console.log("failed", e); }
              u.balance = 0;
              await db.users.save(u);
            }
        "#);
        // both the member-assignment and the save make this FLOOR-2
        assert_eq!(r, vec![("FLOOR-2", "network".to_string())]);
    }

    #[test]
    fn rethrow_is_not_flagged() {
        let r = floor(r#"
            async function f(u) {
              try { await fetch("/x"); }
              catch (e) { throw e; }
              u.balance = 0;
            }
        "#);
        assert!(r.is_empty(), "rethrow handles the error -> not a swallow");
    }

    #[test]
    fn return_in_catch_is_not_flagged() {
        let r = floor(r#"
            async function f(u) {
              try { return await fetch("/x"); }
              catch (e) { return null; }
            }
        "#);
        assert!(r.is_empty(), "early-return in catch is handling, not swallow-then-continue");
    }

    #[test]
    fn non_failure_kind_not_flagged() {
        // Date.now() is a clock read, not failure-capable -> excluded
        let r = floor(r#"
            function f(u) {
              try { const t = Date.now(); }
              catch (e) { console.log(e); }
              u.t = 1;
            }
        "#);
        assert!(r.is_empty(), "clock is not a failure-capable boundary");
    }

    #[test]
    fn nested_fn_commit_does_not_count() {
        let r = floor(r#"
            async function f(u) {
              try { await fetch("/x"); }
              catch (e) { console.log(e); }
              const cb = () => { u.balance = 0; };
            }
        "#);
        // the only "mutation" is inside a nested arrow -> not this fn's control flow
        assert_eq!(r, vec![("FLOOR-1", "network".to_string())]);
    }
}
