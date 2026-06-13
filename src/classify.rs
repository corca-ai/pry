//! TS boundary recognition + two-tier seam classification (spec F18/F19/F27).
//!
//! Leaf match (catalog) + 0-hop (intra-fn: `??` / default-param / local decl /
//! formal-param receiver) + one-hop (`this.attr` <- constructor). Beyond that ->
//! Ambiguous with a reason code. Network/subprocess wrappers behind injected
//! transport/executor interfaces are leaf-WELDED here (F22 rung-3 = stage 2).

use crate::catalog::{Boundary, Catalog};
use tree_sitter::Node;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Class {
    Seamed,
    Welded,
    Ambiguous,
}

impl Class {
    pub fn as_str(self) -> &'static str {
        match self {
            Class::Seamed => "seamed",
            Class::Welded => "welded",
            Class::Ambiguous => "ambiguous",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Finding {
    pub file: String,
    pub line: usize,
    pub col: usize,
    pub kind: String,
    pub class: Class,
    pub input_sim: bool,
    pub demand: bool,
    pub leg: Vec<String>,
    pub reason: String,
}

const FUNCTION_KINDS: &[&str] = &[
    "function_declaration",
    "function_expression",
    "arrow_function",
    "method_definition",
    "generator_function_declaration",
    "generator_function",
];

fn text<'a>(n: Node, src: &'a [u8]) -> &'a str {
    n.utf8_text(src).unwrap_or("")
}

/// inputSimulation tag (two-tier, F18): true = operand-redirectable (path/url/
/// connstring/cmd — cheap to test). clock & randomness have no operand to redirect
/// (you must substitute the source), so they are the hard welds.
fn kind_input_sim(kind: &str) -> bool {
    !matches!(kind, "clock" | "random")
}

/// Climb to the nearest enclosing function-like node.
fn enclosing_function<'t>(n: Node<'t>) -> Option<Node<'t>> {
    let mut cur = n.parent();
    while let Some(p) = cur {
        if FUNCTION_KINDS.contains(&p.kind()) {
            return Some(p);
        }
        cur = p.parent();
    }
    None
}

/// Names bound by a function-like node's parameter list (minimal: direct
/// identifiers, required/optional params, defaulted params, simple this-params).
fn param_names(fnode: Node, src: &[u8]) -> Vec<String> {
    let mut out = Vec::new();
    let params = fnode
        .child_by_field_name("parameters")
        .or_else(|| fnode.child_by_field_name("parameter"));
    let Some(params) = params else { return out };
    let mut cur = params.walk();
    for child in params.named_children(&mut cur) {
        collect_pattern_idents(child, src, &mut out);
    }
    out
}

fn collect_pattern_idents(n: Node, src: &[u8], out: &mut Vec<String>) {
    match n.kind() {
        "identifier" | "shorthand_property_identifier_pattern" => {
            out.push(text(n, src).to_string());
        }
        "required_parameter" | "optional_parameter" | "assignment_pattern" => {
            // the bound name is the parameter's pattern / left identifier
            if let Some(pat) = n
                .child_by_field_name("pattern")
                .or_else(|| n.child_by_field_name("left"))
                .or_else(|| n.named_child(0))
            {
                collect_pattern_idents(pat, src, out);
            }
        }
        "object_pattern" | "array_pattern" => {
            let mut c = n.walk();
            for ch in n.named_children(&mut c) {
                collect_pattern_idents(ch, src, out);
            }
        }
        _ => {}
    }
}

/// Is `name` a formal parameter of any enclosing function (closure-aware)?
fn is_enclosing_param(n: Node, name: &str, src: &[u8]) -> bool {
    let mut f = enclosing_function(n);
    while let Some(fnode) = f {
        if param_names(fnode, src).iter().any(|p| p == name) {
            return true;
        }
        f = enclosing_function(fnode);
    }
    false
}

/// Acquisition is in a `?? new X()` / nullish-default or a default-parameter
/// value -> the boundary has an in-band injectable alternative (SEAMED, F18).
fn nullish_or_default_context(n: Node, src: &[u8]) -> bool {
    let mut cur = n.parent();
    while let Some(p) = cur {
        match p.kind() {
            "binary_expression" => {
                if let Some(op) = p.child_by_field_name("operator") {
                    if text(op, src) == "??" {
                        return true;
                    }
                }
            }
            // default-param value lives inside the parameter list, not the body
            "formal_parameters" | "required_parameter" | "optional_parameter"
            | "assignment_pattern" => return true,
            // stop at a function/body boundary
            "statement_block" => break,
            k if FUNCTION_KINDS.contains(&k) => break,
            _ => {}
        }
        cur = p.parent();
    }
    false
}

