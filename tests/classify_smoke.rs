//! Classifier regression guard (and F26 self-application: pry's analysis core is
//! testable by injection — no file I/O, the source is passed in).

use pry::analyze_str;
use pry::classify::Class;

fn find<'a>(fs: &'a [pry::classify::Finding], line: usize) -> &'a pry::classify::Finding {
    fs.iter().find(|f| f.line == line).unwrap_or_else(|| panic!("no finding on line {line}"))
}

const SRC: &str = r#"
export function stampRaw(): string { return new Date().toISOString(); }
export function stampInjected(now = new Date()): string { return now.toISOString(); }
export function stampNullish(input: { now?: Date }): string { const t = input.now ?? new Date(); return t.toISOString(); }
export function parseTs(ms: number): string { return new Date(ms).toISOString(); }
let client: any;
export async function search(k: string) { client ??= new OpenAI({ apiKey: k }); return await client.responses.create({}); }
export class Notifier {
  private webClient: any;
  constructor(config: { webClient?: any; botToken: string }) { this.webClient = config.webClient ?? new WebClient(config.botToken); }
  async notify(p: unknown) { await this.webClient.chat.postMessage(p as never); }
}
export async function postWith(webClient: any, p: unknown) { await webClient.chat.postMessage(p as never); }
export async function get(url: string) { return await fetch(url); }
export function rng(): number { return Math.random(); }
export function db(p: string) { return new Database(p); }
export async function http2(u: string) { return await axios.get(u); }
"#;

#[test]
fn smoke_classifications() {
    let fs = analyze_str(SRC, "smoke.ts");

    // raw clock = welded (hard weld, input-sim NO)
    let raw = find(&fs, 2);
    assert_eq!(raw.kind, "clock");
    assert_eq!(raw.class, Class::Welded);
    assert!(!raw.input_sim);

    // default-param injected clock = seamed
    assert_eq!(find(&fs, 3).class, Class::Seamed);
    // nullish-default injected clock = seamed
    assert_eq!(find(&fs, 4).class, Class::Seamed);

    // new Date(arg) is NOT a boundary -> no clock finding on line 5
    assert!(!fs.iter().any(|f| f.line == 5 && f.kind == "clock"));

    // inline lazy OpenAI -> welded llm (both the `new` and the `.create` receiver)
    assert!(fs.iter().any(|f| f.line == 7 && f.kind == "llm" && f.class == Class::Welded));

    // ctor-config DI used via this.attr (one-hop) -> seamed slack
    assert_eq!(find(&fs, 11).class, Class::Seamed);
    // receiver is a formal param -> seamed slack
    assert_eq!(find(&fs, 13).class, Class::Seamed);

    // global fetch leaf -> welded network
    let net = find(&fs, 14);
    assert_eq!(net.kind, "network");
    assert_eq!(net.class, Class::Welded);

    // broadened catalog (Run 6): random / db / http(axios) are recognized + welded,
    // and random is a hard weld (input-sim NO, like clock)
    let rng = fs.iter().find(|f| f.kind == "random").expect("Math.random not recognized");
    assert_eq!(rng.class, Class::Welded);
    assert!(!rng.input_sim, "randomness has no operand to redirect");
    assert!(!rng.demand, "welded random is never a substitution-demand point (cosmetic-random lever)");
    assert!(fs.iter().any(|f| f.kind == "db" && f.class == Class::Welded), "new Database not recognized");
    assert!(fs.iter().any(|f| f.kind == "network" && f.reason.contains("builtin")), "axios.get not recognized");
}

#[test]
fn determinism_same_input_same_output() {
    let a = analyze_str(SRC, "smoke.ts");
    let b = analyze_str(SRC, "smoke.ts");
    assert_eq!(a.len(), b.len());
    for (x, y) in a.iter().zip(b.iter()) {
        assert_eq!((x.line, x.col, &x.kind, x.class), (y.line, y.col, &y.kind, y.class));
    }
}

const SRC2: &str = r#"
export function rec() { return { ts: new Date().toISOString(), n: Date.now() }; }
export function clk() { const c = { now: () => new Date() }; return c; }
export function tern(input: { make?: () => any }) { return input.make ? input.make() : new WebClient("t"); }
export function arrowDef(input: { now?: () => number }) { const now = input.now ?? (() => Date.now()); return now(); }
class LocalExec implements Executor { run(cmd: string) { return spawn(cmd, []); } }
const transport: HttpTransport = { request(u: string) { return fetch(u); } };
export async function bareGet(u: string) { return await fetch(u); }
"#;

