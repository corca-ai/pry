# Step-1b result — adversarial verification (dynamic workflow, before closeout)

Slice: Next Session Step-1b — the static failure-test detector + its number, before
the eval-gate closeout. Pending: `harness/step1b.py`, `harness/test_step1b.py`,
`harness/fixtures/eval/step1b_result.json` (the number, uncommitted at verify time).

**Execution:** dynamic Workflow `step1b-verify` (operator chose "build focused →
verify via workflow"). 5 parallel fresh-eye dimension reviewers + 1 skeptical
synthesis (6 agents, ~16min, ~464k subagent tokens). Each grounded findings in real
corpus source (`git cat-file` at pinned commits) + live detector re-runs. No
same-agent substitute.

## Synthesis verdict: result_trustworthy = TRUE, verdict_confirmed = WEAK, must_fix = none.

Independently reproduced every headline number **byte-identically**; confirmed the
honesty gate, determinism, AC4-cleanliness, sweep-immutability, 26/26 tests; and
proved **the WEAK verdict is robust to every reviewer-found defect in BOTH
directions** — dropping all over-credit markers moves L-module 71.1→70.0% and
L-import-strict 10.3→8.4%; applying all under-credit fixes moves L-import-strict only
to ~10.5% (would need +494 welds to reach the 40% OVERSTATED bar). No combination
crosses either threshold.

## Dimension results (5)

- **module-extraction → trustworthy.** §3 binding-precedence faithfully implemented
  (verified bare-fetch/node-fetch/member/new-Redis against real source). 3.7%
  UNRESOLVED honest (~62/64 genuine local wrappers/globals/minified). Caveats: dynamic-
  import destructure missed (3 findings); root-only alias resolver. Neither moves verdict.
- **lmodule-overcredit → trustworthy-with-caveats.** 71% reproduces; NOT meaningfully
  inflated (removing all suspect markers → ~70%). NETWORK_ANY sole-creditor only 39/1170
  (3.3%). **Found a real false-positive:** `_RESOLVE_FAIL`'s bare `\berror:` matched
  logger-mock factories (`{ error: vi.fn() }`) — concrete: calcom selfHostedHandler.test.ts.
  Permissive direction (toward OVERSTATED), immaterial, but **fixed post-verify** (tightened
  to the frozen `{ error:`; L-import-strict 10.3→9.1%).
- **limport-undercredit → trustworthy.** 9–10% is a FAIR tight lower bound: an
  aggressive alias-resolver fix recovers only +1 boundary (2 genuine missed tests
  corpus-wide: n8n http-proxy-agent, twenty getClientConfig). A one-hop-transitive
  "fix" is itself spurious over-credit. Most of the 10→71 gap is L-module's per-module
  over-credit, not L-import loss.
- **integrity-repro → trustworthy-with-caveats.** Honesty gate OK (5469026/db138e7
  ancestors; result untracked); byte-identical determinism; AC4-clean (only git
  plumbing); sweep unmutated; config↔prereg match; all §4.1/§4.2 catalog families
  implemented EXCEPT `moduleNameMapper`/`setupFiles` (deferred, **now disclosed in
  prereg**; 0 FC config mocks on corpus).
- **interpretation → trustworthy-with-caveats.** All four candidate closeout claims
  earned, none smuggles a dead thesis — with 4 corrections (below).

## Corrections folded into the closeout

1. Truth = a **wide unknown interval 9.1–71.1%**, not a point — static fingerprint can't pin it.
2. **Narrow the 71% reading**: "a mockable seam is AVAILABLE somewhere for ~71% of welds'
   modules," NOT "these welds' failures are tested" (one fetch test credits all fetch welds).
3. **welded≈seamed is point-flat but UNDERPOWERED** (CI width 0.318, n=138, 1 repo) — only
   welded≈rest / welded≈wnd are *confidently* flat. Do not lump seamed in unqualified.
4. **Qualify "no wedge"**: ~91% lack a co-located own-file failure test, so an
   undifferentiated set of tight-linkage-untested welds exists; what fails is the
   *dense/generous* yield wedge AND the *weld-specific* wedge — not "all welded failures tested."

Plus the operator-raised **testing-quality caveat**: "tested" counts mock-based sims;
~97% of network credit is *middle* mocking (stubGlobal/vi.mock), only ~3.3% *edge*
(msw/nock) — a "mock the network not the module" bar discounts most of the 71%.

## Post-verification fixes applied (contract fidelity, pre-number-commit)

- `_RESOLVE_FAIL` `\berror:` → `{ error:` + dedicated `_FACTORY_FAIL` (no bare `error:`),
  faithful to the frozen §4.2 catalog. L-import-strict 10.3→9.1%; verdict unchanged WEAK.
- Disclosed the `moduleNameMapper`/`setupFiles` deferral in prereg §4.1 (immaterial).

**Fresh-Eye Satisfaction:** parent-delegated (workflow subagents). **Packet:** n/a.
