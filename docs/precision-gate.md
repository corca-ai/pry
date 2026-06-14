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

## After levers 1+2 (implemented 2026-06-14, this run)

Levers 1 (cosmetic filter) + 2 (rung-3 + the 2 0-hop bug fixes) are **built** in
`src/classify.rs` (tests in `tests/classify_smoke.rs::precision_filters_and_rung3`,
green; output still byte-deterministic). Re-run on ceal `cdd31884`:

| metric | before | after 1+2 |
| --- | --- | --- |
| demand-welded **count** | 174 | **85** |
| demand-welded **precision** (re-labeled, 28-sample) | ~32% | **~70%** (±5) |
| demand-welded **fraction** (lens metric) | 0.75 | 0.545 |
| cosmetic clock/random demoted out of demand | — | 76 |
| rung-3 transport/executor impls → seamed | — | 7 |
| 0-hop seam bugs fixed (`input.now ??`, `input.clientFactory ?`) | — | 2 |

What each lever did, verified on the real findings:

- **Lever 1 (cosmetic):** 72 clock + 4 random `new Date().toISOString()`/template/
  record-field values left the demand subset (`-cosmetic` reason, still welded
  *class* but `demand=false`). The dominant noise category named by H1 is gone.
- **Lever 2b (rung-3):** 7 leaves correctly reclassified seamed — `impl-interface:
  Executor` (sandbox `LocalCommandExecutor`), `ExchangeTokenFetch`, 3×
  `NotionHttpTransport`, 2× github runners. **Guardrail held:** the genuine bare
  globals (`google-workspace-rest-client` fetch, `store.ts` fetch, OpenAI clients,
  `control-auto-commit` spawn) stayed welded+demand.
- **Lever 2a (0-hop bugs):** `slack-search-public.ts:129` and
  `github-app-installations.ts:107` now classify seamed.

**The lens metric dropped 0.75→0.545 — that is not a regression.** It reflects
ceal being *more* DI-disciplined than the leaf model saw (71 seamed demand
boundaries vs 58 before) once transport/factory seams resolve and cosmetic noise
leaves the denominator. Precision (the useful-output metric) is what rose: 32%→~70%.

**Residual to ~80% (deferred lever 3):** the noise is now almost entirely the
**37 bare `Date.now()`/`new Date()`** findings (`clock-inline`/`builtin-inline`,
not in a cosmetic context) — a mix of genuine timing (`deadline - Date.now()`,
`cachedUntil > Date.now()`) and uncaught logging (`const now = Date.now()`,
`getTimestampPrefix(new Date())`). Splitting them needs **one-hop dataflow**
(does the value feed a comparison/timer vs a record/log sink?), which lever 3
was scoped to and this slice deliberately did not build.

## Caveats

- Clock figures are a 32/135 (24%) sample extrapolation, not a census; non-clock
  is a full census. The ~32%/~71%/~80% line should be read ±a few points.
- Single corpus (ceal), which is DI-disciplined — a welded-at-demand repo
  (0%-injection; Run 6's broad market) may shift the cosmetic/genuine mix. H3
  (broad-market value test) remains the complementary unrun gate.
- "Genuine" here = *structural* testability gap. Whether the author would *act* on
  each (wantedness, the (c) axis) is not measured — that needs author judgment or
  H4 (end-to-end one-example proof).
