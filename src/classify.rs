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
        // destructured default: `{ spawn = spawnSync }` -> bind `spawn`
        "object_assignment_pattern" => {
            if let Some(left) = n.child_by_field_name("left").or_else(|| n.named_child(0)) {
                collect_pattern_idents(left, src, out);
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

/// Acquisition is in a `?? new X()` / nullish-default, a default-parameter value,
/// a `<param-selector> ? … : new X()` factory ternary, or a `?? (() => new X())`
/// default-factory closure -> the boundary has an in-band injectable alternative
/// (SEAMED, F18). The ternary + arrow-default arms fix two 0-hop seams the leaf
/// model previously mis-called welded (`input.clientFactory ? …`, `input.now ??`).
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
            // `<param-selector> ? … : <boundary>`: an in-band conditional
            // alternative gated by the *presence* of an injectable dependency.
            "ternary_expression" => {
                if let Some(cond) = p.child_by_field_name("condition") {
                    if is_factory_selector(cond, p, src) {
                        return true;
                    }
                }
            }
            // default-param value lives inside the parameter list, not the body
            "formal_parameters" | "required_parameter" | "optional_parameter"
            | "assignment_pattern" => return true,
            // a `?? (() => new Date())` default factory: the inner boundary is the
            // default *behind* an injectable seam -> recurse on the wrapper fn.
            k if FUNCTION_KINDS.contains(&k) => return nullish_or_default_context(p, src),
            // stop at a statement boundary
            "statement_block" => break,
            _ => {}
        }
        cur = p.parent();
    }
    false
}

/// A ternary condition that selects on the *presence* of an injectable dependency
/// (`input.clientFactory ? …`, `factory ? …`) — a bare param/param-member
/// truthiness test, NOT a value comparison like `x > 0 ? new A() : new B()`.
fn is_factory_selector(cond: Node, scope: Node, src: &[u8]) -> bool {
    match cond.kind() {
        "identifier" => is_enclosing_param(scope, text(cond, src), src),
        "member_expression" => member_root_ident(cond)
            .map(|r| is_enclosing_param(scope, text(r, src), src))
            .unwrap_or(false),
        _ => false,
    }
}

const SERIALIZE_METHODS: &[&str] = &[
    "toISOString", "toString", "toLocaleString", "toLocaleDateString",
    "toLocaleTimeString", "toUTCString", "toDateString", "toTimeString", "toJSON",
];

/// A clock/randomness value used purely for display/record rather than control
/// flow: serialized via a `to*String`/`toJSON` method, embedded in a template
/// string, or placed directly as an object-property value. These have no failure
/// to inject, so they are NOT substitution-demand points (precision filter:
/// `new Date().toISOString()` record fields are ~half of ceal's raw demand-welds).
fn cosmetic_value_context(n: Node, src: &[u8]) -> bool {
    // (a) directly serialized: `new Date().toISOString()`, `Date.now().toString()`
    if let Some(p) = n.parent() {
        if p.kind() == "member_expression"
            && p.child_by_field_name("object").map(|o| o.id() == n.id()).unwrap_or(false)
        {
            if let Some(prop) = p.child_by_field_name("property") {
                if SERIALIZE_METHODS.contains(&text(prop, src)) {
                    return true;
                }
            }
        }
        // a `() => new Date()` / `() => Date.now()` thunk is a clock *provider*
        // definition (the injectable itself), not a consumption weld.
        if p.kind() == "arrow_function"
            && p.child_by_field_name("body").map(|b| b.id() == n.id()).unwrap_or(false)
        {
            return true;
        }
    }
    // (b) inside a template substitution, or (c) the value of an object pair
    let mut prev = n;
    let mut cur = n.parent();
    while let Some(p) = cur {
        match p.kind() {
            "template_substitution" => return true,
            "pair" => {
                return p
                    .child_by_field_name("value")
                    .map(|v| v.id() == prev.id())
                    .unwrap_or(false);
            }
            // a call argument may feed control flow (setTimeout, cache.set(TTL)) —
            // do not treat as cosmetic.
            "arguments" => return false,
            "statement_block" | "expression_statement" => break,
            k if FUNCTION_KINDS.contains(&k) => break,
            _ => {}
        }
        prev = p;
        cur = p.parent();
    }
    false
}

/// Timing arithmetic/relational operators — numeric, so a clock operand here is
/// control logic (elapsed/deadline/expiry), not a record value. `+` is handled
/// separately (it is timing for `Date.now() + ttl` but string concat for
/// `"at " + Date.now()`).
const ARITH_REL_OPS: &[&str] = &["-", "<", ">", "<=", ">=", "/", "*", "%"];

