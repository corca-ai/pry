# Handoff

## ▶ Resume protocol — if the operator just says "계속합시다" / "continue"

Do **NEXT ACTION** below, autonomously, via the `impl` skill. **Current operator-chosen
direction (2026-06-15): the nose-style multi-repo validation SWEEP** — pause the
precision-lever march to first prove the signal predicts bugs (쟁점 4) and generalizes
(쟁점 2). Levers #1/#2/#3 are shipped; lever #4 is now CONDITIONAL on the sweep. No
re-confirmation needed — just build, verify, critique, commit, push, then report and
continue. The sweep's step 1 (corpus discovery from GitHub) IS approved. Read
`docs/spec-eval-harness.md` (contract) + `docs/eval-gate.md` (results + levers + the
calibration ruleset) + nose's `eval/hazard/` (the pattern to reuse) first. Default order
is the queue below; if the operator names a different item, do that instead.

## ▶ NEXT ACTION — E9: nose-style multi-repo validation SWEEP

**Strategic redirect (operator-chosen 2026-06-15).** Before more precision polish
(lever #4), answer the load-bearing questions the levers *assume*: 쟁점 4 — does
welded-at-demand actually predict real defects? — and 쟁점 2 — does the signal
generalize beyond the 4 H3 apps? One multi-repo sweep answers both. Modeled on nose's
`eval/hazard/` (its `run_corpus.sh` + `corpus.json` + 3-persona panel). **Reuse nose's
PATTERN, NOT its repos** — nose's corpus is 15-per-language libraries (its 15 TS/JS are
all libs: axios/zod/jest/zustand/…), the WRONG shape; pry needs boundary-welding *apps*.

**The decisive nose lesson (do not repeat it):** nose built an automatic bug-linked gold
(G2 = a co-change miss whose sibling was a bugfix, function-level `git -L` attribution —
*exactly* pry's SZZ idea). The auto-rate matched the literature (1–3%) but an LLM-judge
audit found it **only ~11% precise → they RETRACTED the "validated against bug-linked
harm" claim** and kept the clean directly-observed signal. So pry's SZZ gold is fragile
and must be **audited, not trusted** (see Tier 2). The robust result is Tier 1.

Steps (each is its own slice; commit + critique as you go):
1. **Corpus discovery + freeze (self-select from GitHub — operator-requested).** Seed =
   the 4 H3 apps (already app-shaped, have maps + frozen labels). EXPAND by discovering
   app-shaped TS/JS OSS from GitHub: criteria — an *app* not a library (route handlers /
   service layer / DB clients / env+config, NOT a single-purpose lib), real
   error-handling, substantial bugfix history (for mining), permissive license, NOT
   corca, active. Score app-shapedness, stratify by domain, **pin commits**, and
   **pre-register the `dev|heldout` split BEFORE measuring** (honesty, like the kill-gate
   floor). Freeze to a `corpus.json` (nose schema: id/name/primary_language/domain/url/
   commit/split). Tooling: `gh`/GitHub API + a discovery subagent reading repo structure;
   route external fetches through `gather`. Reuse nose's `setup_repos.sh` prune discipline
   (drop vendored/generated/`.vitest` so churn isn't boilerplate-skewed).
2. **Deterministic sweep harness** (nose `run_corpus.sh` analog): per repo, clone@pinned →
   `pry map` → mine bugfix commits (PORT `harness/mine.py`: its regex is Python tokens —
   need JS EH tokens `catch`/`throw`/`.catch(`/`reject`/`retry`/`timeout` + boundary
   names) → cross bugfix-touched lines with pry findings. Parallel + incremental (skip
   mined). Fan out via the **Workflow** orchestration tool.
3. **Tier 1 — directly-observed ENRICHMENT (the MAIN result, nose's G1 analog):** across
   the corpus, are **welded-at-demand** sites touched by bugfix commits at a higher rate
   than **seamed** sites? Pure git + map join, no per-site gold → robust. **Pre-register
   the floor** (what enrichment ratio = "signal real") before computing.
4. **Tier 2 — SZZ bug-linked gold (the fragile cherry):** port `harness/szz.py` (its
   `ast` function-resolution is Python → tree-sitter-typescript) on a sample; **LLM-panel
   audit the gold for precision** (the ~11% check). Illustration, NOT load-bearing.
5. **Generalization (쟁점 2):** tune any threshold on `dev` only, report `heldout`
   separately — this ABSORBS the old "corpus-expansion / SC2 gate-close" queue item.
6. **Python branch (the recorded reopen):** include non-glue Python *apps* in discovery;
   run the cheap analyzer-free **(b)-gate lens** on them (does welded/seamed discriminate,
   unlike the author's glue?). If yes → build the Python frontend (`catalog/python.toml`
   exists) → fold Python into the sweep (its mine.py/szz.py are already Python-native).

**Honesty gates:** pre-registered floor + dev/heldout split chosen BEFORE measuring; SZZ
gold audited not trusted (the nose 11% lesson); `log`/report what was pruned or excluded
(no silent truncation). **Close:** fresh-eye critique (required), commit, push, advance.

## ▶ Queue (after the sweep; the sweep gates whether further polish is worth it)

1. **Lever #4 — rung-3 stage-2 (CONDITIONAL on the sweep validating the thesis):**
   two faces — (a) injected-transport (`customFetch`) precision gap (continue llm crater
   2/35); (b) interface-impl OVER-seaming recall hole (`implements I` blanket-seams the
   impl's own error handling, 2/3 seamed-control false-seams). Cross-file + bidirectional
   → gate BOTH against the demand-weld labelset (precision) AND the Slice-2 recall arm +
   seamed-control pool. `src/classify.rs` `injectable_impl_context` + net/subproc leaf
   arms. Polish like this is premature until Tier 1 says the signal predicts bugs.

### Deferred — lever #5 (construction dedup, R7): NEGLIGIBLE measured impact

Assessed 2026-06-15 (read-only, re-derived via a fresh `pry map` + label join). The
`const client = new X(); client.method()` double-count the dedup targets is **almost
absent** from the validation surface: **1** `receiver-local:inline-new` method across
all 4 H3 repos (the one is GENUINE), and **1** in ceal/packages (+ 4 construction
origins) — **~2 dedup targets total.** Most SDK calls go through `this.client`
(ctor-injected → seamed) or imported singletons, not a same-scope local `new`. So
lever #5 would change ~1 demand-weld and is not a meaningful precision lever; the
handoff's earlier "expect a ceal delta" was an over-estimate. **Deferred** as a
low-priority backlog-hygiene cleanup (R7 is still a sound principle — fold it in when a
construct-heavy corpus surfaces it, or alongside a catalog refresh), behind the
validation sweep + lever #4. Not dropped; just not worth a classifier
change + critique cycle for 2 findings now.

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
  reshaped lever #3 into a discrimination fix (now SHIPPED, `49ecd36`, 16 → 5).
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
