# Spec — Layer 0 + Validation Harness (build contract)

Canonical implementation contract for the first `pry` deliverable. Refines
[`initial-plan.md`](../initial-plan.md) §8–§10/§13 and
[`docs/roadmap.md`](roadmap.md) into something `impl` can execute without
rediscovering the problem. Acceptance bar lives in
[`docs/operator-acceptance.md`](operator-acceptance.md); this spec ties each of
its checklist items to a concrete check.

Status: **ready for `impl`** (architecture-corrected + critiqued — see
`Critique`). First slice: the **validation harness** (the falsifier), per
kill-gate discipline.

> **Architecture correction (2026-06-13).** An earlier draft put the LLM
> *intelligence* (commit labeling) inside a Python harness script that called the
> Anthropic API with its own key + a cost gate. That is the wrong shape — and it
> is exactly why implementation hit a "no credential" wall. The corrected model
> mirrors **`nose`**: a deterministic CLI with **zero intelligence** that emits an
> *advisory* signal as data, consumed by an **agent-run skill**. See `The two
> layers` and F1/F2/F10/F15.
>
> This solves the *credential* problem but **creates an independence problem** —
> the agent now both runs `pry` and grades it. Not a free win: it is paid for
> separately by **blinded, single-pass, monotone-subtractive** labeling with a
> **contestable transcript** and a **high-confidence floor** (F10/F16/F17). The
> §13 B.1 discipline that pre-registered the *analyst* knobs (`T`, budget unit,
> mute-gate) now also has to cover the *labeling* knob.

> **Signal re-centering (2026-06-13, post nose/cautilus study).** Gate 0 returned
> RE-TARGET on both own-repos — but it measured only the **(a) predictive** claim
> ("error-handling defects *cluster* in welded boundaries", via SZZ bug-history),
> not pry's deeper **(b) testability-surface** claim ("a welded boundary is one a
> failure *cannot be injected into*"), which is the literal thesis. (b) is
> structural and always valid; (a) = (b) ∧ a contingent breeding assumption these
> repos lack. So the map/floor are **not** invalidated by Gate 0 — only the
> (a)-lens is, for these repos. pry is re-centered on (b) as the **substrate**,
> with (a), error-path proximity, and **cautilus-demand** as pluggable
> prioritization **lenses**. The boundary catalog is **broadened (not swapped)**
> to every recognizable boundary; the static map + syntactic floor stay the whole
> deliverable. Mechanically the static/behavioral line *is* the local/whole-program
> line: pry decides what is cheaply, locally, honestly decidable and emits
> `ambiguous` (→ cautilus) for the rest. See `Seam classification & analysis
> depth`, `Extension ladder`, `Testability-surface gate`, and F18–F24.

## The two layers (load-bearing)

| Layer | What it is | Intelligence | Mirrors |
|-------|-----------|--------------|---------|
| **`pry` CLI (Rust)** | Deterministic analyzer. Emits the **map** (risk *advisory*) + **floor** (claims) as **data**. Never calls an LLM. | **None** | `nose` (`external_binary`) |
| **`pry` skill (agent-run)** | Runs *in the coding agent*. Consumes the CLI's map/floor; and for the validation experiment, **does the commit labeling itself** using the agent's own intelligence. | The coding agent | `quality` skill consuming `nose` |
| **harness mechanics (Python)** | `mine` / `szz` / `baseline` / `repo_fit` / `score` — git mining, blame, AST, scoring. Pure mechanism. | **None** | `nose`-eval scripts |

The intelligence is **the agent**, never a script holding a credential. No
harness component calls an LLM API or spends money.

## Problem

We do not yet know whether `pry`'s thesis holds *on this author's own code*: that
error-handling defects concentrate in welded (un-seamed) boundaries, denser than
a churn baseline. The most likely cause of death (§13) is **repo-fit** — building
an elegant instrument for a bottleneck the repo doesn't have. So Layer 0 must,
cheaply and falsifiably, produce **one number** and a go/kill decision — with
every analyst knob **pre-registered** so an invested future self cannot wriggle a
"no lift" result into a "go."