/// Does the node feed an arithmetic/relational comparison (climbing through
/// member/call/paren wrappers, e.g. `now.getTime() - x`)? `Date.now() + ttl` is
/// timing; `"at " + Date.now()` (a string operand) is concat. A logical binary
/// (`&&`, `||`, `==`) or any other context stops the climb.
fn in_arith_relational(n: Node, src: &[u8]) -> bool {
    let mut cur = n.parent();
    while let Some(p) = cur {
        match p.kind() {
            "binary_expression" => {
                let op = p.child_by_field_name("operator").map(|o| text(o, src)).unwrap_or("");
                if op == "+" {
                    // numeric addition (deadline/TTL) is timing; reject only if an
                    // operand is a string/template literal (concatenation).
                    let is_str = |f| {
                        p.child_by_field_name(f)
                            .map(|x| matches!(x.kind(), "string" | "template_string"))
                            .unwrap_or(false)
                    };
                    return !(is_str("left") || is_str("right"));
                }
                return ARITH_REL_OPS.contains(&op);
            }
            "member_expression" | "call_expression" | "parenthesized_expression"
            | "non_null_expression" | "as_expression" => {}
            _ => return false,
        }
        cur = p.parent();
    }
    false
}

const RELATIONAL_OPS: &[&str] = &["<", ">", "<=", ">=", "==", "===", "!=", "!=="];
const ARITHMETIC_OPS: &[&str] = &["-", "+", "*", "/", "%"];

/// Wrapper kinds that pass an expression's value through unchanged when climbing.
fn is_value_wrapper(kind: &str) -> bool {
    matches!(
        kind,
        "member_expression"
            | "call_expression"
            | "parenthesized_expression"
            | "non_null_expression"
            | "as_expression"
    )
}

/// If `n` (through value wrappers) is the *minuend* — the left operand — of a `-`
/// subtraction, return that subtraction node. A clock minuend (`Date.now() - X`) is
/// a duration/elapsed shape, the candidate for the duration-record sink hop. The
/// clock as a *subtrahend* (`deadline - Date.now()` = remaining time) or in any
/// other operator returns None, so the recall guard keeps it.
fn clock_subtraction_minuend<'t>(n: Node<'t>, src: &[u8]) -> Option<Node<'t>> {
    let mut prev = n;
    let mut cur = n.parent();
    while let Some(p) = cur {
        match p.kind() {
            k if is_value_wrapper(k) => {}
            "binary_expression" => {
                let op = p.child_by_field_name("operator").map(|o| text(o, src)).unwrap_or("");
                let is_left = p.child_by_field_name("left").map(|l| l.id() == prev.id()).unwrap_or(false);
                return if op == "-" && is_left { Some(p) } else { None };
            }
            _ => return None,
        }
        prev = p;
        cur = p.parent();
    }
    None
}

/// The enclosing `-` subtraction `n` is an operand of (either side), through value
/// wrappers, if any. Used for a *binding anchor's* uses, where the anchor can be
/// either operand (`Date.now() - started` reads `started` as the subtrahend).
fn enclosing_subtraction<'t>(n: Node<'t>, src: &[u8]) -> Option<Node<'t>> {
    let mut cur = n.parent();
    while let Some(p) = cur {
        match p.kind() {
            k if is_value_wrapper(k) => {}
            "binary_expression" => {
                let op = p.child_by_field_name("operator").map(|o| text(o, src)).unwrap_or("");
                return if op == "-" { Some(p) } else { None };
            }
            _ => return None,
        }
        cur = p.parent();
    }
    None
}

