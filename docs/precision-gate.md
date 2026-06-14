# Precision Gate (H1) — is pry's welded-at-demand backlog *reliably useful*?

**Run date:** 2026-06-14 · **Corpus:** ceal `cdd31884` (`packages/`, 461 src files)
· **Analyzer:** `pry map` (Stage-1, frozen `fixtures/ceal-ts-map.summary.json`)

## Why this gate

Earlier runs proved pry is *deterministic and stable* (Run 6, Stage-1) but never
proved it is *useful* — i.e. that the findings it ranks are genuine, actionable
testability gaps and not noise. Hand-checking 3 findings (subprocess/network/llm)
showed real gaps exist, but n=3 is an anecdote. This gate measures **precision**:
of the welded-at-demand findings pry emits, what fraction is a genuine
failure-injection gap on a path worth testing?

**Hypothesis H1 (pre-registered):** *"pry's demand-subset welds are ≥80% genuine
actionable gaps, and the remaining noise is dominated by one or two nameable,
filterable categories."*

## Method

- **Subject:** the 174 **welded** findings on pry's **substitution-demand subset**
  (`demand=true`), the kinds pry already markets as the backlog: clock 135,
  subprocess 16, network 12, random 5, llm 3, slack 3. (`fileio` 540 + `env` 75
  are the known diagnostic swamp — excluded by design, not counted here.)
- **Labeling:** non-clock (39) labeled **by full census**, reading ceal source at
  each `file:line`; clock (135) by a **stratified sample of 32** (every 4th),
  extrapolated. Zero code written — pure measurement.
- **Labels:**
  - **GENUINE** — real weld, on/near a failure path, no seam to inject a failure,
    worth making injectable.
  - **FALSE-WELD** (FP) — actually *already seamed* via an injected
    interface/factory/param that pry's leaf model missed (rung-3 gap).
  - **COSMETIC** — real weld but outside pry's thesis: a display/record value
    (`new Date().toISOString()` as a field, temp-file name randomness) where there
    is no failure to inject.
  - **AMBIGUOUS** — bare `const now = Date.now()` whose downstream use (control vs
    log) isn't decidable from local context.

## Result — H1 FALSIFIED at the raw level, but its second clause holds strongly

| | total | genuine | false-weld | cosmetic | ambiguous | precision |
|---|---|---|---|---|---|---|
| subprocess | 16 | 14 | 1 | 1 | 0 | 88% |
| llm | 3 | 3 | 0 | 0 | 0 | 100% |
| network | 12 | 7 | 4 | 0 | 1 | 58% |
| slack | 3 | 2 | 1 | 0 | 0 | 67% |
| random | 5 | 0 | 0 | 5 | 0 | 0% |
| **non-clock (census)** | **39** | **26** | **6** | **6** | **1** | **67%** |
| clock (sample 32) | 32 | 7 | 1 | 21 | 3 | 22% |
| clock (extrapolated) | 135 | ~30 | ~4 | ~89 | ~13 | ~22% |
| **OVERALL demand-welded** | **174** | **~56** | **~10** | **~95** | **~14** | **~32%** |

- **Raw precision ≈ 32%.** Two of every three top findings are noise → pry as it
  emits today is **not reliably useful**. H1's "≥80% raw" is **false**.
- **But the noise is dominated by ONE cheap-to-filter category** (H1's second
  clause = **true**): **cosmetic clock** (`new Date().toISOString()` /
  `Date.now()` used directly as an object field or template value, *not* inside a
  `setTimeout`/`setInterval`/deadline/TTL) is **~89 findings = ~51% of the entire
  demand-welded set**. Cosmetic random (temp-name/ID/MIME-boundary) adds ~5.
- **Curated precision climbs fast:**
  - after a syntactic **cosmetic-clock/random filter** → **56/79 ≈ 71%**
  - after also fixing the **false-welds** (rung-3) → **56/70 ≈ 80%**

## Noise taxonomy (the deliverable that picks the next lever)

1. **Cosmetic clock — ~89 (51% of all).** `timestamp:`/`created_at:`/`updated_at:`/
   `recordedAt:`/`fetched_at: new Date().toISOString()` record fields. Not a
   failure path. *Lever: a deterministic classifier filter — demote `new Date()`/
   `Date.now()` that is an object-property value or template literal and NOT an
   argument to `setTimeout`/`setInterval`/a deadline/TTL computation.* Biggest,
   cheapest win. Examples: `agent-runner-output.ts:300`, `memory/store.ts:537`,
   `turn-bridge.ts:408`.
