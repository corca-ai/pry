# Handoff

## Workflow Trigger — if the operator says "계속합시다" / "continue"

The measurement arc is **DONE** (4 negatives). The direction is **decided and
agreed**: build pry's real product shape — **dogfood on the author's own repos via
a per-repo `.pryconfig.toml`** — per
[`charness-artifacts/ideation/2026-06-16-pryconfig-and-dogfood.md`](../charness-artifacts/ideation/2026-06-16-pryconfig-and-dogfood.md)
(read it first; it has the full design + impl plan). Route to **`spec`** then
**`impl`** for slice 1 below. Do **not** re-open the dead theses or run a fifth
measurement — this is a product-shape build, not a new experiment.

**First slice (operator-deferred until after this compaction):** `pry untested`
subcommand (Rust) — port `harness/step1b.py`'s failure-test cross into the binary
(pry already has tree-sitter + catalog + welded classification; add test-file
mock/failure-sim fingerprinting + import linkage) → emit the welded∧untested∧
production worklist. `step1b.py` is the validated reference/oracle. Then the
`.pryconfig.toml` (ignore + structured per-repo `[[boundary]]` extensions + seed-vs-
repo provenance tag + completeness probe) and the own-repo LLM-judge triage.

## Current State — 4 value-bridges down; pry = validated classifier, no measured payoff

Detail/numbers in `docs/eval-gate.md`. All pre-registered, git-provable, honest:

- **E9 (bugs)** FALSIFIED 1.05 — welded-at-demand not bugfix-enriched.
- **Step-1 (file coverage)** FALSIFIED 0.95 — `demand` buys no file-level coverage signal.
- **Floor (swallowed-failure claim)** KILL 3.8% — mature OSS swallows are mostly intentional.
- **Step-1b (failure-test detection)** WEAK — per-boundary failure-tested rate is a
  wide unknown interval **9.1%–71.1%** (static fingerprints can't pin it); and the
  welded-vs-rest / welded-vs-wnd contrasts are **confidently flat** (0.965 / 0.961)
  → welded/demand does NOT pick out a differentially-untested population (Step-1's
  demand-null recurs at the failure-path level). welded-vs-seamed flat but underpowered.

pry stays a **precise injectability classifier** (H3: net/subproc 100%) with **no
proven actionable recommender/defect payoff** on this corpus.

## Decision — MADE: dogfood-on-own-repos via `.pryconfig.toml` (supersedes ratchet-vs-ship)

The operator's north star (NOT a generalizable OSS product): **pry surfaces, in the
author's own products, welded boundaries whose failure is untested → they get tested.**
The 4 negatives refute the *generalizable* claim; they do NOT refute this. **Dogfood
proved it:** `pry map` + a live failure-test cross on **ceal** found **142 welded FC →
114 untested → 12 production → ~5-6 genuine gaps** (e.g. `control-auto-commit.ts:133`),
while **craken-agents** was clean (6 untested, all `bin/` tooling). On the author's own
(less-mature) repos the welded∧untested gap is real and large — the opposite of mature
OSS (~71% mock-tested). This is the opt-in/config home the old "ratchet" pointed at,
now concrete. Full design + impl plan: the ideation note linked in the trigger.

**Mechanism (confirmed from source, shapes the build):** pry = syntactic AST matching
against a curated boundary **catalog** (`catalog/typescript.toml`, ~63 entries / 9 kinds,
structured `[[boundary]]` fingerprints) — a whitelist; `failure-capable` = a hardcoded
subset `{net,subproc,db,fileio}` (llm/slack omitted — a gap to fix). The `.pryconfig.toml`
makes the catalog **per-repo extensible** (agent-authored), with two non-negotiables:
**(1) structured entries not loose keywords** (preserve AST matching + precision),
**(2) seed-vs-repo provenance tagged in output** (don't dilute the validated number).

## References

- `docs/eval-gate.md` — E9 + Step-1 + Floor + **Step-1b** results (+ the testing-
  quality caveat: middle-mock vs edge-mock msw).
- `harness/step1b.py` + `harness/fixtures/eval/preregistration-step1b.md` — the
  failure-test detector + its frozen contract (binding-precedence module extraction,
  mock/failure-sim catalogs, L-import/L-module bracket).
- `charness-artifacts/critique/2026-06-16-step1b-{spec-critique,verification}.md`.
- **`charness-artifacts/ideation/2026-06-16-pryconfig-and-dogfood.md`** — the DECIDED
  direction: dogfood result (craken-agents/ceal) + the `.pryconfig.toml` design + impl plan.
- `charness-artifacts/ideation/2026-06-16-concept-ideation.md` — the earlier wedge
  analysis that named the floor (done) and the ratchet (now realized as the dogfood/config shape).
- `catalog/typescript.toml` — the boundary whitelist the `.pryconfig.toml` will extend.
- `initial-plan.md` §1.3/§5 (testability=injectability thesis, two channels).
