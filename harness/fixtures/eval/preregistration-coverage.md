# Step-1 coverage (testability) — PRE-REGISTRATION

**Status: frozen. This file's git commit MUST precede the commit that writes any
wd-vs-rest coverage number.** A fresh reviewer proves the order from git, not from
a self-attesting line:

```
git merge-base --is-ancestor <this-commit-sha> <first-coverage-number-commit-sha>
```

This is the load-bearing honesty gate for step 1, identical in discipline to the
E9 enrichment pre-registration (`preregistration.md`). It matters **more** here:
this is the *rescue* thesis. E9 Tier-1 FALSIFIED the bug-prediction claim
(welded-at-demand is **not** bugfix-enriched; the genuine-kind re-cut even shows a
mild *anti*-correlation — `docs/eval-gate.md`). The remaining honest candidate is
that pry's welded-at-demand signal is a **testability** signal: a welded boundary
has no seam to inject a failure, so its code is harder to test, hence **less
tested**. The motivated-reasoning risk (manufacturing a rescue) is exactly why the
split, denominator, metric, and two-sided floor are frozen before any number.

The machine-readable copy of every threshold lives in `harness/config.py` (the
`Step-1 coverage` block). This document is the human-readable contract; config.py
is the source of truth the harness reads. If the two disagree, the git history of
*this file* governs.

---

## 1. Corpus, split, and data source — REUSED from E9, no new mining

Identical to E9 (`corpus.json`): **25 TS/JS apps**, dev 5 / heldout 20, pinned
commits. **Zero new mining, zero outbound.** The coverage signal is joined from
the existing clones at the **same pinned commits** via git plumbing
(`git ls-tree` for the file list, `git cat-file` for test-file contents) — fully
deterministic and offline. The frozen E9 sweep records (`sweep/*.json`) supply the
finding set, arms, `file_churn`, and `site_size`; this step only **adds** a
per-file coverage bit. The E9 sweep records are NOT mutated.

## 2. Unit and arms — REUSED from E9

- **Unit:** one pry *finding* (a boundary call).
- **Signal arm — welded-at-demand (wd):** `class == "welded" AND demand == true`.
- **PRIMARY control — "rest":** every other decided boundary finding
  (`class == "seamed"` OR (`class == "welded"` AND `demand == false`)).
- **SECONDARY breakdowns (reported, not the verdict):** wd vs `seamed`-only; wd vs
  `welded-not-demand`-only.

## 3. The coverage outcome (the NUMERATOR), pinned here

A source file `F` is **test-associated ("covered")** iff **at least one** of:

- **(a) MIRROR** — there exists a test file whose basename *stem* equals `F`'s stem
  (`foo.ts` ↔ `foo.{test,spec,e2e,vitest,cy}.*`), located anywhere in the repo
  (co-located or under a test directory).
- **(b) IMPORTED-BY-TEST** — `F` is the resolved target of an `import` / `require` /
  dynamic `import()` specifier appearing in at least one test file. Resolution:
  relative specifiers (`./`, `../`) resolved with standard TS/JS resolution
  (extension inference over `COVERAGE_RESOLVE_EXTS` + `/index.*`); `tsconfig` /
  `jsconfig` `compilerOptions.{baseUrl,paths}` aliases applied best-effort per repo.

A **test file** = a code file (`COVERAGE_CODE_EXT_REGEX`) whose basename matches
`COVERAGE_TEST_BASENAME_REGEX` OR whose path contains a test-dir segment
(`COVERAGE_TEST_DIR_REGEX`). This mirrors pry's own `is_source` test-stem heuristics
so "what counts as a test" is the same definition the binary already uses.

- **untested(finding)** = the finding's file is NOT test-associated. This is the
  per-finding binary outcome. **Orientation is deliberate:** measuring `untested`
  (not `covered`) makes wd-more-untested produce a ratio **> 1**, the *same*
  direction as E9's enrichment, so the E9 machinery and two-sided floor apply
  unchanged (§5).
- **Coarseness, disclosed up front:** file-level association is a coarse **upper
  bound** on boundary-line coverage — a covered file may never exercise the
  specific boundary's error path. It is applied **identically to both arms**, so
  the *ratio* stays a valid relative signal. Claim is "is the file under test at
  all," never line/branch coverage.

## 4. The metric and its denominator — REUSED machinery from E9

- **matched untested ratio = THE verdict metric** = (wd untested rate) / (rest
  untested rate), direct standardization over `(file-churn tercile × site-size
  tercile)` strata; a stratum is used only with ≥ `ENRICHMENT_MIN_STRATUM` (5)
  findings in EACH arm; dropped strata are logged (no silent truncation).