2. **False-weld / rung-3 — ~10 (6%).** Leaf boundary inside a *named default
   implementation of an injectable interface/factory*. The seam exists; pry sees
   the leaf. *Lever: F22 rung-3 wrapper/factory detection — now evidence-backed.*
   Examples:
   - `connectors/notion/*`: `const defaultNotionHttpTransport: NotionHttpTransport
     = { request(){ fetch(...) } }` (×3) — seam is `NotionHttpTransport`.
   - `ceal-runtime/src/google-connect-server.ts:259`: `httpsTokenExchange:
     ExchangeTokenFetch = …` — seam is the `ExchangeTokenFetch` type.
   - `ceal-agent/src/sandbox.ts:151`: `class LocalCommandExecutor implements
     Executor { exec(){ spawn } }` — seam is `Executor`.
   - **Two are outright classifier BUGS, not missing features** — pry's existing
     0-hop seam logic *should* catch these and didn't:
     - `slack-search-public.ts:129`: `input.clientFactory ? input.clientFactory(t)
       : new WebClient(t)` — a ternary-factory seam flagged welded.
     - `github-app-installations.ts:107`: `const now = input.now ?? (() =>
       Date.now())` — an `input.now ??` injection seam flagged welded.
3. **Cosmetic random — ~5.** `${Date.now()}.${Math.random()}` temp-file names,
   tool-call IDs, MIME boundaries. Filter with the same rule as (1).
4. **Ambiguous bare-`now` — ~14.** `const now = Date.now()` with non-local use.
   Needs one-hop dataflow to resolve control vs log; lower priority.

## What IS genuine (the ~56 that survive) — pry's real value

Concentrated, coherent clusters — all "you cannot inject a failure to test this":

- **subprocess (14/16):** inline `spawnSync`/`spawn`/`execFileSync` on git/flock/
  guardian-child paths with real error handling (`Outcome`, `status !== 0`,
  deadline/timeout). E.g. `control-auto-commit.ts:133` (flock git commit),
  `observability.ts:58-68` (git probe try/catch — *one* gap counted 3×: a
  granularity note for later). A recurring **guardian-child spawn** sub-cluster
  (`*-guardian-child-protocol.ts`) is one seam shape worth a dedicated rec.
- **llm (3/3):** `client ??= new OpenAI(...)` over a `let client = null` local —
  memoization, not a seam. Can't inject an API failure for image-gen / web_search.
- **network (7/12):** genuine bare global `fetch` — Codex responses, Google OAuth
  token refresh, Slack file download. *This refutes the handoff's worry that
  network welds are mostly rung-3 FP: ~58% are real bare globals.*

## Verdict & next lever

- **GATE: pry is not yet reliably useful (raw 32%), but the gap is one cheap
  filter away from ~71% and a known-scoped rung-3 pass from ~80%.** The hypothesis
  failed on its headline number but *succeeded* at its real job: it produced a
  clean, ranked noise taxonomy that names the exact next work.
- **Next lever (ordered by leverage/cost):**
  1. **Cosmetic-clock/random filter** (deterministic, ~1 classifier rule) →
     biggest single precision jump (32%→~71%); pry should stop emitting `created_at`
     timestamps as a "testability backlog."
  2. **F22 rung-3 wrapper/factory detection** + fix the **2 0-hop classifier bugs**
     (`input.now ??`, `input.clientFactory ?`) → ~71%→~80% and removes the
     false-positive class that most erodes trust.
  3. (Deferred) one-hop dataflow for the ~14 ambiguous bare-`now`.
- **Framing correction (carries into any packaging):** the headline output must be
  the *curated* genuine subset (~56 here: subprocess/llm/network/inline-client on
  error paths), never "789 welded" or even "174 demand-welded." Sell **measurement
  of failure-injection gaps**, not a 789-row map.

## After levers 1+2+3 (implemented 2026-06-14, this run)

All three levers are **built** in `src/classify.rs` (5 tests in
`tests/classify_smoke.rs`, green; output byte-deterministic). On ceal `cdd31884`:

| metric | before | 1+2 | **1+2+3** |
| --- | --- | --- | --- |
| demand-welded **count** | 174 | 85 | **67** |
| demand-welded **precision** (hand-sampled) | ~32% | ~70% | **~88%** |
| demand-welded **fraction** (lens metric) | 0.75 | 0.545 | 0.486 |
| cosmetic clock/random demoted (lever 1) | — | 76 | 76 |
| bare-clock log-sinks demoted (lever 3) | — | — | 13 |
| rung-3 transport/executor impls → seamed (lever 2b) | — | 7 | 7 |
| 0-hop seam bugs fixed (lever 2a) | — | 2 | 2 |

