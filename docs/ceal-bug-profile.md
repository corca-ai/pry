# ceal bug profile — seed for the "pivot the signal" discussion

Why this exists: Gate 0 on ceal returned RE-TARGET — only 2/26 candidates were
Yuan-shape error-handling bugfixes. But the user wants pry to **catch the bugs
that keep recurring in ceal earlier**. So the real question is not "does ceal
have boundary-failure bugs" (it barely does) but **"what bug shape DOES ceal keep
hitting, and could pry target it?"** This characterizes ceal's actual recurring
py-bugfix profile from the 31 mined+labeled bugfix commits (`harness/fixtures/
ceal/labels.json`) so the next session's `ideation` starts from evidence.

## What ceal is

`ceal` = "a surface-extensible organizational AI agent runtime… Slack ingests DM
and channel messages, dispatches them to isolated agent workers, replies with
skill-driven autonomous capabilities." Its defect surface is **agent-workflow
orchestration**, not distributed-systems I/O.

## The recurring clusters (31 py-bugfix commits)

Boundary-failure error handling (pry's *current* target): **2** — `465e665`
handle KST without tzdata (`ZoneInfoNotFoundError`), `d0d7b75` block a slot
computed over a failed calendar read. Everything else recurs in these shapes:

1. **Scheduled-workflow correctness / visibility** (the dominant cluster):
   `ed9903d` scheduled workflow abort *visibility*; `69b5f48` scheduled-thread
   provider-boundary regressions; `4e9f36a` survey/scrum workflow regressions;
   `35e5f84` survey deadline close records a *post-deadline* decision;
   `d0d7b75`/`9f69332` schedule-match findings; `f6d2a1a` resume recommendations
   after group posts. → *a scheduled/async agent action fires, aborts, or records
   the wrong thing without the workflow noticing.*
2. **Required step / proof / contract not enforced** across an agent hop:
   `89046613` preserve slack follow-up evidence; `cbe82db` require daily
   follow-up contracts; `a851b7a` close slack workflow proof gaps; `58ef8ea`
   require proof ladder in external closeouts. → *a workflow completes without
   enforcing that a required artifact/proof actually exists.*
3. **Slack / provider dispatch semantics**: `acaa910` Slack event posting
   semantics; `1f88ce6` manual Slack API helper for GET; `dec61f6` retro proposal
   Slack lifecycle; `d09ac86` runtime slack/workflow reliability gaps.
4. **Anniversary / scheduling state drift**: `2fda41c` event channel drift;
   `4f7e64e` require event target ids.
5. **Credential / provider boundary policy**: `a5ea0d2` block agent credential
   passthrough; `ac5c3a6` remove raw slack credential fallbacks.
6. **Skill/adapter parsing + materialization pins** (infra): `8ece278` adapter
   list parsing; `e01610a`/`30b84ab` charness materialization pin.

## Implication for pry (the pivot-signal hypothesis)

pry's boundary catalog (`requests`/`open`/`socket`/…) and bug shape (swallowed
boundary failure → mutation → commit-anyway) are tuned for Yuan's distributed
systems. For ceal-shaped repos the **injectability/seam thesis may still hold**
but the *boundaries* and *invariants* differ:

- **Boundaries to catalog:** LLM/tool dispatch, Slack/provider API calls,
  **scheduled-task / cron / async-worker hops**, subprocess agent workers,
  workflow-state persistence.
- **Bug shapes to flag:** a required workflow step / proof / contract not
  enforced across an async agent boundary; a scheduled action that fires or
  aborts without a visible, testable outcome; state/decision recorded after a
  deadline or on the wrong channel.
- **Seam question, restated:** is there a seam to inject "the scheduled job
  failed / the agent worker crashed / the provider returned an error / the
  follow-up was never posted" and assert the workflow refuses to record success?
  Clusters 1–3 are exactly *missing such seams* — welded scheduled/dispatch
  boundaries with no injectable failure point.

This is a hypothesis to test, not a decision. Next session: take it into
`ideation` (the thesis shifts from "boundary I/O failure" to "agent-workflow
failure injectability"), then re-run Gate 0 with a re-tuned miner + boundary
catalog against this signal on ceal/charness.
