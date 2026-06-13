# pry — make the *injectability* of your code visible

> **Name.** `pry` — a lever you work into a seam to force it open, and also “to pry” as in
> probing where things are hidden. It encodes the thesis in one word: *no seam, nothing to
> pry* — un-testable code is code you cannot get a lever into. The companion to `nose`:
> where `nose` sniffs out duplicated *logic*, `pry` finds the boundaries welded into your
> logic where failures hide because nothing can reach in to test them. (`seam`, the
> Feathers term, is the honest alternative if a plainer name is ever wanted.)

> **One line.** Most catastrophic bugs live in error-handling paths, and those paths hide
> where code is *un-testable*. `pry` turns “testability” into a measurable, mechanical
> signal — **injectability** — maps where your repo is un-testable, flags the
> error-handling defects that already follow from it, and (later) turns the worst spots
> into seams so the repo gets better even if you stop using the tool.

This document is opinionated on purpose. It carries the problem framing and the prior art,
fixes the few things that must be fixed, and deliberately leaves the rest loose so that
**measurement, not a gantt chart, shapes what comes after Layer 0.**

-----

## 1. Why this exists

### 1.1 The Pareto bug source is error/failure handling

We are not guessing where the bugs are. The strongest empirical anchor is Yuan et al.,
*“Simple Testing Can Prevent Most Critical Failures”* (OSDI 2014), which read 198 randomly
sampled real production failures across Cassandra, HBase, HDFS, MapReduce, and Redis. The
finding: the large majority of *catastrophic* failures came from **incorrect handling of
errors that the software had already explicitly detected** — and most were reproducible
with tiny inputs (≤3 nodes). They distilled three syntactic rules into a static checker
(“Aspirator”) and found 100+ real, developer-confirmed bugs and bad practices across nine
systems.

So: error handling is the duplication-equivalent bottleneck — high frequency, high
severity, and (still) poorly served by tooling.

### 1.2 The deeper truth: those bugs hide where code is un-testable

The reason error paths are buggy is that they are rarely *exercised*. A normal-path test
suite walks straight past them. And the reason they are rarely exercised is structural: the
failing operation (a network call, a disk write, a clock read) is **welded directly into
the business logic**, with no point where a test can substitute a failure. No seam, no
test; no test, no coverage; no coverage, the bug ships.

### 1.3 The thesis

> **Testability is not a separate virtue. It is the observable shadow of modularity and
> coupling. Its mechanical proxy is *injectability*: is there a seam you can pry open at
> this boundary to substitute a failure?**

This is the move `nose` taught us, transferred — **mindset, not engine**:

|                             |`nose`                    |`pry`                                                  |
|-----------------------------|--------------------------|-------------------------------------------------------|
|Intangible target            |“duplication”             |“good design / testability”                            |
|Measurable semantic proxy    |behavioral equivalence    |injectability (seamed vs welded boundary)              |
|What today’s tools do instead|token overlap (jscpd)     |line/complexity metrics, “empty catch” lint (Aspirator)|
|The cheap independent oracle |differential interpreter  |fault injection at the boundary                        |
|Soundness lives in           |the exact channel         |the syntactic floor + injection oracle                 |
|Fuzziness lives in           |candidate / `near` scoring|the injectability *map* (a prediction)                 |

We borrow none of `nose`’s IL or value graph. We borrow its **way of choosing a problem**:
find a quality concern with a real semantic ground truth that current tools approximate
syntactically; **define the cheap independent oracle first**; keep soundness on the channels
that make a *claim* and keep fuzziness on the channel that makes a *prediction*.

### 1.4 What slips past today’s tools

The point is sharpest on code that every existing linter passes as clean.

**Python — a swallowed boundary failure on a mutation path:**

```python
def sync_user(user):
    user.credits -= COST                 # state mutation
    try:
        billing.charge(user.id, COST)    # network boundary
    except BillingError:
        log.warning("charge failed")     # swallowed, control falls through
    user.save()                          # mutation committed; the charge was not
```

