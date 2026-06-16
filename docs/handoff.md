# Handoff

## Workflow Trigger — if the operator says "계속합시다" / "continue"

There is an **open product decision** (see Discuss): **ratchet** vs **ship-as-is**.
The defect-finding direction is exhausted — do NOT re-run bug/coverage/floor
experiments on these corpora. If the operator has chosen, route: **ratchet →
`spec`** (then `impl`); **ship-as-is → wire `pry map` into charness `quality` and
close**. If not chosen, present the Discuss fork. Read `docs/eval-gate.md` first.

## Current State — all THREE value-bridges are down; pry is a precise classifier with no proven payoff

Three pre-registered experiments, all reported honestly (detail + non-claims in
`docs/eval-gate.md`):

- **E9 (bugs): FALSIFIED** — welded-at-demand not bugfix-enriched (matched 1.05).
- **Step-1 (coverage): FALSIFIED** — welded-at-demand files not less test-associated
  (matched 0.95); line-level claim unmeasured (outbound forbidden), not refuted.
- **Floor (claim channel): KILL** — `pry floor` built (FLOOR-1/FLOOR-2, separate
  channel, weld-agnostic; `src/floor.rs`, 6 tests). FLOOR-2 precision **1/26 =
  3.8%**: on mature OSS, swallowed boundary failures are overwhelmingly
  *intentional* best-effort. KILL scopes to this minimal rule set. Honesty gate
  proven (`git merge-base --is-ancestor c7f4308 <result>`).

**The pincer (the load-bearing synthesis):** mature OSS *has* pry's shapes but they
are intentional/benign; the author's own pre-DI repos (`kill-gate.md`: charness
7/126, ceal 2/26) *lack* the shape. Both ends of the maturity axis are negative, so
**no corpus tried supports an actionable defect/testability payoff.** pry stays a
*validated precise injectability classifier* (net/subproc 100%) — that is intact;
what is unproven is any downstream payoff. Roadmap demotes the precision-lever march
+ the floor. Honesty guard: do not pitch "fix welds → fewer bugs / better coverage /
fewer swallowed-failure bugs."

## Next Session — decide the two live options (operator-gated)

1. **Ratchet** (`spec` → `impl`): a "no new welded boundary" CI gate. Survives all
   three negatives (it is policy-conformance, NOT risk prediction); ships on the
   already-validated precision; bets on niche DI-bought-in demand. The only option
   that turns the validated classifier into a product without a defect payoff.
2. **Ship-as-is + stop:** wire `pry map` into charness `quality` as a precise
   injectability inventory; make no prioritization/defect claim; close the project.

## Discuss — the open decision (operator's call)

Ratchet vs ship-as-is. A defect-finding wedge is **unsupported by all evidence
gathered** — reopening it needs a genuinely new corpus hypothesis (e.g. Yuan's
distributed-systems shape, untested in any gate), not another run on these repos.
The deferred Aspirator floor rules (over-catch→abort, etc.) remain unexplored but
face the same "mature apps swallow on purpose" precision ceiling.

## References

- `docs/eval-gate.md` — E9 + Step-1 + Floor results + non-claims (owns the numbers).
- `charness-artifacts/ideation/2026-06-16-concept-ideation.md` — wedge analysis.
- `docs/roadmap.md` — premise-update banner + floor KILL note.
- `docs/kill-gate.md` — the owned-repo / pre-DI negative (the other pincer arm).
- `harness/floor_verdict.py` + `floor-labels.json` / `floor-votes/` — frozen panel.
- `initial-plan.md` §5 (two channels), §13 (premortem — corpus-fit is the killer).
