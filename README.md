# pry

> Make the *injectability* of your code visible.

`pry` is a static-analysis tool that turns "testability" into a measurable,
mechanical signal — **injectability** — and maps where a codebase is un-testable.
It finds boundary calls (network, file I/O, clock, randomness, DB, subprocess)
**welded** directly into business logic with no seam where a test can substitute
a failure, and ranks the ones sitting at a real failure-injection demand point.

The name encodes the thesis in one word: *no seam, nothing to pry* — un-testable
code is code you cannot get a lever into. It is the companion to
[`nose`](https://github.com/corca-ai/nose) (which sniffs out duplicated *logic*);
`pry` finds the boundaries welded into your logic where failures hide because
nothing can reach in to test them.

**Output is a risk ranking, not a bug list.**

## Install

```sh
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/corca-ai/pry/releases/latest/download/pry-installer.sh | sh
```

Prebuilt binaries for macOS and Linux (arm64 / x86_64). Or build from source
(Rust ≥ 1.85): `cargo build --release` → `target/release/pry`.

## Usage

```sh
pry map path/to/ts-or-js                       # full finding map (deterministic JSON)
pry map path/to/ts-or-js --summary-only        # coverage summary only
pry map path/to/ts-or-js --exclude 'src/smoke-*.ts'  # skip paths (repeatable glob)
```

**Scope is your call.** `pry map` already honors `.gitignore` and drops
conventional test files (`*.test.ts`, `*.spec.ts`, `test/`, `__tests__/`). For
anything else your repo considers out of scope (e.g. non-test-named `smoke-*.ts`
harnesses), add a **`.pryignore`** file (full gitignore syntax, incl. `!`
re-include) or pass **`--exclude <glob>`** (positive-sense, repeatable). pry never
*guesses* wantedness — it does not auto-demote files by heuristic; any exclusion
is your explicit declaration, not a silent pry-side demotion.

`pry map` is deterministic (byte-identical across runs/machines) and zero-LLM.
The actionable backlog is the **welded-at-demand** subset (`demand=true`,
`class="welded"`): boundary calls with no seam to inject a failure, on a path
worth testing. `fileio`/`env` are the diagnostic swamp and are excluded from that
subset by design.

For a ranked + labeled view, the bundled **`pry` agent skill** (`skills/pry/`)
consumes `pry map` JSON and labels each finding GENUINE / FALSE-WELD / COSMETIC /
AMBIGUOUS (`skills/pry/scripts/rank_backlog.py`, honors `PRY_BIN`).

## Why

The strongest empirical anchor is Yuan et al., *"Simple Testing Can Prevent Most
Critical Failures"* (OSDI 2014): the large majority of catastrophic failures
came from **incorrect handling of errors the software had already detected**.
Those error paths are buggy because they are rarely exercised — and they are
rarely exercised because the failing operation is welded into the business logic
with no injection point. No seam, no test; no test, no coverage; the bug ships.

> **Thesis.** Testability is not a separate virtue. It is the observable shadow
> of modularity and coupling. Its mechanical proxy is *injectability*: is there a
> seam you can pry open at this boundary to substitute a failure?

## How it is meant to work (three layers)

The layers are centers, not a schedule — each stands alone, and stopping at any
layer preserves the whole.

- **Layer 0 — static map (shipped).** Deterministic, language-cataloged, no test
  runner. Produces the injectability/risk map: every boundary classified
  seamed / welded / ambiguous, with a substitution-demand flag.
- **Layer 1 — seam generation (future).** Propose refactorings that put a hot
  boundary behind a port/adapter (a DI seam). Output is an ordinary PR a human
  merges — the seams are the permanent asset even if the tool is later deleted.
- **Layer 2 — injection oracle (future).** Inject failures at seams and check
  that invariants hold; the runner is earned only where Layers 0/1 created a seam.

The **syntactic floor** (a zero-false-positive *claim* channel: empty catch,
swallowed errors, log-and-continue on a mutating path) is designed in
[`initial-plan.md`](initial-plan.md) but **not yet built** — pry today ships the
*prediction* channel (the map) only.

## Status

**v0.1.0 — Layer-0 static map, released.** Built as a prebuilt Rust binary
(cargo-dist installer) and wired into
[charness](https://github.com/corca-ai/charness) as an `external_binary` the
**`quality`** skill can detect/recommend. Source parsing uses tree-sitter's Rust
bindings.

- **Validated surface: TypeScript / JavaScript.** On the substitution-demand
  subset, curated precision is ~88% (ceal) / ~97% (cautilus) after the
  cosmetic-clock + duration-record filters; the welded/seamed signal carries
  information (lens GO across 8 corpora). See [`docs/precision-gate.md`](docs/precision-gate.md).
- **First off-corca evidence (H3):** an LLM-panel eval on 4 independent
  third-party OSS apps (outline / flowise / continue / librechat) finds
  **network + subprocess demand-welds are 100% genuine (261/261)** and the
  non-cosmetic surface is **89.3%** — matching the ceal hand-validation. The
  precision drag is the cosmetic `clock`/`random` tail (a named filter gap, not a
  thesis problem). The eval/panel is a **dev-time** tool only — the shipped binary
  stays zero-LLM. See [`docs/eval-gate.md`](docs/eval-gate.md). *(Panel-labeled,
  human-calibration pending; gate opened, not closed.)*
- **Python is out of scope — a recorded KILL.** The author's Python repos are
  uniformly welded *glue* with no discrimination, so pry's ranker gets no
  traction there. See [`docs/kill-gate.md`](docs/kill-gate.md). A *non-glue* OSS
  Python corpus could revisit this.
- **Scouted, deferred:** a possible recall gap — network/subprocess seams behind
  an injected transport/executor wrapper one hop up (rung-3 stage-2) — was
  censused on ceal and found *not material* (the welds there are genuine inline
  calls, not false-welds). Deferred until a corpus surfaces it; see
  [`docs/precision-gate.md`](docs/precision-gate.md).

## Reference docs

- [`initial-plan.md`](initial-plan.md) — full design spec (thesis, layers, metric
  philosophy, boundary/seam catalog, validation, premortem, prior art).
- [`docs/roadmap.md`](docs/roadmap.md) — ordered priorities.
- [`docs/precision-gate.md`](docs/precision-gate.md) — validated precision + the
  GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS labeling taxonomy.
- [`docs/kill-gate.md`](docs/kill-gate.md) — the go/kill record (why TS, not Python).
- [`docs/operator-acceptance.md`](docs/operator-acceptance.md) — what a human
  maintainer needs to take this over.
- [`AGENTS.md`](AGENTS.md) — operating contract for agents working in this repo.

## Prior art / lineage

Yuan et al. (OSDI 2014, *Aspirator*) · Feathers, *seams* · Cockburn (hexagonal /
ports & adapters) · Bernhardt (functional core, imperative shell) ·
Ostrand–Weyuker & Walkinshaw et al. (defect concentration) · `nose` (the mindset
source) · Cunningham (DTSTTCPW) · Alexander (unfolding of centers) · charness.
