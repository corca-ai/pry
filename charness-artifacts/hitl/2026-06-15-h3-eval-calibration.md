# HITL — H3 eval panel calibration (E4)

Session `h3-eval-calibration`. Goal: bound the same-model panel's error rate
(item #2 / E4) by having the operator blind-label a stratified sample of the
frozen H3 findings and compare to the panel. Target doc: `docs/eval-gate.md`.

## Result

- **Overall agreement: 15/17 (88%)** on the in-scope sample (26 sampled, 9
  test-file cards excluded by R5). demand-weld 12/14, seamed-control 3/3.
- Per-card record: `harness/fixtures/eval/calibration.json`.
- **Only disagreements: C02, C04 — both clock `setTimeout` (panel=GENUINE,
  human=COSMETIC).** One-directional: the panel over-calls retry/timeout timers.
  No other stratum drifts → the headline (network+subprocess 100%, ex-tail 89.3%)
  is human-validated; clock-genuine 5/130 is an over-count (true ≈3/130).
- **Recall hole named:** seamed-control 2/3 false-seams from rung-3 form-A
  interface-impl over-seaming (`ContinueServerClient implements
  IContinueServerClient` → its impl-internal `!response.ok throw` is un-testable
  via the interface seam). 1/3 (`http.ts` destructured `fetch` param) was a
  correct seam.

## Ruleset derived (operator-confirmed)

- **R1** blind calibration (panel verdict withheld until the human labels).
- **R2** 4-way vocab GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS.
- **R3** `setTimeout`/`setInterval` timers = COSMETIC — **fake timers
  (`useFakeTimers`/`setSystemTime`) are the seam for time**, so a welded timer
  doesn't block testing the way a welded network *failure* does.
- **R4** clock *comparisons* (`expiresAt < new Date()`, `Date.now()-x > N`) =
  GENUINE (control/security branch on an inline clock).
- **R5** test files out of scope: `.vitest.` / `.e2e.` / `manual-testing-sandbox/`
  / `-sol.ts` (lever 2).
- **R6** module-mocking ≠ a seam → welded network/llm calls are GENUINE even if
  `jest.mock`-able. **Foundational:** relaxing this collapses the network 100%
  signal. (Asymmetry with R3 is intentional: time is one clean global with no
  failure modes; network clients are many with rich failure modes and
  module-mocking is fragile/design-smell.)
- **R7** client *construction* (`new OpenAI()`) = the welded-client origin (the
  seam-decision point: inline `new` = welded, injected param/factory = seamed).
  **Dedup** construction + downstream method finding; do **not** enumerate SDK
  methods (a losing game) — keep `.create` only as an import-singleton fallback.
- Reachability / dead-code pruning is **knip's job, not pry's** →
  visibility-agnostic is the correct (safe) default.

## What changed in the target

`docs/eval-gate.md`: status banner + "Human calibration (E4) — done" section
added; lever 2 (clock: demote timers even on retry/error paths, true ≈3/130),
lever 4 (rung-3: + interface-impl over-seaming recall face), new lever 5
(construction dedup); seamed-control + gate-status sections updated.

## Caveats

Small N (17), weighted to contested strata — not a uniform statistical bound.
Human and panel read the same full source, so this measures "given the same code,
does the human agree with the panel's label" (the right question for label trust),
not an independent recall re-derivation. The seamed-control 3 were a recall audit
(pry:SEAMED was shown), not blind precision.
