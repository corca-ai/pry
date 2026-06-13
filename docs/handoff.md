# Handoff

## Workflow Trigger

Next session: run **`spec`** to turn **Layer 0 + its validation harness** into an
executable plan, then **`impl`**. Read [`docs/roadmap.md`](roadmap.md) and
[`initial-plan.md`](../initial-plan.md) §8–§10 first. Validation harness comes
**before** the analyzer (kill-gate discipline).

## Recommended next-turn prompt (paste this)

> Start Layer 0 of `pry` per `docs/roadmap.md`, using the charness `spec` →
> `impl` flow. `pry` is a standalone **Rust** binary (this repo), distributed
> like `nose` and consumed by charness's `quality` skill as an external binary.
> Build the **validation harness first**: a git-history miner for error-handling
> bugfix commits → LLM labeler → SZZ trace to the bug-introducing commit →
> churn/LOC baseline → negative control (a clean functional-core/hexagonal app
> must score low). Then a minimal analyzer that parses **Python source** (the
> analysis target) via tree-sitter's Rust bindings, classifies boundary calls as
> seamed vs welded (conservative, with an explicit "ambiguous" bucket), and
> applies the Aspirator-derived syntactic floor. Output deterministic, map
> (prediction) and floor (claim) separated. Run it on my own Python repos to
> produce the one kill-gate number and decide go/kill.

## Current State

- Design-stage repo; **no analyzer code yet**. Operating surfaces are set up and
  committed; design spec committed. Working tree clean. (`git log` for hashes.)
- **Decided:** implementation language is **Rust**. Distribution/integration
  model mirrors `nose` (`corca-ai/nose`): a standalone prebuilt binary (release
  installer + Homebrew tap) wired into charness as an `external_binary`
  (`integrations/tools/pry.json`) that the **`quality`** skill calls — not a
  Python charness skill. This refines `initial-plan.md` §10's "packaging option".
- `initial-plan.md` is the verbatim founding spec; `README`, `AGENTS.md`
  (+`CLAUDE.md` symlink), `docs/roadmap.md`, `docs/operator-acceptance.md` exist.
- `charness-artifacts/` is tracked in git (user-approved); holds `gather` +
  `setup` provenance.

## Discuss (needs user input)

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
- `nose` integration pattern to mirror: `corca-ai/nose`, charness
  `integrations/tools/nose.json` (`kind: external_binary`, consumed by `quality`).
- Source note: `initial-plan.md` came from a Cloudflare-gated claude.ai artifact
  (`charness-artifacts/gather/latest.md`); refresh from a trusted source.