A "no lift"/null result has **two distinct meanings the verdict must keep apart**
(§13 A vs B): *repo-fit death* ("my repo has no gradient / not this bug shape →
change the target") versus *tool death* ("the map is weak or mute → fix or kill
the tool"). A single Z-vs-B number collapses them; the contract below keeps them
on separate axes.

## Current Slice

> **Update (signal re-centering, F18–F24).** Gate 0 (step 0 below, the **(a)-axis**:
> bug-history fit) ran → **RE-TARGET on both own-repos** (`docs/kill-gate.md`). The
> new gating experiment is the **(b)-axis testability-surface gate (F24)** —
> analyzer-free hand/script-sample on `ceal` — which Gate 0 never measured. Steps
> 1–3 below (the (a)/tool path) are unchanged; a **(b)-gate GO** unlocks them.

Reach the **kill gate**, in forced order:

0. **Repo-fit gate (harness-only, analyzer-free).** Before any Rust is written,
   establish from git history alone that charness *has the bug shape at all*: a
   non-trivial mined+labeled error-handling bug-site set (clearing a
   pre-registered floor) and a mining-recall sanity check. Labeling here is
   **agent-driven** (the agent reads each mined diff and applies the rubric). If
   this gate fails, **re-target or pull `ceal` earlier — do not build the
   analyzer.** The cheapest possible kill (§9 reframe).
1. **Validation harness** (Python mechanics + agent labeling) — the falsifier.
   Frozen labeled set + SZZ-resolved bug sites + churn/any-boundary baselines.
2. **Minimal analyzer = the MAP** (Rust + tree-sitter, **zero LLM**) — boundary
   catalog as data, conservative seamed/welded/**ambiguous** classification with
   a reported coverage denominator, deterministic emit.
3. **Join → the one number → go/kill** — run the map at the pre-registered split,
   score lift over baselines at equal #-function budget, gate against the
   mute-map ceiling, record the two-axis verdict.

The syntactic **floor**, SARIF, the `external_binary` manifest, and the formal
**`pry` skill package** complete **only on a "go"** — the map must earn them by
beating the baselines first (kill-cheaply).

## Fixed Decisions

| # | Decision | Why |
|---|----------|-----|
| F1 | **`pry` CLI = deterministic Rust analyzer with ZERO intelligence.** It parses Python via tree-sitter, spans on every node, and emits map + floor as data. It never calls an LLM. | Roadmap/handoff; the `nose` model. Determinism is the binary's hard invariant. |
| F2 | **Harness mechanics = Python**, deterministic only (`mine`/`szz`/`baseline`/`repo_fit`/`score`). Separate from the binary; never call an LLM. | git/blame/AST/scoring glue is natural in Python; keeps the binary's determinism contract clean. |
| F3 | **First corpus = charness**, then **ceal** as a second corpus. | §9: own repo, ~97% Python, most honest. (User-confirmed.) |
| F4 | **Label source = own-repo git history only** for the first number; BugsInPy deferred. | DTSTTCPW (§9). (User-confirmed.) |
| F5 | **Prediction grain = function-level**; record call-site spans as evidence; file roll-up is a trivial aggregation. | §11: method-level concentration is the literature's strong grain and matches SZZ blame resolution. |
| F6 | **First number = single temporal split** (not per-commit replay). Split `T` is **pre-registered by a mechanical rule before any map run**: `T` = the commit at the timestamp that splits the *mined+labeled* error-handling bug-site history **70% (pre, for churn) / 30% (post, as test labels)**. The verdict states Z is reported at this `T`, **not** as a max over a `T`-sweep. | Honest (no hand-picked split) and cheap (one analyzer run). |
| F7 | **Equal-budget comparison is by #functions flagged**, not LOC. The map flags `K` functions; each baseline gets the same `K`-function budget. Baselines: **(a) churn rank**, **(b) "all functions containing any catalogued boundary call"** (the decisive null), (c) random (optional). | §8 effort-aware lift; #functions is the decision unit; LOC budget lets large welded I/O functions inflate Z. |
| F8 | **Map and floor are physically separate** outputs (distinct subcommands → distinct files). Map labeled "risk ranking, not a bug list". `pry --version` exists for `external_binary` detection (mirrors `nose --version`). | §13 B.2 / operator-acceptance. |
| F9 | **The SZZ-resolved bug-site set is frozen** as `{repo SHA, fix commit, bug-introducing commit, file, fully-qualified function}` per site; the **scoring path reads only frozen files** (no live `git`). | The *scoring* is byte-reproducible; the *labels* feeding it carry irreducible noise — made contestable by F16 and bounded by F17, never silently called "ground truth". |
| F10 | **The labeler IS the coding agent**, NOT an API-calling script with a pinned model + cost gate. **Blinded + single-pass + monotone-subtractive:** the labeling worklist strips all pry-identifying framing (the agent labels commits as a generic defect study, *not knowing it serves pry* — the bias guard); the first number is labeled by **one agent, no parallel-subagent batching** (consistency); labeling can only **prune** the miner's recall-oriented candidate set to confirmed fixes, never *add* a site (a label cannot inflate past the floor). `labels.json` records the **driving model id (passed to `freeze --model-id`) + rubric hash**. No credential, no spend, no cost gate. | Intelligence = the agent (`nose` two-layer model); retires the API-labeler and dissolves the credential blocker. Blinding/single-pass/monotone are what stop the *agent* from re-opening the bias §13 B.1 closed for *analyst knobs*. |
| F11 | **Join key = file path + fully-qualified function name (module-qualified), resolved at commit `T`.** SZZ blame line ranges map back to `T`'s line ranges; matching is by qualified name, never raw line number. | The join is load-bearing; left implicit, impl would invent it and corrupt Z. |
| F12 | **The map reports a coverage denominator and the verdict is gated on it.** Output carries `seamed`/`welded`/`ambiguous` counts and the **decided fraction** = (seamed+welded)/total catalogued boundary calls. If the **ambiguous fraction exceeds a pre-registered ceiling** (default **0.60**), the verdict is **"map is mute (P3 fired) — not a go,"** regardless of Z. | §13 B.3: SC2's non-zero check guards silence, not muteness. |
| F13 | **The verdict is two-axis** (in `docs/kill-gate.md`): a **repo-fit axis** from harness-only signals (labeled-site count vs floor; mining-recall) and a **tool axis** (given a usable gradient, does the map beat the baselines, under the mute-gate). "No lift" routes to *change the target* vs *fix the tool* by which axis failed. The repo-fit axis now spans **two sub-axes**: (a) bug-history fit (Gate 0) and (b) testability-surface (F24). | §13 A vs B must stay separable. |
| F14 | **SZZ uses `git blame -w`** (ignore whitespace) and records each site kept/dropped; residual noise is acknowledged to bias Z **downward** (conservative — against the thesis). | Cheap honesty without research-grade SZZ machinery. |
| F15 | **Packaging = `external_binary` (Rust CLI) + a `pry` agent skill** (the intelligence layer), mirroring `nose` (external_binary) consumed by the `quality` skill. The CLI emits advisory data; the agent-run skill consumes it AND drives validation labeling. For Layer 0 the skill is **enacted by the agent inline** (run mechanics → label → score); the formal `SKILL.md` package + `integrations/tools/pry.json` manifest are deferred to the go path. | The user-confirmed architecture: CLI dumb, intelligence in the agent skill. |
| F16 | **Frozen, contestable label transcript.** `labels.json` carries, per commit, the verdict + confidence + one-clause reason, keyed to the frozen `corpus_head` + sha — so a skeptic re-runs `git show <sha>` against the frozen corpus and re-judges any label **without re-running the agent**. Labels are *auditable*, not byte-reproducible. | The label-producing step is the one non-deterministic link; a checked-in transcript makes it contestable instead of opaque. |
| F17 | **High-confidence floor + provenance caveat.** The repo-fit floor (P1) must be cleared by **high-confidence** sites only; borderline/low-confidence commits get a **refute pass** (a second judgment instructed to argue NOT-count). The verdict line (SC5) carries `n`, the high/med/low confidence breakdown, and a "self-labeled, blinded single-pass" caveat. | The rubric already collects confidence; this stops a margin-of-3 floor win being manufactured by low-confidence yes-votes. |
| F18 | **Seam definition (two-tier; finding C resolved 2026-06-13).** The headline **SEAMED/WELDED** bit answers the **`externalSubstitution`** question: is the boundary's *provider/endpoint/client* obtained in-band — a function **param**, a `self.attr` from an `__init__` **param**, or a **config/env-selected dependency the runner can swap for a controllable double** (`OpenAI(base_url=cfg)`, `subprocess([cfg.bin,…])`)? Else **WELDED**. A parameter that selects only the **operand/data** of a *fixed real* boundary (`open(args.out)`, `urlopen(args.url)`) is **WELDED** for substitution but recorded on a separate **`inputSimulation`-seam** tier (runner can redirect input / inject value-shaped failures). **Monkeypatchability / attribute-replacement never upgrades a site to SEAMED.** | Loose "any parameterized target = seam" degenerates on glue (everything is param-driven) — the monkeypatch trap's mirror. cautilus's `externalSubstitution` ("substitute at the same boundary the product uses") is *behavior* substitution (a runner-controlled endpoint/exe/client), distinct from `inputSimulation` (steering a fixed real boundary's data); the two-tier rule keeps them separate so welded-fraction discriminates and per-leg lift is measurable. |
| F19 | **Analysis depth = nose-grade local + exactly one bounded hop.** 0-hop (param/local via intra-function dataflow; module imports via one-level resolution) **+ one hop** `self.attr`→same-file same-class `__init__`. Beyond (cross-function, cross-file, factory return, dynamic dispatch, depth>1) → **`ambiguous`**, never guessed. | nose proves intra-fn dataflow + one-level import resolution are affordable, but *deliberately omits* `self.attr`→ctor — which pry's seam question (OOP agent runtimes) load-bearingly needs. The mute-gate (F12) backstops an over-tight cap. |
| F20 | **Lower to a thin pry-IR; analyze the IR, not raw tree-sitter nodes; manual walk, no `.scm` queries.** | nose's model (CST→normalized IL→manual visitor): decouples analysis from grammar specifics, expresses the one-hop resolution queries cannot, keeps determinism controllable. |
| F21 | **Boundary catalog = data (`catalog/python.toml`), broadened to all recognizable boundaries, each tagged with the cautilus verification *leg* it serves** (`externalSubstitution` / `triggerControl` / `inputSimulation` / `externalObservation`). Two forms: `construct` (resource constructors) + `direct_call` (module/builtin boundary calls). | Catalog precision ↔ required flow depth is a trade-off — rich leaf fingerprints keep analysis shallow. Flat names are data (unlike nose's hardcoded operator semantics); leg tags enable per-leg lift. |
| F22 | **Extension is a pre-registered ladder — evidence-gated, cheapest-first, with a principled ceiling — not open-ended.** Rungs 0 (now) → intra-file cross-function → depth k=2 → boundary-bearing propagation → (cliff) cross-file resolution → (≈never) type inference. A rung is **kept only if it converts ≥15%p ambiguous→decided** and does not raise floor FP; **ceiling** = the static/behavioral line (runtime-determined injectability → `ambiguous` → cautilus). | The one-hop cap is a hypothesis the gate measures (ambiguous fraction). "Prepared to extend" must not slide into a whole-program analyzer; rent rule + principled ceiling + determinism-erosion cost bound it. |
| F23 | **cautilus-demand is pry's actionability lens, evidence-grounded.** cautilus (built, eval-slice shipping) *requires the host* to expose controllable boundaries (its 4 verification legs) and only documents controlled-vs-not *reactively per-runner*; it has **no** static/exhaustive/ahead-of-time scorer. pry is that scorer; welded boundaries on `externalSubstitution`/`triggerControl` points = exactly where cautilus's legs fail. | Resolves the marginal-value question (①): pry is a structural pre-pass, not a convenience byproduct. Complementarity is non-overlapping by construction. |
| F24 | **Testability-surface gate (the (b)-axis gate) precedes any Rust**, analyzer-free hand/script-sample first (Gate-0 spirit). Metrics: recognizability, decided-fraction (mute-gate `< 0.40`), welded-fraction (band `[0.15, 0.85]`), **ambiguous-reason histogram**, cautilus-demand lift. Verdict is **3-way: GO / EXTEND / KILL·HANDOFF** (EXTEND routes to F22's ladder by the ambiguous-reason shape). Numbers **frozen per-run** (re-tunable between runs, never after seeing a run — §13 B.1). | Gate 0 tested (a) only; (b) was never measured. The reason-histogram steers extend-vs-ceiling. |
| F25 | **Dogfood the Python harness as a known-ground-truth calibration *control*, not a gate corpus.** The harness (`harness/*.py`: git/subprocess/file-I/O-heavy, every seam known to the author) is hand-sampled under the (b)-gate protocol **before ceal** — as the protocol **shakedown** (catch bad reason-codes / catalog gaps on code with ground truth) and a **welded-detection calibration**. It is **never** a gate-clearing signal: dogfooding is maximally non-independent (own tool · own code · own ground truth) → circular self-validation (the §13 B.1 / F10 independence concern). It also confirms substrate+lens: throwaway glue is welded-but-fine, so raw welded ≠ bad — only the lens makes it actionable. | Dogfooding strengthens a testability tool, but its value is discipline/fast-feedback/calibration, not the verdict; the verdict must rest on a corpus the author did not shape to pry's taste (ceal). |
| F26 | **Architecture self-application invariant.** pry's own implementation satisfies pry's own seam standard — its boundaries (source-file reads, catalog TOML read, output emit) are injectable/seamed, so pry is testable by its own definition. A testability tool that is not testable is self-refuting. Literal self-analysis is **deferred** (pry parses Python, not Rust; a nose-style tree-sitter-rust frontend would make it the literal proof someday). | pry's product *is* testability; its credibility collapses if its own implementation welds the very boundaries it flags. |
| F28 | **TS frontend build, staged (post-Run-5 GO).** Run 5's frozen lens GO on ceal TS reopens the Python-only Layer-0 scope (F3 / Non-Goals): the **first analyzer is built for TypeScript**, not Python, because that is where the (b)-thesis cleared the gate. Staged: **(1) minimal TS map** — Rust + tree-sitter-typescript, TS catalog (`catalog/typescript.toml`), leaf + 0-hop + one-hop seam classification + the two-tier `inputSimulation` tag, deterministic emit; goal = reproduce the ceal-TS lens hand-gate (**~0.74** demand-subset welded) with real output and enable analyzer-driven gating of further corpora. **(2) F22 rung-3 wrapper detection** (transport/executor interfaces) added **only after** the minimal map validates. **Stage 1 BUILT & validated (2026-06-13):** `pry map` (Rust + tree-sitter-typescript) reproduces the analyzer-free hand-gate — demand-subset welded **0.7352** (vs ~0.74), bare 0.8878, decided 0.9942 on ceal/packages — byte-deterministic (SC3), no LLM/HTTP deps (SC2), 3 classifier tests pass, pure I/O-free core (F26). See `docs/ceal-ts-gate.md` (Stage-1 section). | A GO means build the map (F24); the GO is on TS, so the map is TS. Staging keeps kill-cheaply alive into the build (validate the minimal map before adding the new rung-3 capability). Python remains a deferred second frontend. |
| F27 | **(b)-gate GO criterion recalibrated to the *lens* (Runs 3+4 finding; frozen before Run 5).** The bare welded-fraction `welded/decided` is **fs-swamped**: the high-volume, input-redirectable boundary (file I/O, env) is uniformly welded-but-cheaply-testable in *any* codebase, so the bare fraction trends `> 0.85` regardless (0.95 ceal-Py, ~0.89 ceal-TS) and does not discriminate. The GO test moves from the bare fraction to **lens discrimination on the substitution-demand subset.** Partition decided boundaries into **(i) input-redirectable** (`inputSimulation`-seam YES + value-shaped failures: file I/O, env, db-path, tz-key, url-as-data) — *excluded* from the GO test (welded≠bad, F25) — and **(ii) the substitution-demand subset** (leg `triggerControl`, or `externalSubstitution` on clock / provider-client / network-transport / subprocess — boundaries whose failure modes are **not** value-shaped, so only `externalSubstitution`/`triggerControl` reaches them). **GO** = subset is non-trivial (≥ floor) **and** discriminates (within-subset welded-fraction in `[0.15,0.85]` with a real seamed population). **KILL·HANDOFF** = subset trivially small (glue) or uniformly welded (no seam population). **EXTEND** = subset discriminates but a material part is `ambiguous` for a rung-resolvable reason. The bare fraction is retained as a reported *diagnostic*, not the gate. | The bare fraction measured file-I/O volume, not testability (confirmed on two corpora); the substrate+lens model (F25) says the *lens* is the product. This correctly KILLs ceal-Py (tiny, all-welded substitution-demand subset) and GOs ceal-TS (mixed) — a better metric, not a verdict-flip (it sharpens Py's KILL too). Between-runs tuning, frozen before Run 5 (§13 B.1). |

## Seam classification & analysis depth (the map's mechanics)

The map answers one structural question per catalogued boundary site: **is the
boundary obtained through a substitution point the *runner can use*, or welded?**
Grounded in `nose`'s shallow-analysis ceiling and `cautilus`'s substitution legs.

**Recognition (catalog, F21).** Lower each file to a thin pry-IR (F20), then match
boundary sites by leaf fingerprint resolved through **one-level import tracking**
(so `import openai`, `from openai import OpenAI`, `import requests as r` all
resolve — nose proves this affordable). Unrecognized boundaries (a project wrapper
hiding the leaf) are honestly **under-counted**, never guessed.

**Classification (F18/F19) — 0-hop + exactly one bounded hop:**

| callee / resource origin | resolution | class |
|---|---|---|
| function **param**, or local from a param | 0-hop (intra-fn dataflow) | **SEAMED** (DI) |
| param selects the boundary's **provider/endpoint/client** (`OpenAI(base_url=cfg)`, `subprocess([cfg.bin,…])`) | 0-hop | **SEAMED** (config-substitution) |
| param selects only the **operand/data** of a fixed real boundary (`open(args.out)`, `urlopen(args.url)`) | 0-hop | **WELDED** (subst.) + `inputSimulation`-seam tag |
| `self.attr` ← same-class `__init__` **param** | one hop (same file) | **SEAMED** (DI) |
| **inline construction** at site, or **imported module** direct call | 0-hop | **WELDED** |
| `self.attr` ← `__init__` **inline construction** | one hop | **WELDED** (ctor-chokepoint) |
| `self.attr` multi/conditional, no `__init__`, class spans files | cap exceeded | **AMBIGUOUS** |
| callee from a call (`get_x()`), cross-function/file, dynamic dispatch | not followed | **AMBIGUOUS** |

**Monkeypatch / attribute-replacement never upgrades a site to SEAMED** (F18) — it
reaches into internals, not "the same boundary the product uses". Each `ambiguous`
verdict carries a **reason code**; the reason *histogram*, not the bare fraction,
steers extension vs ceiling (F22/F24).

**Two-tier seam (finding C, frozen 2026-06-13).** Seam-ness is asked *per cautilus
leg*. The headline `SEAMED/WELDED` bit tracks **`externalSubstitution`** — can the
runner replace the boundary with an artifact whose *failure behavior it controls*
(an endpoint it runs, an executable it wrote, an injected client/transport/object)?
A parameter that merely steers a *fixed real* engine's data/location (a path, a
filename, a DB file, a url-as-data) does **not** grant behavior substitution (you
get only the value-shaped failure, e.g. not-found — not disk-full / partial-write /
dropped-connection); it is recorded as a separate **`inputSimulation`-seam** sub-tag,
never folded into the headline bit. The litmus: *can you make the boundary fail in
arbitrary ways via this parameter?* `base_url`→mock-server = yes (substitution);
`open(path)` = no, only path-shaped (input-sim). This keeps welded-fraction from
degenerating on parameter-driven glue and lets the gate report **per-leg lift**
(substitution-welded vs input-welded). The `inputSimulation`-seam set is itself a
product signal (the cheapest-to-test welds), not noise.

## Extension ladder (F22)

The one-hop cap is a hypothesis the gate measures (ambiguous fraction). If
insufficient, extend — but only as a pre-registered, evidence-gated, cheapest-first
ladder with a principled ceiling, never an open invitation to whole-program
analysis.

| rung | mechanism | cost | unlock signal |
|---|---|---|---|
| 0 (now) | 0-hop + `self.attr`→same-class `__init__` | lowest | — |
| 1 | intra-file cross-function (same-module `get_x()`, one hop) | low | ambiguous reason ≈ "same-file factory/helper" dominates |
| 2 | depth k=2 on existing mechanisms | low, decaying | rung-1 residual |
| 3 | boundary-bearing propagation (wrapper detection) | medium | hidden-wrapper under-count is material |
| 4 (cliff) | cross-file / cross-module symbol resolution | high; erodes determinism | ambiguous mass proven cross-module **and** pry value depends on it |
| 5 | type inference / points-to | prohibitive | ≈never (different tool) |

**Rent rule:** keep a rung only if it converts **≥15%p** ambiguous→decided and does
not raise the floor's FP rate. **Ceiling:** when injectability is runtime-determined
(dynamic dispatch, env-driven provider/plugin selection) it is *behavioral* — pry
emits `ambiguous` and hands off to cautilus. The ambiguous-with-reasons set is
itself a product: the cautilus handoff list + the refactor-candidate list.

## Testability-surface gate — the (b)-axis gate (F24)

Gate 0 tested (a) (bug-history fit) → RE-TARGET; it never measured (b). This gate
does, **analyzer-free first** (hand/script-sample N≈30–50 boundary sites on `ceal`,
Gate-0 spirit), before any Rust.

**Ordering (F25):** hand-sample the Python **harness first** — the protocol
shakedown + a ground-truth-known calibration *control* (not a gate corpus) — then
`ceal`, the independent gate corpus that carries the verdict.

Metrics: **recognizability** (catalog hit rate), **decided-fraction**
`(seamed+welded)/recognized` (mute-gate `< 0.40` → map mute), **ambiguous-reason
histogram** (steers the ladder), and — **the GO metric (recalibrated, F27)** —
**lens discrimination on the substitution-demand subset.** The bare welded-fraction
`welded/decided` is **fs-swamped** (file-I/O/env volume → always `> 0.85`; confirmed
on ceal-Py 0.95 and ceal-TS ~0.89) and is kept only as a reported **diagnostic**, not
the gate.

The substitution-demand subset (F27): decided boundaries with leg `triggerControl`,
or `externalSubstitution` on **clock / provider-client / network-transport /
subprocess** — i.e. boundaries whose failure modes are **not** value-shaped, so an
`inputSimulation` redirect can't reach them. The high-volume **input-redirectable**
boundaries (file I/O, env, db-path, tz-key, url-as-data — `inputSimulation`-seam YES,
value-shaped failures) are **excluded** from the GO test (welded≠bad, F25).

Verdict (numbers frozen per-run, re-tunable between runs, never after seeing a run —
§13 B.1):

- **GO** — decided ≥ 0.40; the substitution-demand subset is non-trivial (≥ floor)
  **and discriminates** (within-subset welded-fraction in `[0.15,0.85]` with a real
  seamed population) → the map separates seamed-good from welded-gaps where it matters
  → build the Rust map.
- **EXTEND** — the subset discriminates but a material part is `ambiguous` for a
  rung-1/2-resolvable reason → climb one ladder rung (F22) and re-measure (**not** a
  kill). (Also: mute, `decided < 0.40`, with resolvable ambiguous reasons.)
- **KILL · HANDOFF** — the substitution-demand subset is **trivially small** (glue,
  e.g. ceal-Py ~4% all-clock) **or uniformly welded** (no seam population), **or** mute
  with ambiguous mostly runtime/dynamic/cross-module (the ceiling = cautilus
  territory). Re-think pry for these repos.

## Labeling rubric (the intelligence the agent applies)

A mined commit COUNTS as an *error-handling bugfix* iff it **fixes a bug in
error-/failure-handling logic** — the handling of a failure the program
encountered or could encounter at a boundary (network, file/IO, subprocess, DB,
clock, randomness). Counts: fixing a swallowed exception, a wrong/missing
`except`, a missing rollback/cleanup after failure, a broken retry/timeout,
mishandling a boundary call's failure, log-and-continue on a path that should
abort. Does NOT count: new features, refactors, pure business-logic fixes with no
failure-handling aspect, test-only/docs/config/formatting changes, or adding
error handling to brand-new code (no prior bug). Per-commit verdict:
`{is_error_handling_fix: bool, confidence: high|medium|low, reason: <clause>}`.
The agent applies this rubric; a hash of this rubric text is frozen into
`labels.json` (F10). **Blinding (F10):** the worklist the agent reads contains
only `{sha, subject, diff}` — no "pry", "seam", "welded", or thesis framing — so
the agent grades a generic defect study. **Refute pass (F17):** any commit
labeled `low` confidence (or sitting within the floor margin) is judged a second
time under an instruction to argue it does *not* count; the surviving verdict is
frozen.

### Labeling protocol & `label_io.py` contract (deterministic, no LLM)

- **`emit`** writes a worklist JSON: a list of `{sha, subject, diff}` (diff capped
  at `config.LABEL_DIFF_CHAR_CAP`) for **every** candidate + the P1b sample
  (`non_matched_bugfix[:MINING_RECALL_SAMPLE]`). Blinded — no pry framing.
- **the agent** produces a verdicts file `{sha: {is_error_handling_fix,
  confidence, reason}}` by applying the rubric (single-pass; refute borderline).
- **`freeze --model-id <id>`** is a **pure schema validator** (never adjudicates
  correctness): it **refuses (exit non-zero)** unless *every* candidate sha and
  *every* P1b sha is present with `is_error_handling_fix ∈ {true,false}`,
  `confidence ∈ {high,medium,low}`, `reason: str` (completeness guard — a
  half-labeled run cannot silently undercount the floor). It writes `labels.json`
  in the **exact existing schema** `szz.py`/`repo_fit.py` already consume:
  top-level `{corpus, corpus_head, labeler_model, rubric_hash, labels}`, per-sha
  `{subject, date, group, is_error_handling_fix, confidence, reason}`,
  `group ∈ {candidate, recall_sample}`. (`rubric_hash` replaces the old
  `prompt_hash` field name; `labeler_model` ← `--model-id`.)
- **`config.py` keep-list:** `MINING_RECALL_SAMPLE`, `LABEL_DIFF_CHAR_CAP`, all
  paths, `REPO_FIT_SITE_FLOOR`, pathspec, regexes, `MINER_VERSION`. **strike-list:**
  `PRICING`, `LABELER_MODEL`, `LABELER_MODEL_FALLBACK`, `CHARS_PER_TOKEN`,
  `PROMPT_OVERHEAD_TOKENS`, `OUTPUT_TOKENS_PER_CALL` (cost-estimation only; used
  only by the retired `doctor.py`/`label.py`).

## Probe Questions

- **P1 — Does charness have the bug shape? (repo-fit, gate 0, harness-only.)**
  Answer = mined+labeled error-handling bug-site count vs the pre-registered
  floor (**default ≥ 30 SZZ-attributable sites**; below it → *underpowered →
  re-target*), plus **P1b** mining-recall: the agent labels a sample of
  *non-matched* bugfix commits to estimate error-handling fixes the lexical miner
  missed (a low match-count is only "no gradient" if recall is high). Written back
  to `harness/fixtures/repo_fit.json` + the repo-fit axis of `docs/kill-gate.md`.
- **P2 — What is the churn baseline `B` (and any-boundary baseline `A`)?**
  Measured before the map is trusted. Written to `harness/fixtures/baseline.json`.
- **P3 — How much lands in `ambiguous`?** Guarded by F12's coverage gate; the
  ambiguous set is the catalog to-do list. Written to the map output + tool axis.
- **P4 — Weld-depth weighting** vs a flat seamed/welded bit (§11): recorded as a
  measured ranking input. Written back to this spec once the first map output
  shows the depth distribution.

## Deferred Decisions (each names its reopen trigger)

- **Formal `pry` SKILL.md package + `integrations/tools/pry.json` external_binary
  manifest** (mirror `nose.json` consumed by `quality`). *Reopen when:* the
  verdict is "go". For Layer 0 the skill is enacted by the agent inline (F15).
- **Per-commit temporal predictive validity** (stronger than F6). *Reopen when:*
  the single-split number is a "go" and Layer 1 needs tighter evidence.
- **BugsInPy / cross-language (JS/TS) label sets.** *Reopen when:* own-repo number
  is a "go" and external generalization is in question.
- **Non-circular negative control:** also measure `F%` on charness functions
  demonstrably pure by an independent signal. *Reopen when:* `F%` materially
  drives the verdict.
- **Statistical confidence interval on (Z−B).** *Reopen when:* the first number is
  a marginal "go" near the floor (raw n + counts suffice otherwise).
- **Cross-machine/thread determinism diff** (downgraded — see Constraints).
  *Reopen when:* `pry` is wired into multi-runner CI.
- **Exact `pry`-binary no-LLM dep check command** for SC2 (e.g.
  `grep -Ei 'reqwest|hyper|anthropic|openai|tonic' Cargo.lock` must be empty).
  *Reopen when:* Slice 2 (the Rust map) lands — it belongs to that slice, not the
  current harness slice.
- **Layer 1 / Layer 2 internals**, **final per-language floor rule set.**
  *Reopen when:* the relevant layer is unfolded.
- **Boundary-bearing propagation** (wrapper detection, F22 rung 3) — deferred out
  of Layer 0 (needs cross-function resolution past nose-grade). *Reopen when:* the
  (b)-gate's ambiguous-reason histogram shows hidden-wrapper under-count is
  material and clears the F22 rent rule.
- **Test-only monkeypatch as standing evidence.** F18 settles the *general* case
  (monkeypatchability ≠ seam). Only the narrow question — does a *pre-existing*
  test-only patch count as evidence a site is de-facto seamed — stays open.
  *Reopen when:* the first map run shows pre-existing test patches would change a
  site's class.

## Non-Goals

- Not a complexity/length metric; not a security/taint tool; not a
  mutation-testing replacement (§2).
- Not OSS-corpus benchmarking yet — own repos first (§9/§13 A).
- Not Layers 1–2; not the runner (Layer 0 has no runner). *(JS/TS was a non-goal
  until the Run-5 GO; **TS is now the first frontend** per F28 — the GO landed there,
  not on the author's Python. Python frontend deferred.)*
- **No LLM intelligence inside the CLI or any harness script** — the agent is the
  only intelligence.

## Deliberately Not Doing (rejected, with reasons — so the branch stays closed)

- **API-calling labeler script with its own credential + cost gate** (the prior
  `label.py`/`doctor.py` design) — rejected: embeds intelligence + a credential
  in a script; that is the `nose` anti-pattern and caused the credential wall.
  The labeler is the agent (F10). `doctor.py` is retired.
- **All-Rust harness** — heavier git/agent glue, no determinism benefit for
  throwaway eval mechanics.
- **Pull BugsInPy now** — scope creep risking the kill-gate.
- **Per-commit temporal replay for the first number** — expensive; single-split
  (F6) is the cheap honest first cut.
- **File-level or call-site-only as the sole prediction grain** — function-level
  is the concentration grain and matches blame.
- **Building the full floor before the number** — violates kill-cheaply.
- **Bootstrap/Wilson CIs for the first number** — research-grade for n≈15–40.
  Substitute: report raw `n` + counts + the pre-registered n-floor.
- **Full SZZ hygiene** (`-C -M`, ignore-revs, per-site confidence) — substitute:
  `git blame -w` + the conservative-bias note (F14).

## Constraints

- **Determinism is a hard invariant on the analyzer**: byte-identical output
  across runs/threads on one machine (SC3). Cross-machine identity is a
  code-level invariant (no abs paths/timestamps/hashmap order; stable-sort; fixed
  float formatting) checked by inspection, not a cross-machine diff in Layer 0.
- **The CLI never calls an LLM**; **no harness script calls an LLM or spends
  money** — labeling is performed by the coding agent that runs the experiment.
- **Functional-core exemption is load-bearing**: only *boundary-crossing* code
  lacking a seam is flagged; a pure functional core scores low.
- **Two-channel discipline**: map = prediction (judged by lift); floor = claim
  (≈0 FP, `# pry-ignore`). Physically separate outputs (F8).
- **Boundary + seam catalog is *data*** (`catalog/python.toml`), not code.
- **Self-application invariant (F26):** pry's own implementation is seamed by pry's
  own standard — pry must be testable by its own definition.
- **No live `git` in the scoring path** — scoring reads frozen SZZ sites (F9).
- Toolchain present: `cargo`/`rustc` 1.93, `python3` 3.10.
- Charness durable artifacts under `charness-artifacts/` are repo state.

## Success Criteria

0. **Repo-fit gate runs first and is analyzer-free**, with **agent-driven
   labeling** (no script API call). The harness produces a mined+labeled
   bug-site count and a mining-recall result for charness *before* any analyzer
   code; below the floor the recorded verdict is *underpowered → re-target* and
   the analyzer is not built. (P1.)
1. The harness produces a **frozen, byte-reproducible** SZZ-resolved bug-site set
   (F9), churn baseline `B`, and any-boundary baseline `A`.
2. The analyzer (Rust, **no LLM**) parses charness Python, classifies boundary
   calls **seamed/welded/ambiguous** conservatively, reports the **coverage
   denominator**, and every finding traces to exact source lines.
3. Output is **deterministic** (byte-identical on repeat) and **map and floor are
   physically separate**, the map labeled "risk ranking, not a bug list".
4. The **negative control** (hexagonal core fixture) scores **relatively low**
   and a deliberately-welded twin scores **relatively high** (a *discrimination*
   smoke test — relative, not an absolute threshold).
5. The **one number** is produced with its honesty guards: *"Z% of post-`T`
   bug sites in the map's `K`-function flagged set, vs churn `B%` / any-boundary
   `A%` at equal `K`-function budget, at `F%` on the negative control, decided
   fraction `D%` (mute-gate `D ≥ 1−ceiling`), n = `<count>`"* — and a **two-axis
   go/kill decision** is recorded in `docs/kill-gate.md` (F13), Z at the
   pre-registered `T`.
6. On a **go**: the syntactic floor (≈0 FP + `# pry-ignore`), SARIF, and the
   formal `pry` skill + `external_binary` manifest exist.

## Acceptance Checks

| Criterion | Check |
|-----------|-------|
| SC0 | `label_io.py freeze` refuses unless every candidate + P1b sha is present (completeness guard); `labels.json` records `labeler_model` (from `--model-id`) + `rubric_hash`; `harness/fixtures/repo_fit.json` exists with `{labeled_site_count, high_confidence_site_count, floor, mining_recall_*}`. The floor is cleared by **high-confidence** sites (F17); below it the verdict reads `underpowered/inconclusive` and no `pry`/Cargo code is required. |
| SC1 | Re-running `score.py`/`baseline.py` on the frozen `bug_sites.json` reproduces byte-identical `B`/`A`/`F` (assert by running with the repo at a different HEAD → identical numbers; no live `git`). |
| SC2 | `pry map <charness>` emits per-function findings `{file, qualified_function, line span, class}` **and** a coverage block `{seamed,welded,ambiguous,decided_fraction}`; no LLM is invoked (grep the binary's deps — no HTTP/LLM client). |
| SC3 | `pry map <path>` run twice → `diff` empty. Map and floor are separate subcommands writing separate files; map output carries the "risk ranking, not a bug list" header. |
| SC4 | On `fixtures/negative_control/` the map flags **fewer** functions than on `fixtures/welded_twin/` (relative inequality in a harness test). |
| SC5 | `score.py` joins map output (run at the pre-registered `T`) against post-`T` frozen sites using the F11 key, emits `Z`/`B`/`A`/`F`/`D`/`n` **plus the high/med/low confidence breakdown and a "self-labeled, blinded single-pass" caveat** (F17), applies the F12 mute-gate, and writes the **two-axis verdict** (F13) to `docs/kill-gate.md`, naming `T` and asserting it was fixed before the map ran. |
| SC6 | (go path) `pry floor <path>` emits Aspirator claims with `# pry-ignore` honored; SARIF validates. The formal `pry` skill + `integrations/tools/pry.json` exist and `quality`/the skill can invoke `pry --version`. |

## Critique

Bounded fresh-eye critique on this **redesign completed** before finalizing (spec
step 7 + repo subagent-delegation policy). No forced debug interrupt was reported.

- **Execution:** ran. **Fresh-Eye Satisfaction:** `nested-delegated` (spec→critique
  parent delegated to fresh-eye subagents).
- **Target:** `spec-critique` (pre-impl lock-in of the architecture correction).
- **Angles:** Jackson (problem-framing), Weinberg (diagnostic), Gawande
  (operational) + one separate counterweight pass.
- **Central finding (all three converged):** the architecture fix solved the
  *credential* problem but re-opened an *independence* problem — the agent both
  runs `pry` and grades it, re-exposing the §13 B.1 bias the spec closed for
  analyst knobs.

Counterweight four-bin triage and disposition:

- **Act Before Ship (applied):** blinded worklist (F10) · contestable label
  transcript (F16) · high-confidence floor + verdict caveat (F17, SC0/SC5) ·
  `label_io.py` emit/freeze contract + exact preserved schema (Labeling protocol) ·
  `freeze --model-id` provenance source (F10/protocol) · freeze completeness guard
  (protocol, SC0).
- **Bundle Anyway (applied):** borderline refute-pass (F17) · `config.py`
  keep/strike list (protocol) · `freeze` is pure schema validation, never
  adjudicates (protocol).
- **Over-Worry (dropped, cheaper substitute):** full inter-rater / inter-batch
  calibration study → substitute = **forbid subagent batching, one agent labels
  all** (F10) + the borderline refute-pass · code restructure for monotone
  labeling → substitute = pin the monotone-subtractive property in one sentence
  (F10).
- **Valid but Defer (recorded):** exact `Cargo.lock` no-LLM dep-check command →
  Deferred Decision tied to the Slice-2 reopen trigger.

Provenance: `charness-artifacts/critique/2026-06-13-spec-layer0-redesign.md`.

## Canonical Artifact

This file (`docs/spec-layer0.md`) is the canonical build contract. Keep it
synchronized. The two-axis go/kill verdict lands in `docs/kill-gate.md`.

## First Implementation Slice

**The validation harness (the falsifier) — Python mechanics + agent labeling —
beginning with the analyzer-free repo-fit gate (Slice 0).**

```
harness/
  mine.py        # [built] git-mine charness -> candidates.json (+ non_matched for P1b)
  label_io.py    # [NEW, deterministic] `emit` dumps candidate diffs as a labeling
                 #   worklist; `freeze` validates agent-produced labels and writes
                 #   labels.json (records labeler model id + rubric hash). NO API call.
  szz.py         # [built] git blame -w + stdlib ast -> bug_sites.json (F11 key)
  baseline.py    # churn / any-boundary-call baselines (B, A) at split T
  repo_fit.py    # [built] floor + P1b -> repo_fit.json + repo-fit verdict
  score.py       # (slice 3) join map@T x frozen sites -> Z/B/A/F/D/n + two-axis verdict
  fixtures/      # candidates.json [built], labels.json, bug_sites.json, baseline.json,
                 #   repo_fit.json, negative_control/, welded_twin/ (slice 2)
```

**Retire** (architecture correction): delete `harness/label.py` (API path) and
`harness/doctor.py` (cost gate); strip pricing/model-API constants from
`config.py`.

**Build order:**
- **Slice 0 (repo-fit, analyzer-free, no spend):** `label_io.py emit` (blinded
  worklist) → **one agent labels** candidates + P1b sample in a single pass
  (refute borderline; no subagent batching) → `label_io.py freeze --model-id <id>`
  (completeness-checked, exact schema) writes `labels.json` → `szz.py` freezes
  `bug_sites.json` → `repo_fit.py` (high-confidence floor). If below floor, record
  *underpowered → re-target* and **stop** (or pull `ceal`).
- **Slice 1 (baselines):** `baseline.py` → `B`, `A`. Delivers the bars **before**
  any analyzer code — the un-wrigglable pre-commitment.
- **Slice 2 (minimal map — Rust, zero LLM):** Cargo scaffold + `pry --version` +
  a 3-line `pry map` smoke fixture first, then `catalog/python.toml`,
  seamed/welded/ambiguous classification with the coverage block, and the
  `negative_control`/`welded_twin` fixtures.
- **Slice 3 (the number):** `score.py` → honesty-guarded triplet + two-axis
  verdict → `docs/kill-gate.md` → go/kill.
