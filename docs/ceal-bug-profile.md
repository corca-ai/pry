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

## Scope line: pry (static) vs cautilus (behavioral) — do not blur them

The clusters above are *behavioral* bugs. Whether ceal's scheduled workflow
**actually** aborts correctly, enforces a follow-up, or records the right
decision is a **behavioral / runtime** question — and that is
[`cautilus`](../../cautilus)'s job (it keeps agent/workflow *behavior* honest by
running bounded evaluation packets as prompts change). **pry must not chase
behavioral correctness — that is cautilus's lane.**

pry is **static**: it never runs the agent. Its only question about any boundary
is structural and answerable from the AST/imports alone — **is this boundary
welded inline, or reachable through an injectable seam?** So the recurring
clusters matter to pry *only* as a clue to *which boundaries* to catalog, not as
behaviors to verify.

## Implication for pry (the pivot-signal hypothesis) — kept strictly static

The thesis is unchanged: *injectability is the static shadow of testability.*
Only the **boundary catalog** would shift from Yuan's I/O primitives
(`requests`/`open`/`socket`) to the boundaries these repos actually cross:

- **Boundaries to catalog (static targets):** LLM/tool dispatch, Slack/provider
  SDK calls, scheduled-task / cron enqueue, subprocess agent-worker spawn,
  workflow-state store reads/writes.
- **Static map signal (prediction):** is that boundary call **welded inline**
  (constructed/imported/dispatched directly in the business function, no
  parameter/constructor/patchable indirection) vs **seamed**? Pure structural
  analysis — no execution, no behavioral claim.
- **Static floor signal (claim, Aspirator-style):** syntactic patterns only —
  e.g. a catalogued boundary call inside a `try` whose handler swallows; a
  boundary call followed by a state-store write in the same function with no
  intervening seam. Visible in the tree, not in behavior.

**The complementarity (why both tools exist):** pry statically finds the
boundaries that have **no seam** — and a boundary with no seam is *precisely one
cautilus cannot write a bounded failure-injection eval for*. pry surfaces (and
later, Layer 1, proposes) the seam; cautilus then exercises behavior *through*
it. pry makes the un-testable testable; cautilus tests it. They do not overlap.

This is a hypothesis to test, not a decision. Next session: take it into
`ideation` keeping pry **strictly static** (boundary catalog re-tune only; the
seamed/welded map + syntactic floor stay the whole deliverable — behavioral
verification stays with cautilus), then re-run Gate 0 with the re-tuned static
miner + catalog on ceal/charness.