ruff / pylint / flake8 are green: the `except` is non-empty (it logs) and is not a bare
`try/except/pass`; mypy is green. **pry** sees two things no linter does. *The map
(prediction):* `billing.charge` is a network boundary welded into `sync_user` with no seam
to substitute a failure — an un-testable failure path, flagged. *The floor (claim):* a
boundary error is swallowed and control then reaches a **commit that follows a mutation**
(`user.save()`) — “log-and-continue on a mutating path,” seen via lightweight dataflow
(*mutation → boundary failure → commit anyway*). The real bug: credits debited, charge
lost.

**TypeScript — partial failure with no compensation:**

```ts
async function placeOrder(order: Order) {
  await inventory.reserve(order.items);  // boundary 1: succeeds
  await payments.charge(order.total);    // boundary 2: throws — reservation never released
  await orders.save(order);
}
```

tsc and typescript-eslint are green: every call is `await`ed (`no-floating-promises`
passes), types are sound, there is no empty `catch`. **pry**: *the map* — all three calls
are welded to imported singletons, so the *failure interleaving* between boundary 1 and 2
is un-testable. *The floor / oracle* — if boundary 2 throws, boundary 1’s effect (the
reservation) is **never rolled back**: a partial failure leaves an inconsistent state, a
violation of an invariant (`reserved ⟺ saved`) that no linter checks. Layer 2 confirms it
by injecting a failure at boundary 2 and watching the invariant break.

The common move: linters read *syntax* (“is the catch empty? did you await?”) and pass.
`pry` reads *semantics* — **is the boundary behind a seam (map), and how does the failure
interleave with mutation and commit (floor/oracle)** — the same shift `nose` made from
tokens to “what does this compute.”

-----

## 2. What it is **not** (anti-goals)

- **Not another complexity/length metric.** Those have no semantic ground truth — the
  metric *is* the definition — and the literature shows basic structural metrics (LOC,
  size) are weak defect predictors (Walkinshaw et al., ESEM 2018, 100 repos; Ostrand &
  Weyuker). We pick a *semantic* signal precisely because the structural ones don’t carry.
- **Not a security/taint tool.** Injection/SSRF/secret-scanning is a red ocean (CodeQL,
  Semgrep). Different game.
- **Not a mutation-testing replacement.** charness already runs `cosmic-ray` (Python) and
  `stryker` (JS/TS). `pry` is **complementary and explanatory**: mutation testing asks
  “do your tests catch arbitrary code changes?”; `pry`’s injection oracle asks the
  narrower, semantic question “do your error paths preserve invariants under an injected
  failure *at a boundary*?” And the map explains *where surviving mutants concentrate* —
  un-seamed boundaries — so it makes your existing mutation score legible.

-----

## 3. North Star

Become the tool that makes a repo’s **testability gradient** visible and actionable, and
that converts the worst hotspots into seams — **such that the repo improves even if the tool
is then deleted.** The seams are the permanent asset; `pry` is the thing that found and
justified them.

**The predict/verify contract.** The map *predicts* risk (“this boundary is welded →
likely-buggy, definitely un-testable”). Injection *verifies* it (“inject here → invariant
holds / breaks”). The map is allowed to be a fuzzy prediction **only because injection can
falsify it.** That falsifiability is what keeps the map from degenerating into “yet another
score.” (Same discipline as `nose`’s oracle keeping the fingerprint honest.)

-----

## 4. The generative sequence (layers as centers, not a schedule)

Following the dependency structure (and Alexander’s unfolding-of-centers): each layer is a
**center** that the next one differentiates. The dependency runs one way — injection needs
seams, seams come from the map — so the order is *forced*, not chosen. Each layer stands
alone; **stop at any layer and the wholeness is preserved.**

- **Layer 0 — the center, ship first. Static map + syntactic floor.**
  Deterministic, language-cataloged, **no runner**. Independently valuable on day one:
  a testability/risk map *and* real error-handling bugs (the floor). This is the DTSTTCPW
  cut (Cunningham): the simplest thing that already works and already pays.