fn enclosing_class_body<'t>(n: Node<'t>) -> Option<Node<'t>> {
    let mut cur = n.parent();
    while let Some(p) = cur {
        if p.kind() == "class_body" {
            return Some(p);
        }
        cur = p.parent();
    }
    None
}

/// Within a class body, find the constructor's `this.<attr> = RHS` and the
/// constructor's parameter names. Returns (rhs, ctor_params).
fn ctor_assignment<'t>(
    class_body: Node<'t>,
    attr: &str,
    src: &[u8],
) -> Option<(Node<'t>, Vec<String>)> {
    let mut c = class_body.walk();
    for member in class_body.named_children(&mut c) {
        if member.kind() != "method_definition" {
            continue;
        }
        let name = member.child_by_field_name("name").map(|n| text(n, src));
        if name != Some("constructor") {
            continue;
        }
        let ctor_params = param_names(member, src);
        let body = member.child_by_field_name("body")?;
        let rhs = find_this_assignment(body, attr, src)?;
        return Some((rhs, ctor_params));
    }
    None
}

fn find_this_assignment<'t>(node: Node<'t>, attr: &str, src: &[u8]) -> Option<Node<'t>> {
    if node.kind() == "assignment_expression" {
        if let Some(left) = node.child_by_field_name("left") {
            if left.kind() == "member_expression" {
                let is_this = left
                    .child_by_field_name("object")
                    .map(|o| o.kind() == "this")
                    .unwrap_or(false);
                let prop = left.child_by_field_name("property").map(|p| text(p, src));
                if is_this && prop == Some(attr) {
                    return node.child_by_field_name("right");
                }
            }
        }
    }
    let mut c = node.walk();
    for child in node.named_children(&mut c) {
        if let Some(found) = find_this_assignment(child, attr, src) {
            return Some(found);
        }
    }
    None
}

/// Classify a right-hand-side / declarator value against a set of in-scope
/// injectable names (constructor params or enclosing-fn params).
fn classify_rhs(rhs: Node, scope_params: &[String], src: &[u8]) -> (Class, &'static str) {
    match rhs.kind() {
        "binary_expression" => {
            if let Some(op) = rhs.child_by_field_name("operator") {
                if text(op, src) == "??" {
                    return (Class::Seamed, "nullish-default");
                }
            }
            (Class::Ambiguous, "rhs-expr")
        }
        "identifier" => {
            if scope_params.iter().any(|p| p == text(rhs, src)) {
                (Class::Seamed, "param-injected")
            } else {
                (Class::Ambiguous, "rhs-ident-origin")
            }
        }
        "member_expression" => {
            // e.g. `config.webClient` where `config` is a ctor/fn param
            let root = member_root_ident(rhs);
            if let Some(r) = root {
                if scope_params.iter().any(|p| p == text(r, src)) {
                    return (Class::Seamed, "param-config-injected");
                }
            }
            (Class::Ambiguous, "rhs-member-origin")
        }
        "new_expression" => (Class::Welded, "inline-new"),
        _ => (Class::Ambiguous, "rhs-other"),
    }
}

/// Leftmost identifier of a member chain (root receiver), if any.
fn member_root_ident<'t>(member: Node<'t>) -> Option<Node<'t>> {
    let mut obj = member.child_by_field_name("object")?;
    while obj.kind() == "member_expression" {
        obj = obj.child_by_field_name("object")?;
    }
    if obj.kind() == "identifier" {
        Some(obj)
    } else {
        None
    }
}

/// Scan the enclosing function body for `const name = RHS` / `name = RHS` /
/// `name ??= RHS` and return the RHS (0-hop dataflow).
fn local_decl_rhs<'t>(n: Node<'t>, name: &str, src: &[u8]) -> Option<Node<'t>> {
    let fnode = enclosing_function(n)?;
    let body = fnode.child_by_field_name("body")?;
    find_local_binding(body, name, src)
}

fn find_local_binding<'t>(node: Node<'t>, name: &str, src: &[u8]) -> Option<Node<'t>> {
    match node.kind() {
        "variable_declarator" => {
            if node.child_by_field_name("name").map(|x| text(x, src)) == Some(name) {
                return node.child_by_field_name("value");
            }
        }
        "assignment_expression" | "augmented_assignment_expression" => {
            if let Some(left) = node.child_by_field_name("left") {
                if left.kind() == "identifier" && text(left, src) == name {
                    return node.child_by_field_name("right");
                }
            }
        }
        _ => {}
    }
    let mut c = node.walk();
    for child in node.named_children(&mut c) {
        if let Some(f) = find_local_binding(child, name, src) {
            return Some(f);
        }
    }
    None
}

