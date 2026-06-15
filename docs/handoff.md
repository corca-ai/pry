# Handoff

## ▶ Resume protocol — if the operator just says "계속합시다" / "continue"

Do **NEXT ACTION** below, autonomously, via the `impl` skill. The operator has
**already approved** building the precision levers (#1) and the corpus expansion
(#3); human calibration (#2) is **done**. No re-confirmation needed — just build,
verify, critique, commit, push, then report and continue to the next queued item.
Read `docs/spec-eval-harness.md` (contract) + `docs/eval-gate.md` (results +
levers + the calibration ruleset) first. Default order is the queue below; if the
operator names a different item, do that instead.

## ▶ NEXT ACTION — lever #3: clock control-vs-record DISCRIMINATION fix

**Reshaped by Slice 2 (this is NOT "demote more clock").** The filter-recall arm
(`dcf59f2`) found the *opposite* failure dominates: the shipped `clock_is_logsink` /
`cosmetic_value_context` filters already **over-demote genuine clock** — 16/143
(11.2%) of the demoted-clock pool is panel-GENUINE (random 0/11, lossless). So lever
#3 tightens the clock heuristic to **rescue** those while still demoting true record
sinks. Net: precision ↑ (drop true-cosmetic) AND recall ↑ (rescue the 11%).

- **The two rescue targets (from the 16 misses; pry_reason in `*-barepool-labels.json`):**
  1. **DB-query date bounds** (the bulk): clock as an object-pair value under a query
     operator — `where: { expiresAt: { [Op.lt]: new Date() } }`, `findOne({ displayFrom:
     { $lte: now } })`. The `cosmetic_value_context` `pair` rule demotes ALL object-pair
     values; it must NOT demote a clock pair whose key is a query operator (`$lt/$lte/
     $gt/$gte/$ne`, `[Op.lt]`/`Op.gt`/…) or that sits in an object passed to a `find*`/
     `delete*`/`update*`/query call. (Distinguish a query-filter object from a record
     object — the operator-key signal is the cleanest discriminator.)
  2. **Date-math thresholds:** `const x = subMinutes(new Date(), 5)` → later `if
     (lastActiveAt < x)`. `clock_binding_is_control` / `name_used_in_control` doesn't
     trace the clock through a date-math helper wrapper (`subMinutes(clock, n)` /
     `dayjs(clock)`…) to the binding. Follow the clock up through a single wrapping
     call to its `const` binding, then run the existing control-use check on that name.
- **Where:** `src/classify.rs` — `cosmetic_value_context` (the `pair` arm ~L218-225)
  and `clock_is_logsink`/`clock_binding_is_control` (the dataflow helpers).
- **⚠ Caveat (1 of 16, flowise `genericHelper.js:788`):** a `setTimeout`-throttle
  `lastRan = Date.now()` is a borderline over-call — the rescue must target query-bounds
  + compared-thresholds, NOT all clock-in-call-args, or it will re-promote throttle
  timestamps. Keep timers (R3) demoted.
- **Gate (hard, mechanical):** after each change, `python3 harness/filter_recall.py`
  — the **demoted-pool GENUINE count must go DOWN** (rescue the 16), never up; AND
  re-derive demand-weld precision from the frozen labelsets — it must not drop (don't
  un-demote true cosmetic). Plus `cargo test` (the `lever3_clock_timing_vs_logsink`
  guards must stay green). Add classify_smoke fixtures mirroring the 3 miss shapes
  (`[Op.lt]: new Date()` query bound, `$lte: now` mongo, `subMinutes(new Date(),5)` →
  compared) + a throttle negative (must stay demoted).
- **Close:** fresh-eye critique (required), commit, push, advance this handoff.

## ▶ Queue (after lever #3; operator pre-approved the levers and #3 corpus)

1. **Lever #5 — construction dedup (R7):** treat `new OpenAI()` as the welded-client
   origin and dedup the downstream catalogued method finding (same client counted
   twice); do **not** enumerate SDK methods. Likely partly checkable from the existing
   demand-weld labelset (assess before any panel) — may be EXACT-ish.
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

## Current state (all pushed; HEAD = Slice 2 `dcf59f2` + this handoff)

- **Slice 2 (filter-recall arm) DONE** (`dcf59f2`): the gate's recall half. Labeled a
  154-finding sample of the demoted pool (welded, demand=false) via `finding_io.py
  emit --pool demoted`; frozen `*-barepool-labels.json` + `votes-barepool/`;
  re-derive with `python3 harness/filter_recall.py`. **Caught a real recall hole:**
  shipped clock filters over-demote **16/143 = 11.2%** genuine clock (DB-query date
  bounds + date-math thresholds, 15/16 via `clock_is_logsink`); random **0/11**
  (lossless). Gate rule: a lever must not raise the demoted-pool GENUINE count.
  Critique independently re-verified all 16 misses against source = SOUND. This
  reshaped lever #3 (NEXT ACTION) into a discrimination fix.
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
