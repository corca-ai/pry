# Handoff

## Workflow Trigger

Next session, in order: (1) **confirm the implementation language** — it is an
open decision (see Discuss), not yet in the spec; (2) run **`spec`** to turn
**Layer 0 + its validation harness** into an executable plan; (3) **`impl`**.
Read [`docs/roadmap.md`](roadmap.md) and [`initial-plan.md`](../initial-plan.md)
§8–§10 first. Validation harness comes **before** the analyzer (kill-gate
discipline).

## Recommended next-turn prompt (paste this)

> First lock `pry`'s implementation language (it's an open decision — see the
> tradeoff in `docs/handoff.md` Discuss). Then start Layer 0 per
> `docs/roadmap.md` via the charness `spec` → `impl` flow. Build the
> **validation harness first**: a git-history miner for error-handling bugfix
> commits → LLM labeler → SZZ trace to the bug-introducing commit → churn/LOC
> baseline → negative control (a clean functional-core/hexagonal app must score
> low). Then a minimal analyzer (in the chosen impl language) that parses
> **Python source** — the analysis target — via tree-sitter, classifies boundary
> calls as seamed vs welded (conservative, with an explicit "ambiguous" bucket),
> and applies the Aspirator-derived syntactic floor.
> Output must be deterministic, with the map (prediction) and floor (claim) in
> separate outputs. Run it on my own Python repos to produce the one kill-gate
> number: *Z% of error-handling bugfixes touched pre-flagged code vs B% churn
> baseline at F% false-flag on the negative control.* Decide go/kill from it.

## Current State

- Design-stage repo; **no analyzer code yet**. Operating surfaces are set up and
  committed (`f6237d2`); design spec committed (`5c85ef6`). Working tree clean.
- `initial-plan.md` is the verbatim founding spec; `README`, `AGENTS.md`
  (+`CLAUDE.md` symlink), `docs/roadmap.md`, `docs/operator-acceptance.md` exist.
- `charness-artifacts/` is tracked in git (user-approved) and holds `gather` +
  `setup` provenance.

## Discuss (needs user input)

- **Implementation language — UNDECIDED in the spec.** `initial-plan.md` never
  names the tool's own language; "Python" in it = the *target* code analyzed,
  not the impl. User leaned Rust — confirm to lock it in. Tension to weigh: Rust
  fits the determinism invariant and tree-sitter's native side; but §10 wants to
  ship `pry` as a **charness skill**, and charness is ~97% Python, so a Rust core
  likely needs a Python-facing wrapper. Decide before `impl`.
- **First corpus:** which of your own Python repos to measure first? Spec names
  charness (~97% Python) as the most honest starting corpus.
- **Map granularity:** call-site vs function vs file — left open by design, to be
  decided by measurement. Pick a starting grain for the first run.
- **Label source:** own-repo git history only for the first number, or also pull
  BugsInPy's error-handling subset?

## References

- [`docs/roadmap.md`](roadmap.md) — ordered priorities + the kill gate.
- [`initial-plan.md`](../initial-plan.md) — full thesis (§8 validation, §9 first
  experiment, §10 build moves, §13 premortem).
- [`docs/operator-acceptance.md`](operator-acceptance.md) — Layer 0 acceptance
  checklist.
- Source note: `initial-plan.md` came from a Cloudflare-gated claude.ai artifact
  (`charness-artifacts/gather/latest.md`); refresh from a trusted source, not by
  re-scraping the URL from this headless host.
