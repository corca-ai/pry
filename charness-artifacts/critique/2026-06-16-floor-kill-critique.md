# Floor KILL — bounded fresh-eye result critique

Slice: the floor go/kill VERDICT (KILL) + `docs/eval-gate.md` "Floor experiment"
section + `harness/floor_verdict.py` + frozen votes/labels.

**Execution:** parent-delegated fresh-eye subagent (1 reviewer, proportionate to a
KILL with reproducible artifacts + a prior 3-rater labeling panel). No same-agent
substitute. The 3-rater panel itself was the fresh-eye labeling pass.

## Verdict: KILL is SOUND and the math correct (reproduced byte-identical). Two framing fixes folded. Cleared to commit.

## Findings + disposition

**Act Before Commit (folded into eval-gate):**
- *(Strategic-leap gap — most substantive)* The conclusion pointed at a
  "less-mature / pre-DI corpus" as a defect-finding rescue, but `kill-gate.md`
  already found the author's own pre-DI repos LACK the swallow shape (charness
  7/126, ceal 2/26). Rewrote to the honest **pincer**: mature OSS has the shape
  but intentional (KILL); pre-DI lacks it (RE-TARGETed); both maturity ends are
  negative, no obvious rescue corpus on that axis; defect wedge unsupported.
- *(Under-disclosure)* The `googleTranslate.ts:92` 2-1 BENIGN is arguably a real
  cache-poisoning bug the panel under-called. Noted as a near-miss; "20 intentional"
  → "~20"; precision at 2/26 = 7.7% still KILL.
- *(Nit)* Added the same-model asymmetry: builder-biased panel over-calls GENUINE,
  so a KILL is conservative w.r.t. it.

**Confirmed sound (not re-litigated):**
- Verdict math: FLOOR-2 precision 1/26 = 3.8% reproduced; `floor_verdict.py`
  applies the FROZEN config thresholds faithfully (both KILL clauses fire); the
  27→26 gap is the seerr dup-id collapse (lossless, both BENIGN), not an exclusion.
- KILL robust to label noise (holds until genuine ≈ 11/26).
- Honesty gate provable (`git merge-base --is-ancestor c7f4308 <result>`).
- Scoping caveat ("this rule set, not the concept") held consistently.
- Spot-checked rater labels: FileUpload GENUINE correct; payload:1238 FALSE-FLAG
  correct (commit in a different rethrowing catch); seerr dup BENIGN correct.

## Strategic consequence
All three value-bridges (bugs, coverage, swallowed-failure claim) now negative.
The live options are the policy **ratchet** or **ship-as-is**; no evidence supports
a defect-finding wedge. Recorded in eval-gate + handoff.
