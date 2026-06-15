# Handoff

## ▶ Resume protocol — if the operator just says "계속합시다" / "continue"

Do **NEXT ACTION** below, autonomously, via the `impl` skill. The operator has
**already approved** building the precision levers (#1) and the corpus expansion
(#3); human calibration (#2) is **done**. No re-confirmation needed — just build,
verify, critique, commit, push, then report and continue to the next queued item.
Read `docs/spec-eval-harness.md` (contract) + `docs/eval-gate.md` (results +
levers + the calibration ruleset) first. Default order is the queue below; if the
operator names a different item, do that instead.

## ▶ NEXT ACTION — Slice 2: the filter-recall arm (the gate for every harder lever)

Both EXACT levers are shipped (#1 cosmetic-random `58b5f31`, #2 test-file `94de55e`).
**Everything past them is gated behind Slice 2.** The remaining levers (stronger-clock,
rung-3) are **CEILING** levers: their syntactic filters are *imperfect*, so they can
over-demote a genuine weld — a recall risk the existing demand-weld labelset **cannot**
measure (it only labels findings pry already demand-flagged). Slice 2 builds the
missing denominator. Per spec E5/SC3/AC3 (`spec-eval-harness.md`):

- **What:** label a sample of pry's **bare pool** — welded+seamed findings *before*
  demand-filtering, the pool a precision filter could wrongly demote from — with the
  same `harness/finding_io.py` machinery (3 personas → reconcile → freeze). Then
  **filter-recall** = of the panel-GENUINE welds in the bare pool, how many a lever
  keeps (does not demote). Document the gate rule + a worked example in `eval-gate.md`:
  *a lever ships only if dev precision↑ ∧ held-out filter-recall held* (E5).
- **⚠ This is a DECISION, not a mechanical step — it is an LLM-panel campaign** (E8:
  "LLM once → frozen labelset"). Sampling scope is a real cost/quality choice: how
  large a bare-pool sample, which repos, clock-stratification. **Get operator scope
  before launching the panel.** Default if they don't specify: a stratified
  ~150-finding bare-pool sample across the 4 repos, clock/llm-weighted (the contested
  strata), seamed+welded pre-demand. *Bare-pool ≫ the 589 demand-findings, so this is
  the most expensive eval step so far.*
- **Output:** `harness/fixtures/eval/*-barepool-labels.json` (frozen), a filter-recall
  baseline number, the documented gate rule. Then re-derive a worked filter-recall for
  the two shipped EXACT levers (sanity: both should be 100% — they only dropped labeled
  COSMETIC/FALSE-WELD).
- **Then unblocks:** queue #1 (stronger-clock + construction-dedup) and #2 (rung-3).

## ▶ Queue (after Slice 2; operator pre-approved the levers and #3 corpus)

1. **Lever #3 — stronger clock + Lever #5 — construction dedup** (gated by Slice 2;
   calibration-refined):
   - clock: demote timers (`setTimeout`/`setInterval`) and record-`Date` **even on
     retry/error paths** (fake timers are the time-seam, R3); keep only clock
     *comparisons* (R4). Panel over-called timers GENUINE → true clock-genuine ≈3/130.
     CEILING lever (imperfect filter) → must pass the Slice-2 filter-recall gate.
   - construction dedup (R7): treat `new OpenAI()` as the welded-client origin and
     dedup the downstream method finding; do **not** enumerate SDK methods. (May be
     partly checkable from the existing labelset — assess before launching.)
2. **Lever #4 — rung-3 stage-2 (two faces, calibration-confirmed):** (a) injected
   transport (`customFetch`) precision gap; (b) interface-impl **over-seaming**
   recall hole (`implements I` blanket-seams the impl's own error handling — 2/3
   seamed-control false-seams). Cross-file, risky → gate hard against the labelset
   + Slice-2 recall arm.
3. **#3 Corpus expansion (operator-approved) — close the gate (SC2):** scout a
   **DI-disciplined exemplar** (high clock-injection; `n8n`/`cal.com`) as dev #5,
   assemble the **held-out arm** (target dev 5 / held-out 10), run the panel, tune
   only on dev. This is what formally *closes* the gate + ships the levers.
4. **E9 SZZ structural-improvement** on an EH-bugfix-rich OSS repo (reuse
   `harness/mine.py`+`szz.py`+commit labeler) — catalog-recall + calibration.

## Current state (all pushed; HEAD = lever #2 `94de55e` + this handoff)

- **Lever #2 (test-file heuristic) SHIPPED** (`94de55e`): `is_source` (`src/main.rs:63`)
  now drops `.vitest.`/`.e2e.` stems. Dev precision **66.0% → 69.7%, 0 genuine lost**
  (25 `.vitest.` false-welds; the further 69.7%→70.3% is `manual-testing-sandbox/`+`-sol`
  = repo `.pryignore` scope, NOT pry's default). ceal unaffected (0 `.vitest`/`.e2e`
  files → fixture + SKILL.md unchanged). New `src/main.rs` unit tests. Critique = SHIP.
- **Lever #1 (cosmetic-random) SHIPPED** (`58b5f31`): welded `random` →
  `demand=false` at every call form (`demote_welded_random` in `src/classify.rs`).
  Dev precision **56.7% → 66.0%, 0 genuine lost** (matched the projection exactly);
  ceal fixture demand-weld 68→67 (regenerated at pinned `cdd31884`, delta isolated);
  `random_is_never_demand` test; fresh-eye critique = SHIP. Truth surfaces synced
  (eval-gate / precision-gate / roadmap / SKILL.md / README).
- **H3 gate OPENED + human-calibrated.** Panel ran on 4 pinned third-party repos
  (outline `d85ead5` / flowise `f4e2794` / continue `eaa23c5` / librechat `8154a31`;
  589 findings frozen to `harness/fixtures/eval/*-labels.json`). **network+subprocess
  100% (261/261), ex-tail 89.3% (≈ ceal 88%), raw pooled 56.7%** — clock/random
  cosmetic tail is the whole drag. **Calibration: 15/17 (88%)** human–panel
  agreement; only disagreements = panel over-calling clock timers (one-directional);
  headline human-validated. Recall hole named (rung-3 interface-impl over-seaming).
  Full results + ruleset R1–R7: `docs/eval-gate.md`, `harness/fixtures/eval/calibration.json`,
  `charness-artifacts/hitl/2026-06-15-h3-eval-calibration.md`.
- **Ruleset R1–R7 (operator-confirmed)** — the labeling/scope philosophy now: fake
  timers = the time-seam (timers→COSMETIC); clock *comparisons*→GENUINE; test files
  out of scope; **module-mock ≠ a seam** (foundational to the network signal);
  construction = welded-client origin + dedup; reachability/dead-code is knip's job
  (pry stays visibility-agnostic).
- **Built earlier:** scope-control (`dd97cad` — `.pryignore`/`--exclude`),
  mechanical eval harness (`ac4d4e2` — `harness/finding_io.py` + 8 tests).
- **Corpus** cloned at `~/codes/_pry-corpus/{outline,flowise,continue,librechat}`
  (re-clone at the pinned commits above if cleaned). Shipped binary stays zero-LLM;
  all panel/eval work is dev-time only (E2).
- **ceal#350** re-scoped to validated `packages/` (70). Issues filed: ceal#350,
  cautilus#48, open-ax-day#5 (corca-owned dogfood only; no outbound on the H3 repos).

### Layer-0 + packaging arc (prior, COMPLETE)
pry **v0.1.0 released + wired**: TS/JS analyzer (~88% ceal / ~97% cautilus);
`corca-ai/pry` PUBLIC; cargo-dist release; charness `external_binary` (`validation`
role for `quality`); F15 skill `skills/pry/SKILL.md` + `rank_backlog.py`.

## Deferred (each names its reopen trigger — see spec)

- **Python (b)-gate + frontend** — reopen on a third-party non-glue OSS Python corpus.
- **Inline `// pry-ignore`** (per-finding hatch) — ideally with the syntactic floor.
- **Syntactic floor** (zero-FP claim channel) — the one un-built Layer-0 deliverable.
- **Homebrew tap; SARIF emit.**

## References

- `docs/spec-eval-harness.md` — canonical build contract (E1–E9, SC/AC).
- `docs/eval-gate.md` — H3 results, per-kind/stratum precision, named levers,
  projected lever impact, human-calibration section.
- `harness/finding_io.py` + `test_finding_io.py` — mechanical panel plumbing;
  `harness/fixtures/eval/*-labels.json` + `calibration.json` — frozen labelsets + calibration.
- `docs/precision-gate.md` (H1 precision + taxonomy), `docs/kill-gate.md` (TS GO / Python KILL).
- `charness-artifacts/hitl/2026-06-15-h3-eval-calibration.md` — calibration session + ruleset.