/// Does this expression's value ultimately reach a relational comparison or branch
/// condition (control), versus terminating in a record/log/return/argument sink?
/// Climbs through arithmetic (a duration in other units is still a duration) and
/// `?:`/parenthesized value-arms; a relational operator or an `if`/`while`/`?:`
/// *condition* is control; a `const` binding hops to its uses; any other terminal
/// (return, call argument, object pair, field assignment) is a sink. This is the
/// sink hop that separates `if (Date.now() - started > timeout)` (control, kept)
/// from `rec.ms = Date.now() - started` / `log(Date.now() - started)` (record,
/// demoted) — the cautilus duration-record class lever 3 over-kept.
fn value_reaches_control(node: Node, src: &[u8]) -> bool {
    let mut prev = node;
    let mut cur = node.parent();
    while let Some(p) = cur {
        match p.kind() {
            "parenthesized_expression" | "non_null_expression" | "as_expression" => {}
            "binary_expression" => {
                let op = p.child_by_field_name("operator").map(|o| text(o, src)).unwrap_or("");
                if RELATIONAL_OPS.contains(&op) {
                    return true;
                }
                if !ARITHMETIC_OPS.contains(&op) {
                    return false; // logical / `??` / bitwise -> not a timing comparison
                }
                // arithmetic: the value flows on (e.g. `(now - start) / 1000`)
            }
            "ternary_expression" => {
                // only the condition is control; a value-arm propagates the value
                if p.child_by_field_name("condition").map(|c| c.id() == prev.id()).unwrap_or(false) {
                    return true;
                }
            }
            "if_statement" | "while_statement" | "do_statement" | "for_statement" => {
                return p
                    .child_by_field_name("condition")
                    .map(|c| c.id() == prev.id())
                    .unwrap_or(false);
            }
            "variable_declarator" => {
                if p.child_by_field_name("value").map(|v| v.id() == prev.id()).unwrap_or(false) {
                    if let Some(nm) = p.child_by_field_name("name") {
                        return name_used_in_control(p, text(nm, src), prev.id(), src);
                    }
                }
                return false;
            }
            _ => return false,
        }
        prev = p;
        cur = p.parent();
    }
    false
}

/// A use of an in-scope name is a *control* use if it participates in a subtraction
/// whose result reaches control, or otherwise in timing arithmetic/relational
/// (`x + ttl`, `x > deadline`, `x / 1000`). A use that only feeds a record/log sink
/// is not control.
fn use_is_control(use_node: Node, src: &[u8]) -> bool {
    if let Some(sub) = enclosing_subtraction(use_node, src) {
        return value_reaches_control(sub, src);
    }
    in_arith_relational(use_node, src)
}

/// Scan the enclosing function body for identifier uses of `name` (excluding the
/// binding node `exclude_id`) and return true if any is a control use.
fn name_used_in_control(anchor: Node, name: &str, exclude_id: usize, src: &[u8]) -> bool {
    let Some(body) = enclosing_function(anchor).and_then(|f| f.child_by_field_name("body")) else {
        return false;
    };
    let mut stack = vec![body];
    while let Some(nd) = stack.pop() {
        if nd.kind() == "identifier"
            && nd.id() != exclude_id
            && text(nd, src) == name
            && use_is_control(nd, src)
        {
            return true;
        }
        let mut c = nd.walk();
        for ch in nd.named_children(&mut c) {
            stack.push(ch);
        }
    }
    false
}

/// One-hop: a clock bound to `const x = <clock>` is control iff some later use of
/// `x` is a control use (`Date.now() - x` feeding a comparison, `x > deadline`,
/// `x + ttl`). A binding whose only uses feed record/log sinks (incl. a recorded
/// `Date.now() - x` duration) is NOT control. `None` = not a simple local binding.
fn clock_binding_is_control(n: Node, src: &[u8]) -> Option<bool> {
    let p = n.parent()?;
    if p.kind() != "variable_declarator"
        || !p.child_by_field_name("value").map(|v| v.id() == n.id()).unwrap_or(false)
    {
        return None;
    }
    let name = p.child_by_field_name("name").map(|x| text(x, src))?.to_string();
    Some(name_used_in_control(n, &name, n.id(), src))
}

/// Lever 3 (one-hop) + the duration-record sink hop: a bare welded clock that is
/// neither timing control nor a control-used binding is a record/log sink — not a
/// substitution-demand point. Splits the ambiguous `Date.now()`/`new Date()` tail
/// the cosmetic filter could not (it has no serialization marker), and the
/// duration-record tail (`Date.now() - started` recorded, not compared) lever 3
/// previously over-kept as "arithmetic = control".
fn clock_is_logsink(n: Node, src: &[u8]) -> bool {
    // duration-record sink hop: clock as the minuend of `-` whose elapsed result
    // only records (field/log/return/arg) -> cosmetic; KEEP if it feeds a branch.
    if let Some(sub) = clock_subtraction_minuend(n, src) {
        return !value_reaches_control(sub, src);
    }
    if in_arith_relational(n, src) {
        return false; // relational / addition / division / clock-as-subtrahend -> control
    }
    if clock_binding_is_control(n, src) == Some(true) {
        return false; // elapsed/deadline anchor used in timing math -> control
    }
    true
}