#[test]
fn precision_filters_and_rung3() {
    let fs = analyze_str(SRC2, "p.ts");

    // lever 1 — cosmetic clock (record field / serialize) stays welded but is NOT
    // a substitution-demand point.
    let cos = fs.iter().find(|f| f.kind == "clock" && f.reason.contains("cosmetic")).expect("no cosmetic clock");
    assert_eq!(cos.class, Class::Welded);
    assert!(!cos.demand, "cosmetic timestamp must drop out of the demand subset");
    // `now: () => new Date()` thunk -> provider definition, demoted
    assert!(fs.iter().any(|f| f.kind == "clock" && f.line == 3 && !f.demand), "clock thunk not demoted");

    // lever 2a — the two 0-hop seam bugs are fixed
    assert!(fs.iter().any(|f| f.line == 4 && f.class == Class::Seamed), "ternary-factory seam missed");
    assert!(fs.iter().any(|f| f.line == 5 && f.kind == "clock" && f.class == Class::Seamed), "arrow-?? default seam missed");

    // lever 2b — rung-3: leaf inside a named injectable-interface impl -> seamed
    assert!(fs.iter().any(|f| f.line == 6 && f.reason.contains("impl-interface:Executor") && f.class == Class::Seamed), "implements rung-3 missed");
    assert!(fs.iter().any(|f| f.line == 7 && f.reason.contains("impl-interface:HttpTransport") && f.class == Class::Seamed), "typed-const rung-3 missed");

    // guardrail — a genuine bare fetch (not inside an impl) stays welded + demand
    let bare = fs.iter().find(|f| f.line == 8 && f.kind == "network").expect("no bare fetch");
    assert_eq!(bare.class, Class::Welded);
    assert!(bare.demand, "genuine bare fetch must remain a demand weld");
}

const SRC3: &str = r#"
export function rel(d: number) { return Date.now() > d; }
export function ttl(m: Map<string, number>) { m.set("k", Date.now() + 1000); return m; }
export function remaining(deadline: number) { return deadline - Date.now(); }
export function guarded(started: number, timeout: number) { if (Date.now() - started > timeout) return 1; return 0; }
export function recordField(started: number, rec: { ms?: number }) { rec.ms = Date.now() - started; return rec; }
export function durationArg(started: number) { return formatDuration(Date.now() - started); }
export function elapsed() { const startedAt = Date.now(); doWork(); return Date.now() - startedAt; }
export function logOnly(rec: { at?: number }) { const now = Date.now(); rec.at = now; return rec; }
export function concat() { return "at " + Date.now(); }
"#;

#[test]
fn lever3_clock_timing_vs_logsink() {
    let fs = analyze_str(SRC3, "l3.ts");
    let demand_clock = |line: usize| {
        fs.iter().find(|f| f.line == line && f.kind == "clock").map(|f| f.demand)
    };

    // KEEP — genuine timing the recall guard must preserve.
    assert_eq!(demand_clock(2), Some(true), "`Date.now() > d` relational must stay demand");
    assert_eq!(demand_clock(3), Some(true), "`Date.now() + 1000` TTL addition must stay demand");
    assert_eq!(demand_clock(4), Some(true), "`deadline - Date.now()` clock-as-subtrahend must stay demand");
    assert_eq!(demand_clock(5), Some(true), "`Date.now() - started > timeout` duration feeds a relational -> keep");

    // DEMOTE — duration-record sink hop (the new lever): a clock subtraction whose
    // elapsed result only records (field / call arg / return) is cosmetic.
    assert_eq!(demand_clock(6), Some(false), "duration assigned to a record field is cosmetic");
    assert_eq!(demand_clock(7), Some(false), "duration passed as a call argument is cosmetic");
    // elapsed(): the revised expectation — a *returned* bare duration is a record
    // sink, so BOTH the minuend read and its anchor binding demote.
    let l8: Vec<_> = fs.iter().filter(|f| f.line == 8 && f.kind == "clock").collect();
    assert!(l8.len() >= 2, "elapsed() has an anchor read and a subtraction read");
    assert!(l8.iter().all(|f| !f.demand),
        "a returned bare duration demotes both the `Date.now() - startedAt` read and the `startedAt` anchor");

    // DEMOTE — existing lever 3 (no arithmetic at all).
    assert_eq!(demand_clock(9), Some(false), "`const now = Date.now(); rec.at = now` is a log sink");
    assert_eq!(demand_clock(10), Some(false), "string-concat clock is a log sink");
}

