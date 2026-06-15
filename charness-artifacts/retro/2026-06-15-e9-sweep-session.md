# Retro — E9 multi-repo validation sweep (session)

Goal artifact: charness-artifacts/goals/2026-06-15-e9-multi-repo-validation-sweep.md

**Mode:** session

## Context
One-session execution of the E9 goal S1–S5: discover+freeze a 33-repo corpus,
pre-register the metric, sweep 25 TS apps (clone→map→mine→blame-join), compute the
matched enrichment, run the Python (b)-gate. **Main result: 쟁점 4 FALSIFIED**
(welded-at-demand matched enrichment 1.05, CI [0.96,1.18]); 쟁점 2 dev 0.93 /
heldout 1.11 (weak, below GO bar); Python (b)-gate KILL (welded-saturated 0.902).

## Waste
- **Shallow seed clones (debug cycle).** The 4 seed clones were depth-1; the
  blame/mine join returned all-zero bugfix-touched + file_churn=1 before I realized
  there was no history. Cost one diagnosis cycle. The fix (un-shallow in
  ensure_clone) was clean, but a pre-check would have skipped the detour.
- **Analyzer-free lens heuristic noise (re-run).** The (b)-gate lens's first run
  was an artifactual *mute* (decided 0.198) because a greedy receiver-name
  substring lexicon matched `dict.get`/`list.append`/`signal.connect`. Needed a
  fix (boundary-VERB gate) + re-run. A hand spot-check earlier would have caught
  it before the first full run.
- **Sequential-then-parallel sweep.** Started the corpus sweep sequential, added a
  2nd worker mid-run to halve wall-clock. The collision-safety reasoning was
  sound, but parallelizing from the start was the obvious move.

## Critical Decisions
- **Amendment A (control = "rest", not seamed-only).** Power-motivated,
  pre-measurement (arm SIZES only, no outcome peek): the seamed arm was ~14×
  thinner than welded-at-demand. The right call — and the angle-3 critique later
  confirmed the thesis fails under *every* framing (seamed rate 0.437 > wd 0.394).
- **Reporting FALSIFIED honestly.** The nose-retraction discipline in action:
  three fresh-eye angles independently verified the negative is sound (not a bug),
  and I disclosed the base-rate ceiling + heldout-not-refuted rather than
  massaging. This was the core integrity decision of the goal.
- **Pinning the bugfix numerator into the frozen pre-registration** (S1 critique
  fold #8) — closed the one real honesty-gate hole (the most outcome-sensitive
  knob was otherwise left tunable in S2).

## Expert Counterfactuals
- **Gary Klein (pre-mortem):** a power analysis on arm sizes *before* writing the
  pre-registration would have set the "rest" control from the start, avoiding the
  Amendment-A churn. (Mitigated: I caught it pre-measurement, so honesty held.)
- **Measurement-validity lens (Meehl/Weinberg):** the broad bugfix regex (~48% of
  commits) is a base-rate ceiling that compresses the achievable ratio toward 1.0
  — a narrower bugfix predicate or a base-rate-adjusted effect size would resolve
  small effects better. Recorded as a disclosed limitation, not hidden.

## Next Improvements
- **workflow:** before building any git-history harness on pre-existing clones,
  assert full history (`! -f .git/shallow`) as the first check.
- **capability:** the sweep harness (`mine_ts.py` + `sweep.py` + `enrichment.py` +
  `corpus_*` + `bgate_lens.py`) is a reusable, deterministic, zero-LLM corpus-study
  engine — a genuine asset for future validation goals.
- **memory:** the FALSIFIED verdict + base-rate-ceiling + Python clock-culture
  difference are recorded in `docs/eval-gate.md` + `docs/kill-gate.md` Run 7.

## Sibling Search
Two transferable waste patterns:
- *Shallow-clone-before-history-mining* — recurs in any future git-mining harness;
  mitigated by the ensure_clone un-shallow + the workflow check above. No other
  current git-mining sites beyond mine.py/mine_ts.py/sweep.py (all now full-history
  aware).
- *Greedy-substring classification noise* — recurs in any analyzer-free token
  classifier; `bgate_lens.py` fixed (boundary-verb gate). `corpus_fit.py` uses
  curated distinctive keywords (already de-greedied during S1 critique). No other
  substring-classifier siblings in harness/.

**Persisted:** yes (see path below).