What each lever did, verified on the real findings:

- **Lever 1 (cosmetic):** 72 clock + 4 random `new Date().toISOString()`/template/
  record-field/`() => clock` thunk values left the demand subset (`-cosmetic`,
  still welded *class* but `demand=false`). The dominant H1 noise category, gone.
- **Lever 2b (rung-3):** 7 leaves correctly reclassified seamed — `impl-interface:
  Executor` (sandbox `LocalCommandExecutor`), `ExchangeTokenFetch`, 3×
  `NotionHttpTransport`, 2× github runners. **Guardrail held:** the genuine bare
  globals (`google-workspace-rest-client` fetch, `store.ts` fetch, OpenAI clients,
  `control-auto-commit` spawn) stayed welded+demand.
- **Lever 2a (0-hop bugs):** `slack-search-public.ts:129` (ternary factory) and
  `github-app-installations.ts:107` (`input.now ??` arrow default) now seamed.
- **Lever 3 (one-hop):** the bare-`Date.now()`/`new Date()` tail split by
  dataflow. A clock that feeds **timing arithmetic/relational** logic
  (`deadline - Date.now()`, `cachedUntil > Date.now()`, `Date.now() + ttl`,
  `Date.now()/1000`) — directly or through a local binding (`const startedAt =
  Date.now()` later used in `Date.now() - startedAt`) — **stays a demand weld**;
  one that flows only to a record/log sink (`const now = Date.now(); rec.at =
  now`, `getTimestampPrefix(new Date())`, `"at " + Date.now()` concat) is demoted
  (`-logsink`). 13 demoted; recall-checked — none were genuine timing (an early
  `+`-exclusion bug that mis-demoted 3 deadline/TTL computations was caught and
  fixed: numeric `Date.now() + ttl` is timing, only a string operand is concat).

**The lens metric dropped 0.75→0.486 — not a regression.** It reflects ceal being
*more* DI-disciplined than the leaf model saw (71 seamed demand boundaries vs 58)
once transport/factory seams resolve and clock noise leaves the denominator.
Precision — the *useful-output* metric — is what rose: ~32%→~88%.

**Precision/recall trade:** lever 3 is deliberately precision-favoring — ~13
ambiguous clock anchors (e.g. `const startedAt = Date.now()` whose elapsed math
runs on a *field* copy) demote even though some are arguably genuine. For a
backlog-finder, a trustworthy top-of-list beats catching every weld. The residual
~12% noise is the no-op `setInterval`, a best-effort `taskkill`, and two
`(Date.now()/1000).toFixed()` timestamps that the `/` arithmetic keeps.

**Net:** `pry map`'s welded-at-demand backlog on ceal is now ~88% genuine,
actionable failure-injection gaps — the gate's "reliably useful" bar, met.

## Cross-corpus: cautilus (JS) — does ~88% hold? (2026-06-14)

First test outside ceal, enabled by the JS frontend (`is_source` now accepts
`.mjs`/`.cjs`/`.js`, parsed with the same TS-superset grammar). **Corpus:**
cautilus `3027ba4` `scripts/` — 143 files, all tracked `.mjs` (cautilus is a Go
project; its
JS is build/release/eval **automation**, a deliberately different shape from
ceal's DI-disciplined agent runtime). 546 boundaries; **92 demand-welds**, hand-
labeled as a **full census** (every finding read or deterministically classified;
the 5 FALSE-WELDs and all 28 clocks are exact, ~29 of 62 subprocess are
shape-extrapolated from a verified global-callee census + 33 spot-reads).

| kind | total | genuine | false-weld | cosmetic | precision |
|---|---|---|---|---|---|
| subprocess | 62 | 57 | 5 | 0 | 92% |
| clock | 28 | 5 | 0 | 23 | 18% |
| network | 2 | 2 | 0 | 0 | 100% |
| **demand-welded** | **92** | **64** | **5** | **23** | **~70%** |

**ceal's ~88% does NOT directly transfer — cautilus ships at ~70% raw.** But H1's
*second clause holds again*: the 30% noise is **two nameable, cheap-to-filter
classes**, and after filtering, cautilus precision ≈ ceal's:

1. **Duration-record clock — 23 (25% of all demand-welds).** `const started =
   Date.now(); … const durationMs = Date.now() - started;` where `durationMs`
   only flows to a recorded field / log / `metrics.duration_ms` — never a control
   branch. **This is a lever-3 *over-keep*:** lever 3 treats arithmetic as control,
   but `now - start` feeding a *recorded* elapsed is a display value, not a
   deadline. ceal didn't surface this because its cosmetic clocks were record
   *fields* (`created_at: new Date().toISOString()`, caught by lever 1); cautilus's
   are *subtractions* (caught by neither filter). *Next lever (the high-leverage
   one): a duration-record sink filter — a clock in bare subtraction (`now - X`,
   clock as minuend) whose result is assigned/logged/returned and never feeds a
   relational is cosmetic. Must KEEP ceal's genuine timing (`X > Date.now()`
   relational, `Date.now() + ttl` addition, `deadline - Date.now()` clock-as-
   subtrahend) — that distinction is the recall guard, validate on both corpora.*
