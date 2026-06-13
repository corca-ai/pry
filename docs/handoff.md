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
- **Architecture (user-corrected, locked in `docs/spec-layer0.md`):** `pry` CLI =
  deterministic Rust analyzer, **zero intelligence** (map/floor as data, like
  `nose`); intelligence in an **agent-run `pry` skill**; **labeling is
  agent-driven** (blinded single-rater), never a script with an API key.
- **The validation harness is built/verified/committed** (`harness/` +
  `harness/README.md`): `mine → label_io emit → agent labels → label_io freeze →
  szz → repo_fit`, all deterministic/no-LLM except the agent label step. Frozen
  per-corpus evidence under `harness/fixtures/{,ceal/}`.

## Discuss (needs user input — the fork)

Present all three neutrally; the lean is the user's prior, not a branch to advocate.

**Scope invariant for the whole discussion (user-set):** pry stays **static**
(seamed/welded injectability map + syntactic floor, no execution). Agent/workflow
**behavioral** correctness is **cautilus**'s job (`../cautilus`) — pry must not
chase it. The two are complementary: pry statically finds boundaries with *no
seam*; those are exactly what cautilus cannot write a failure-injection eval for.

1. **Pivot the signal** (user's lean): re-tune only the **boundary catalog** to
   what these repos cross — LLM/tool dispatch, scheduled-task/cron enqueue,
   subprocess agent-worker spawn, workflow-state store reads/writes. The map
   stays the static seamed-vs-welded question; the floor stays syntactic. The
   catalog is a **hypothesis seed for `ideation`, not settled** — see
   `docs/ceal-bug-profile.md` (Scope line + Implication). → `ideation`.
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
