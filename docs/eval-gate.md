# Eval Gate — H3 broad-market precision (first off-corca evidence)

The result doc for the finding-eval harness ([`spec-eval-harness.md`](spec-eval-harness.md)).
Sibling to [`precision-gate.md`](precision-gate.md) (the hand-validated H1 result on
corca's own repos) — this generalizes that to **independent, third-party,
application-shaped OSS**, the population pry actually deploys onto (E3).

> **Status: the H3 gate is OPENED, not CLOSED.** Harness proven end-to-end on 4
> third-party repos + first off-corca precision points. It does **not** close the
> gate: per-repo precision is high-variance (43–80%), the slate is all
> welded-end (no DI-disciplined exemplar yet), and the held-out split is unrun.
> Closing needs the pre-registered target (dev 5 / held-out 10, SC2).
>
> **Numbers are panel-labeled (3 same-model coding-subagent personas), now
> human-calibrated (E4): 15/17 (88%) agreement on a stratified blind sample, and
> the *only* disagreements are the panel over-calling clock *timers* as GENUINE.**
> So the headline (network+subprocess 100%, ex-tail 89.3%) is human-validated; only
> the already-tiny clock-genuine is slightly inflated (true ≈3/130). See **Human
> calibration** below. Still **OPENED, not CLOSED**: the held-out arm + a
> DI-disciplined exemplar are unrun.

## E9 Tier-1 enrichment — does welded-at-demand predict defects? (쟁점 4 + 쟁점 2)

> **VERDICT: FALSIFIED for this corpus.** Across **25 third-party TS/JS apps**,
> welded-at-demand sites are **NOT** meaningfully bugfix-enriched vs other boundary
> sites under the pre-registered matched comparison: **matched ratio 1.05, 95% CI
> [0.96, 1.18]** — which trips the pre-registered FALSIFIER (≤1.1 OR CI-lower≤1.0).
> This is the **directly-observed enrichment** result (nose's G1 analog), the
> robust deliverable this goal set out to test. It is reported honestly as a valid
> negative, not massaged toward the thesis (the nose `rate-match ≠ precision` /
> retraction discipline).

> **Power caveat (don't over-read the negative).** The pre-registered bugfix
> predicate is broad — its message regex matches **~48% of all commits** (e.g.
> 4433/9226 in outline) — so the per-line "bugfix-touched" base rate is high
> (~40%) in *both* arms, which structurally compresses the achievable ratio toward
> 1.0. A 1.05 against a ~48% base rate is a **structurally weak test**: it cleanly
> rules out a *large* enrichment (the ≥1.5 GO effect this goal set out to find),
> but it does not finely resolve a *small* one. The regex is frozen/pre-registered
> (it cannot be tuned post hoc); this is disclosed as an interpretation ceiling,
> not a fixable defect. The negative is "no actionable bug-prediction signal," not
> "provably zero correlation."

**Pre-registration (honesty gate).** The split, the matched-comparison
denominator, the bugfix-set numerator, the two-sided floor, and the bootstrap CI
were all frozen in [`harness/fixtures/eval/preregistration.md`](../harness/fixtures/eval/preregistration.md)
+ `harness/config.py` **before** this number existed. Git-provable:
`git merge-base --is-ancestor 47eeb633 <this-commit>` (the prereg commit precedes
the first enrichment-number commit). Signal arm = welded-at-demand
(`class=welded AND demand`); PRIMARY control = "rest" (seamed | welded-not-demand).
Matched on (file-churn × site-size) terciles, direct standardization; 95% CI =
repo-cluster bootstrap (B=2000, seed=0). **GO** = matched≥1.5 AND CI-lower>1.0;
**FALSIFIED** = matched≤1.1 OR CI-lower≤1.0.

| arm set | repos | wd bugfix-rate | ctrl rate | raw | **matched** | 95% CI | strata u/d | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **corpus** | 25 | 39.4% (2111/5364) | 37.9% (6683/17636) | 1.04 | **1.05** | [0.96, 1.18] | 9/0 | **FALSIFIED** |
| dev | 5 | 53.9% (590/1094) | 58.0% (2249/3879) | 0.93 | **0.93** | [0.79, 1.04] | 9/0 | FALSIFIED |
| **heldout** | 20 | 35.6% (1521/4270) | 32.2% (4434/13757) | 1.11 | **1.11** | [1.02, 1.29] | 9/0 | WEAK |

**Generalization (쟁점 2).** Reported `dev` vs `heldout` separately; no threshold
was tuned (none needed — the result is below every GO bar, so there was nothing to
tune on `dev`). The held-out arm shows a **weak ~11% effect** whose CI excludes 1.0
([1.02, 1.29]) but lands **far below the pre-registered "signal real" bar (1.5)** —
a statistically-detectable but practically-negligible tendency. dev (the 4
disciplined H3 seeds + medusa) is at 0.93 (below 1). The signal does **not**
generalize to a level worth acting on. **To be explicit and not bury it:** the
held-out arm is *not refuted* — its CI excludes 1.0 — so "welded-at-demand carries
a small bug-correlation" is a **hypothesis left standing, just far below the
actionable bar**, not a hypothesis the held-out arm disproves. The *corpus*
headline (the pre-registered primary) is FALSIFIED; the held-out weak-positive is
the honest asterisk on it.

**Per-repo distribution (Simpson's-paradox guard).** Of 25 eligible repos
(≥20/arm), **17/25 (68%) have a per-repo ratio > 1** — so the *direction* is mildly
positive — but the *magnitude* is small and the largest repos drag the matched
pool to ~1.0. Range 0.67 (twenty) → 2.23 (linkwarden); the high-ratio repos
(linkwarden 2.23, formbricks 2.09, vendure 1.49, nocodb 1.47) are smaller, while
the biggest finding-pools sit near or below 1.0 (twenty 0.67, n8n 1.18, novu 1.20,
calcom 1.09, librechat 1.06, medusa 0.94, strapi 0.99, midday 0.71). The guard's
threshold *passes* (≥60% repos >1) but the matched pooled effect is negligible —
direction without magnitude.

**Secondary controls (pre-registered breakdowns).** vs **seamed-only**: matched
**0.91** (wd 39.4% vs 43.7%; welded-at-demand is, if anything, *less* bugfix-touched
than the thin seamed arm, n=478) → FALSIFIED. vs **welded-not-demand-only**:
matched **1.05** → FALSIFIED. Neither component control rescues the thesis. (The
seamed-only arm is thin — see [`preregistration.md`](../harness/fixtures/eval/preregistration.md)
Amendment A — which is exactly why "rest" is the primary, well-powered control.)

**What this means.** pry's structural welded-at-demand signal is a *testability*
classifier; this result says it is **not also a defect predictor** on a broad
app corpus — the two are decoupled here. The shipped binary's framing stays
correct and unchanged: **"risk ranking, NOT a bug list."** The precision-lever
march (lever #4) was premised on this enrichment holding; it does not, so further
precision polish is **not** justified by a bug-prediction payoff (it may still be
justified by the testability-surface product goal, a separate question).

**Standing non-claims (restated).** This is a correlation measurement, never
causal; one-directional (a seamed-no-bugfix site is not "safe"); the file-KIND
residual confound is named-not-neutralized; last-touch blame is a conservative
lower-bound proxy; the broad bugfix predicate is a base-rate ceiling (above);
**frontend and backend boundary findings are pooled, un-stratified by tier**, so
frontend boundary calls (mostly UI fetch) dilute backend error-path density (an
external-validity caveat that works *against* finding a signal); no SZZ Tier 2, no
per-repo precision panel on heldout, no live/release/outbound proof. The FALSIFIED
outcome is the honest result, not a failure to report.

**Python branch ((b)-gate).** The 8 non-glue Python apps were run through the
analyzer-free (b)-gate lens (sequenced after this verdict). Result: **KILL** —
demand-subset welded-fraction **0.906** (out of band [0.15,0.85], decided 0.742,
not mute): idiomatic Python app code reaches boundaries module-directly, so the
welded/seamed lens is saturated (only mealie, DI-explicit, discriminates). **No
Python frontend was built** — both because the (b)-gate KILLs it and because
folding Python into a FALSIFIED enrichment would add nothing. Full record:
[`kill-gate.md`](kill-gate.md) Run 7.

**Reproduce.** `python3 harness/sweep.py --corpus` (deterministic; clones at pinned
commits) → `python3 harness/enrichment.py` (re-derives every number above from the
frozen sweep records; seeded bootstrap is byte-reproducible). Note: `calcom` =
`calcom/cal.com`, since rebranded `cal.diy` on GitHub — the pinned commit + clone
URL track the rename.

## The slate (dev; pinned, frozen)

Third-party app-shaped OSS (agent/LLM/automation runtimes), `pry map` at the
pinned commit. None is a general-purpose library; none is a corca repo (E3/E6).

| repo | commit | files | demand-welded | clock-share | role |
|---|---|---|---|---|---|
| outline | `d85ead5` | 1363 | 109 | 52% | dev |
| flowise | `f4e2794` | 1324 | 152 | 44% | dev |
| continue | `eaa23c5` | 1176 | 292 | 56% | dev |
| librechat | `8154a31` | 1425 | 386 | 58% | dev |

Per PQ3, non-clock demand-welds were a full census; clock demand-welds a
deterministic ≥25% (`ceil`) stride sample; a 10-finding (or pool-capped) sample
of pry-**seamed** findings was mixed in blind as a false-seam probe (E4). Labeled
worklist = **589 findings** (556 demand-weld graded + 33 seamed-control).

**Spectrum gap (carried from PQ1):** all four cluster at the welded / low-DI end
(the H3 *target* population, and a useful refutation of "mature ⇒ DI-disciplined").
The slate still lacks a **DI-disciplined exemplar** (high clock-injection, more
genuinely-seamed boundaries) — the end where precision should be *lower* because
more welds are truly false. That repo is the missing dev #5 + the held-out arm.

## Headline — pry's core signal generalizes; a cosmetic tail drags the pooled number

| stratum | genuine / decided | precision | 95% CI |
|---|---|---|---|
| **network + subprocess (pry's core)** | **261 / 261** | **100.0%** | [98.5, 100] |
| all **except** clock + random | 310 / 347 | **89.3%** | [85.6, 92.2] |
| **clock + random (cosmetic tail)** | 5 / 209 | **2.4%** | [1.0, 5.5] |
| raw pooled (all demand-welds) | 315 / 556 | 56.7% | [52.5, 60.7] |

Two findings, both decisive:

1. **The core thesis holds off-corca.** Every one of 261 `network`/`subprocess`
   demand-welds across 4 independent repos is GENUINE (100%), and the whole
   non-cosmetic surface is **89.3% ≈ the ceal hand-validation (88%)**. pry's
   welded-at-demand signal is **not a *ceal* artifact** (it generalizes off-corca
   on the welded-end population). *Two caveats on the comparison:* (a) ceal's 88%
   was measured **after** the rung-3 false-weld filter, whereas this 89.3% still
   **includes** rung-3 false-welds (lever #4, unbuilt) — so the eval number is, if
   anything, *conservative* vs ceal; (b) all 4 repos are welded-end (low-DI), so
   this shows generalization to that population, not yet to the DI-disciplined end
   (where precision should be lower — that is the held-out / spectrum gap below).
2. **The cosmetic clock/random tail is the entire precision drag.** It is 209/556
   (38%) of the raw backlog at **2.4%** genuine. The raw pooled 56.7% is almost
   entirely this tail pulling down a near-perfect core — and it is exactly what
   pry's existing filters are *supposed* to catch (and the F15 skill already ranks
   last). This is a filter gap, not a thesis problem.

The raw pooled figure has a **clustering caveat**: per-repo precision is 43–80%
(below), so the pooled Wilson CI understates between-repo variance. Read the
strata and per-kind tables, not the single pooled number.

## Per-repo precision (demand-weld, Wilson 95% CI)

| repo | genuine / decided | precision | 95% CI |
|---|---|---|---|
| outline | 42 / 67 | 62.7% | [50.7, 73.3] |
| flowise | 82 / 102 | 80.4% | [71.6, 86.9] |
| continue | 73 / 169 | 43.2% | [36.0, 50.7] |
| librechat | 118 / 218 | 54.1% | [47.5, 60.6] |

Variance is driven by backlog *composition*: continue's low number is its huge
clock/random tail (62/169) + an llm crater (below); flowise is high because it
barely DI's its clients (almost everything is a real inline weld).

## Per-kind precision (pooled, Wilson 95% CI)

| kind | genuine / decided | precision | 95% CI | note |
|---|---|---|---|---|
| network | 196 / 196 | 100.0% | [98.1, 100] | bare `fetch`/`axios`, no transport seam |
| subprocess | 65 / 65 | 100.0% | [94.4, 100] | `execSync`/`spawn`/`execFileSync` |
| db | 20 / 23 | 87.0% | [67.9, 95.5] | inline `new Redis/Pool/MongoClient` |
| llm | 29 / 63 | 46.0% | [34.3, 58.2] | **corpus-split** — see taxonomy #3/#4 |
| clock | 5 / 130 | 3.8% | [1.7, 8.7] | cosmetic-clock filter far too weak |
| random | 0 / 79 | 0.0% | [0.0, 4.6] | no failure worth injecting, anywhere |

## Noise taxonomy → next levers (SC5 / AC5)

Ranked by lift. Each is a dev-time lever gated against the frozen labelset (E8) —
recompute precision/filter-recall from the labels, no new LLM call.

1. **`random` is never a genuine weld (0/79). — ✓ BUILT 2026-06-15.** Across all 4
   repos, every `random` demand-weld is a cosmetic id/nonce/IV/jitter/shuffle value.
   **Lever: a cosmetic-random filter** — `demote_welded_random` in `src/classify.rs`,
   applied at every random call form (`Math.random` builtin, `crypto.*` ns-call):
   welded `random` drops out of `demand` by default (an RNG has no failure to inject;
   its only test concern is determinism, met by a seeded/fake source). *Verified by
   the build:* re-derived dev precision **56.7% → 66.0%**, **0/79 genuine lost** —
   the projection below, confirmed exactly; ceal demand-weld 68→67; `random_is_never_demand`
   test green. *Highest-lift, lowest-risk lever in the repo; it was the first built.*
2. **`clock` is almost never genuine (5/130 = 3.8%, true ≈3/130 post-calibration).**
   The existing cosmetic-clock filter under-catches by an order of magnitude. The
   genuine cases are token-expiry **comparisons** driving a security branch
   (`expiresAt < new Date()` → throw); the principle (operator-confirmed in
   calibration) is **fake timers are the seam for time** — `vi.useFakeTimers()` /
   `setSystemTime()` control global `setTimeout`/`Date` with no code seam, so a
   welded timer doesn't block testing the way a welded network *failure* does.
   **Lever: demote timers (`setTimeout`/`setInterval`) and record-`Date`
   aggressively — even on retry/error paths — keeping only clock reads that feed a
   control-flow comparison.** *Calibration sharpened this:* the panel itself
   **over-called retry/timeout `setTimeout`s as GENUINE** (the 2 of 2 calibration
   disagreements were exactly this — notion retry-wait, redis ping-timeout), so the
   panel's 5/130 is an over-count and the timer-demotion is even more justified.
   **⚠ Slice 2 REFRAMED this lever (do not just demote more) — ✓ SHIPPED 2026-06-15.**
   The filter-recall arm found the opposite failure dominates: the *existing*
   `clock_is_logsink`/cosmetic filter already **over-demoted** genuine clock (16/143 =
   11.2% of the demoted pool), because it misread **DB-query date bounds** (`where
   expiresAt < new Date()`) and **date-math thresholds** (`subMinutes(new Date(),5)` →
   later compared) as record-sinks. So lever #3 became a **discrimination fix**
   (`clock_is_demand_control` in `src/classify.rs`): before the cosmetic/logsink
   demotion, RESCUE a clock that (a) sits under a query operator key (`[Op.lt]`/`$lte`/
   `$gte`, bare or via a `const`) — Rescue A; or (b) was DERIVED through a date helper /
   arithmetic (`subMinutes(new Date(),5)`, `new Date(Date.now()-WEEK)`) whose result
   reaches a comparison — Rescue B. The rescue is **purely additive** (it only ever
   *prevents* a demotion), so no kept finding can be lost. **Result: demoted-pool
   GENUINE misses 16 → 5 (11 rescued), 0 precision-damage, 0 lost-recall**, re-derived
   against the frozen oracle by `python3 harness/filter_recall.py --remap`. The 5
   residual are 3 bare record timestamps (throttle `lastRan = Date.now()`, the
   flowise:788 caveat / R3 timers) + 2 hard-tail shapes (equality on `.getMonth()`,
   clock into a date-range lib call) — left demoted, precision-favoring. Two
   precision-damage shapes the `--remap` gate surfaced and the fix excludes: a
   serialized-then-concatenated clock (`Date.now().toString()`), and a BARE `new
   Date()` fallback merely clamped before storage (`importers.js` — B requires the
   clock be genuinely date-derived). ceal zero-delta (no query/threshold clocks in its
   demoted pool; verified at pinned cdd31884).
3. **Test-file leak: `.vitest.ts` (and `manual-testing-sandbox/`, `*-sol.ts`). — ✓
   BUILT 2026-06-15 (default-stem part).** pry's `is_source` dropped `.test.`/`.spec.`
   but not `.vitest.`; continue's llm crater (2/35) is largely its `*.vitest.ts`
   suites, where `fetch` is mock-injected (FALSE-WELD). **Lever: extend the test-file
   heuristic** — `is_source` (`src/main.rs:63`) now also drops `.vitest.`/`.e2e.`
   stems. *Scope split (verified):* the default heuristic owns only the **conventional
   stems** = **25** demand-weld findings (all `.vitest.` on this corpus; `.e2e.` is
   added as a forward-looking convention, 0 hits here) → **66.0% → 69.7%, 0 genuine
   lost** (the 25 are 21 FALSE-WELD + 4 COSMETIC). The
   remaining **4** (`manual-testing-sandbox/` + `*-sol.ts`) are **repo `.pryignore`
   scope (E7), not the default** — they are what takes the lumped number to 70.3%, so
   the binary's honest default lift is 69.7%, not 70.3%. (Exclude is off during eval,
   so all 29 count against pry in the raw pool; only 25 are the default's to fix.)
4. **Rung-3 stage-2 — REOPEN (two faces, both calibration-confirmed).**
   (a) *Injected transport (precision):* continue's production `openai-adapters`
   calls sit behind an injectable `customFetch(config.requestOptions)` one hop up —
   the transport/executor-wrapper gap the roadmap *deferred "until a corpus surfaces
   it"*. continue surfaces it materially (not material on ceal).
   (b) *Interface-impl OVER-seaming (recall):* the inverse and more concerning —
   pry's rung-3 form-A marks a welded `fetch` SEAMED whenever its class
   `implements` an injectable interface (`ContinueServerClient implements
   IContinueServerClient`). But the interface seam only makes *consumers* testable;
   **the impl's own error handling on the welded boundary stays un-testable** (e.g.
   `getConfig`'s `if (!response.ok) throw` — you can't inject the fetch failure into
   the real impl). Human calibration confirmed this directly: 2/3 sampled
   pry-seamed findings were real welds pry false-seamed via exactly this rule.
   **Fix: rung-3 form-A should not blanket-seam a boundary whose impl has its own
   error handling on it.** Needs cross-file analysis + risks false-seaming, so gate
   any rule hard against this labelset + the Slice-2 recall arm.
5. **Client construction is double-counted (`new OpenAI()` + `.create()`).**
   pry flags both the inline client construction *and* catalogued method calls on
   the same client → the same welded client counts twice. **Lever: treat the
   construction as the single "welded-client origin" (the seam-decision point:
   inline `new` = welded, injected param/factory = seamed) and DEDUP the downstream
   method finding.** Do **not** chase per-method catalog entries (a losing game);
   keep a few high-value method patterns (`.create`) only as a fallback for
   import-singleton clients with no local `new`. (Operator-confirmed in calibration;
   the `new OpenAI()` line is not "cosmetic" — it is where injectability is decided.)

## Projected lever impact (dev, against the frozen labelset)

What each lever buys, computed by applying it to the 4 frozen labelsets (demote =
remove from the demand-welded decided set). "EXACT" = the lever only touches
findings already labeled, so both the precision lift and the recall cost are
directly read off the labels. "CEILING" = assumes a *perfect* syntactic filter
(real ones are imperfect) — an upper bound, not a promise.

| applied lever | precision | genuine welds lost | basis |
|---|---|---|---|
| baseline (existing pry) | 315/556 = **56.7%** | — | — |
| + cosmetic-random (drop 79 `random`) — **✓ BUILT** | 315/477 = **66.0%** | **0 / 79** | EXACT (measured) |
| + test-file heuristic — default stems (drop 25 `.vitest`; `.e2e` forward-looking, 0 on this corpus) — **✓ BUILT** | 315/452 = **69.7%** | **0 / 25** | EXACT (measured) |
| + repo `.pryignore` (drop 4 `sandbox`/`-sol`; E7, not the default) | 315/448 = **70.3%** | **0 / 4** | EXACT (repo scope) |
| + clock control-vs-record **discrimination** (lever #3) — **✓ BUILT** | precision held (rescue only) | **recall ↑: demoted misses 16 → 5** | measured (`--remap`) |
| + rung-3 / remaining false-welds (drop 11) | 315/318 = **99.1%** | 0 | CEILING |

> ⚠ The old "stronger cosmetic-clock" CEILING row assumed a *perfect* filter that
> drops 119 clock at 0 recall cost. **Slice 2 refuted it:** the demoted clock pool is
> already 11.2% genuine, so demoting *more* clock raises recall loss. Lever #3 shipped
> instead as a control-vs-record **discrimination fix** — it RESCUES the genuine
> shapes (demoted misses 16 → 5) rather than demoting more, and is recall-positive /
> precision-neutral by construction (it only ever prevents a demotion). See taxonomy
> #2 + the Slice 2 section.

**Across every lever, zero of the 315 genuine welds are lost** (in the labeled
set). The two EXACT levers — cosmetic-random and the test-file heuristic — are now
**both built**, lifting dev precision **56.7% → 69.7% at zero recall cost** (the
binary's honest default; the further 69.7% → 70.3% is the repo's `.pryignore` job,
not pry's default). They were *directly gate-checkable*: they only demote findings
already labeled COSMETIC/FALSE-WELD, so E5's recall condition holds on dev by
construction (no bare-pool labeling needed for *these two*). They still need the
**held-out arm** before shipping (E5/SC2) — this is the dev-side evidence, not the
ship decision. The clock/rung-3 ceilings need
real (imperfect) filters + the Slice-2 recall arm, so treat them as the prize, not a
guarantee. **Build order:** cosmetic-random **✓ done** and the test-file heuristic
**✓ done** (both 2026-06-15 — the two EXACT rows are now *measured build results*:
56.7%→66.0%→69.7%, 0 genuine lost, matching the projection); next the harder
clock/rung-3 work behind Slice 2.

## Seamed-control — a recall flag for Slice 2

The blind pry-**seamed** control sample (E4) is the false-seam probe: a pry-seamed
finding the panel relabels GENUINE = a real weld pry demoted (a recall miss).

| repo | relabeled GENUINE / control |
|---|---|
| outline | 0 / 3 |
| flowise | 7 / 10 |
| continue | 5 / 10 |
| librechat | 1 / 10 |
| **total** | **13 / 33** |

This is **noisy and concentrated** in the DI-heavy repos (flowise/continue). It is
a **flag**, not a conclusion — but **human calibration confirmed the mechanism**:
of 3 sampled pry-seamed findings, 2 (`ContinueServerClient.getConfig`/`sendFeedback`)
were real welds pry false-seamed via **rung-3 form-A interface-impl over-seaming**
(taxonomy #4b), and 1 (`http.ts` with a destructured `fetch` param) was a correct
seam. So the recall hole has a named cause, not just a count. The **rung-3** recall
hole is a *seam-side* miss (pry called a weld seamed); Slice 2 below measures the
complementary *filter-side* miss (a filter demoted a weld). Do not ship a rung-3
change before extending the recall arm to the seamed pool.

## Slice 2 — filter-recall arm (E5/SC3/AC3) — DONE 2026-06-15

**The gate's recall half.** Precision (Slice 1) asks "is a kept finding genuine?";
filter-recall asks the inverse: **did a precision filter DEMOTE a genuine weld?** The
denominator is pry's pre-demand pool, so the un-labeled part is the **demoted pool** —
class=welded, `demand=false`, in a filter-demotable kind (clock/random; the fileio/env
diagnostic swamp is excluded — it is demand=false by catalog, never demoted). The
panel labeled a **stride sample of 154** of the 733-finding demoted pool (143 clock at
~22%, 11 random control; `harness/finding_io.py emit --pool demoted`). Reconcile:
**150/154 unanimous, 4 majority, 0 ties.** Frozen to
`harness/fixtures/eval/*-barepool-labels.json`; re-derive with `python3
harness/filter_recall.py`.

**Result — the clock filters are NOT lossless; the cosmetic-random filter is.**

| pool | GENUINE (= filter-recall miss) | read as |
|---|---|---|
| demoted **clock** | **16 / 143 = 11.2%** | the cosmetic/`logsink` filter over-demotes genuine clock |
| demoted **random** | **0 / 11** | cosmetic-random is lossless (confirms lever #1, 0/79 earlier) |

Concentrated in **DB-heavy apps** (clock-only denominators): outline 7/30 (23%),
librechat 7/43 (16%) vs continue 1/51 (2%), flowise 1/19 (5%). **15 of the 16 misses
were demoted by `clock_is_logsink`** (8 `clock-inline-logsink` + 7 `builtin-inline-logsink`),
1 by cosmetic — auditable via the `pry_reason` field in each `*-barepool-labels.json`.
The named cause — clock reads that feed
**control** but in shapes the log-sink heuristic misreads as record-sinks:
- **DB-query date bounds:** `where: { expiresAt: { [Op.lt]: new Date() } }`
  (CleanupExpiredAttachmentsTask), `findOne({ displayFrom: { $lte: now } })` (banner)
  — the clock is an object-pair value, which the cosmetic `pair` rule demotes, but in
  a query it *selects/gates which rows are read or deleted*.
- **Date-math thresholds:** `subMinutes(new Date(), 5)` → later `if (lastActiveAt <
  fiveMinutesAgo)` (Team.updateActiveAt throttle) — demoted as a call argument; the
  comparison is one binding hop away through a helper the dataflow doesn't trace.
- **Window bins:** `new Date(Date.now() - WEEK)` used to bucket records.

**Population caveat (honest):** the demoted side is a 22% clock sample, so scaling to
the full 637-clock demoted pool implies **~71** genuine clock demoted (wide CI) versus
only **5** genuine clock *kept* in the demand-weld census — i.e. the clock filters keep
a small minority of genuine clock. The 95.2% "labeled-union recall" the script prints
mixes a census with a sample and reads high; the honest takeaway is **clock recall is
poor and app-shape-dependent**, not that 95% is safe.

**Gate rule (SC3).** A lever ships only if **dev precision ↑ ∧ held-out filter-recall
held** — concretely, *a new lever must not raise the demoted-pool GENUINE count*
(re-run `filter_recall.py` after applying the lever). The two EXACT levers pass
trivially: random demoted 0 genuine (0/11 here, 0/79 before); the test-file heuristic
demoted 0 genuine (0/25, demand-weld labels). **This refutes the "stronger-clock → 0
lost" CEILING below** and reshaped lever #3 (see taxonomy #2).

**Lever #3 (clock discrimination) closed the recall hole — ✓ SHIPPED 2026-06-15.**
Because lever #3 *changes pry's demand bit* (it does not just demote already-labeled
findings), the frozen-only `filter_recall.py` cannot see it — so the gate runs as
`python3 harness/filter_recall.py --remap`, which re-runs the freshly-built `pry map`
on the pinned corpus and re-joins by `file:line:col:kind` to the frozen panel labels
(the stable oracle; the `label` never moves, only pry's mechanical `demand`/`class` is
recomputed). The `--remap` run is the gate of record: **demoted-pool GENUINE misses 16
→ 5, 11 rescued, 0 precision-damage (no COSMETIC/FALSE-WELD promoted), 0 lost-recall
(no kept GENUINE demoted).** The 31 test-file labels now absent from the map are
lever #2's correct removals (R5), reported separately, not drift. The 5 residual misses
are 3 bare record timestamps (R3 throttle/timer class — kept demoted on purpose) + 2
hard-tail shapes (equality on a `.getMonth()` accessor, clock fed to a date-range lib
call). `cargo test`'s `lever3_query_bounds_and_thresholds` pins the rescue shapes + the
throttle / serialized-concat / bare-fallback negatives.

## Panel quality — and why the agreement rate is weak evidence

589 findings × 3 personas. Reconciliation: **469 unanimous (79.6%), 118 majority
(2-1), 2 tie-break, 0 arbiter, 0 undecidable.**

**Read the 79.6% agreement with strong caution — it is not 3 independent
confirmations.** Three compounding reasons, in increasing severity:

1. *Weak blinding (E4):* the worklist hides pry's verdict bit, but `source_context`
   + a taxonomy rubric let a persona reconstruct pry's rule.
2. *Same-model correlation:* all 3 personas are `claude-opus-4-8`, so their errors
   are correlated; "2/3 agree" overstates confidence.
3. ***Shared full-source access (the decisive one):*** the personas were
   explicitly allowed to open the repo files (not just the ±12-line window) to
   check for an injected seam before deciding. This was a deliberate choice for
   label **accuracy** (you often cannot tell GENUINE from FALSE-WELD without the
   constructor/imports) — but it means the three votes are **not independent at the
   evidence level**: they converge on the *same source*, so the agreement largely
   measures "one source read three times," not three independent judgments. The
   tell is in the data: **AMBIGUOUS was emitted once in 1,770 votes (0.06%)** —
   impossible for raters confined to 25 lines, expected when they read the whole
   file.

Net: the panel was optimized for per-label accuracy over vote independence, so the
agreement rate is **not** the confidence signal it looks like. The real accuracy
bound is the **human calibration** below.

The full audit trail is checked in: `harness/fixtures/eval/votes/<repo>/{pragmatic,
skeptic,neutral}.json` (each persona's label + confidence + one-clause reason) and
`continue/tiebreak.json`. The blinded worklist (the exact `source_context` shown)
is reproducible via `finding_io.py emit` against the pinned corpus.

## Human calibration (E4) — done

The operator blind-labeled a **stratified 26-finding sample** (weighted to the
contested clock/llm strata + a seamed-control recall probe), then compared to the
frozen panel labels. After R5 test-file exclusion, **17 in-scope**; full record in
`harness/fixtures/eval/calibration.json` (per-card human vs panel).

| stratum | human–panel agreement |
|---|---|
| demand-weld (precision) | **12 / 14** |
| seamed-control (recall) | **3 / 3** |
| **overall** | **15 / 17 (88%)** |

The result is strong *and* informative:

- **The headline holds under human eyes.** Every sampled `network`/`subprocess`/
  `random`/`db` and the flowise `llm` welds matched the panel. The core 100% +
  ex-tail 89.3% are human-validated.
- **The panel's *only* error is one-directional: it over-calls clock TIMERS as
  GENUINE.** Both disagreements (notion retry-wait, redis ping-timeout `setTimeout`)
  were panel=GENUINE / human=COSMETIC. So the panel's clock-genuine (5/130) is an
  over-count; true ≈3/130 — which only *strengthens* the clock lever. No other
  stratum drifts.
- **Recall hole has a named cause** (seamed-control: 2/3 false-seams from rung-3
  interface-impl over-seaming — taxonomy #4b).
- **A refined ruleset fell out** (operator-confirmed): fake-timers = the time-seam
  (timers → COSMETIC); clock *comparisons* → GENUINE; test files out of scope;
  **module-mocking ≠ a seam** (this is what makes the network 100% meaningful —
  relax it and the signal collapses); client *construction* = the welded-client
  origin (dedup, don't enumerate SDK methods); dead-code reachability is knip's job,
  not pry's (visibility-agnostic is correct).

**Caveats:** small N (17), weighted to contested strata (not a uniform statistical
bound); human and panel read the same full source, so this measures "given the same
code, does the human agree with the panel's label" — the right question for label
trust, but it does not independently re-derive recall. Session: `h3-eval-calibration`
(HITL); ruleset in `charness-artifacts/hitl/`.

## Gate status (SC2)

- **OPENED:** harness proven end-to-end (emit → 3-persona panel → reconcile →
  tie-break → freeze) on 4 independent third-party repos; first off-corca
  precision points exist; the core signal validated (100% network/subprocess,
  89.3% ex-tail ≈ ceal 88%); the next levers are named with counts.
- **DONE since:** human calibration (E4) — 15/17 (88%), headline validated, panel
  error one-directional (clock-timer over-call). See Human calibration.
- **STILL NOT CLOSED:** (a) all-welded-end slate — no DI-disciplined exemplar
  (dev #5 / spectrum gap); (b) held-out arm unrun. Close per the pre-registered
  target: **dev 5 / held-out 10** (≈15 repos), tune only on dev, held-out is the
  generalization gate.

## Reproduce

The frozen labelsets are the ground truth (E8: LLM once → deterministic forever).
Every label is contestable via its `file:line:kind` against the pinned corpus
(AC2); each carries its 3 persona votes + reconciled decision.

```sh
# frozen labelsets (checked in; reconciled label + 3 votes + decision per finding):
harness/fixtures/eval/{outline,flowise,continue,librechat}-labels.json
# per-persona audit trail (label + confidence + reason, + the one tie-break round):
harness/fixtures/eval/votes/<repo>/{pragmatic,skeptic,neutral}.json

# re-derive any number above from the frozen labels (no LLM):
python3 - <<'PY'
import json,glob
g=d=0
for f in glob.glob("harness/fixtures/eval/*-labels.json"):
    for v in json.load(open(f))["labels"].values():
        if v["group"]!="demand_weld": continue
        if v["label"]!="AMBIGUOUS": d+=1
        if v["label"]=="GENUINE": g+=1
print(f"pooled demand-weld precision: {g}/{d} = {g/d:.1%}")
PY

# regenerate a worklist from a fresh pry map (corpus pinned at the commit above):
pry map <repo> > map.json
python3 harness/finding_io.py emit --map map.json --repo <repo> --out worklist.json
```

## Provenance

- Panel model: `claude-opus-4-8` (3 prompt-differentiated personas: pragmatic /
  skeptic / neutral-no-taxonomy, E4/PQ2). Rubric hash `35b8e3a960452ccc`.
- Tie-break: 1 judge pass (2 findings, both `manual-testing-sandbox` stubs → COSMETIC).
- Harness: `harness/finding_io.py` v0.1.0 (mechanical; no LLM/credential, E2/SC4).
- Corpus pinned at the commits above (cloned default-branch HEADs, which matched
  the PQ1 scout commits exactly — zero drift).
