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
- **First off-corca evidence (H3 gate OPENED):** the finding-eval panel ran on 4
  independent third-party app-shaped repos (outline/flowise/continue/librechat).
  **network + subprocess = 100% (261/261); ex-cosmetic-tail = 89.3%** (matches
  ceal's 88%) — the core signal is not a corca artifact. See
  [`eval-gate.md`](eval-gate.md). (Panel-labeled, human-calibration pending; gate
  opened, not closed.)
- **Packaged + released:** prebuilt binary (cargo-dist installer), wired into
  charness as an `external_binary` for the `quality` skill.

**Not built yet in Layer 0:** the **syntactic floor** (the zero-false-positive
*claim* channel — empty catch, swallowed error, log-and-continue on a mutating
path, bare `except`). pry today ships the *map* (prediction); the *floor* (claim)
does not exist. SARIF emit is also future (JSON only today).

## Now — precision levers (eval-gated) + the floor

> **⚠ Premise update (2026-06-16): the *unbuilt* precision-lever march is DEMOTED
> to backlog.** The remaining precision polish (rung-3 form-B below; the rung-3
> "ceiling" row in eval-gate's projected-impact table) was justified by an assumed
> payoff — that welded-at-demand sites concentrate something actionable, so
> sharpening precision sharpens a *prioritized risk* signal. Two pre-registered
> multi-repo validations refute the payoff: **E9 Tier-1** — welded-at-demand is
> **not** bugfix-enriched (matched 1.05, CI [0.96, 1.18]); and **step-1 coverage**
> — welded-at-demand files are **not** less test-associated (matched 0.95, CI
> [0.88, 1.02]). pry stays validated as a **precise injectability classifier**
> (network/subprocess 100%), but neither *prioritization* payoff (bugs, file-level
> coverage) holds, so further precision polish is **not** justified by it. It might
> still be justified by a testability-surface product goal — but that wedge is
> itself **unproven** (the line-level/error-path coverage claim is unmeasured here;
> see [`eval-gate.md`](eval-gate.md) §Step-1 scope) and is an **open `ideation`
> question**, not a settled identity. Honesty guard: do **not** pitch "fix welds →
> fewer bugs / better coverage." The shipped levers (0a–0d) stand; the **syntactic
> floor (#1)** and **quality auto-invoke (#2)** are independent of this premise and
> remain valid.

**Precision levers (named by [`eval-gate.md`](eval-gate.md), ranked by lift).**
Sequenced behind **Slice 2 (filter-recall arm)** — the spec requires the recall
arm online before any precision filter ships (a filter that over-demotes a genuine
weld must be catchable). Each lever then gates on E5: dev precision↑ ∧ held-out
filter-recall held, recomputed deterministically against the frozen labelset (E8).
**Exception — the two EXACT levers (cosmetic-random, test-file):** they only demote
findings *already labeled* COSMETIC/FALSE-WELD, so their recall cost reads directly
off the frozen labels (no bare-pool labeling needed). They may be **built +
dev-validated before Slice 2**; only their formal *ship*-close stays gated on the
held-out arm.

0a. **Slice 2 — filter-recall arm** (`spec-eval-harness.md` SC3/AC3) — **✓ DONE
    2026-06-15.** Labeled a 154-finding sample of the demoted pool (`finding_io.py
    emit --pool demoted`); frozen `*-barepool-labels.json`; `harness/filter_recall.py`
    re-derives. **Caught a real recall hole:** the shipped clock filters demote
    **16/143 = 11.2%** genuine clock (DB-query date bounds, date-math thresholds);
    random **0/11** (lossless). Gate rule: a lever must not raise the demoted-pool
    GENUINE count. Unblocks + reshapes the levers below.
0b. **Cosmetic-random filter** (#1 lever) — **✓ BUILT 2026-06-15.** `random` is
    **0/79** genuine across all 4 repos; `demote_welded_random` (`src/classify.rs`)
    demotes welded `random` from `demand` by default at every call form. Dev
    precision **56.7% → 66.0%, 0 genuine lost** (matched the projection exactly);
    ceal fixture demand-weld 68→67. The highest-lift, lowest-risk lever — built
    first, as an EXACT lever (see the exception above; held-out arm pends ship).
0c. **Clock control-vs-record discrimination fix** (was "stronger cosmetic-clock";
    reshaped by Slice 2) — **✓ BUILT 2026-06-15.** Not a blanket demotion: the
    `clock_is_logsink`/cosmetic filter over-demoted genuine clock (11.2% of the demoted
    pool) by misreading DB-query date bounds (`expiresAt < new Date()`) and date-math
    thresholds (`subMinutes(new Date(),5)` → later compared) as record-sinks.
    `clock_is_demand_control` (`src/classify.rs`) now RESCUES those before demotion —
    Rescue A (clock under a `[Op.lt]`/`$lte` query operator key, bare or via const) +
    Rescue B (a date-DERIVED clock whose result is compared) — while keeping true
    record/log sinks and bare record timestamps demoted. **Purely additive (only
    prevents demotion) → recall ↑, precision neutral: demoted-pool misses 16 → 5, 11
    rescued, 0 precision-damage, 0 lost-recall.** Gate: `python3 harness/filter_recall.py
    --remap` (re-runs pry, re-joins to the frozen oracle — needed because this lever
    changes pry's demand bit, unlike the EXACT levers). ceal zero-delta (cdd31884).
0d. **Extend the test-file heuristic** (`is_source`) — **✓ BUILT 2026-06-15.**
    `src/main.rs:63` now drops `.vitest.`/`.e2e.` stems (drove continue's llm crater).
    Default-stem scope only = **66.0% → 69.7%, 0 genuine lost**; repo-specific
    harness dirs (`manual-testing-sandbox/`, `*-sol.ts`) stay the `.pryignore` job
    (E7), which is the further 69.7%→70.3% — not pry's default. EXACT lever.

Then the structural deepeners:

1. **Syntactic floor.** Build the un-built Layer-0 claim channel (empty catch,
   swallowed error, log-and-continue on a mutating path), kept physically separate
   from the map output. High precision + `# pry-ignore` escape hatch (the
   *path-level* half — `.pryignore` + `--exclude` — already shipped, see
   `spec-eval-harness.md` E7; the inline `// pry-ignore` per-finding hatch lands
   here). This is the genuine un-built Layer-0 deliverable.
2. **quality auto-invoke** (charness-side): a `quality` driver that runs `pry map`
   as a standing advisory inventory, mirroring nose's consumer. Today pry is
   agent-invoked on-request via the `skills/pry/` F15 skill, not auto-run.

### Reopened by H3 — stage-2 rung-3 wrapper detection (F22, "form-B")

> **DEMOTED to backlog (2026-06-16) — premise dead (see the banner above).** This
> is precision polish whose payoff (a prioritized bug/coverage signal) is now
> falsified by E9 + step-1. Reopen only if an `ideation` pass revives a
> precision-justifying wedge. Kept here for the record, not as a Now item.

The `kill-gate.md` Run 5 EXTEND rider flagged network/subprocess seams behind an
injected transport/executor wrapper one hop up. A census on ceal found the gap
**not material** and it was deferred "until a corpus surfaces it." **continue
surfaces it:** its `openai-adapters` llm calls go through an injectable
`customFetch(config.requestOptions)` seam one hop up, driving the llm precision
crater (2/35) — see [`eval-gate.md`](eval-gate.md) taxonomy #4. **Reopen for a
scoped re-examination**, but it needs cross-file analysis + risks false-seaming,
so gate any rule hard against the frozen labelset + the Slice-2 recall arm.
Form-A (`implements I` / typed-const impl) is already built.

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