- **Layer 1 — unfold when Layer 0 is stable. Seam generation.**
  Propose/refactor each hotspot’s boundary behind a port/adapter (a DI seam). The output
  is an ordinary PR a human merges — **value independent of the tool.** AI proposes
  (exploration), human reviews (judgment) — charness’s “Human-Code-AI Symbiosis,” exactly.
- **Layer 2 — unfold when seams exist. The injection oracle.**
  Inject failures at seams, check invariants. The runner requirement is now **earned, not
  forced**: it runs only where Layer 0/1 already created a seam. The targeted, semantic
  cousin of the mutation testing you already run.

**Deliberately not specified now:** the internals of Layers 1–2. Pre-deciding them would
trade away flexibility for a false sense of progress. Layer 0’s measurements (which
boundaries, which welds, which floor rules actually correlate with your bugs) will shape
them. We let the center stabilize before differentiating it.

-----

## 5. Metric philosophy: where **zero** is the target, and where it is a category error

The single most important design decision. The tool has **two kinds of channels**, with
**two different disciplines** — this is `nose`‘s two-axis principle, and it is also exactly
charness’s “code keeps repeatable proof, AI handles exploration.”

**Claim channels → target ≈ zero false positives.**
The syntactic floor (empty catch; catch-all-then-abort; log-and-continue on a mutating
path; swallowed errors; Python bare `except`; an `await` in a `try` whose `catch` does
nothing) and, later, the injection oracle. A flagged welded-empty-catch or “injected a
failure here and an invariant broke” is a **fact, not a guess.** Aim for very high
precision; provide an inline ignore escape hatch (`# pry-ignore`), the way `nose` does.
This is where you are *right* to want zero — `nose` enforces zero false merges on its exact
channel, and reports zero violations.

**Prediction channel → zero is a category error.**
The injectability **map** is a *risk signal*, not a claim. Risk signals are judged by
**concentration / lift over a baseline**, never by zero-error. Forcing the map to “0
false-flags or 100% hit-rate” either collapses recall (it flags almost nothing) or is
conceptually confused about what a prediction is. The value of the map is the *ranking*: it
should pile error-handling defects into a small slice of the code far denser than chance or
than a churn baseline.

The research backs both halves. Defect concentration is real — a small minority of
files/methods carries the majority of defects (Ostrand–Weyuker; the Pareto-of-defects
literature) — **so a localizing map can have value.** But identifying that slice from basic
metrics is hard, and LOC correlates poorly with defect-proneness (Walkinshaw, 100 repos);
churn is better only at extremes. **So the map must earn its keep by beating churn** on
error-handling defects specifically. That is the bar — and it is why we validate before we
trust (§7), instead of assuming the signal is good because defects cluster.

-----

## 6. What counts as a boundary, and as a seam (the moat — per language)

Like `nose`’s per-language frontends, **the catalog is the engineering investment and the
moat.** Two pieces, both authored as *data* (auditable, extensible config), not buried in
code.

**Boundary catalog** — what crosses out of pure computation into the world:

- **Python:** `requests` / `httpx` / `urllib`, `open`, `socket`, `subprocess`, `os` / `os.environ`,
  `datetime.now` / `time.time`, `random`, DB drivers (`psycopg`, `sqlite3`, SQLAlchemy
  engine calls), cloud SDKs (`boto3`), file/network in the stdlib.
- **JS/TS:** `fetch` / `axios`, `fs` / `fs/promises`, `child_process`, `net` / `dns`,
  `Date.now` / `new Date()`, `Math.random`, `process.env`, DB clients (`pg`, `mysql2`,
  Prisma client calls), timers.

**Seam recognition** — is that boundary call reachable only through an *injectable
indirection* (a parameter, a constructor/closure dependency, a module-level patchable ref,
a DI container)? Or is it welded inline?

