# Handoff

## Workflow Trigger — if the operator says "계속합시다" / "continue"

Step-1b is **DONE (WEAK)**. The measurement arc is exhausted — four pre-registered
value-bridges have all come back negative. The next move is **not another
measurement**; it is the **ratchet-vs-ship-as-is decision** (below), which is an
`ideation`/`critique` *decision frame* (options, trade-offs, recommendation, next
step), not a new harness. Start there. Do **not** open a fifth measurement without
an explicit new hypothesis and corpus — the honest options have narrowed to a
product/policy choice.

## Current State — 4 value-bridges down; pry = validated classifier, no measured payoff

Detail/numbers in `docs/eval-gate.md`. All pre-registered, git-provable, honest:

- **E9 (bugs)** FALSIFIED 1.05 — welded-at-demand not bugfix-enriched.
- **Step-1 (file coverage)** FALSIFIED 0.95 — `demand` buys no file-level coverage signal.
- **Floor (swallowed-failure claim)** KILL 3.8% — mature OSS swallows are mostly intentional.
- **Step-1b (failure-test detection)** WEAK — per-boundary failure-tested rate is a
  wide unknown interval **9.1%–71.1%** (static fingerprints can't pin it); and the
  welded-vs-rest / welded-vs-wnd contrasts are **confidently flat** (0.965 / 0.961)
  → welded/demand does NOT pick out a differentially-untested population (Step-1's
  demand-null recurs at the failure-path level). welded-vs-seamed flat but underpowered.

pry stays a **precise injectability classifier** (H3: net/subproc 100%) with **no
proven actionable recommender/defect payoff** on this corpus.

## The live thread (operator-raised, the real remaining value)

The honest surviving value is a **design-philosophy** one, not a measured payoff:
"a welded boundary whose failure is only *middle*-mocked (`vi.mock('axios')` /
`stubGlobal('fetch')`) is a smell — prefer a seam, or edge-mocking (msw) for HTTP."
This is the **"don't mock what you don't own" / hexagonal** school — legitimate and
strongest for **non-HTTP** boundaries (db/subprocess), **weakest for HTTP** (where
msw tests a *welded* fetch's failure fine, no seam needed, and is ~70% of pry's
findings). Step-1b neither proves nor refutes it — it is taste, not a defect/coverage
fact. That value's natural home is the **ratchet**, which needs no measured payoff.

## Decision — ratchet vs ship-as-is (the next session's work)

- **Ratchet (no-new-welded-boundary CI gate):** design-conformance, not risk
  prediction; **survives every falsification** (makes no defect/coverage claim);
  ships on the *already-validated* 100% net/subproc precision; the home for the
  design-philosophy value above. Bets on **unverified niche demand** (teams that
  bought DI discipline) and a smaller surface. Open: would the operator/any team
  actually turn on "no new welds"? Consider scoping it to non-HTTP kinds (where the
  seam argument is strongest) + an msw-aware exemption for network.
- **Ship-as-is (map into `quality`, stop):** banks the validated precise classifier
  as an *inventory*; makes no prioritization claim. Lowest cost, honest, ends the arc.

Route via `ideation` (or `critique` as a decision pre-mortem) for the framed choice;
then `spec`/`impl` only if ratchet is chosen.

## References

- `docs/eval-gate.md` — E9 + Step-1 + Floor + **Step-1b** results (+ the testing-
  quality caveat: middle-mock vs edge-mock msw).
- `harness/step1b.py` + `harness/fixtures/eval/preregistration-step1b.md` — the
  failure-test detector + its frozen contract (binding-precedence module extraction,
  mock/failure-sim catalogs, L-import/L-module bracket).
- `charness-artifacts/critique/2026-06-16-step1b-{spec-critique,verification}.md`.
- `charness-artifacts/ideation/2026-06-16-concept-ideation.md` — the wedge analysis
  that named the floor (done) and the ratchet (the remaining live option).
- `initial-plan.md` §1.3/§5 (testability=injectability thesis, two channels).
