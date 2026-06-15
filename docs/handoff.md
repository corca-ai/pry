# Handoff

## ▶ Resume protocol — if the operator just says "계속합시다" / "continue"

Do **NEXT ACTION** below, autonomously, via the `impl` skill. The operator has
**already approved** building the precision levers (#1) and the corpus expansion
(#3); human calibration (#2) is **done**. No re-confirmation needed — just build,
verify, critique, commit, push, then report and continue to the next queued item.
Read `docs/spec-eval-harness.md` (contract) + `docs/eval-gate.md` (results +
levers + the calibration ruleset) first. Default order is the queue below; if the
operator names a different item, do that instead.

## ▶ NEXT ACTION — build lever #1: cosmetic-random filter

**Goal:** demote `random` from the substitution-demand subset by default — the
single highest-lift, lowest-risk, EXACT win (random is **0/79 genuine** across all
4 H3 repos; calibration agreed random = cosmetic-by-nature, no failure to inject).
Lifts dev precision **56.7% → 66.0%, zero genuine welds lost.**

- **Where:** `src/classify.rs`. Today `cosmetic_value_context` is applied to
  clock+random only in narrow record positions (`builtin_call` branch ~L856), and
  the `global_call` `random-global` (~L826) gets **no** cosmetic check at all.
  Make welded `random` `demand=false` by default. Simplest defensible version
  (given 0/79): demote all welded random. Optional safer refinement (mirrors clock
  R4): keep random used *directly in a branch condition* (`if (Math.random()<x)`)
  — rare; ship the simple version first unless it's trivial.
- **Fixture cascade (this is why it's operator-in-loop, now approved):** ceal
  `packages/` has 1 random demand-weld → regenerate `fixtures/ceal-ts-map.summary.json`
  (count drops by the random welds), update `classify_smoke.rs` if it asserts
  counts, and the **`skills/pry/SKILL.md` self-test number (68 → 67)**. Check
  `docs/precision-gate.md` / `README.md` citations for any count that shifts.
- **Verify (dev-side E5):** `cargo test`; re-run `pry map` on `~/codes/_pry-corpus/*`
  and confirm the `random` welds are now `demand=false` and nothing else moved;
  re-derive precision from the frozen labelsets (drop random from the demand-weld
  group → expect 315/477 = 66.0%, 0 genuine lost). The labelsets already label all
  random COSMETIC, so recall cost = 0 by construction.
- **Why this is allowed before Slice 2:** the spec gates levers behind the
  filter-recall arm, **but** random + test-file are the documented EXCEPTION
  (`eval-gate.md` "Projected lever impact"): they only demote findings *already in
  the labeled demand set* (all COSMETIC), so their recall cost is read directly off
  the frozen labels — no bare-pool labeling needed. Formal *ship*-close still wants
  the held-out arm (#3); building + dev-validating now is approved.
- **Close:** fresh-eye critique (required), commit, push, update this handoff
  (tick NEXT ACTION → the next queue item).

## ▶ Queue (after lever #1; operator pre-approved #1 and #3)

1. **Lever #2 — test-file heuristic.** Extend `is_source` (`src/main.rs`) to drop
   `.vitest.` / `.e2e.` stems (conventional test files pry currently misses;
   drove continue's llm crater). EXACT, 0 genuine lost → 66.0% → 70.3%. Repo-specific
   dirs (`manual-testing-sandbox/`) stay the repo's `.pryignore` job (E7), not the
   default heuristic.
2. **Lever #3 — stronger clock + Lever #5 — construction dedup** (need a bit more
   care; calibration-refined):
   - clock: demote timers (`setTimeout`/`setInterval`) and record-`Date` **even on
     retry/error paths** (fake timers are the time-seam, R3); keep only clock
     *comparisons* (R4). Panel over-called timers GENUINE → true clock-genuine ≈3/130.
   - construction dedup (R7): treat `new OpenAI()` as the welded-client origin and
     dedup the downstream method finding; do **not** enumerate SDK methods.
3. **Slice 2 — filter-recall arm** (E5/SC3/AC3): label a bare-pool sample, compute
   baseline filter-recall, document the gate rule. Required before the *harder*
   levers (clock/rung-3) and before formally shipping any lever.
4. **Lever #4 — rung-3 stage-2 (two faces, calibration-confirmed):** (a) injected
   transport (`customFetch`) precision gap; (b) interface-impl **over-seaming**
   recall hole (`implements I` blanket-seams the impl's own error handling — 2/3
   seamed-control false-seams). Cross-file, risky → gate hard against the labelset
   + Slice-2 recall arm.
5. **#3 Corpus expansion (operator-approved) — close the gate (SC2):** scout a
   **DI-disciplined exemplar** (high clock-injection; `n8n`/`cal.com`) as dev #5,
   assemble the **held-out arm** (target dev 5 / held-out 10), run the panel, tune
   only on dev. This is what formally *closes* the gate + ships the levers.
6. **E9 SZZ structural-improvement** on an EH-bugfix-rich OSS repo (reuse
   `harness/mine.py`+`szz.py`+commit labeler) — catalog-recall + calibration.

## Current state (all pushed; HEAD `67ba37c`)

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
