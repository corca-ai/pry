# Handoff

## Workflow Trigger — if the operator says "계속합시다" / "continue"

There is an **open product decision** (see Discuss). If the operator has already
chosen, route: **floor experiment → `spec`** (pre-registered go/kill, then
`impl`); **ratchet → `spec`**; **stop → wire the map into `quality` and close**.
If no choice is recorded yet, present the Discuss fork; do **not** auto-build a new
direction. Read `docs/eval-gate.md` + `charness-artifacts/ideation/2026-06-16-concept-ideation.md`
first.

## Current State — both MAP prediction payoffs are FALSIFIED; the FLOOR is the un-killed bet

The validation march is **done and negative for the prediction channel.** Detail
+ non-claims in `docs/eval-gate.md`; wedge analysis in the ideation artifact.

- **E9 Tier-1 (bugs): FALSIFIED** — welded-at-demand not bugfix-enriched (matched
  1.05, CI [0.96,1.18]; per-kind re-cut mildly anti-correlated).
- **Step-1 (coverage): FILE-LEVEL gap FALSIFIED** — welded-at-demand files not
  less test-associated (matched 0.95, CI [0.88,1.02]; robust over 7 cuts; ceiling
  1.62 > 1.5 floor → genuine null). Honesty gate proven (`git merge-base
  --is-ancestor cd90d1d 3584359`); `harness/coverage.py` deterministic/offline/AC4.
  **Scope:** *file-level* only; the *line-level/error-path* claim needs executed
  coverage (outbound, forbidden) → **unmeasured, not refuted**.
- **Decisive reframe (ideation):** `initial-plan.md` §5 defines TWO channels —
  **map (prediction)** and **floor (claim)** — with different validity bases. Only
  the MAP was built, and only the MAP died. The **FLOOR** (Aspirator-lineage
  syntactic error-handling bug finder: empty catch / swallowed boundary error /
  log-and-continue on a mutating path) was **never built** and is **not what
  failed** — its bar is *precision-of-a-fact*, not lift-over-churn.

**Consequence (committed):** roadmap demotes the unbuilt precision-lever march
(premise dead). pry's honest identity = a **precise injectability classifier**
(net/subproc 100%) with **no proven prioritization payoff** — NOT a "testability
debt ranker." Honesty guard: do not pitch "fix welds → fewer bugs/coverage."

## Next Session — the recommended path (operator-gated)

1. **`spec` a bounded FLOOR go/kill experiment** (the un-killed bet): implement
   Aspirator's 3 rules, run on the **already-cloned** corpus offline (AC4, no
   outbound), sample ~30 flags for **precision + repo-fit** labeling. Pre-register
   the go/kill BEFORE numbers (same honesty discipline). GO = high precision ∧ ≥1
   meaningful bug class → build the floor (Layer-0's genuine un-built deliverable).
   KILL = fires only on trivial/correct swallows (premortem §13.A repo-fit death)
   → fall back to 2 or 3. Reuses parse/catalog/dataflow-lite already in the binary.
2. **Fallback — seam-coverage RATCHET** (`spec`): a "no new welded boundary" CI
   gate. Survives the falsification (policy-conformance, not risk prediction);
   shippable on the already-validated precision; bets on niche DI-bought-in demand.
3. **Fallback — ship-as-is + stop:** wire the map into charness `quality` as a
   precise injectability inventory; make no prioritization claim.

## Discuss — the open decision (operator's call)

Which direction: **(1) build+test the floor** [ideation recommendation — the only
candidate not premised on the dead prediction, with Aspirator prior art],
**(2) ratchet**, or **(3) stop**? `(d)` line-level coverage measurement on an
owned/local corpus is a sub-experiment, only worth it behind a chosen testability
direction. Wedges (a) fault-test enablement / (b) testability-debt ranker / (e)
feeder-to-mutation all re-lean on the dead "welds = risk" premise — demoted.

## References

- `docs/eval-gate.md` — E9 Tier-1 + Step-1 coverage results + non-claims.
- `charness-artifacts/ideation/2026-06-16-concept-ideation.md` — wedge analysis,
  scoring, recommendation, truth tests.
- `docs/roadmap.md` — premise-update banner (precision-lever demotion).
- `initial-plan.md` §5 (two channels), §1.4 (floor's swallowed-then-commit shape),
  §13 (premortem — repo-fit is the real killer).
