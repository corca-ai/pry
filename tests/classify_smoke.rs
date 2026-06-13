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