// Lever 3 — clock control-vs-record DISCRIMINATION rescue (Slice 2 reshaped it from
// "demote more clock" into "rescue genuine clock the cosmetic/logsink filters
// over-demoted"). The two rescue targets are DB-query date bounds and compared
// date-math thresholds; the negatives are bare record timestamps + serialized
// clocks that must STAY demoted. Each line mirrors one of the 16 frozen misses (or
// the precision-damage shapes the --remap gate surfaced).
const SRC_LV3: &str = r#"
import { Op } from "sequelize";
export function qOpLt() { return M.findAll({ where: { expiresAt: { [Op.lt]: new Date() } } }); }
export function qMongoBinding() { const now = new Date(); return B.findOne({ displayFrom: { $lte: now } }); }
export function threshInline(self: { at: number }) { return self.at > subMinutes(Date.now(), 5); }
export function threshConstQuery() { const cutoff = subDays(new Date(), 1); return M.destroy({ where: { createdAt: { [Op.lt]: cutoff } } }); }
export function threshConstCompare(x: number) { const five = subMinutes(new Date(), 5); if (x < five) return 1; return 0; }
export function dateArithCompare(d: number) { const lastWeek = new Date(Date.now() - 604800000); return d > lastWeek; }
export function throttle() { if (!lastRan) { run(); lastRan = Date.now(); } return lastRan; }
export function fallbackClamp(msg: any, last: Date) { const t = msg.created_at; let createdAt = t ? new Date(t) : new Date(); if (last && createdAt <= last) createdAt = new Date(0); return createdAt; }
export function serializedConcat(j: number) { const x = Date.now().toString(); return x.slice(0, -2) + j.toString(); }
export function recordField() { return { createdAt: new Date(), n: 1 }; }
"#;

#[test]
fn lever3_query_bounds_and_thresholds() {
    let fs = analyze_str(SRC_LV3, "lv3.ts");
    let demand = |line: usize| {
        fs.iter()
            .find(|f| f.line == line && f.kind == "clock")
            .unwrap_or_else(|| panic!("no clock finding on line {line}"))
            .demand
    };

    // RESCUE A — DB-query date bounds (Op.lt / $lte query-operator keys).
    assert!(demand(3), "Op.lt new Date() is a query date bound, not a record");
    assert!(demand(4), "const now = new Date() spent as a $lte query bound via const");
    // RESCUE B — compared date-math thresholds (clock DERIVED through a helper / arith).
    assert!(demand(5), "self.at > subMinutes(Date.now(),5) inline threshold");
    assert!(demand(6), "const cutoff = subDays(new Date(),1) spent in an Op.lt query");
    assert!(demand(7), "const five = subMinutes(new Date(),5); x < five threshold");
    assert!(demand(8), "new Date(Date.now()-WEEK) compared d > lastWeek");

    // NEGATIVES — must STAY demoted (the gate's precision-damage lessons).
    assert!(!demand(9), "throttle lastRan = Date.now() record timestamp stays demoted");
    assert!(!demand(10),
        "bare new Date() fallback merely clamped before storing is NOT a computed threshold");
    assert!(!demand(11),
        "Date.now().toString() serialized then string-concatenated is cosmetic");
    assert!(!demand(12), "non-query record field new Date() is cosmetic");
}

// Type-free JavaScript (a `.mjs`-shaped string with no annotations). The frontend
// parses JS with the same TS-superset grammar, so the 0-hop param/default seam
// logic must keep working. What's lost is only the TS-only rung-3 signal
// (`implements` / `: Type`), which has no JS analog — verified absent below.
const SRC_JS: &str = r#"
export function stampRaw() { return new Date().toISOString(); }
export function stampInjected(now = new Date()) { return now.toISOString(); }
export function deadline(input) { const now = input.now ?? Date.now(); return now > input.until; }
export async function get(url) { return await fetch(url); }
export function spawnGit(args) { return execFileSync("git", args); }
export class LocalExec { run(args) { return spawn("git", args); } }
"#;

#[test]
fn js_frontend_parses_and_classifies() {
    // production path: analyze_str always uses the TS grammar; a `.mjs` name just
    // documents intent. Type-free JS must still classify by structure.
    let fs = analyze_str(SRC_JS, "j.mjs");

    // default-param injected clock -> seamed (the param wrapper logic survives on JS)
    assert_eq!(find(&fs, 3).class, Class::Seamed);
    // `?? Date.now()` nullish default -> seamed, even with no type annotation
    assert_eq!(find(&fs, 4).kind, "clock");
    assert_eq!(find(&fs, 4).class, Class::Seamed);
    // bare global fetch -> welded network, stays a demand weld
    let net = find(&fs, 5);
    assert_eq!((net.kind.as_str(), net.class, net.demand), ("network", Class::Welded, true));
    // inline execFileSync("git", …) -> welded subprocess
    assert!(fs.iter().any(|f| f.line == 6 && f.kind == "subprocess" && f.class == Class::Welded));

    // TS-only rung-3 is correctly INERT on JS: `class LocalExec { run(){ spawn } }`
    // has no `implements`, so its spawn is welded (no false impl-interface seam).
    let spawn = find(&fs, 7);
    assert_eq!(spawn.kind, "subprocess");
    assert_eq!(spawn.class, Class::Welded);
    assert!(!spawn.reason.contains("impl-interface"), "JS class without `implements` must not fake a rung-3 seam");
}