**Functional-core exemption (Bernhardt: functional core, imperative shell).** Pure code
needs no seam — you test it by passing inputs. We must **only** flag *boundary-crossing*
code that lacks a seam. Flagging a clean functional core as “un-testable” is the
false-positive that would discredit the tool (the negative-control failure in §7). This
exemption is load-bearing.

-----

## 7. The central risk (named honestly, not papered over)

> **Static injectability analysis in dynamic, untyped, monkey-patchable Python and JS is
> the make-or-break.** Resolving “where does this call go, and is it behind a seam” is hard
> precisely in the languages we target.

**Stance: conservative by default.** Flag only **high-confidence welded boundaries** —
accept lower recall to protect precision. A map that is quiet but trustworthy beats a noisy
one. The catalog grows from evidence (your own bug history), not speculation. We treat this
as the thing most likely to kill the project and validate it first (§8), rather than
discovering it late.

-----

## 8. Validation — the `nose` discipline, automated for the AI era

`nose` proved its claims with gold sets, cross-language convergence tests, and
precision/recall. Same regimen, one question:

> **Does the map’s flagged set concentrate *error-handling* defects more than a baseline?**

Git history is the label source — what Yuan et al. read by hand across 198 failures, we
mine automatically:

1. **Mine + label + SZZ.** Collect error-handling bugfix commits (diffs touching
   catch/except/retry/rollback/timeout/boundary calls); LLM-label them; SZZ-trace back to
   the **bug-introducing** commit.
1. **Temporal predictive validity.** At bug-introduction time, did the map already flag
   that location as welded/high-risk? (Did it predict the bug *before* it was a bug?) This
   is the strongest evidence, and the auto/at-scale version of Yuan’s manual study.
1. **Baselines to beat:** random, and **churn/LOC**. The literature says these are the bar
   and that beating them is non-trivial — so beating them is a real result.
1. **Negative control (the `nose` “sum vs product must NOT converge” analog).** Clean
   hexagonal / functional-core reference apps and high-quality, low-incident code must
   score **low**. High recall with no negative control is meaningless.
1. **Reuse labeled sets:** BugsInPy (Python); a hand-mined JS set / Defects4J-analog —
   filter to the error-handling subset.
1. **Internal consistency via Layer 2:** where seams exist, run injection and measure the
   **escaped-injection rate** (the surviving-mutant analog). The map score should correlate
   inversely with it.

**On the numbers (answering “why not target 0”, §5, operationally):** we do **not** set a
threshold a priori. Research gives the *evaluation frame* (defect concentration,
effort-aware lift), not a magic constant. We **measure the churn baseline first**, then set
the go/kill line as *lift over that baseline on error-handling defects*. Provisional, to be
filled after the baseline run:

> The map flags ≤ **N%** of LOC yet contains ≥ **M%** of error-handling bug sites, at
> ≤ **K%** false-flag on the negative control. `N / M / K` are set from the measured
> baseline, not invented.

-----

## 9. First experiment (DTSTTCPW applies to validation too)

Don’t build a benchmark suite first. Aim for **one number.**

- **One language to start: Python** (charness is ~97% Python — your own repos are the
  first, most honest corpus). Then 20–50 OSS repos.
- **Produce:** *“Z% of error-handling bugfix commits touched code the map pre-flagged, vs a
  churn-baseline of B%, at F% false-flag on the negative control.”*
- **Decision:** real lift over churn → thesis survives, unfold Layer 1. No lift → cheap
  kill or pivot the signal. **The experiment is designed to be able to kill the idea.**

**Reframe (from the premortem, §13).** The first experiment’s real purpose is *not* “is the
tool accurate.” It is **“does my repo even have this bottleneck”** — is there a testability
gradient, and does my product’s bug profile actually look like swallowed boundary failures
and missing rollbacks? The most likely way `pry` dies is not being wrong; it is being
*correct about a problem your repo doesn’t have much of.* So run it on **your** code first,
and let it tell you whether error-handling/testability is your bottleneck before building
anything more.

-----

## 10. Building it with Claude Code (in the charness idiom)

