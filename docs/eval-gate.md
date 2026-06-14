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
> **Every number here is panel-labeled (3 same-model coding-subagent personas),
> human-calibration PENDING (E4).** Same-model votes are correlated, so the panel
> can be confidently wrong; a small human-labeled calibration subset (operator's
> step) is still owed to bound the panel's own error rate. Treat these as
> provisional-but-actionable, not final.

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

1. **`random` is never a genuine weld (0/79).** Across all 4 repos, every `random`
   demand-weld is a cosmetic id/nonce/IV/jitter/shuffle value. **Lever: a
   cosmetic-random filter** (demote `random` from `demand` by default, mirroring
   the cosmetic-clock filter; surface only a narrow allowlist if one ever earns
   it). Removes 79 false positives at zero measured genuine cost. *Highest-lift,
   lowest-risk lever in the repo.*
2. **`clock` is almost never genuine (5/130 = 3.8%).** The existing cosmetic-clock
   filter under-catches by an order of magnitude on third-party code. The 5
   genuine cases are token-expiry comparisons that *drive a security branch*
   (`expiresAt < new Date()` → throw). **Lever: strengthen the cosmetic-clock
   filter** to demote timers/`setTimeout`/record-`Date` aggressively, keeping only
   clock reads that feed a control-flow comparison. Removes ~125 false positives.
3. **Test-file leak: `.vitest.ts` (and `manual-testing-sandbox/`, `*-sol.ts`).**
   pry's `is_source` drops `.test.`/`.spec.` but not `.vitest.`; continue's llm
   crater (2/35) is largely its `*.vitest.ts` suites, where `fetch` is mock-injected
   (FALSE-WELD). **Lever: extend the test-file heuristic** to `.vitest.`/`.e2e.`
   + obvious fixture dirs (`manual-testing-sandbox/`). (Per E7 a repo would
   `.pryignore` these, but the default heuristic should catch the conventional
   ones; exclude is off during eval, so they count against pry here.)
4. **Rung-3 stage-2 (injected transport) — REOPEN.** continue's other llm
   FALSE-WELDs are production `openai-adapters` calls behind an injectable
   `customFetch(config.requestOptions)` seam one hop up — the exact
   transport/executor-wrapper gap the roadmap *deferred "until a corpus surfaces
   it"* ([`precision-gate.md`](precision-gate.md) rung-3 census; [`handoff`](handoff.md)).
   **continue surfaces it materially** (it was *not* material on ceal). Worth a
   scoped re-examination — but it needs cross-file analysis and risks
   false-seaming, so gate any rule hard against this labelset + the recall arm.

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

This is **noisy and concentrated** in the DI-heavy repos (flowise/continue), and
some may be panel over-calling GENUINE on borderline seams — it is **not** a
conclusion, it is a **flag**. It is exactly the signal **Slice 2 (filter-recall,
E5)** exists to quantify properly against the larger bare pool. Do not act on it
before Slice 2.

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
agreement rate is **not** the confidence signal it looks like. The only real
accuracy bound is the **human-labeled calibration subset (E4, operator-pending)**;
until that exists the panel's error rate is unmeasured. Treat the numbers as a
strong directional result, not a measured ground truth.

The full audit trail is checked in: `harness/fixtures/eval/votes/<repo>/{pragmatic,
skeptic,neutral}.json` (each persona's label + confidence + one-clause reason) and
`continue/tiebreak.json`. The blinded worklist (the exact `source_context` shown)
is reproducible via `finding_io.py emit` against the pinned corpus.

## Gate status (SC2)

- **OPENED:** harness proven end-to-end (emit → 3-persona panel → reconcile →
  tie-break → freeze) on 4 independent third-party repos; first off-corca
  precision points exist; the core signal validated (100% network/subprocess,
  89.3% ex-tail ≈ ceal 88%); the next levers are named with counts.
- **NOT CLOSED:** (a) human calibration owed (E4); (b) all-welded-end slate — no
  DI-disciplined exemplar (dev #5 / spectrum gap); (c) held-out arm unrun. Close
  per the pre-registered target: **dev 5 / held-out 10** (≈15 repos), tune only on
  dev, held-out is the generalization gate.

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
