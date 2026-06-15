# Handoff

## ▶ Resume protocol — if the operator just says "계속합시다" / "continue"

Do **NEXT ACTION** below, autonomously, via the `impl` skill. The operator has
**already approved** building the precision levers (#1) and the corpus expansion
(#3); human calibration (#2) is **done**. No re-confirmation needed — just build,
verify, critique, commit, push, then report and continue to the next queued item.
Read `docs/spec-eval-harness.md` (contract) + `docs/eval-gate.md` (results +
levers + the calibration ruleset) first. Default order is the queue below; if the
operator names a different item, do that instead.

## ▶ NEXT ACTION — lever #5: construction dedup (R7)

**Assess before building — likely EXACT-ish (no new panel).** A welded SDK client
(`const client = new OpenAI()` / `new WebClient(token)`) is counted twice in the
demand backlog: once at the `new` construction (the welded-client origin) and again
at each downstream catalogued method (`client.responses.create(...)`). R7: the `new`
is where injectability is decided; the method finding on the *same* client is a
duplicate, not a second weld. Dedup the downstream method against its construction
origin — but do **not** enumerate SDK methods (the catalog stays data; no per-SDK
method lists).

- **First, assess from the FROZEN demand-weld labelset (no panel needed):** how many
  demand-welds are construction/method pairs on the same client in
  `harness/fixtures/eval/*-labels.json`? If the duplicate methods are a clean subset,
  the recall cost reads directly off the labels (EXACT, like levers #1/#2). If it is
  entangled, scope a small targeted check before touching the classifier.
- **Where:** `src/classify.rs` — `classify_receiver` / `local_decl_rhs` already trace a
  method receiver to its `const x = new Client()` origin (the `receiver-local:inline-new`
  reason). The dedup is: when a method's receiver origin is an in-scope welded
  construction that pry ALSO emits as its own finding, demote the method (the
  construction carries the demand). Keep a param/ctor-injected receiver SEAMED (untouched).
- **Gate:** `cargo test` + (if any demand bit moves) `python3 harness/filter_recall.py
  --remap` must stay PASS (0 precision-damage, 0 lost-recall, misses ≤ baseline). Add a
  classify_smoke fixture: `const c = new OpenAI(); c.responses.create()` should yield
  ONE demand weld (the construction), the method deduped; a param-injected client stays
  seamed. ceal: regenerate `fixtures/ceal-ts-map.summary.json` at pinned cdd31884 if the
  demand count moves (ceal has welded `new`-client + method pairs, so expect a delta).
- **Close:** fresh-eye critique (required, same-agent forbidden), commit, push, advance
  this handoff.

## ▶ Queue (after lever #5; operator pre-approved the levers and #3 corpus)

1. **Lever #4 — rung-3 stage-2 (two faces, calibration-confirmed):** (a) injected
   transport (`customFetch`) precision gap; (b) interface-impl **over-seaming**
   recall hole (`implements I` blanket-seams the impl's own error handling — 2/3
   seamed-control false-seams). Cross-file, risky → gate hard against the labelset
   + Slice-2 recall arm.
2. **#3 Corpus expansion (operator-approved) — close the gate (SC2):** scout a
   **DI-disciplined exemplar** (high clock-injection; `n8n`/`cal.com`) as dev #5,
   assemble the **held-out arm** (target dev 5 / held-out 10), run the panel, tune
   only on dev. This is what formally *closes* the gate + ships the levers.
3. **E9 SZZ structural-improvement** on an EH-bugfix-rich OSS repo (reuse
   `harness/mine.py`+`szz.py`+commit labeler) — catalog-recall + calibration.

## Current state (all pushed; HEAD = lever #3 `49ecd36` + this handoff)

- **Lever #3 (clock control-vs-record discrimination) SHIPPED** (`49ecd36`): the
  reshaped lever closed the Slice-2 recall hole. `clock_is_demand_control`
  (`src/classify.rs`) RESCUES the two over-demoted shapes before demotion — Rescue A
  (clock under an `[Op.lt]`/`$lte` query-operator key, bare or via const) + Rescue B (a
  date-DERIVED clock — `subMinutes(new Date(),5)`, `new Date(Date.now()-WEEK)` — whose
  result is compared). **Purely additive** (gates as `!rescue && (cosmetic||logsink)` —
  only ever prevents a demotion; critique verified via a neutered-binary diff: 53
  changes, all promotions, 0 demotions). **Result: demoted-pool misses 16 → 5, 11
  rescued, 0 precision-damage, 0 lost-recall**, re-derived by `python3
  harness/filter_recall.py --remap` (re-runs pry, re-joins to the frozen oracle — the
  code-reflecting gate, still no new LLM since the lever moves pry's demand bit). 5
  residual = 3 bare record timestamps (R3) + 2 hard-tail (equality on `.getMonth()`,
  clock→date-range lib). `cargo test lever3_query_bounds_and_thresholds` pins the
  shapes + negatives. Gate hardened (critique): lost-recall branch un-deadened +
  misses-ceiling guard. ceal zero-delta (cdd31884). Truth surfaces synced.
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
