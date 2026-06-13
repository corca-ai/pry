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

---

## Run 3 — corpus: **ceal** @ `8238b245` — the (b)-axis gate (2026-06-13)

The testability-surface gate (F24), analyzer-free hand-sample, two-tier F18 rule
(finding C resolved, frozen before the run). Full evidence + sample table:
[`docs/ceal-b-gate.md`](ceal-b-gate.md). N = 59 non-test boundary sites, stratified
(net/db/tz exhaustive; file I/O / subprocess / clock / env sampled).

| metric | value | frozen bar | result |
|--------|-------|------------|--------|
| recognizability | ~1.0 | high | clears |
| decided-fraction | **1.00** (59/59) | mute-gate `< 0.40` | NOT mute (fully decidable) |
| welded-fraction (substitution) | **0.95** (56/59) | band `[0.15, 0.85]` | **OUT (high)** — bare bit non-discriminating |
| ambiguous | **0** | reason histogram | empty (no extend signal) |
| cautilus-demand lift (substitution) | ≈ **1.0** | > 1 | **no lift** (welded is uniform) |
| input-sim tier (two-tier) | welds YES 45 / **NO 11** | — | hard-welds concentrate **100% at clock** |

**Verdict: KILL · HANDOFF (substitution-ranker), "saturated-welded / glue" variant.**
ceal Python is procedural agent-tooling glue (zero `self.attr`-DI, zero
computed-targets, 1 injected callable — *structurally identical to pry's own
harness*). The bare seamed/welded map ≈ the any-boundary baseline (no lift) → fails
the frozen GO criterion. This is **decided-but-saturated-welded**, the *opposite* of
F24's "undecidable→cautilus" KILL rationale (a fourth outcome F24 didn't enumerate).
The two-tier lens recovers one small real signal — ~4% hard welds, all clock =
genuine cautilus substitution-demand — but it does not flip the headline verdict
(§13 B.1 anti-wriggle). **No Rust built.** Convergent with the (a)-gate RE-TARGET.

## Cross-axis synthesis (3 of 3 own-repo signals → not pry's corpus)

| run | corpus | axis | headline | verdict |
|-----|--------|------|----------|---------|
| 1 | charness | (a) bug-history | 6 high-conf sites ≪ 30 | RE-TARGET |
| 2 | ceal | (a) bug-history | 2 high-conf sites ≪ 30 | RE-TARGET |
| 3 | ceal | (b) testability-surface | welded 0.95 (no lift), decided 1.0 | KILL·HANDOFF (glue) |

Both pry axes now agree on the author's repos: **the Python is uniformly welded glue
that pry's thesis gets no traction on as a ranker, and the interesting agent
boundaries are TS** (finding A). The (b)-gate adds the precise mechanism: not "no
bugs" but "no *discrimination*" — ~94% of welds are cheaply input-redirectable
(already testable the way ceal's tests do it), only ~4% (clock) are true
substitution-demand. **The (b)-axis strategic fork (needs the author):** (1) a **TS
frontend** to reach ceal's real agent surface; (2) an **OSS non-glue Python corpus**
(§9) where boundaries are mixed; (3) **re-scope** pry's product to the two-tier lens
output (hard-weld + cautilus-handoff + cheap-test list), dropping the bare-bit ranker.
Still **no analyzer code** until a corpus clears a gate.

---

## Run 4 — corpus: **ceal TypeScript** — the (b)-axis gate (2026-06-13)

The author chose to gate ceal's **TS agent surface** (finding A: LLM/Slack/calendar
are 0 in Python, all in TS) as the cheap next step after Run 3. Analyzer-free,
no build, two-tier F18. Full evidence: [`docs/ceal-ts-gate.md`](ceal-ts-gate.md).
Hand-sample + aggregate-derived splits → welded-fraction is approximate (±).

| metric | value | vs Run 3 (ceal Py) |
|--------|-------|--------------------|
| decided-fraction | ~0.92 (not mute) | 1.00 |
| welded-fraction (substitution) | **~0.89** (over band, fs-swamped) | 0.95 |
| **SEAMED population** | **~11–13%, real, at agent boundaries** | ~5%, all in 3 wrappers |
| **clock injected** | **~25%** (`input.now ?? new Date()`) | **0%** (always hard-weld) |
| cautilus-demand lift | low (agent boundaries already seamed) | none (uniform weld) |

