# pry

> Make the *injectability* of your code visible.

`pry` is a proposed static-analysis tool that turns "testability" into a
measurable, mechanical signal — **injectability** — and maps where a repository
is un-testable. It finds boundary calls (network, file I/O, clock, randomness,
DB drivers, subprocess) **welded** directly into business logic with no seam
where a test can substitute a failure, and it focuses on the error-handling
paths where catastrophic bugs concentrate.

The name encodes the thesis in one word: *no seam, nothing to pry* — un-testable
code is code you cannot get a lever into. It is the companion to
[`nose`](https://github.com/corca-ai/nose) (which sniffs out duplicated
*logic*); `pry` finds the boundaries welded into your logic where failures hide
because nothing can reach in to test them.

**Implementation & integration.** `pry` is a standalone **Rust** binary built in
this repository. Like `nose`, it ships as a prebuilt release (installer +
Homebrew tap) and is wired into [charness](https://github.com/corca-ai/charness)
as an `external_binary` that the **`quality`** skill calls to surface testability
hotspots and error-handling defects — it is not embedded as a Python charness
skill. Source parsing uses tree-sitter's Rust bindings.

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

- **Layer 0 — static map + syntactic floor (ship first).** Deterministic,
  language-cataloged, no test runner. Produces a testability/risk map *and* real
  error-handling-defect findings (empty catch, swallowed errors,
  log-and-continue on a mutating path, …).
- **Layer 1 — seam generation.** Propose refactorings that put a hot boundary
  behind a port/adapter (a DI seam). Output is an ordinary PR a human merges —
  the seams are the permanent asset even if the tool is later deleted.
- **Layer 2 — injection oracle.** Inject failures at seams and check that
  invariants hold. The runner is earned, not forced: it runs only where Layers
  0/1 created a seam.

## Two channels, two disciplines

- **Claim channels** (syntactic floor, injection oracle) → target ≈ zero false
  positives; a flag is a *fact*, with a `# pry-ignore` escape hatch.
- **Prediction channel** (the injectability *map*) → a risk signal judged by
  concentration / lift over a churn baseline, never by zero-error. These outputs
  are kept physically separate so a fuzzy map flag never poisons trust in the
  sound floor.

## Validation before building

The project is committed to being killable. Before trusting the map, measure
whether error-handling defects concentrate in flagged locations more than a
churn/LOC baseline — mined automatically from git history (SZZ-labeled
bug-introducing commits) with a negative control (clean hexagonal / functional-
core code must score low). First corpus: the author's own (≈Python) repos. If
there is no lift over churn, the thesis is cheaply killed or the signal pivots.

## Status

Design stage. This repository currently holds the founding design document and
its provenance; no analyzer code exists yet.

- [`initial-plan.md`](initial-plan.md) — full design spec (thesis, layers,
  metric philosophy, boundary/seam catalog, validation, premortem, prior art).
- [`docs/roadmap.md`](docs/roadmap.md) — ordered near-term priorities.
- [`docs/operator-acceptance.md`](docs/operator-acceptance.md) — what a human
  maintainer needs to take this over.
- [`AGENTS.md`](AGENTS.md) — operating contract for agents working in this repo.

## Prior art / lineage

Yuan et al. (OSDI 2014, *Aspirator*) · Feathers, *seams* · Cockburn (hexagonal /
ports & adapters) · Bernhardt (functional core, imperative shell) ·
Ostrand–Weyuker & Walkinshaw et al. (defect concentration) · `nose` (the mindset
source) · Cunningham (DTSTTCPW) · Alexander (unfolding of centers) · charness.