// Injected-callee seam (cautilus cross-corpus lever): the call target itself is an
// injected param (`spawn = spawnSync`), so the subprocess is seamed even though the
// callee NAME matches a global catalog entry. Mirrors exe-/receiver-param-injected.
const SRC_INJ: &str = r#"
export function commandExists(command, spawn = spawnSync) { return spawn("sh", ["-c", command]); }
export function runPhases(phases, { spawn = spawnSync } = {}) { return spawn("npm", ["run"]); }
export function real(args) { return spawnSync("git", args); }
"#;

#[test]
fn injected_callee_is_seamed() {
    let fs = analyze_str(SRC_INJ, "inj.mjs");

    // direct default param `spawn = spawnSync` -> the spawn("sh",…) is seamed
    let direct = find(&fs, 2);
    assert_eq!(direct.kind, "subprocess");
    assert_eq!(direct.class, Class::Seamed);
    assert!(direct.reason.contains("callee-param-injected"));

    // destructured default `{ spawn = spawnSync } = {}` -> also seamed
    let destructured = find(&fs, 3);
    assert_eq!(destructured.class, Class::Seamed, "destructured spawn default must seam");

    // guardrail: a genuine global spawnSync("git",…) stays welded + demand
    let real = find(&fs, 4);
    assert_eq!((real.class, real.demand), (Class::Welded, true), "global spawnSync must stay a demand weld");
}

// A self-referential declarator (`const d = Date.now() - d`) is a TDZ bug at
// runtime but parses fine; the binding-hop dataflow must not recurse forever on it
// (main.rs has no per-file panic isolation, so a stack overflow would abort the
// whole scan). Regression guard for the MAX_BINDING_HOPS cap.
#[test]
fn self_referential_declarator_terminates() {
    let fs = analyze_str(
        "export function f() { const d = Date.now() - d; return d; }\n",
        "selfref.ts",
    );
    // must classify (not crash) and emit the clock finding
    assert!(fs.iter().any(|f| f.kind == "clock"), "self-ref clock still found, no overflow");
}

// cosmetic-random lever (eval-gate): randomness was 0/79 genuine across the 4 H3
// corpora — an RNG has no failure to inject, so a welded random leaf is never a
// substitution-demand point regardless of call form (Math.random / crypto.*) or
// position (record, control comparison). Demand is dropped; class stays welded.
const SRC_RAND: &str = r#"
export function token() { return Math.random().toString(36).slice(2); }
export function pick(xs) { return xs[Math.floor(Math.random() * xs.length)]; }
export function uuid() { return crypto.randomUUID(); }
export function salt() { return crypto.randomBytes(16); }
export function coin() { return Math.random() < 0.5; }
"#;

#[test]
fn random_is_never_demand() {
    let fs = analyze_str(SRC_RAND, "rand.ts");
    let rands: Vec<_> = fs.iter().filter(|f| f.kind == "random").collect();
    // Math.random x3 (builtin_call) + crypto.randomUUID/randomBytes x2 (ns_call)
    assert!(rands.len() >= 5, "all five random boundaries recognized, got {}", rands.len());
    assert!(rands.iter().all(|f| f.class == Class::Welded), "random is a hard weld");
    assert!(rands.iter().all(|f| !f.input_sim), "randomness has no operand to redirect");
    // the lever: every welded random — cosmetic position, the `< 0.5` control
    // comparison, builtin and namespaced alike — drops out of the demand subset.
    assert!(rands.iter().all(|f| !f.demand),
        "welded random is never a substitution-demand point (cosmetic-random lever)");
    // both call forms carry the demotion marker (builtin Math.random + crypto ns_call)
    assert!(fs.iter().any(|f| f.kind == "random" && f.reason.contains("builtin") && f.reason.contains("random-cosmetic")),
        "Math.random demotion marked");
    assert!(fs.iter().any(|f| f.kind == "random" && f.reason.contains("ns-call-leaf-random-cosmetic")),
        "crypto.* demotion marked");
}

#[test]
fn demand_subset_discriminates() {
    // The lens metric: among the substitution-demand subset, both seamed and welded
    // are present (a real seam population) — not degenerate.
    let fs = analyze_str(SRC, "smoke.ts");
    let demand: Vec<_> = fs.iter().filter(|f| f.demand).collect();
    let seamed = demand.iter().filter(|f| f.class == Class::Seamed).count();
    let welded = demand.iter().filter(|f| f.class == Class::Welded).count();
    assert!(seamed > 0, "expected a seam population in the demand subset");
    assert!(welded > 0, "expected welded boundaries in the demand subset");
}
