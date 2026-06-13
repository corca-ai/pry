# Handoff

## Workflow Trigger

**First action: open the §13 strategic fork as a discussion with the user and do
NOT pick a branch yourself.** Layer 0's first experiment returned **RE-TARGET on
both own-repos**; the user wants to decide the direction live next session. Read
[`docs/kill-gate.md`](kill-gate.md) and [`docs/ceal-bug-profile.md`](ceal-bug-profile.md)
first. Sequence:

1. Present the 3-way fork (see `Discuss`) **neutrally** to the user.
2. **Only if the user confirms "pivot the signal"** → run **`ideation`** to
   reshape the thesis for the agent/LLM defect profile.
3. **Then** re-run **Gate 0** with a re-tuned miner + boundary catalog.

The user's prior leans toward "pivot the signal" (*"catch ceal's recurring bugs
earlier"*) — that is their lean to confirm, not a branch to advocate. Do **not**
start the Rust analyzer until a corpus/signal clears Gate 0.

## Current State

- **Layer 0 first experiment COMPLETE** — and it did its designed job: cheaply
  falsified corpus-fit with **no analyzer code written** (§9/§13). Working tree
  clean; all committed (`git log`).
- **Verdict: both own-repos → RE-TARGET.** charness 7/126 confirmed
  error-handling fixes (6 high-conf sites ≪ floor 30, recall 1/40); ceal 2/26
  (2 high-conf sites, recall 0/5). Both are AI-agent/LLM-orchestration tools that
  **lack** pry's target shape (swallowed boundary-failure → mutation → commit).
  Textbook §13 A.2, confirmed twice. Numbers + synthesis: `docs/kill-gate.md`.
- **Architecture (user-corrected, locked in the spec):** the **`pry` CLI is a
  deterministic Rust analyzer with ZERO intelligence** (emits map advisory +
  floor claims as data, like `nose`); intelligence lives in an **agent-run `pry`
  skill**; **validation labeling is agent-driven** (blinded single-rater), never
  a script with an API key. Contract: `docs/spec-layer0.md`.
- **The validation harness is built/verified/committed** (`harness/`): `mine.py`,
  `label_io.py` (emit/freeze, no LLM), `szz.py` (`blame -w` + AST), `repo_fit.py`
  (high-confidence floor). Frozen per-corpus evidence under `harness/fixtures/`
  (charness) and `harness/fixtures/ceal/`. Re-run any corpus:
  `mine → label_io emit → agent labels → label_io freeze → szz → repo_fit`.

## Discuss (needs user input — the fork)

Present all three neutrally; the lean is the user's prior, not a branch to advocate.

1. **Pivot the signal** (user's lean): redefine the boundary catalog + bug shape
   for the agent/LLM domain. The boundary list (LLM/tool dispatch,
   scheduled-task/cron hops, subprocess agent workers, workflow-state
   persistence) and the flag *"required workflow step / proof / contract not
   enforced across an async agent boundary"* are a **hypothesis seed for
   `ideation`, not a settled catalog** — see `docs/ceal-bug-profile.md`'s closing
   caveat. → `ideation`.
2. **Pivot the target**: validate the tool as-built on OSS distributed-systems
   repos (§9's "20–50 OSS repos") + BugsInPy — proves the mechanism but on repos
   the author doesn't own.
3. **Shelve**: accept error-handling/testability isn't the bottleneck for these
   repos; the honest cheap-kill outcome.

## References

- [`docs/kill-gate.md`](kill-gate.md) — the go/kill verdicts + cross-corpus synthesis.
- [`docs/ceal-bug-profile.md`](ceal-bug-profile.md) — ceal's recurring bug shape; the pivot-signal seed.
- [`docs/spec-layer0.md`](spec-layer0.md) — the build contract (nose-model architecture, kill-gate methodology).
- `harness/` + `harness/README.md` — the built falsifier; `harness/fixtures/` holds the frozen evidence.
- [`initial-plan.md`](../initial-plan.md) §9 (first experiment), §13 (premortem — A.2 is the outcome we hit).
