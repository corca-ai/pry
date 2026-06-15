# Spec — Finding-Eval Harness (H3 broad-market gate) · build contract

The next build contract after Layer-0 map + precision levers. Turns pry's
*precision/recall claim* into something **measured on independent code** and
keeps every future algorithm change honest. Sibling docs:
[`spec-layer0.md`](spec-layer0.md) (the map + kill-gate harness contract),
[`precision-gate.md`](precision-gate.md) (the hand-labeled H1 precision result
this generalizes), [`kill-gate.md`](kill-gate.md) (the go/kill record).

This is the `nose` `bench/` discipline applied to pry: a frozen, panel-labeled,
dev/held-out corpus that has *rejected plausible-but-wrong ideas* — except pry's
unit is a **finding** (a welded-at-demand boundary), not a clone family.

## Problem

pry's entire value proposition — "the welded-at-demand backlog is ~88% genuine
(ceal) / ~97% (cautilus)" — rests **only on corca's own repos**: ceal, cautilus,
charness, Run 6's 7 own TS codebases, and now open-ax-day. Every number pry has
ever produced is self-corpus.

- The **H3 broad-market gate is pre-registered but unrun** (`precision-gate.md`
  Caveats: *"H3 (broad-market value test) remains the complementary unrun
  gate"*); §9 of `initial-plan.md` always named "then 20–50 OSS repos."
- Precision is **corpus-sensitive** (ceal raw 32% vs cautilus raw 70%; different
  noise classes each time) — so one more own-repo does not de-risk it.
- There is **no reusable harness** to (a) measure precision *and recall* of pry
  findings on a new corpus, or (b) gate a new filter/lever against a held-out
  generalization split. Today that work is ad-hoc, single-rater, in-session hand
  labeling.

nose closed exactly this with a 105-repo (7-lang × 15, dev 58 / heldout 47),
3-persona-panel-labeled benchmark. pry needs the finding-level analog.

## Current Slice

A **dev-time, in-repo, LLM-panel finding-eval harness** for the TS/JS analyzer.
**Slice 1 is precision-only**; the filter-recall arm is Slice 2 (E5):

1. `pry map` → demand-welded findings (+ a control sample of pry-**seamed**
   findings, so the panel can also catch pry's false-*seams*, not only grade its
   positives — E4).
2. mechanical `emit` → a finding worklist (`{file, line, kind, source_context}`).
   Blinding hides pry's verdict *bit* only — a **weak** guard (E4).
3. **3 independent coding-subagent personas** label each finding
   `GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS` (PQ2: 2 taxonomy personas + 1
   neutral "is this testable?" persona).
4. mechanical `reconcile` → majority (≥2/3); 2-1 → tie-break judge; residual →
   arbiter; genuinely-undecidable marked as such. `freeze` → schema-validated,
   provenance-stamped labelset (votes retained for audit).
5. report **precision** (demand-welded), per-repo / per-stratum / pooled (with a
   CI), on a **third-party application-shaped** TS/JS corpus with a **dev/held-out**
   split.

The **first measurement slice runs existing pry unchanged** (no algorithm change)
and emits the noise taxonomy that names the next lever. It **opens** the H3 gate
(≥3 dev repos = harness proven + first off-corca precision point), it does **not
close** it — the gate closes only at the held-out target (SC2). **Slice 2** adds
the filter-recall arm (E5) before any lever ships.

## Fixed Decisions

- **E1 — TS/JS first.** The analyzer has a TS/JS frontend and a hand-validated
  88/97%. Python has *no frontend* and is a separate, deferred, analyzer-free
  (b)-gate phase (see Deferred). No Python frontend is built on faith.
- **E2 — dev-time intelligence only; shipped CLI unchanged.** The LLM panel
  exists *only in this repo's harness*. The `pry` binary stays **zero-LLM,
  zero-credential, deterministic** (the existing harness rule: *"No harness
  script calls an LLM or holds a credential. The intelligence is the coding
  agent"*; F10/F16). The panel is **3 coding-subagents** (personas), **not** an
  LLM-calling script; mechanical scripts only `emit` / `reconcile` / `freeze`.
  *Confirmed by the operator: LLM eval is for building the algorithm here; each
  repo running `pry map` uses no LLM.*
- **E3 — corpus = third-party, application-shaped, not libraries, not own
  repos.** Validation corpus is independent (non-corca) OSS **applications /
  services** (agent/LLM runtimes, automation/workflow apps, web services, CLIs) —
  the population pry actually deploys onto. **Excluded:** (a) general-purpose
  libraries (`date-fns`/`zod`/`hono`-style) — more DI-disciplined/seamed → wrong
  population, operator-flagged; (b) corca's own repos — the very gap being closed
  is "all validation is self-corpus." Pinned commits + generated/vendored prune
  (borrow nose `prune_corpus.py`). **dev / held-out split; tune only on dev.**
- **E4 — labels reuse the precision-gate taxonomy.** `GENUINE / FALSE-WELD /
  COSMETIC / AMBIGUOUS` (already validated in `precision-gate.md`);
  **refute-borderline** (F17). **Blinding is weak, and stated as such:** the
  worklist hides pry's verdict *bit*, but `source_context` + a rubric that *is*
  pry's seam taxonomy let a subagent reconstruct pry's call — so a naive run
  measures inter-rater agreement on pry's rule more than independent truth. Two
  guards (PQ2): (a) a **control sample of pry-seamed findings** so the panel can
  catch pry's false-*seams* (the FALSE-WELD inverse), not only grade pry's
  positives; (b) **one persona prompted from a neutral "is this testable?"** frame
  *without* the pry taxonomy, to break rubric-circularity. **Rater independence
  (operator-decided): same model for all 3 personas (prompt-differentiated) + a
  small human-labeled calibration set** — 3 same-model votes are *correlated*, so
  "2/3 agreement" alone overstates confidence; the human-labeled subset quantifies
  the panel's own error rate and bounds it. Multi-model personas: not needed now.
- **E5 — metric = precision AND *filter* recall; gate = dev precision↑ ∧ held-out
  filter-recall held.** Precision on the demand-welded subset. **"Recall" here =
  *filter recall within pry-recognized boundaries*:** the denominator is pry's
  bare/diagnostic pool (what pry surfaced *before* demand-filtering), so it measures
  whether a lever **demoted** a genuine weld pry had already found — the exact
  failure mode of a precision filter. It does **not** measure detection recall
  (boundary kinds the catalog never models / parse shapes pry can't resolve are
  absent from the pool, so they can't count as misses). **Catalog-completeness
  recall (the nose-`jscpd` independent-arm analog) is a separate, deferred
  question** — not this gate's job. A lever ships **only if** it raises dev
  precision **without** dropping held-out filter-recall. Sequencing: **Slice 1 =
  precision only**; the **filter-recall arm (Slice 2) comes online before any new
  lever ships** (it needs the larger bare pool labeled, so it is its own slice, not
  piggybacked on the precision pass).
- **E6 — own repos are dogfood, not validation.** open-ax-day, ceal, cautilus,
  etc. are dogfood / dev-signal targets — valuable for surfacing candidate noise
  classes (open-ax-day surfaced the smoke-harness scope question now resolved by
  E7) — but **never** counted as the external-validity proof.
- **E7 — scope is user-controlled, not heuristic (resolves PQ4).** pry does not
  *guess* wantedness (the (c)-axis `precision-gate.md` leaves unmeasured): instead
  of auto-demoting test/smoke-harness-shaped files in `src/`, **each repo declares
  its own out-of-scope set** (operator: *"the decision belongs to each repo"*).
  Three granularities:
  (a) **`.pryignore`** — gitignore syntax, committed per-repo; near-free since the
  `ignore` crate already backs the walk (`WalkBuilder::add_custom_ignore_filename`);
  (b) **`--exclude <glob>`** — ad-hoc / CI, no commit;
  (c) **inline `// pry-ignore`** (`# pry-ignore` for future Python) — the
  per-finding escape hatch the roadmap already names for the floor, extended to the
  map. (`.gitignore` is **already** respected via the `ignore` crate.)
  **Exclude is NOT an algorithmic precision lever** — it is user scoping, **off
  during eval measurement** (third-party corpora have no `.pryignore`), so it never
  inflates the precision claim. Sequenced independently of the eval.
  **Path-level `.pryignore` + `--exclude <glob>` are BUILT** (`src/main.rs`
  `discover`; `tests/exclude_smoke.rs`; proven on open-ax-day: `--exclude
  'src/smoke-*.ts'` drops the 8 smoke-harness welds, keeps the 3 genuine
  identity/kit-runtime welds). Inline `// pry-ignore` remains future, ideally with
  the floor.
- **E8 — the LLM panel is a *one-time* improvement campaign, not a standing
  harness** (operator: *"LLM is for algorithm improvement, once"*). The panel runs
  a bounded number of times to produce a **frozen, checked-in labelset** (the
  ground truth). Thereafter **every lever/filter change is gated deterministically
  against the frozen labelset** — recompute precision/filter-recall from the frozen
  labels, **no new LLM call** — exactly like pry's existing frozen fixtures +
  `classify_smoke.rs`. An EXACT lever (only demotes findings *already labeled*) is
  re-derived from the frozen `group`/`label` directly (`filter_recall.py`). A lever
  that **changes pry's mechanical classification** (its demand bit), like lever #3,
  cannot be read off the frozen `group` — so the gate re-runs the freshly-built `pry
  map` and **re-joins by `file:line:col:kind` to the frozen labels**
  (`filter_recall.py --remap`): pry is deterministic, the panel `label` is still the
  frozen oracle, **still no new LLM call**. Re-label only on a *deliberate corpus
  refresh* (new repos, or pry changes enough that findings no longer map). This is
  what makes E5's "keeps every future change honest" affordable: **LLM once →
  deterministic regression forever after.**
- **E9 — SZZ is an *active* structural-improvement input** (operator: *"use SZZ to
  improve the structural algorithm"*), **dev-time only**. Reusing the existing
  kill-gate machinery (`harness/mine.py` + `szz.py` + the commit labeler), trace
  OSS error-handling bug-fixes to make the **structural detector** better:
  (a) **detection-recall / catalog completeness** — a real EH bug at a site pry
  flagged *nothing* = a boundary the catalog missed → add it (the independent arm
  the bare pool structurally cannot be); (b) **calibration** — which weld
  categories actually bite → prioritize. Part of the one-time improvement campaign
  (E8), run where a repo has rich EH-bugfix history. **The product stays
  structural-only** — SZZ never ships as a prediction claim (Deliberately Not
  Doing); it only makes the deterministic structural detector better.

## Probe Questions

- **PQ1 — the dev corpus slate. (Scouted 2026-06-14.)** Four app-shaped
  third-party OSS clear the fit bar (real TS/JS, ample demand boundaries),
  `pry map --summary-only` at the scouted commit:

  | repo | commit | files | demand-welded | lens | clock-inj |
  |---|---|---|---|---|---|
  | librechat | `8154a31` | 1425 | 386 | 0.93 | 5% |
  | continue | `eaa23c5` | 1176 | 292 | 0.95 | 0% |
  | flowise | `f4e2794` | 1324 | 152 | 0.90 | 3% |
  | outline | `d85ead5` | 1363 | 109 | 0.97 | 2% |

  All four are **welded-at-demand "broad market"** (the H3 target population, *not*
  the ceal DI-disciplined outlier — a useful refutation of "mature ⇒ DI-disciplined").
  **Selection criterion (de-bias, per critique): stratify on clock-injection rate**
  (Run 6's discipline fingerprint, computable pre-labeling) and report precision
  *per stratum*, not only pooled — else the pooled number inherits the slate's
  discipline bias. **Gap:** these four cluster at the low/disciplined-injection end
  (0–5%); the slate still needs a **higher-injection exemplar** to span the
  spectrum (scout next — `n8n`/`cal.com` large monorepos for the disciplined +
  clock-heavy end; ceal is the disciplined reference but own-repo, excluded).
- **PQ2 — panel personas + reconciliation.** Three lenses: (1) pragmatic,
  (2) skeptic (both keyed to the pry taxonomy: *"a real failure to inject, on a
  path worth testing, with no existing seam?"*), (3) a **neutral "is this testable
  — can you inject a failure here?" persona that does NOT see the pry taxonomy**
  (breaks rubric-circularity, E4). Plus the **pry-seamed control sample** (E4).
  Define tie-break/arbiter mechanics on the first run.
- **PQ3 — sampling design (pre-registered, per cost-realism).** The panel is
  3×(+tie-break) passes per finding and demand sets are large (109–386 per scouted
  repo), so census-everything is mis-costed. Pre-registered, mirroring
  `precision-gate.md`: per repo, **non-clock demand-welds = 3-vote census** (the
  high-value, smaller set); **clock demand-welds = 3-vote on a stratified ≥25%
  sample**. **Minimum to *open* the gate:** ≥3 dev repos labeled to this design;
  below it the result is "harness-proven but **underpowered**," not "gate answered"
  (ties to SC2 open-vs-close). Slice-2 recall-pool sampling: stratified, sized when
  Slice 2 starts.
- ~~**PQ4 — test/smoke-harness scope.**~~ **RESOLVED → E7.** open-ax-day's 9/11
  demand-welds in `src/smoke-*.ts` are handled by user-controlled exclude
  (`.pryignore` / `--exclude` / inline), not a pry heuristic — pry never guesses
  wantedness, so it cannot false-demote a genuine gap.

## Deferred Decisions (each names its reopen trigger)

- **Python (b)-gate phase, then a Python frontend.** *Reopen when:* the TS/JS
  harness is stable AND a **third-party non-glue OSS Python** corpus
  (distributed-systems / data-pipeline shape, pry's original §9 target) is
  assembled. Run the analyzer-free (b)-gate first (welded/seamed hand/script
  sample, as Runs 1–5 did, no frontend); build a Python frontend **only on a
  (b)-gate GO**. *Note:* `parental-interaction-eval` (239 Py, own repo) is a
  tempting candidate but is the **own-repo glue population kill-gate already
  KILLed** — it does not test the open Python question; use independent non-glue
  OSS Python instead. *No-build answer available today:* for any single repo the
  analyzer-free (b)-gate (the kill-gate hand/script sample) already answers "does
  pry have traction on this Python?" with **no frontend** — saturated glue (like
  the author's) ⇒ no lift; build a frontend only on a per-corpus GO. So "deferred"
  means "no frontend yet," not "no Python answer."
- **SZZ structural-improvement use is now ACTIVE — see E9** (not deferred). Only
  the *consequentiality-as-a-product-metric* variant stays deferred: shipping a
  "welded findings correlate with real bugs" number as pry output re-opens the
  dropped (a)-axis. The *dev-time* use (catalog-recall + calibration feeding the
  structural detector, E9) is part of the improvement campaign. Caveats carried
  into E9 use: SZZ is **noisy** (`git blame -w` over-attributes ~8 fns/fix,
  kill-gate), a **one-directional** signal (a welded site that *bit* = strong;
  absence of a historical bug ≠ safe, so it cannot *reject* a finding), and its
  yield depends on a repo's EH-bugfix history (the author's repos had little; OSS
  apps vary).
- **Held-out expansion / per-corpus client fingerprints / SARIF emit.** *Reopen
  when:* the dev gate is green and generalization or tooling needs sharpening.
- **Homebrew tap (packaging polish).** *Reopen when:* a tap repo + token exist.

## Non-Goals

- **No OSS showcase / leaderboard / outbound PRs** (operator killed the
  marketing/adoption play; this is measurement-for-the-algorithm only).
- **No LLM in the shipped binary** (E2).
- **Not** validating on general-purpose libraries, or on additional own repos
  (E3/E6).
- **Not** building the Python frontend in this slice (Deferred).

## Deliberately Not Doing (rejected, with reasons)

- **LLM-calling eval script with an embedded credential** — rejected: violates
  pry's zero-intelligence-CLI rule and is the explicit "nose anti-pattern" the
  harness README names. The panel is coding-subagents; scripts stay mechanical.
- **Precision-only metric** — rejected: pry improves precision by *filtering*, so
  a precision-only optimizer silently over-filters and craters recall (lever 3 is
  already "precision-favoring"; W1–W3 are named recall holes). Recall arm is
  required before any new lever.
- **Own-repo / library validation corpus** — rejected: representativeness
  (libraries are more seamed; pry deploys on apps) + independence (self-corpus is
  the exact gap). Own repos stay as dogfood only (E6).
- **SZZ as a *product* / marketed prediction claim** — dropped (the kill-gate
  *(a)-axis*). The shipped `pry` binary stays **testability-only** (*(b)-axis*),
  "risk ranking, NOT a bug list" — no SZZ / churn / bug-prediction in the product.
  A *marketed* "welded predicts bugs" claim re-introduces the prediction angle the
  operator removed. **NOTE — SZZ as a *dev-time structural-improvement input* is
  ACTIVE (E9)**: it makes the deterministic structural detector better
  (catalog-recall + calibration); it just never ships as a product prediction.

## Constraints

- `pry map` stays **byte-deterministic** (existing; unchanged this slice).
- Harness scripts are **mechanical**: no LLM call, no credential, no spend
  (extends `harness/label_io.py`).
- Labels are **auditable, not byte-reproducible**: provenance = labeler model-id
  + rubric-hash (F16); the 3 votes are retained per finding (nose-style audit).
- **Held-out discipline:** tune only on dev; held-out is the generalization gate.
- **Frozen corpus:** pinned commits + prune manifest for reproducibility.

## Success Criteria

- **SC1** — a frozen, auditable finding-labelset exists for the dev corpus
  (per-finding: 3 votes + reconciled label + provenance).
- **SC2** — per-repo / per-stratum / pooled **precision** of demand-welded is
  reported on **≥3 third-party app-shaped TS/JS repos *with a CI***, which
  **opens** the H3 gate (harness proven + first off-corca precision point). It does
  **not close** it: ceal 32% vs cautilus 70% shows per-corpus precision is
  high-variance, so the gate **closes** only at the **pre-registered held-out
  target — dev 5 / held-out 10 (≈15 TS/JS repos, nose-analog; operator-confirmable).**
  Labels are file:line-auditable.
- **SC3 (Slice 2) — MET 2026-06-15.** **filter-recall** (within pry-recognized
  boundaries, E5) is measurable against the bare pool: a lever that demotes a
  panel-GENUINE weld is identifiable (the demoted-pool labelset + `filter_recall.py`
  do exactly this; it caught the shipped clock filters demoting 16/143 genuine). The
  gate rule (dev precision↑ ∧ held-out filter-recall held) is documented and
  runnable. (Detection/catalog-completeness recall is out of scope, E5.)
- **SC4** — the shipped `pry` binary is unchanged: no new LLM/credential
  dependency; harness scripts contain no network/LLM call.
- **SC5** — a **noise taxonomy** names the next lever (precision-gate-style
  deliverable), with counts.

## Acceptance Checks

- **AC1 (SC1)** — `freeze` refuses (exit ≠ 0) on any incomplete/malformed verdict
  set (completeness guard, mirroring `label_io.py freeze`); the checked-in
  labelset validates against its schema.
- **AC2 (SC2)** — a precision table (precision-gate format) is checked into
  `docs/eval-gate.md`; every label is contestable via the cited `file:line`
  against the pinned corpus.
- **AC3 (SC3, Slice 2) — MET 2026-06-15.** filter-recall is computed from the
  labeled bare-pool sample (`*-barepool-labels.json`); `python3
  harness/filter_recall.py` re-derives it from the frozen labelset (demoted clock
  16/143, random 0/11); the gate rule ("a lever must not raise the demoted-pool
  GENUINE count") is stated with the worked clock examples in eval-gate.md.
- **AC4 (SC4)** — the binary's transitive deps contain **no** HTTP/gRPC/LLM client
  (assert `Cargo.lock` has none of
  `reqwest|hyper|ureq|isahc|surf|curl|awc|tonic|anthropic|openai`, and `src/` has
  no `std::process::Command` shelling to `curl`/an LLM CLI); harness scripts import
  none of `openai|anthropic|httpx|requests|urllib3|aiohttp` and make no subprocess
  HTTP call.
- **AC5 (SC5)** — the taxonomy section in `docs/eval-gate.md` lists each noise
  class with its count and the candidate lever it implies.

## Critique

**Done** — bounded fresh-eye subagent (general-purpose; not a same-agent pass),
reviewing E1–E7 against `precision-gate.md` / `kill-gate.md`. Verdict FIX-FIRST;
all four BLOCKERs folded into this revision:
1. **"recall" was filter-recall mislabeled** → E5/SC3/AC3 renamed to *filter
   recall (within recognized boundaries)* + ceiling stated; catalog-completeness
   recall declared a separate deferred question.
2. **SC2 closed the gate on 3 repos (underpowered — ceal 32% vs cautilus 70%)** →
   SC2 now "open vs close" with a pre-registered held-out target (dev 5 / held-out
   10, ≈15).
3. **panel mis-costed + blinding near-circular** → PQ3 pre-registers the sampling
   design + an underpowered floor; E4/PQ2 state blinding is weak and add a
   pry-seamed control sample + a neutral-taxonomy persona.
4. **slate not controlled for DI-discipline** → PQ1 adds clock-injection
   stratification + per-stratum reporting; scout data recorded (4 welded-end repos,
   spectrum gap flagged).
Plus: sequencing contradiction fixed (Slice 1 precision-only, Slice 2 recall); AC4
denylist hardened; Python "no-build answer today" line added; SZZ-prediction
explicitly excluded (Deliberately Not Doing).

No forced debug interrupt reported by the risk planner for this contract.

## Canonical Artifact

This doc (`docs/spec-eval-harness.md`) is canonical during implementation.
Results land in a new **`docs/eval-gate.md`** (the H3 result doc, sibling to
`precision-gate.md`). Harness code extends `harness/` (`finding_io.py` +
reconcile **built**, mirroring `label_io.py`); panel verdict/labelset fixtures
under `harness/fixtures/eval/` (created on first panel run).

## First Implementation Slice

**Slice 1 — precision, existing pry (no algorithm change):**
1. **Freeze the dev slate (PQ1):** the ≥3 scouted app-shaped repos at pinned
   commits (+ scout one higher-injection exemplar to span the spectrum), pruned.
   Record the slate (ids, commits, file count, split, clock-inj stratum) in
   `docs/eval-gate.md`.
2. **Build the mechanical harness — BUILT** (`harness/finding_io.py`;
   `harness/test_finding_io.py`, 8 stdlib-unittest cases green; config in
   `harness/config.py`). `emit` (blinded worklist from a `pry map` JSON: PQ3
   census/sample + E4 seamed-control, verdict bit hidden) + `reconcile`
   (3-persona majority ≥2/3 → 1-1-1 tie-break worklist → arbiter → undecidable;
   escalation votes get the same schema guard as the panel) + `freeze`
   (schema/completeness-validated, provenance-stamped, votes retained; precision
   recovered over the demand-weld group). No LLM in scripts (E2). Proven on the
   synthetic fixture (refuse paths = AC1, tie-break + arbiter loops,
   malformed-escalation refuse, determinism) **and** on a real `pry map`
   (ceal/packages: 68 demand-welded → 41-graded + 15 seamed-control worklist, no
   verdict-bit leak). Bounded fresh-eye critique done (no BLOCKERs; two NOTEs —
   escalation-schema + PQ3 `ceil` sampling — fixed). *Remaining in step 2:*
   nothing — the plumbing is complete and slate-agnostic.
3. **Run the 3-subagent panel — DONE** (4 dev repos: outline `d85ead5` / flowise
   `f4e2794` / continue `eaa23c5` / librechat `8154a31`; 589 findings labeled by
   3 same-model personas, reconciled — 469 unanimous / 118 majority / 2 tie-break;
   frozen to `harness/fixtures/eval/*-labels.json`). Panel-labeled,
   human-calibration pending (E4).
4. **Report — DONE** ([`eval-gate.md`](eval-gate.md)): per-repo / per-kind / per-
   stratum / pooled precision with Wilson CIs + the noise taxonomy. **Result:**
   network+subprocess 100% (261/261), ex-cosmetic-tail 89.3% (≈ ceal 88%), raw
   pooled 56.7% (clock/random tail is the drag). H3 gate **OPENED, not closed**
   (SC2): held-out arm + a DI-disciplined exemplar + human calibration still owed.

**Slice 2 — filter-recall arm (before any lever) — DONE 2026-06-15.** Labeled a
154-finding stride sample of the demoted pool (welded, demand=false; clock+random)
via `finding_io.py emit --pool demoted`; frozen to
`harness/fixtures/eval/*-barepool-labels.json`; gate rule + reproduce in
`harness/filter_recall.py` and [`eval-gate.md`](eval-gate.md) "Slice 2". **Result:**
demoted **clock 16/143 = 11.2% genuine** (the cosmetic/`logsink` filter over-demotes
DB-query date bounds + date-math thresholds), demoted **random 0/11** (lossless). The
two shipped EXACT levers pass the gate (0 genuine demoted); the clock CEILING's "0
lost" was **refuted**, reshaping lever #3 into a discrimination fix.

**Lever #3 (clock discrimination) — ✓ SHIPPED 2026-06-15** closed that hole:
`clock_is_demand_control` rescues the two over-demoted shapes before demotion (Rescue A
query bounds + Rescue B compared date-derived thresholds), purely additively.
Re-derived against the frozen oracle by `python3 harness/filter_recall.py --remap`:
**demoted-pool misses 16 → 5, 11 rescued, 0 precision-damage, 0 lost-recall**;
`cargo test`'s `lever3_query_bounds_and_thresholds` pins the shapes + negatives.

**Then** levers, each gated by E5 (dev precision↑ ∧ held-out filter-recall held).

Ready for `impl` (bounded critique **done** — see Critique) after operator sign-off
on the dev slate (PQ1) + the pre-registered corpus target (SC2).