/// Classify a client method call by its receiver's origin.
fn classify_receiver(root: Node, src: &[u8]) -> (Class, String) {
    match root.kind() {
        // `this.attr.<...>.method()` -> one hop to the constructor
        "member_expression" => {
            let obj_is_this = root
                .child_by_field_name("object")
                .map(|o| o.kind() == "this")
                .unwrap_or(false);
            if obj_is_this {
                let attr = root
                    .child_by_field_name("property")
                    .map(|p| text(p, src))
                    .unwrap_or("");
                if let Some(cb) = enclosing_class_body(root) {
                    if let Some((rhs, ctor_params)) = ctor_assignment(cb, attr, src) {
                        let (c, r) = classify_rhs(rhs, &ctor_params, src);
                        return (c, format!("this.{attr}<-ctor:{r}"));
                    }
                }
                return (Class::Ambiguous, format!("this.{attr}-unresolved"));
            }
            (Class::Ambiguous, "receiver-member-origin".into())
        }
        "identifier" => {
            let name = text(root, src);
            if is_enclosing_param(root, name, src) {
                return (Class::Seamed, "receiver-param-injected".into());
            }
            if let Some(rhs) = local_decl_rhs(root, name, src) {
                let params = enclosing_function(root)
                    .map(|f| param_names(f, src))
                    .unwrap_or_default();
                let (c, r) = classify_rhs(rhs, &params, src);
                return (c, format!("receiver-local:{r}"));
            }
            (Class::Ambiguous, "receiver-ident-origin".into())
        }
        _ => (Class::Ambiguous, "receiver-other".into()),
    }
}

/// First argument node of a call/new expression, if any.
fn first_arg<'t>(call: Node<'t>) -> Option<Node<'t>> {
    let args = call.child_by_field_name("arguments")?;
    let mut c = args.walk();
    let res = args.named_children(&mut c).next();
    res
}

fn args_empty(call: Node) -> bool {
    match call.child_by_field_name("arguments") {
        Some(args) => args.named_child_count() == 0,
        None => true, // `new Date` with no parens
    }
}

fn finding(n: Node, b: &Boundary, file: &str, class: Class, input_sim: bool, reason: &str) -> Finding {
    let pos = n.start_position();
    Finding {
        file: file.to_string(),
        line: pos.row + 1,
        col: pos.column + 1,
        kind: b.kind.clone(),
        class,
        input_sim,
        demand: b.demand,
        leg: b.leg.clone(),
        reason: reason.to_string(),
    }
}