2. **Injected-callee subprocess — 5. ✅ FIXED (commit `2ba9538`).** `spawn("git"/
   "sh"/"glow", …)` where the enclosing fn takes `spawn = spawnSync` as a default
   param (`preview-markdown.mjs` ×4 — a fully DI'd file pry mislabeled entirely —
   + `run-verify.mjs` ×1). pry's seam checks covered the injected *receiver*
   (`receiver-param-injected`) and the injected *executable arg*
   (`exe-param-injected`) but **not the injected *callee identity***. Deterministic
   census: exactly 5/62. Now: a global_call subprocess/network callee that resolves
   to an enclosing param → Seamed (`callee-param-injected`), the same rung the
   receiver/executable checks implement. cautilus demand-welded **92 → 87**; ceal
   `.ts` unchanged (0 hits — no regression); ceal's own `.mjs` gained 2 correct
   seams.

Curated precision climbs the same way ceal's did: **raw ~70% → injected-callee
fixed → ~74% (64/87) → after the duration-record filter (the remaining lever)
~93%+ (64/64), essentially all-genuine.** The genuine 64 are exactly pry's thesis:
inline `spawnSync`/`execFileSync` on git/codex/claude/go orchestration with
`status !== 0` / ENOENT / `result.error` handling (57), real timeouts that kill or
reject a child (`setTimeout(…→child.kill)`, 5 clock), and bare `fetch` /
`new WebSocket` (2). **Verdict: the thesis generalizes — the genuine subset is real
and dominant once two corpus-specific noise classes are filtered — but pry as
*shipped* is corpus-sensitive (70% here vs 88% on ceal). Injected-callee is now
fixed; the duration-record clock filter is the remaining (high-leverage) lever.**

