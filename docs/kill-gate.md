# Kill Gate — go/kill record

The one number(s) the Layer 0 experiment was built to produce, and the decision
they force. Two axes (F13): a **repo-fit axis** (harness-only, analyzer-free) and
a **tool axis** (the map's lift, only if the repo-fit axis clears). Methodology:
[`docs/spec-layer0.md`](spec-layer0.md). Frozen evidence under
`harness/fixtures/`.

---

## Run 1 — corpus: **charness** @ `3b9a2013` (2026-06-13)

### Repo-fit axis (Gate 0 — analyzer-free)

Labeling: **agent-driven, blinded, single-rater** (model `claude-opus-4-8`,
rubric `39d64e30`). The agent never knew it was grading for `pry` or that any
count mattered (F10 independence guard).

| signal | value | floor / bar |
|--------|-------|-------------|
| Candidates mined (error-handling bugfix shape) | 126 | — |
| **Confirmed error-handling bugfixes** (agent-labeled) | **7 / 126** | — |
| — of which high-confidence | **2** | — |
| SZZ-resolved bug *sites* (file, function) | 58 | ≥ 30 (raw) |
| **High-confidence bug sites** | **6** | **≥ 30 (F17, the honest floor)** |
| **P1b mining-recall** (non-matched bugfix commits that were real misses) | **1 / 40** | — |

**Verdict: RE-TARGET.** `repo_fit_axis = inconclusive → re-target`.

> 6 high-confidence sites (of 58 total) ≪ floor 30, and miner recall is adequate
> (1/40 missed). charness may not have this bug shape — pull `ceal` or change the
> target; **do not build the analyzer**.

### Tool axis

**Not evaluated** — killed at Gate 0. The thesis (does the *map* beat churn?) is
not the failure here; the repo simply lacks the bug shape. No Rust analyzer was
built. This is the cheapest possible kill (§9 reframe, §13 A.2).

### Why this is honest, not a too-strict artifact

- **Raw 58 vs high-confidence 6.** The raw site count *clears* 30 — but it is
  SZZ-noise-inflated: 7 fixes blamed across ~58 functions (≈8 functions per fix),
  because `git blame -w` on every pre-fix line catches context/unrelated lines.
  Gating on raw 58 would be the exact §13 B.1 wriggle ("we cleared 30!") on noise.
  The high-confidence floor (F17, added by the redesign critique) is what keeps
  the gate honest. By every clean metric — 7 fixes, 2 high-confidence fixes, 6
  high-confidence sites — charness is far below the floor.
- **Mining recall disambiguates the two §13 failure modes.** 1/40 non-matched
  bugfix commits were real error-handling fixes the lexical miner missed → the
  miner has high recall → the small confirmed count is the repo's truth, **not**
  miner blindness. So the verdict is *re-target the corpus*, not *re-tune the
  miner*.
- **The 7 are genuine pry-shape bugs** (a swallowed `yaml.YAMLError`; a cleanup
  error clobbering the real web-fetch failure; subprocess-crash paths treated as
  success; a mutated source tree left after a subprocess kill). The shape is
  exactly right — there are just very few of them in charness's history, whose
  "Fix…" commits are mostly validation gates, packaging/import fixes, and
  skill-orchestration changes.

### Decision

charness is **not** the corpus that tests the thesis. Per the pre-registered
plan (F3) the next move is **`ceal`** (2804 commits) — or a deliberate re-think of
whether the author's repos have this bug shape at all (§13 takeaway). **No
analyzer code is written until a corpus clears Gate 0.**

Evidence (frozen): `harness/fixtures/labels.json` (verdicts + confidence +
one-clause reasons, contestable via `git show <sha>` at corpus_head),
`label_verdicts.json` (raw agent transcript), `bug_sites.json`, `repo_fit.json`.

---

## Run 2 — corpus: **ceal** @ `bfb097fb` (2026-06-13)

Same analyzer-free gate, same blinded single-rater protocol (model
`claude-opus-4-8`, rubric `39d64e30`). Evidence under `harness/fixtures/ceal/`.

| signal | value | bar |
|--------|-------|-----|
| Python-touching commits (of 2804 total) | 135 | — |
| Candidates mined | **26** | (already < floor 30 before labeling) |
| **Confirmed error-handling bugfixes** | **2 / 26** | — |
| — high-confidence | **1** | — |
| SZZ bug sites / high-confidence sites | 5 / **2** | high-conf ≥ 30 (F17) |
| P1b mining-recall | **0 / 5** | — |

**Verdict: RE-TARGET.** 2 high-confidence sites ≪ floor 30; recall adequate
(0/5 missed). ceal is described as *"a surface-extensible organizational AI agent
runtime… Slack ingests messages, dispatches to agent workers"* — an
LLM-orchestration runtime. Its two genuine error-handling fixes are pry-shape (a
`ZoneInfoNotFoundError` boundary-lookup crash; a calendar-read-failure guard) but
there are only two. Tool axis not evaluated — killed at Gate 0.

---

## Cross-corpus synthesis (2 of 2 own-repos → RE-TARGET)

| corpus | what it is | confirmed EH fixes | high-conf sites | recall miss | verdict |
|--------|-----------|--------------------|-----------------|-------------|---------|
| charness | agent harness / skills tooling | 7 / 126 | 6 | 1/40 | RE-TARGET |
| ceal | organizational AI agent runtime | 2 / 26 | 2 | 0/5 | RE-TARGET |

**Both of the author's own repos lack the swallowed-boundary-failure /
network+mutation+rollback bug shape pry targets — and both are AI-agent /
LLM-orchestration tools.** High miner recall on both rules out miner blindness.
This is the §13 A.2 outcome, now confirmed twice: pry is *correct about a problem
these repos don't have much of.* Their real defect surface is LLM orchestration,
prompt/tool dispatch, and subprocess agent workers — not Yuan's distributed-
systems shape.

**The first experiment did its job (§9/§13): it cheaply falsified corpus-fit
before any analyzer was built.** The open strategic fork (needs the author):
1. **Pivot the target** — validate the *tool* on OSS repos that do have the shape
   (distributed systems / data pipelines), per §9's "then 20–50 OSS repos".
2. **Pivot the signal** — redefine the boundary catalog + bug shape for the
   *agent/LLM* domain (LLM API calls, prompt I/O, tool dispatch, subprocess
   workers) so pry targets the defect profile these repos actually have.
3. **Shelve** — accept that error-handling/testability is not the bottleneck for
   this author's repos and stop here (the honest cheap-kill outcome).

---

## Re-centering note (2026-06-13, post nose/cautilus study)

The fork was resolved live toward **pivot the signal**, reshaped (see
`docs/spec-layer0.md` F18–F24 and `docs/ceal-bug-profile.md` "Grounded outcome"):

- **The RE-TARGET verdicts above measured only the (a) axis** — does the
  *bug-history* match pry's swallowed-boundary shape (via SZZ). They do **not**
  speak to the **(b) testability-surface** axis — are these repos' boundaries
  *welded* (un-injectable)? — which is pry's literal thesis and was **never
  measured** (the map was never built or run on either repo).
- So "RE-TARGET" means "the (a)-lens does not fit these repos," **not** "pry has
  nothing to find here." ceal in particular is full of connector/provider/LLM
  boundaries (the cautilus-demand surface) that the (a)-gate never examined
  through the welded/seamed lens.
- **Next experiment: the (b)-axis testability-surface gate (F24)** — analyzer-free
  hand/script-sample of ceal's boundary sites, scoring welded-fraction +
  ambiguous-reason histogram + cautilus-demand lift, with a 3-way
  GO / EXTEND / KILL·HANDOFF verdict. Still **no Rust until a (b)-gate GO.**