Dogfood through charness’s own loop — `ideation → spec → impl → quality → retro` — on your
own repos. Concrete first moves for Layer 0:

1. **Parse.** tree-sitter for Python + TS/TSX. Spans on every node so every finding traces
   to exact lines (the `nose` provenance discipline).
1. **Catalog as data.** Boundary + seam catalog as auditable config, not code. This is the
   moat; make it easy to extend per framework (FastAPI/Django, Express/Next) as evidence
   arrives.
1. **Dataflow-lite.** For each boundary call, classify **seamed vs welded**, conservatively
   (§7). Record *weld depth* (how many frames from the nearest injectable point) as a
   ranking input — but treat depth-weighting as a measured, not assumed, parameter.
1. **Syntactic floor (Aspirator-derived, then grown from your bug history).** empty catch;
   catch-all → abort/continue; log-and-continue on a mutating path; swallowed error;
   Python bare `except`; JS empty `catch`; un-handled `await` in `try`. High precision +
   `# pry-ignore` escape hatch.
1. **Emit.** Deterministic JSON + a human map (hotspots ranked by error-handling risk
   density) + SARIF for CI. **Determinism is a hard invariant** — byte-identical output
   across runs/threads/machines, like `nose`.
1. **Validation harness as a first-class module from day one** (the `nose-eval` analog):
   git-history miner + LLM labeler + SZZ + churn baseline + negative control. If validation
   is an afterthought, the thesis never gets tested.

**Packaging option:** once Layer 0 is real, ship it as a **charness skill** so the agent can
route to it (“check the testability hotspots in this repo”) underneath normal product
language.

-----

## 11. Open questions — to resolve by measuring, not deciding now

- Map **granularity**: call-site vs function vs file. (Method-level concentration is
  strong in the literature — likely function/call-site — but measure on *your* repos.)
- How to weight **weld depth** vs a flat seamed/welded bit.
- Do **test-only** monkeypatches already in use count a boundary as “seamed enough”?
- The exact per-language **floor rule set** — start from Aspirator’s three, grow from your
  own confirmed error-handling fixes.

Each of these is left open on purpose: the wrong time to fix them is before Layer 0 has
produced evidence.

-----

## 12. Lineage / prior art (so the philosophy is legible)

- **Yuan et al., OSDI 2014** — error handling as the catastrophic-failure Pareto; *Aspirator*
  is the syntactic floor we extend with an oracle.
- **Michael Feathers, *Working Effectively with Legacy Code*** — *seams*.
- **Hexagonal / ports & adapters (Cockburn); functional core, imperative shell (Bernhardt)**
  — every I/O passes through one injectable point; pure cores are exempt.
- **Defect concentration:** Ostrand–Weyuker (negative-binomial fault prediction);
  Walkinshaw et al., ESEM 2018 — the Pareto holds, but basic metrics are weak, so use a
  *semantic* signal and *validate it against churn*.
- **`nose`** — the mindset source: semantic ground truth + cheap independent oracle +
  two-axis (sound base, fuzzy candidate) + benchmark discipline + determinism.
- **Cunningham — DTSTTCPW**; **Alexander — generative sequence / unfolding of centers**.
- **charness** — Less Is More / progressive disclosure; Human-Code-AI Symbiosis; quality as
  a trust surface; the system gets smarter with use. `pry` is built in this grain, and is
  complementary to the mutation testing (`cosmic-ray`, `stryker`) already running there.

-----

## 13. Premortem (Klein) — it is one month later and pry is dead

Imagine it has already failed: a month in, `pry` is a 41-line report someone ran once in CI
and never opened again. Working backward from a foregone failure, here is *why* — ordered by
how likely each cause is, with the pre-commitment that defuses it.

**A. The repo-fit failures (most likely — this is how `pry` actually dies).**

1. **No gradient.** `pry`‘s value comes from *variation* — some boundaries seamed, some
   welded. But a corpus of simple scripts is *uniformly welded* (the map is all red — zero
   information: “scripts are like that, I know, I won’t fix it”), while mature code is
   *uniformly clean* (the map is flat). Either way it tells you nothing you didn’t know.