/// Try to match `node` against the catalog and, on a hit, classify it.
fn match_node(node: Node, src: &[u8], file: &str, cat: &Catalog) -> Option<Finding> {
    match node.kind() {
        "new_expression" => {
            let ctor = node.child_by_field_name("constructor").map(|c| text(c, src))?;
            for b in &cat.boundary {
                if b.form == "construct" && b.ctor.as_deref() == Some(ctor) {
                    if b.clock_ctor {
                        // new Date()  -> clock boundary; new Date(arg) -> not a boundary
                        if !args_empty(node) {
                            return None;
                        }
                        let class = if nullish_or_default_context(node, src) {
                            Class::Seamed
                        } else {
                            Class::Welded
                        };
                        let reason = if class == Class::Seamed { "clock-injected" } else { "clock-inline" };
                        return Some(finding(node, b, file, class, false, reason));
                    }
                    // provider client construction
                    let class = if nullish_or_default_context(node, src) {
                        Class::Seamed
                    } else {
                        Class::Welded
                    };
                    let reason = if class == Class::Seamed { "client-?? -default" } else { "client-inline-new" };
                    return Some(finding(node, b, file, class, true, reason));
                }
            }
            None
        }
        "call_expression" => {
            let func = node.child_by_field_name("function")?;
            match func.kind() {
                "identifier" => {
                    let name = text(func, src);
                    for b in &cat.boundary {
                        if b.form == "global_call" && b.callee.as_deref() == Some(name) {
                            // subprocess spawn with an injected (param) executable -> seam
                            if b.kind == "subprocess" {
                                if let Some(arg0) = first_arg(node) {
                                    if arg0.kind() == "identifier"
                                        && is_enclosing_param(node, text(arg0, src), src)
                                    {
                                        return Some(finding(node, b, file, Class::Seamed, true, "exe-param-injected"));
                                    }
                                }
                                return Some(finding(node, b, file, Class::Welded, true, "exe-inline"));
                            }
                            let reason = match b.kind.as_str() {
                                "network" => "http-global-leaf",
                                "clock" => "timer-global",
                                "random" => "random-global",
                                "fileio" => "fs-global",
                                "llm" => "llm-global-call",
                                _ => "global-call",
                            };
                            return Some(finding(node, b, file, Class::Welded, kind_input_sim(&b.kind), reason));
                        }
                    }
                    None
                }
                "member_expression" => {
                    let obj = func.child_by_field_name("object")?;
                    let prop = func.child_by_field_name("property").map(|p| text(p, src))?;
                    // builtin_call (Date.now / performance.now) + ns_call (fs.* / child_process.*)
                    if obj.kind() == "identifier" {
                        let obj_name = text(obj, src);
                        for b in &cat.boundary {
                            if b.form == "builtin_call"
                                && b.object.as_deref() == Some(obj_name)
                                && b.method.as_deref() == Some(prop)
                            {
                                let class = if nullish_or_default_context(node, src) {
                                    Class::Seamed
                                } else {
                                    Class::Welded
                                };
                                let is = kind_input_sim(&b.kind);
                                let reason = if class == Class::Seamed { "builtin-injected" } else { "builtin-inline" };
                                return Some(finding(node, b, file, class, is, reason));
                            }
                            if b.form == "ns_call"
                                && b.object.as_deref() == Some(obj_name)
                                && b.method.as_deref() == Some(prop)
                            {
                                if b.kind == "subprocess" {
                                    if let Some(arg0) = first_arg(node) {
                                        if arg0.kind() == "identifier"
                                            && is_enclosing_param(node, text(arg0, src), src)
                                        {
                                            return Some(finding(node, b, file, Class::Seamed, true, "exe-param-injected"));
                                        }
                                    }
                                    return Some(finding(node, b, file, Class::Welded, true, "exe-inline"));
                                }
                                return Some(finding(node, b, file, Class::Welded, kind_input_sim(&b.kind), "ns-call-leaf"));
                            }
                        }
                    }
                    // client method calls (.postMessage / .update / .create)
                    for b in &cat.boundary {
                        if b.form != "method" || b.method.as_deref() != Some(prop) {
                            continue;
                        }
                        let roots = b.require_root_set();
                        if !roots.is_empty() {
                            // penultimate segment must be in the allow-list
                            let penult = if obj.kind() == "member_expression" {
                                obj.child_by_field_name("property").map(|p| text(p, src))
                            } else {
                                None
                            };
                            match penult {
                                Some(p) if roots.iter().any(|r| r == p) => {}
                                _ => continue,
                            }
                        }
                        let root = receiver_root(func);
                        let (class, reason) = match root {
                            Some(r) => classify_receiver(r, src),
                            None => (Class::Ambiguous, "no-receiver".into()),
                        };
                        return Some(finding(node, b, file, class, true, &reason));
                    }
                    None
                }
                _ => None,
            }
        }
        "member_expression" => {
            // process.env  (member access, not a call)
            let obj = node.child_by_field_name("object")?;
            let prop = node.child_by_field_name("property").map(|p| text(p, src))?;
            if obj.kind() == "identifier" {
                let obj_name = text(obj, src);
                for b in &cat.boundary {
                    if b.form == "member"
                        && b.object.as_deref() == Some(obj_name)
                        && b.property.as_deref() == Some(prop)
                    {
                        return Some(finding(node, b, file, Class::Welded, true, "env-read"));
                    }
                }
            }
            None
        }
        _ => None,
    }
}

/// Root receiver of a method-call chain: the base identifier, or a `this.attr`
/// member when the chain bottoms out at `this`.
fn receiver_root<'t>(func_member: Node<'t>) -> Option<Node<'t>> {
    let mut cur = func_member.child_by_field_name("object")?;
    let mut prev = cur;
    while cur.kind() == "member_expression" {
        prev = cur;
        cur = cur.child_by_field_name("object")?;
    }
    if cur.kind() == "this" {
        Some(prev) // `this.attr` member_expression
    } else {
        Some(cur) // base identifier / call / etc.
    }
}

pub fn analyze_source(src: &[u8], file: &str, tree: &tree_sitter::Tree, cat: &Catalog) -> Vec<Finding> {
    let mut out = Vec::new();
    let mut stack = vec![tree.root_node()];
    while let Some(node) = stack.pop() {
        if let Some(f) = match_node(node, src, file, cat) {
            out.push(f);
        }
        let mut c = node.walk();
        for child in node.named_children(&mut c) {
            stack.push(child);
        }
    }
    out
}
