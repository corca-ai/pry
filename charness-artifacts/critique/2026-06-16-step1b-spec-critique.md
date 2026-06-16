# Step-1b failure-test pre-registration — bounded fresh-eye SPEC critique

Slice: Next Session Step-1b (`docs/handoff.md`) — for each welded failure-capable
boundary, is its *failure* simulated by a test? Pending change (pre-impl lock-in):
`harness/fixtures/eval/preregistration-step1b.md` (frozen metric + go/kill) +
the `Step-1b` block of `harness/config.py`. No number exists yet — this critique
gates the prereg BEFORE the honesty gate freezes.

**Execution:** parent-delegated fresh-eye subagents — 3 angle (Jackson
problem-framing, Weinberg diagnostic/gameability, Gawande operational/
executability) + 1 separate counterweight. No same-agent substitute. Target
reference: spec-critique. Packet Consumed: n/a (no critique adapter sections).
**Fresh-Eye Satisfaction:** parent-delegated.

## Verdict: FREEZABLE after 2 root fixes + 4 one-line bundles. Folded in.

Convergent finding across all three angles: the gate as first drafted was
**lopsided toward POSITIVE/untested** — it claimed robustness only to *over*-
crediting `failure_tested`, but several mechanisms *under*-credit it (toward the
pry-favorable POSITIVE), and the only real discriminator (the contrast) is both
mis-targeted (demand, not weld/seam) and power-fragile. Both holes are now closed
or honestly labeled. The counterweight correctly **rejected** two "fixes" that
would have over-engineered a gate that is *allowed* to land WEAK/YIELD-ONLY.

## Four-bin triage + disposition

**Act Before Ship (folded into the prereg + config this slice):**
- *(C4 — Gawande+Weinberg, the only number-honesty blocker)* Under-crediting
  `failure_tested` biases toward POSITIVE, the un-robust direction. Folded:
  (a) **frozen binding-precedence rule** for callee→module incl. the
  `fetch`/`node-fetch`/method disambiguation (§3, deterministic single-file scan);
  (b) **per-arm UNRESOLVED reporting + a pre-registered abort** (`>0.30` in `wd`
  → `wd` number UNCOMPUTABLE, never POSITIVE; `STEP1B_UNRESOLVED_ABORT`);
  (c) **permissive `[BRACED]` matcher** — an unparseable failure-sim window is
  counted PRESENT, so detection gaps over-credit `tested` → bias toward OVERSTATED,
  *inverting* the un-robust direction (`STEP1B_BRACE_WINDOW`; §4.2 granularity tags).
- *(C2 — Weinberg+Jackson, truth-in-labeling)* Binding control `rest` is ~92%
  `welded-not-demand`, so the contrast is a **demand** test, not weld/seam. Folded:
  POSITIVE relabeled **"untested-failure wedge real — targeting, NOT weld/seam
  classification"**; §6 states plainly that POSITIVE licenses demand-differentiated
  *targeting* only, the injectability claim rests on the disclosed-underpowered
  `wd`-vs-`seamed` secondary, and (since `rest≈wnd`) a demand-null forces
  YIELD-ONLY by construction — subsuming Jackson's `wd≈wnd` guard.

**Bundle Anyway (folded, one line each):**
- *(C5)* Bare `.rejects`/`.toThrow` (the prereg's own "weakest signal") **excluded
  from the OVERSTATED-deciding strict count** + strict re-pairing; kept in the
  permissive POSITIVE rate (over-credits tested → safe). §4.2/§6.
- *(C6)* "reused verbatim" corrected: L-import re-runs the import scan **retaining
  the `(test, source)` edge** `build_coverage` discards; L-module is a net-new
  per-module index. §1/§4.3. (matched/boot_ci/per_repo reuse IS verbatim — clean.)
- *(C7)* Disclosed that opposite-linkage (L-module≥L-import) **widens the WEAK
  band** + proved POSITIVE/OVERSTATED mutually exclusive (cannot self-contradict). §6.
- *(C8)* §7 trimmed from "recommendation quality is the product value" to **wedge
  EXISTENCE only** (product value would need the dead E9 defect payoff).

**Valid but Defer (recorded as Open Item §7.5, NOT pre-rescued):**
- *(C3)* OR-contrast CI-lo>1 may be unreachable at near-ceiling base rates →
  POSITIVE's contrast clause possibly decorative. **Recorded, not loosened:** a
  decorative GO clause only ever *costs* pry a POSITIVE (lands YIELD-ONLY/WEAK),
  never manufactures one — pre-rescuing would itself rig toward POSITIVE. Closeout
  reports observed base rates + reachability.

**Over-Worry (counterweight pushback — deliberately NOT done):**
- *(C1)* Add a modeled null/expected-rate anchor for the 0.20 bar — over-
  engineering; YIELD-ONLY already catches "low rate, flat contrast," so the
  absolute clause cannot read POSITIVE alone.
- *(C9)* clock/random/env exclusion "inherits" `FLOOR_BOUNDARY_KINDS` — the
  exclusion is independently justified (random 0/79, clock ≈3/130); a footnote.

## Spec-critique required sections
- **Fixed/Probe/Defer coherence:** PASS. Fixed = corpus/arms/outcome/catalogs/
  thresholds/gate (frozen, no unresolved unknown forcing impl to invent contract).
  Probe = the per-entry matcher detail (bounded inside the impl slice, written back
  to the detector + this prereg). Defer = C3 OR-reachability (trigger named:
  closeout base-rate read). No Fixed item hides a Probe.
- **Acceptance-check coverage:** every Success Criterion (POSITIVE/OVERSTATED/
  YIELD-ONLY/WEAK; per-arm UNRESOLVED abort; drop-UNRESOLVED re-cut; strict
  re-pairing; git-provable prereg-precedes-number) maps to a deterministic harness
  computation in `step1b_result.json` + the `merge-base` gate. No prose-only criterion.
- **Pre-Impl Action:** none remaining — all Act-Before-Ship folded; impl may consume.

## Integrity confirmations (Gawande, verified)
Honesty gate INTACT: prereg + config carry the contract + constants, **no number**;
`STEP1B_RESULT_PATH` uncommitted; `git merge-base --is-ancestor <prereg> <number>`
will pass after this commit. Config↔prereg consistent (contrast floor literally
aliases E9's 1.5/1.1; FC-kinds == FLOOR_BOUNDARY_KINDS). AC4 clean (only local git
plumbing; no network/LLM). E9 sweep records NOT mutated. Buildability: BUILDABLE —
file-level pairing + matched machinery deterministic/reproducible; §3 binding +
§4.2 braced matchers are the impl judgment calls, now frozen with granularity tags
+ the abort/permissive guards so both bias the non-POSITIVE direction.