**Verdict: GO-lean (lens criterion) / formally EXTEND (frozen criterion).** ceal TS is
a real, DI-disciplined agent runtime — clients injected (`config.webClient ?? new`),
**clock injected ~25%**, transports injectable (135 interface refs). The welded/seamed
bit **carries information** here; pry's thesis is **meaningful on the TS surface** —
the opposite of Python's saturated glue. **This answers the author's question: yes,
TS is where pry has traction.** No Rust built.

Two honest catches: (1) the bare welded-fraction is **fs-swamped in *both* languages**
(~0.89 TS / 0.95 Py, both over band) → strongest confirmation that the **bare-fraction
band is the wrong GO test; the lens (cautilus-demand subset) is** (TS passes it, Python
fails). (2) ceal TS is **already well-seamed at its agent boundaries** → pry's
find-value on ceal is **regression-guard + minority-gap-flagging, not a large backlog**.
pry's leaf+0-hop+one-hop model **transfers to TS** (DI is same-file ctor/param). Catalog
finding: `new Date(arg)` ≠ clock boundary.

---

## Run 5 — corpus: **ceal TypeScript**, clean re-gate under the lens criterion (2026-06-13)

Author chose recalibrate-then-re-gate. F27 (lens criterion) frozen **before** this run.
GO test = the **substitution-demand subset** (clock/clients/network/subprocess) only,
classified **1-by-1**. Full evidence: [`docs/ceal-ts-gate.md`](ceal-ts-gate.md) Run 5.

| metric | value | F27 bar | result |
|--------|-------|---------|--------|
| substitution-demand welded (pry leaf model) | **~0.74** | band `[0.15,0.85]` | **IN BAND**, real ~26% seam pop |
| same, architectural (DI resolved) | ~0.55 | — | rung-3 gap = 0.74→0.55 |
| bare welded (diagnostic) | ~0.89 | — | fs-swamp, correctly excluded |
| decided-fraction | ~0.92 | mute `<0.40` | not mute |

**Verdict: GO** (lens criterion) — **the first GO in five runs.** The substitution-demand
subset discriminates (welded 0.74, in band, seams concentrate in the testable core;
clock 6S/15W, slack clients param/ctor-injected, LLM inline-welded). pry's existing
leaf+0-hop+one-hop model **catches** the clock/client seams (same-file DI). **EXTEND
rider (evidence-backed):** pry under-detects **network + subprocess** seams (injected
transport/executor wrappers one hop up behind non-catalogued `.request()`/`.exec()`) →
needs **F22 rung-3 wrapper detection** for TS accuracy (not a GO blocker). **No Rust
built.** Catalog finding: `new Date(arg)` ≠ clock; DB in TS = 0.

## Cross-axis + cross-language synthesis (5 runs)

| run | corpus | axis/lang | headline | verdict |
|-----|--------|-----------|----------|---------|
| 1 | charness | (a) Py | 6 hi-conf sites ≪ 30 | RE-TARGET |
| 2 | ceal | (a) Py | 2 hi-conf sites ≪ 30 | RE-TARGET |
| 3 | ceal | (b) Py | welded 0.95, no lift, glue | KILL·HANDOFF |
| 4 | ceal | (b) TS | bare welded ~0.89, mixed (fs-swamped metric) | GO-lean / EXTEND |
| 5 | ceal | (b) TS | **lens: demand-subset welded ~0.74, in band, discriminates** | **GO** |

The five runs converge on a clear map: **the author's *Python* is glue pry can't rank
(a- and b-axis agree → KILL); the author's *TS* agent runtime is the surface where
pry's (b)-thesis holds (lens GO).** The recalibration was decisive — the bare fraction
was fs-swamped (0.89), the lens demand-subset discriminates (0.74). pry's seam model
transfers to TS; the one new capability the TS surface demands is **F22 rung-3
wrapper detection** (transports/executors). **The open decision (needs the author):**
a frozen GO means *build the Rust map for TS* (reopens the Python-only Layer-0 scope) —
commit to the TS-frontend build (with rung-3 in scope) or pause. Still **no analyzer
code** until that call.
