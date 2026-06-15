# Recent Retro Lessons

## Current Focus

- One-session execution of the E9 goal S1–S5: discover+freeze a 33-repo corpus, pre-register the metric, sweep 25 TS apps (clone→map→mine→blame-join), compute the matched enrichment, run the Python (b)-gate. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)

## Repeat Traps

- **Analyzer-free lens heuristic noise (re-run).** The (b)-gate lens's first run was an artifactual *mute* (decided 0.198) because a greedy receiver-name substring lexicon matched `dict.get`/`list.append`/`signal.connect`. Needed a fix (boundary-VERB gate) + re-run. A hand spot-check earlier would have caught it before the first full run. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)
- **Sequential-then-parallel sweep.** Started the corpus sweep sequential, added a 2nd worker mid-run to halve wall-clock. The collision-safety reasoning was sound, but parallelizing from the start was the obvious move. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)
- **Shallow seed clones (debug cycle).** The 4 seed clones were depth-1; the blame/mine join returned all-zero bugfix-touched + file_churn=1 before I realized there was no history. Cost one diagnosis cycle. The fix (un-shallow in ensure_clone) was clean, but a pre-check would have skipped the detour. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)

## Next-Time Checklist

- **capability:** the sweep harness (`mine_ts.py` + `sweep.py` + `enrichment.py` + `corpus_*` + `bgate_lens.py`) is a reusable, deterministic, zero-LLM corpus-study engine — a genuine asset for future validation goals. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)
- **memory:** the FALSIFIED verdict + base-rate-ceiling + Python clock-culture difference are recorded in `docs/eval-gate.md` + `docs/kill-gate.md` Run 7. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)
- **workflow:** before building any git-history harness on pre-existing clones, assert full history (`! -f .git/shallow`) as the first check. (source: `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`
