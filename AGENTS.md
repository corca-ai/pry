# Agents

## Project

`pry` is a static-analysis tool that makes the *injectability* (testability) of
code visible: it finds boundary calls (network, file I/O, clock, randomness, DB,
subprocess) "welded" into business logic with no seam to inject a failure,
concentrating on error-handling paths where defects cluster. See
[`initial-plan.md`](initial-plan.md) for the full design thesis and
[`docs/roadmap.md`](docs/roadmap.md) for ordered priorities.

**Implementation: Rust.** `pry` is a standalone binary built in this repo and,
like its sibling [`nose`](https://github.com/corca-ai/nose), distributed as a
prebuilt release and wired into charness as an `external_binary` that the
**`quality`** skill invokes — it is *not* a Python charness skill. Parsing uses
tree-sitter's Rust bindings. (This is the concrete form of `initial-plan.md`
§10's "packaging option".)

Current state: **product-shape build, post-measurement.** The Rust binary ships
`pry map` (welded/seamed classifier), `pry floor` (swallowed-failure claim
channel), and `pry untested` (welded∧untested worklist). A 25-repo validation
harness ran four pre-registered honesty-gated experiments; all four came back
honest negatives for a *generalizable OSS* prioritization claim (see
`docs/eval-gate.md`). That refocused pry on its actual north star: **dogfood on
the author's own products** via a per-repo `.pryconfig.toml` (in progress). Read
`docs/handoff.md` (the live trigger + slice state) and `docs/roadmap.md` before
starting implementation.

## Skill Routing

At session startup in this repo, call the shared/public charness skill `find-skills` once before broader exploration.

Use its capability inventory as the default map of installed public skills, support skills, synced support surfaces, and integrations.

When a request names a workflow or capability noun such as worktree, browser automation, specdown, or validation, ask the `find-skills` skill to recommend a route for the task before ad hoc shell or tool use; recommendation-shaped probes are read-only by default, while plain inventory refreshes own `charness-artifacts/find-skills/latest.*`.

After that bootstrap pass, choose the durable work skill that best matches the request from the installed charness surface.

External URLs or source links that should become working context for this repo route through `gather` before summarizing, implementing, or deciding from them.

Validation-shaped closeout or operator reading test requests go through `quality` validation recommendations before HITL or same-agent manual review.

Keep this block short. Detailed routing belongs in installed skill metadata and `find-skills` output, not in a long checked-in catalog.
## Commit Discipline

- Commit meaningful work slices as they finish; keep each commit scoped to one
  understandable unit instead of one giant end-of-run commit.
- Treat meaningful `charness-artifacts/` changes as repo state and commit them
  with the work they support.
- Do not report a task-completing goal as done while meaningful implementation,
  workflow, or artifact work remains uncommitted, unless the deferral is
  explicit. The two policies differ: artifact changes are commit targets, and
  implementation/workflow slices are committed as they finish.
## Subagent Delegation

- Repo-mandated bounded fresh-eye subagent reviews are a standing delegation
  request. Canonical scopes: task-completing `setup`, `quality`, `critique`,
  `release`, and GitHub `issue` resolution/closeout review runs. Report a host
  block explicitly; same-agent substitutes are forbidden.
- When a skill or repo adapter owns a subagent review, follow that adapter's
  reviewer tier and concrete spawn fields instead of inheriting the parent
  turn's host defaults or improvising a generic reviewer. For Codex critique
  reviewers, the adapter resolves the high-leverage tier to medium reasoning
  effort unless it says otherwise; that is a per-adapter default, not a claim
  that every subagent is medium. If the required adapter or tier cannot be
  applied, stop and report the concrete signal.
