# Roadmap

Ordered by dependency, following the design in
[`../initial-plan.md`](../initial-plan.md). The sequence is forced, not chosen:
injection needs seams, seams come from the map, the map needs the catalog. Stop
at any layer and the result still stands.

## Shipped — Layer 0 static map (v0.1.0)

The Layer-0 *prediction* channel is built, validated, and released:

- **Validation harness** (`harness/`, the `nose-eval` analog): git-history miner
  → LLM labeler → SZZ trace → repo-fit gate. It did its job — see
  [`kill-gate.md`](kill-gate.md).
- **Parse + catalog + dataflow-lite + emit.** Rust binary, tree-sitter parsing,
  boundary catalog as data (`catalog/`), seamed/welded/ambiguous classification
  with a substitution-demand flag and cosmetic-clock + duration-record filters,
  deterministic JSON (`pry map`).
- **Kill-gate verdict (the experiment ran):** the author's *Python* is welded
  glue → KILL; *TS/JS* is pry's surface → GO across 8 corpora. The analyzer
  therefore targets **TS/JS**; demand-subset precision ~88% (ceal) / ~97%
  (cautilus). See [`precision-gate.md`](precision-gate.md).
- **Packaged + released:** prebuilt binary (cargo-dist installer), wired into
  charness as an `external_binary` for the `quality` skill.

**Not built yet in Layer 0:** the **syntactic floor** (the zero-false-positive
*claim* channel — empty catch, swallowed error, log-and-continue on a mutating
path, bare `except`). pry today ships the *map* (prediction); the *floor* (claim)
does not exist. SARIF emit is also future (JSON only today).

## Now — sharpen the map, then add the floor

1. **Stage-2 rung-3 wrapper detection (F22).** pry under-detects network/subprocess
   seams behind an injected transport/executor wrapper one hop up → welded-at-demand
   is an upper bound. The highest-value accuracy increment on the validated TS/JS
   surface (pre-registered in `kill-gate.md` Run 5's EXTEND rider).
2. **Syntactic floor.** Build the un-built Layer-0 claim channel, kept physically
   separate from the map output. High precision + `# pry-ignore` escape hatch.
3. **quality auto-invoke** (charness-side): a `quality` driver that runs `pry map`
   as a standing advisory inventory, mirroring nose's consumer. Today pry is
   agent-invoked on-request via the `skills/pry/` F15 skill, not auto-run.

## Next — Layer 1 (only after Layer 0 is stable and validated)

Seam generation: propose a port/adapter refactoring for the highest-risk
boundaries; output is a human-reviewed PR. Propose seams only where the map's
risk is high enough that the PR sells itself — never refactor for purity's sake.

## Later — Layer 2 (only after seams exist)

Injection oracle: inject failures at seams, check invariants, measure the
escaped-injection rate; the map score should correlate inversely with it.

## Deliberately deferred

Internals of Layers 1–2, map **granularity** (call-site vs function vs file),
weld-depth weighting, whether test-only monkeypatches count as "seamed enough",
and the final per-language floor rule set. These are resolved by measuring on
real repos, not decided now.

## Adoption guardrails (so it survives)

- Wire into CI / pre-commit so it runs by default — "remember to run it" = dies.
- Label the map "risk ranking, not a bug list" from the first pixel.
- Keep Layer 0 small enough that it pays for itself in week one.
- Ship as an `external_binary` consumed by the charness **`quality`** skill,
  mirroring `nose` (`integrations/tools/nose.json`): a prebuilt Rust release,
  detected by `pry --version`. **Done** — cargo-dist shell installer + charness
  `integrations/tools/pry.json` (on charness `main`). *Remaining:* the Homebrew
  tap and the quality-side consumer/inventory script (the auto-invoke driver).
  This is §10's "packaging option" made concrete — not a Python charness skill.
