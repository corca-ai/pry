# Step-1 coverage measurement — bounded fresh-eye code critique

Slice: Next Session step 1 (docs/handoff.md) — does welded-at-demand sit in
LESS-tested code? Pending change: `harness/coverage.py` (+ `test_coverage.py`),
`harness/fixtures/eval/coverage_result.json`, `preregistration-coverage.md`, and
the `docs/eval-gate.md` "Step-1 coverage" section (FALSIFIED verdict).

**Execution:** parent-delegated fresh-eye subagents (4: Weinberg measurement-bug,
Jackson proxy-framing, Gawande honesty-gate, + counterweight). No same-agent
substitute. Target reference: code-critique. Packet Consumed: n/a (no adapter
sections).

## Verdict: SOUND and HONEST after one headline-scoping fix. Cleared to commit.

The FALSIFIED is located in the data (not a harness artifact); the honesty gate
holds; the only material finding was that the *headline label* over-reached past
what a file-level proxy can claim. That is folded in.

## Findings + disposition (four-bin)

**Act Before Ship (folded into eval-gate this slice):**
- *(Jackson #2/#1)* A file-level OR-proxy is a coarse upper bound that **cannot
  see the line-level claim** (the welded boundary's own error branch). "FALSIFIED"
  was rescoped to the **file-level coverage gap**; a new **Scope of the claim**
  block states the line-level version is *unmeasured here* (needs executed
  coverage = outbound, forbidden) and is therefore *not refuted*, only undetected
  by a coarse instrument.
- *(Jackson #3)* The seamed-only 1.28 (CI excludes 1.0) was reframed from "does
  not rescue the thesis" into the **honest decomposition**: plain welded-vs-seamed
  *injectability* carries a weak CI-positive coverage association, but pry's
  `demand` refinement (wd-vs-welded-not-demand = 0.94, flat) adds nothing.
- *(Jackson #4)* The "both value-bridges down → wedge open" conclusion was pulled
  back to the **earned** claim ("fix welds → fewer bugs" refuted; demand ranking
  buys no file-level coverage signal), explicitly NOT "pry has no value," with the
  line-level path named as the open `ideation` question.

**Bundle Anyway (folded):**
- *(Weinberg #1)* "1/rest_rate" print/markdown label corrected to
  "1/standardized-rest-rate" (the emitted ceiling is 1/std_ct_rate = 1.62). Cosmetic,
  no number changed.

**Over-Worry (counterweight, not done — recorded):**
- Run real line/branch coverage: forbidden (outbound) AND directionally moot — a
  finer proxy raises untested in *both* arms; it cannot manufacture a wd-specific
  1.5× gap from a flat 0.95 quotient.
- More alias-resolution / more robustness cuts: under-resolution biases *toward* a
  gap (robust for a null); 7 agreeing cuts already; diminishing returns.
- Power the seamed-only arm: best case proves "welded code somewhat less tested,"
  which is the injectability bit, **not** pry's demand contribution — a dead end.

**Valid but Defer (recorded):**
- Unit tests for `read_blobs` (the git byte-parser), `boot_ci`, `load_aliases`,
  and the join direction — manually exercised by the reviewer + byte-identical
  reproducibility cover it now; durability gap, not a current defect.
- Drop near-degenerate-coverage repos (cov<5%) as a cut — reviewer verified it
  leaves the null unmoved (degenerate repos sit slightly *above* 1).
- Line-level coverage as a *positive* instrument — only if the wedge revives.

## Integrity confirmations (Gawande, all clean)
Honesty gate HOLDS: prereg cd90d1d contains the contract + constants, **no number**;
result artifacts still uncommitted; `git merge-base --is-ancestor cd90d1d <result>`
will pass. Config↔prereg consistent (floor literally aliases E9's). Byte-identical
re-run. E9 sweep records NOT mutated. Aborts loudly on a missing clone (no silent
"25"). AC4 clean (only `subprocess` → local git plumbing; no network/LLM).
