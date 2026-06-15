# S2/S3/S4 slice review packet — E9 Tier-1 enrichment (bundle boundary)

## Intent
Compute the directly-observed enrichment (쟁점 4): are welded-at-demand pry
findings bugfix-touched at a higher rate than other boundary findings, across a
25-repo TS corpus, under the PRE-REGISTERED matched comparison? And does it
generalize (쟁점 2, dev vs heldout)? **Result: FALSIFIED** (matched 1.05, CI
[0.96,1.18]). A negative result — so the critical question is: **is the
falsification REAL, or an artifact of a harness bug?**

## Result (to stress)
- corpus: matched **1.05**, CI [0.96, 1.18] → FALSIFIED. dev 0.93, heldout 1.11
  (CI [1.02,1.29], weak but below 1.5 GO bar). vs seamed 0.91, vs wnd 1.05.
  17/25 repos per-repo ratio>1 (direction positive, magnitude tiny).

## Changed files / surfaces
- `harness/mine_ts.py` — bugfix-commit set (message-intent, reachable-from-pinned).
- `harness/sweep.py` — clone@pinned → pry map → mine → blame join; arms wd/rest;
  covariates file_churn + enclosing site_size; un-shallows seeds.
- `harness/enrichment.py` — matched ratio (churn×size terciles, direct
  standardization), repo-cluster bootstrap CI, Simpson guard, dev/heldout,
  secondary controls.
- `harness/fixtures/eval/sweep/*.json` (25 records), `enrichment_result.json`.
- `docs/eval-gate.md` Tier-1 section (verdict).

## Commits (ordering)
- prereg anchor `47eeb633` (numerator+CI pinned) precedes enrichment commit
  `6a19e3d` (git merge-base --is-ancestor verified).

## Expected invariants
- Deterministic: sweep + enrichment byte-identical on re-run (verified umami +
  enrichment). matched-ratio neutralizes a pure churn confound (unit test).
- Honesty gate: numerator/denominator/floor/CI all frozen before the number.

## Reviewer questions (the load-bearing ones — is the NEGATIVE real?)
1. **Blame-join correctness:** is "bugfix-touched = last-blame-commit ∈
   message-intent bugfix set" implemented correctly? Could a bug make BOTH arms
   look identical (~1.0) — e.g. blame line-number off-by-one, file-path mismatch
   between `pry map` output and git paths, or the bugfix set being so large that
   nearly every line is "bugfix-touched" (washing out the contrast)? Check the
   bugfix-set SIZE vs total commits (is the regex too broad → everything is a
   bugfix → no discrimination)?
2. **Matched-comparison correctness:** is direct standardization over
   (churn×size) terciles implemented right? Could tercile bucketing or the
   stratum weighting flatten a real signal? Is dropping the raw vs matched
   distinction handled (they're ~equal here — is that suspicious or expected)?
3. **Arm definition:** wd = class=welded&demand; rest = seamed|welded-not-demand.
   Is "rest" the right denominator, or does lumping welded-not-demand (also
   un-injectable) into the control HIDE a real welded-vs-seamed signal? (Secondary
   vs-seamed is 0.91 though.) Is the demand bit being read correctly from pry?
4. **Is FALSIFIED the honest call** given heldout CI [1.02,1.29] excludes 1.0?
   (Pre-registered: FALSIFIED if ≤1.1 OR CI-lower≤1.0; corpus 1.05 trips both.)
   Is reporting FALSIFIED — vs "weak positive" — faithful to the pre-registration?
5. **Selection/coverage:** all 25 TS repos swept (0 dropped)? Any silent
   truncation (R-D)?

## Out of scope
- S5 Python (b)-gate (next). The pre-registration content itself (already
  critiqued in S1).