1. **Wrong bug profile.** It was tuned and validated on Yuan’s distributed-systems shape
   (“network boundary + state mutation + missing rollback”), but the actual bug profile was
   LLM orchestration, subprocess plumbing, prompt IO. Technically correct, and it still
   surfaced only the clean or the trivial — missing the one bar that matters: *meaningful
   bugs, meaningfully.*
   
   *Pre-commitment:* the **first corpus is your own repos, not OSS**, and week-one’s
   question is not “is the map accurate” but **“does my repo have a gradient and this bug
   shape at all.”** If not, that is a signal to change the *target*, not the tool — the
   bottleneck is elsewhere (see §9 reframe).

**B. The self-inflicted failures.**

1. **Skipped the kill-gate.** §8/§9 demanded “validate first, kill cheaply.” A month later
   the validation harness was “later” and never built — or it ran, the map *failed to beat
   the churn baseline* (exactly what the literature warned is hard), and that was
   rationalized instead of faced. The thesis was never once falsified, and a feeling does
   not earn adoption.
   
   *Pre-commitment:* build the validation harness **before** the analyzer, and write the
   kill line down — *“no lift over churn → stop”* — so a future, invested self cannot wriggle
   out of it.
1. **One map false-positive poisoned trust in the floor.** Internally we split “map =
   prediction, floor = claim” carefully — but users don’t read that distinction. Mixed in
   one report, a single absurd map flag (“this script is un-testable”) made someone conclude
   “this tool is wrong,” and the *accurate syntactic floor and injection oracle went down
   with it.* The fuzzy channel poisoned the sound channels on a shared screen.
   
   *Pre-commitment:* **physically separate** the outputs (different command / different
   report), and label the map “risk ranking, not a bug list” from the first pixel.
1. **Conservative defaults made it mute.** To protect precision we flagged only
   high-confidence welds; in dynamic, untyped Python most boundaries landed in “ambiguous”
   and *nothing came out.* The named central risk (§7) fired in the quiet direction — and a
   too-silent tool dies as fast as a too-noisy one.
   
   *Pre-commitment:* surface an explicit **“ambiguous” bucket** rather than silence, so the
   tool looks careful, not empty — and so the ambiguous set becomes the to-do list for the
   catalog.

**C. The structural / organizational failures.**

1. **It never entered the loop.** A tool you must remember to run is a tool you don’t run.
   It wasn’t wired into CI / the charness workflow / pre-commit, so it ran once at the demo
   and stopped. Half of “nobody uses it” is just “it wasn’t on by default.”
   
   *Pre-commitment:* redefine demo success as *“wired in and running automatically for two
   weeks,”* not *“the report looked good.”*
1. **The seam PRs (Layer 1) were never merged.** Even with a correct map, “make a port for
   one `requests` line in a script” read as over-engineering and was rejected. The
   tool-independent asset requires human consent, and `pry` failed to manufacture it.
   
   *Pre-commitment:* propose seams only where the map’s risk is high enough that the PR
   sells itself; never refactor for purity’s sake.
1. **The champion left.** The most common and most honest cause: you got pulled onto product
   work, the `nose` author shipped a flashier “reuse-the-engine” variant, and `pry` was left
   a philosophy exercise without a sponsor.
   
   *Pre-commitment:* keep the surface small enough that Layer 0 pays for itself in week one,
   so it survives without a full-time champion.

**The one-line takeaway.** `pry` almost certainly dies not because it is *wrong* but because
*your repo has little for it to catch.* So the first experiment’s job is less to validate
the tool than to **cheaply falsify whether error-handling/testability is even your
bottleneck** — before you build an elegant instrument that knocks on the wrong wall.

-----

*Name chosen: `pry`. The contract is: a sound floor, a falsifiable map, seams as the
permanent asset, and a first experiment built to tell you — cheaply — whether this is even
your bottleneck.*