**The duration-record lever — why it's deferred, and its design.** It is *not* a
simple filter: lever 3 deliberately keeps `Date.now() - started` arithmetic as a
demand weld (the `elapsed()` case in `lever3_clock_timing_vs_logsink`), on the
theory arithmetic = control. cautilus shows that's an *over-keep* — `Date.now() -
started` feeding a **recorded** `durationMs` is cosmetic. Separating the two needs
a **sink hop**: demote a clock subtraction whose result flows only to a field /
log / return / metric, but KEEP it when the difference feeds a relational/branch
(`if (Date.now() - started > timeout)`). The recall guard is ceal's genuine
timing, which must survive: `X > Date.now()` (relational), `Date.now() + ttl`
(addition), `deadline - Date.now()` (clock as *subtrahend*, not minuend). Implement
with bi-corpus validation (cautilus precision ↑, ceal recall = no genuine demoted)
before committing — same discipline as lever 3's `+`-exclusion fix.

## After the duration-record lever (implemented 2026-06-14)

Built in `src/classify.rs` (`clock_subtraction_minuend` + `value_reaches_control` +
the refined `clock_binding_is_control`/`clock_is_logsink`); `lever3_clock_timing_vs_logsink`
revised, full suite green, output byte-deterministic. The rule: a clock that is the
**minuend** of a `-` (`Date.now() - started`) is a duration; demoted (`-logsink`)
when its result flows only to a field/log/return/call-arg sink, KEPT when it feeds a
relational/branch. The three recall guards never enter the minuend path —
`X > Date.now()` (relational), `Date.now() + ttl` (addition), `deadline - Date.now()`
(clock as *subtrahend*) all stay. The `elapsed()` expectation flipped: a *returned*
bare duration is now a record sink (both the `Date.now() - startedAt` read and the
`startedAt` anchor demote).

| corpus | demand-welded before | after | precision before | **after** |
| --- | --- | --- | --- | --- |
| cautilus (`scripts/`) | 87 | **66** | 64/87 ≈ 74% | **64/66 ≈ 97%** |
| ceal (`packages/`) | 71 | **68** | ~88% | **precision ↑** (3 FPs removed) |

- **cautilus: 21 duration-records demoted** (full census, `diff` of demand-welded
  clocks) — every one a `const started = Date.now(); … Date.now() - started` whose
  result feeds `codexRuntime(options, durationMs)` / `formatDuration(elapsed)` /
  `completedPhaseResult(…, elapsed, …)` / a record field. The 7 clocks that remain are
  **all `timer-global`** (setTimeout/setInterval) — zero `Date.now()`/`new Date()`
  reads left, so no duration-record was missed and no genuine timer was touched. The 2
  non-genuine residual are the no-op `setInterval`/heartbeat timers (a separate noise
  class this lever does not target). Precision **74% → 97%**, exceeding the ~93% target.
- **ceal recall held — and it was a precision gain.** Exactly 3 clocks demoted, every
  one a *log-duration*, not timing: `agent-runner-support.ts:573`
  (`logToolExecutionResult(…, durationMs, …)`), `slack-message-history.ts:155/173`
  (`logBackfillComplete(totalMessages, Date.now() - startTime)`). These were
  false-positives the prior census counted as genuine; demoting them raises ceal
  precision. Every genuine ceal timing (`>= waitMs`, `> LOCK_STALE_MS`, `expires > now`,
  `Date.now()+reserve >= deadline`, `Date.now()/1000`) stayed a demand weld.
- **Class counts unchanged** (the filter flips `demand`, not `class`): ceal
  `total_boundaries` 900, `welded` 826, `by_kind.clock.welded` 131 byte-for-byte;
  fixture `fixtures/ceal-ts-map.summary.json` re-frozen for the demand-subset delta
  only (145→142, welded 71→68, lens 0.5→0.4892).

**Net: the thesis generalizes _and_ ships precise.** Both corpus-specific noise classes
(injected-callee, duration-record) are now filtered; cautilus matches ceal's quality
band (97% / ~88%+) rather than the raw 70%. The remaining residual on both corpora is
timer-global noise, a smaller, named, lower-leverage class.

**Known limitations (dormant — fresh-eye critique, 0 sites in either corpus).** The
sink hop is precision-favoring with three latent recall holes, all requiring an
unusual shape not present in cautilus/ceal: (W1) an elapsed duration fed directly to a
timer as the delay (`setTimeout(fn, Date.now() - start)`) demotes, though the realistic
scheduling shape `deadline - Date.now()` is clock-as-subtrahend and already kept; (W2) a
duration via plain (non-`const`) assignment then compared (`let d; d = Date.now()-s;
if (d>x)`) — only `variable_declarator` hops, not `assignment_expression`; (W3) a duration
written to a field then compared via that field — needs member-alias tracking. Promote
these to filters only if a third corpus surfaces them. (A self-referential-declarator
stack overflow the critique also found was fixed, not deferred — `MAX_BINDING_HOPS`.)

## Caveats

- **cautilus is a single second corpus, and an automation one** — its 67%
  subprocess mix is why raw precision (70%) beats ceal's raw (32%) despite no new
  levers (subprocess is ~92% genuine; ceal's clock-heavy mix was mostly cosmetic).
  A third corpus with a different mix could shift the picture again. The
  injected-callee lever (`2ba9538`) and the duration-record lever (this run, see
  "After the duration-record lever") are both implemented and bi-corpus recall-validated.
- Clock figures are a 32/135 (24%) sample extrapolation, not a census; non-clock
  is a full census. The ~32%/~71%/~80% line should be read ±a few points.
- Single corpus (ceal), which is DI-disciplined — a welded-at-demand repo
  (0%-injection; Run 6's broad market) may shift the cosmetic/genuine mix. H3
  (broad-market value test) remains the complementary unrun gate.
- "Genuine" here = *structural* testability gap. Whether the author would *act* on
  each (wantedness, the (c) axis) is not measured — that needs author judgment or
  H4 (end-to-end one-example proof).

- Clock figures are a 32/135 (24%) sample extrapolation, not a census; non-clock
  is a full census. The ~32%/~71%/~80% line should be read ±a few points.
- Single corpus (ceal), which is DI-disciplined — a welded-at-demand repo
  (0%-injection; Run 6's broad market) may shift the cosmetic/genuine mix. H3
  (broad-market value test) remains the complementary unrun gate.
- "Genuine" here = *structural* testability gap. Whether the author would *act* on
  each (wantedness, the (c) axis) is not measured — that needs author judgment or
  H4 (end-to-end one-example proof).