/// F22 rung-3: the leaf boundary lives inside a *named implementation of an
/// injectable interface* — a `class … implements I` method, or a typed impl
/// `const x: I = (…) => {…}` / `{ method(){…} }`. The seam is interface `I`, not
/// the leaf, so consumers inject a fake `I`. Returns `I`. The typed-const arm
/// requires an intervening function so a plain `const r: T = await fetch()` (where
/// `T` is the result type, not an injected interface) is NOT treated as a seam.
fn injectable_impl_context(n: Node, src: &[u8]) -> Option<String> {
    let mut crossed_fn = false;
    let mut cur = n.parent();
    while let Some(p) = cur {
        match p.kind() {
            k if FUNCTION_KINDS.contains(&k) => crossed_fn = true,
            "class_declaration" | "class" => {
                if let Some(name) = implements_name(p, src) {
                    return Some(name);
                }
            }
            "variable_declarator" if crossed_fn => {
                if let Some(t) = p.child_by_field_name("type") {
                    if let Some(name) = type_ann_name(t, src) {
                        return Some(name);
                    }
                }
            }
            _ => {}
        }
        cur = p.parent();
    }
    None
}

/// First `implements` type name of a class node, if any.
fn implements_name(class_node: Node, src: &[u8]) -> Option<String> {
    let mut c = class_node.walk();
    for ch in class_node.named_children(&mut c) {
        if ch.kind() == "class_heritage" {
            let mut c2 = ch.walk();
            for h in ch.named_children(&mut c2) {
                if h.kind() == "implements_clause" {
                    let mut c3 = h.walk();
                    for t in h.named_children(&mut c3) {
                        if t.kind() == "type_identifier" {
                            return Some(text(t, src).to_string());
                        }
                    }
                }
            }
        }
    }
    None
}

/// Named type of a `: TypeName` annotation (interface-like only).
fn type_ann_name(type_ann: Node, src: &[u8]) -> Option<String> {
    let mut c = type_ann.walk();
    for ch in type_ann.named_children(&mut c) {
        if ch.kind() == "type_identifier" {
            return Some(text(ch, src).to_string());
        }
    }
    None
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
                        let mut f = finding(node, b, file, class, false, reason);
                        if class == Class::Welded {
                            if cosmetic_value_context(node, src) {
                                f.demand = false;
                                f.reason = format!("{reason}-cosmetic");
                            } else if clock_is_logsink(node, src) {
                                f.demand = false;
                                f.reason = format!("{reason}-logsink");
                            }
                        }
                        return Some(f);
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
                            // Injected callee: `spawn(...)` / `request(...)` where the
                            // call target itself is an enclosing param (e.g. a
                            // `spawn = spawnSync` default). The boundary is reached
                            // through an injected dependency -> seamed, the same rung
                            // as receiver-/exe-param-injected applied to the callee.
                            if matches!(b.kind.as_str(), "network" | "subprocess")
                                && is_enclosing_param(node, name, src)
                            {
                                return Some(finding(node, b, file, Class::Seamed, true, "callee-param-injected"));
                            }
                            // F22 rung-3: leaf inside a named injectable-interface impl
                            // (the seam is the interface, not this leaf).
                            if matches!(b.kind.as_str(), "network" | "subprocess") {
                                if let Some(iface) = injectable_impl_context(node, src) {
                                    return Some(finding(node, b, file, Class::Seamed, true, &format!("impl-interface:{iface}")));
                                }
                            }
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
                                let mut f = finding(node, b, file, class, is, reason);
                                if class == Class::Welded {
                                    if matches!(b.kind.as_str(), "clock" | "random")
                                        && cosmetic_value_context(node, src)
                                    {
                                        f.demand = false;
                                        f.reason = format!("{reason}-cosmetic");
                                    } else if b.kind == "clock" && clock_is_logsink(node, src) {
                                        f.demand = false;
                                        f.reason = format!("{reason}-logsink");
                                    }
                                }
                                return Some(f);
                            }
                            if b.form == "ns_call"
                                && b.object.as_deref() == Some(obj_name)
                                && b.method.as_deref() == Some(prop)
                            {
                                // F22 rung-3: leaf inside a named injectable-interface impl.
                                if matches!(b.kind.as_str(), "network" | "subprocess") {
                                    if let Some(iface) = injectable_impl_context(node, src) {
                                        return Some(finding(node, b, file, Class::Seamed, true, &format!("impl-interface:{iface}")));
                                    }
                                }
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
