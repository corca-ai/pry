# Handoff

## ▶ Resume protocol — if the operator just says "계속합시다" / "continue"

Do **NEXT ACTION** below, autonomously, via the `impl` skill. The operator has
**already approved** building the precision levers (#1) and the corpus expansion
(#3); human calibration (#2) is **done**. No re-confirmation needed — just build,
verify, critique, commit, push, then report and continue to the next queued item.
Read `docs/spec-eval-harness.md` (contract) + `docs/eval-gate.md` (results +
levers + the calibration ruleset) first. Default order is the queue below; if the
operator names a different item, do that instead.

## ▶ NEXT ACTION — build lever #2: test-file heuristic

**Goal:** extend pry's default test-file drop to conventional `.vitest.` / `.e2e.`
stems — the second EXACT, zero-recall-cost lever. continue's llm crater (2/35) is
largely its `*.vitest.ts` suites, where `fetch` is mock-injected (FALSE-WELD).

- **Where:** `src/main.rs:63`, the `is_test_stem` array `["test", "spec"]` → add
  `"vitest"`, `"e2e"`. The existing `.{stem}{ext}` matcher already covers
  `.vitest.ts`/`.e2e.ts`/`.mjs`/`.cjs` — a one-line list change. Add an `is_source`
  unit test (a `.vitest.ts` path → dropped) if `main.rs` has a test seam; else a
  `discover`/CLI-level smoke.
- **Scope discipline (do NOT over-reach):** the DEFAULT heuristic catches only
  *conventional* test stems (`.vitest.`/`.e2e.`). Repo-specific dirs
  (`manual-testing-sandbox/`, `*-sol.ts`) stay the repo's `.pryignore` job (E7) —
  do **not** bake them into the default. In the labelset: `.vitest.` = **31**
  demand-weld findings = the lever's true scope; `manual-testing-sandbox/`+`-sol` =
  6 more that eval-gate's lumped "drop 29 → 70.3%" row included but the default
  heuristic does NOT own.
- **Verify (dev-side E5):** `cargo test`; re-derive precision from the frozen
  labelsets dropping ONLY `.vitest.`/`.e2e.` demand-welds (NOT sandbox/-sol) — that
  is the honest default-heuristic lift (66.0% → recompute; it is **less** than the
  table's lumped 70.3% because sandbox/-sol are `.pryignore` scope). All dropped are
  COSMETIC/FALSE-WELD in the labels → 0 genuine lost by construction. Reconcile
  eval-gate.md's "drop 29" row: split it into the default-heuristic part vs the
  `.pryignore` part so the doc claim matches what the binary actually does.
- **Fixture cascade:** ceal `packages/` almost certainly has no `.vitest.`/`.e2e.`
  in scope (it uses `.test.`/`.spec.`). Re-run `pry map ../ceal/packages
  --summary-only` at the pinned `cdd31884` (clean checkout, restore to `main`
  after); if `files_scanned`/counts are unchanged, state explicitly that the ceal
  fixture needs **no** edit. SKILL.md self-test count stays 67 unless ceal moves.
- **Why allowed before Slice 2:** same EXACT-lever exception as cosmetic-random
  (`eval-gate.md`): only demotes findings *already labeled* COSMETIC/FALSE-WELD, so
  recall cost is read off the frozen labels. Formal *ship*-close still wants the
  held-out arm (queue #4).
- **Close:** fresh-eye critique (required), commit, push, advance this handoff.

## ▶ Queue (after lever #2; operator pre-approved the levers and #3 corpus)

1. **Lever #3 — stronger clock + Lever #5 — construction dedup** (need a bit more
   care; calibration-refined):
   - clock: demote timers (`setTimeout`/`setInterval`) and record-`Date` **even on
     retry/error paths** (fake timers are the time-seam, R3); keep only clock
     *comparisons* (R4). Panel over-called timers GENUINE → true clock-genuine ≈3/130.
   - construction dedup (R7): treat `new OpenAI()` as the welded-client origin and
     dedup the downstream method finding; do **not** enumerate SDK methods.
2. **Slice 2 — filter-recall arm** (E5/SC3/AC3): label a bare-pool sample, compute
   baseline filter-recall, document the gate rule. Required before the *harder*
   levers (clock/rung-3) and before formally shipping any lever.
3. **Lever #4 — rung-3 stage-2 (two faces, calibration-confirmed):** (a) injected
   transport (`customFetch`) precision gap; (b) interface-impl **over-seaming**
   recall hole (`implements I` blanket-seams the impl's own error handling — 2/3
   seamed-control false-seams). Cross-file, risky → gate hard against the labelset
   + Slice-2 recall arm.
4. **#3 Corpus expansion (operator-approved) — close the gate (SC2):** scout a
   **DI-disciplined exemplar** (high clock-injection; `n8n`/`cal.com`) as dev #5,
   assemble the **held-out arm** (target dev 5 / held-out 10), run the panel, tune
   only on dev. This is what formally *closes* the gate + ships the levers.
5. **E9 SZZ structural-improvement** on an EH-bugfix-rich OSS repo (reuse
   `harness/mine.py`+`szz.py`+commit labeler) — catalog-recall + calibration.

## Current state (all pushed; HEAD = lever #1 `58b5f31` + this handoff)

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
