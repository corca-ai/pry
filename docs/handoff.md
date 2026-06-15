# Handoff

## Workflow Trigger — if the operator says "계속합시다" / "continue"

Do **Next Session** below directly via `impl` (these are bounded analysis +
doc/roadmap edits, **not a new `/achieve` goal** — operator-decided 2026-06-16).
No re-confirmation needed: build, verify, critique, commit. Read
`docs/eval-gate.md` (the E9 Tier-1 result + the exploratory per-kind re-cut)
first.

## Current State — E9 sweep DONE; the bug-prediction thesis is FALSIFIED

The E9 multi-repo validation sweep is **complete** (goal artifact:
`charness-artifacts/goals/2026-06-15-e9-multi-repo-validation-sweep.md`, status
complete). Result, with full detail + non-claims in `docs/eval-gate.md` Tier-1:

- **쟁점 4 FALSIFIED.** welded-at-demand vs rest matched enrichment **1.05, CI
  [0.96,1.18]** across 25 TS apps → trips the pre-registered falsifier. The signal
  is a **testability classifier, NOT a defect predictor.**
- **쟁점 2:** dev 0.93 / heldout 1.11 (weak, far below the 1.5 GO bar).
- **Exploratory per-kind re-cut** (`harness/enrichment_bykind.py`, post-hoc, not a
  verdict): the genuine high-precision kinds go the *wrong* way — network 0.83,
  subprocess 0.73, genuine subset matched 0.82. So bug-prediction is dead even for
  the boundaries pry detects best; SZZ Tier-2 / narrow-numerator chasing is **not
  worth it** (wrong direction, not merely weak).
- **Python (b)-gate KILL** (welded-saturated 0.902; `docs/kill-gate.md` Run 7); no
  frontend built.

**Consequence:** lever #4 (precision polish) is **deprioritized** — its premise
(enrichment holds) is dead. The shipped binary is unchanged and correct
("risk ranking, NOT a bug list"). The reusable zero-LLM sweep engine lives in
`harness/{corpus_*,mine_ts,sweep,enrichment*,bgate_lens}.py`.

## Next Session — pivot to the testability-tool identity (do in order)

1. **Verify the honest first-link claim: welded-at-demand → LOWER test coverage**
   (not bugs — the bug link is dead). This is pry's *real* candidate thesis and is
   directly measurable. Reuse the sweep engine: join each weld site to
   test-file proximity / coverage (coverage-report repos first). GO here makes
   pry's identity a *measured* claim, not a guess.
2. **Confirm pry's identity + fix the roadmap.** pry = testability/injectability
   **debt ranker**, not a bug finder. Update `docs/roadmap.md`: demote lever #4 to
   backlog (premise dead). Honesty guard: do **not** pitch "fix welds → fewer
   bugs" — the data refutes it (remaining welds sit in lower-risk code). The honest
   value is testability for its own sake (coverage / failure-test enablement).
3. **(Optional, after 1) `ideation`/`spec` the wedge.** Does a "DI/testability
   debt backlog" tool have real demand / status-quo / moat? Natural follow-up if
   step 1 is a GO.

## Discuss

- None blocking. If step 1 is also flat/negative, the open question becomes
  whether pry's testability framing has a wedge at all (an `ideation` question),
  vs. shipping it as-is into charness `quality` and stopping.

## References

- `docs/eval-gate.md` — E9 Tier-1 result + per-kind re-cut + non-claims (owns the
  numbers).
- `charness-artifacts/goals/2026-06-15-e9-multi-repo-validation-sweep.md` — full
  slice log, critiques, closeout.
- `docs/kill-gate.md` Run 7 — Python (b)-gate KILL.
- `docs/spec-eval-harness.md` — the build contract (SC/AC, AC4 zero-LLM).
- `harness/` — the sweep engine (reuse for step 1); `config.py` E9 block.