- **Raw pooled ratio** reported alongside (confound visibility).
- **95% CI** = repo-cluster bootstrap (`ENRICHMENT_BOOTSTRAP_B=2000`,
  `SEED=0`, `CI=0.95`), resampling repos with replacement.
- **Per-repo distribution (Simpson guard):** of repos with ≥
  `ENRICHMENT_PERREPO_MIN_FINDINGS` (20) per arm, report the fraction with per-repo
  ratio > 1 (majority ≥ `ENRICHMENT_PERREPO_MAJORITY` = 0.60).
- **dev vs heldout reported separately** (쟁점 2 analog). **Nothing is tuned on
  dev** — the thresholds are reused from E9 by symmetry, so there is no free
  parameter to fit.
- **Companion effect sizes (pre-registered, robust to base-rate compression):**
  the matched **odds ratio** `[wd_unt/wd_cov]/[rest_unt/rest_cov]` and the **raw
  rate difference** are reported next to the risk ratio, because a risk ratio is
  compressed toward 1.0 when the untested base rate is high (the same base-rate
  ceiling E9 disclosed).

## 5. The two-sided floor / FALSIFIER — set blind, REUSED from E9 by symmetry

On the **matched untested ratio**, with the repo-cluster bootstrap CI:

- **GO (testability-coverage gap real):** matched ratio ≥ `COVERAGE_GO_FLOOR`
  (= `ENRICHMENT_GO_FLOOR` = 1.5) **AND** CI lower bound > 1.0. I.e. wd sites are
  reliably ≥1.5× as likely to sit in untested files.
- **FALSIFIED (no actionable coverage gap):** matched ratio ≤ `COVERAGE_FALSIFIER`
  (= `ENRICHMENT_FALSIFIER` = 1.1) **OR** CI lower bound ≤ 1.0. A valid, honest
  outcome to report (nose retraction discipline), not a failure to hide.
- **WEAK / inconclusive:** anything between.

Rationale for reuse: the bar that made E9's *bug* signal "actionable" (≥1.5×,
CI-excludes-1) is the same bar a *testability* signal must clear to be a product
claim. No bar is tuned to this outcome.

- **Base-rate ceiling (pre-registered contingency).** The max achievable risk
  ratio is `1 / rest_untested_rate`. If that is `< COVERAGE_GO_FLOOR` (rest base
  rate > ~0.67, making GO structurally unreachable), the closeout LEADS with the
  **odds ratio + rate difference** as the effect-size verdict and flags the risk-
  ratio bar as structurally unreachable — rather than reporting a forced,
  uninformative FALSIFIED. This contingency is set blind, before any rate is seen.

## 6. Pre-specified robustness cuts (reported; do not move the verdict)

- **Backend-only:** repeat the matched ratio excluding frontend files
  (`COVERAGE_FRONTEND_REGEX`: `.tsx`/`.jsx` or a `components|pages|app|ui|views|
  client|frontend` dir segment). The named E9 file-kind confound is frontend-vs-
  backend: welded `fetch` concentrates in less-unit-tested UI code. If the gap is
  that artifact, it weakens/vanishes backend-only; if it holds, the confound is
  not driving it.
- **File-level (dedup):** collapse to unique source files per arm (coverage bit
  once per file) to bound within-file clustering inflation of the site-level N.
- **Proxy components:** report mirror-only and imported-by-test-only coverage rates
  so the OR is not a black box.

## 7. Standing non-claims (restated at closeout)

- **Structural proxy, not executed coverage.** No test suites were run (that needs
  `npm install` = outbound, forbidden on corpus repos). This is "is the file under
  test at all," inferred from the repo tree.
- **File-level, not line/branch** — a coarse upper bound on boundary coverage.
- **Correlational.** "welded → untested" is an association on this corpus, not
  causation; we never claim fixing a weld adds a test.
- **File-KIND residual** (frontend/backend) is named and partially probed (§6
  backend-only), not fully neutralized.
- **Import resolution is best-effort** (aliases / monorepo package specifiers may
  under-resolve), which *undercounts* imported-by-test coverage. If that undercount
  is heavier for wd files it would BIAS TOWARD a gap — so a GO must survive the
  **mirror-only** cut (no resolution dependency) to be trusted; a FALSIFIED is
  robust to it.

---

*Frozen at step 1. The harness reads config.py; it does not re-derive these
numbers. Changing any threshold above after a coverage number exists voids the
honesty gate and must be called out explicitly in the closeout.*
