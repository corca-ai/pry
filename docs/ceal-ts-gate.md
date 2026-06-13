# (b)-gate — ceal **TypeScript** surface (analyzer-free, 2026-06-13)

The (b)-axis testability-surface gate (F24) run **analyzer-free, no build** on ceal's
**TS** agent surface — the corpus finding A pointed to (LLM/Slack/calendar boundaries
are 0 in ceal Python, all in TS). Chosen by the author as the cheap next step after
the Python gate's KILL·HANDOFF. Two-tier F18 rule applied (substitution bit +
`inputSimulation` tag). Corpus `8238b245`.

**This is a hand-sample with some aggregate-derived splits** (clock/client/fs ratios
from full-tree counts, not 1-by-1). Qualitative conclusions are solid; the headline
welded-fraction is **approximate (±)**. Tests excluded (`__tests__/`, `*.test.ts`,
`test/`, `*-test-support.ts`).

## Architecture (≠ the Python glue)

ceal TS is a real agent runtime, not CLI scripts: `connectors` (206 — slack 101,
github 46, notion 31, google-workspace 21), `ceal-agent` (153), `ceal-runtime` (86),
`ceal-core` (39). It has **two layers**: leaf SDK calls (fs/fetch/spawn/`new Date`)
*and* an **injected-abstraction layer** — and it practices real DI discipline.

**TS seam idioms found (the two-tier `externalSubstitution` SEAMED cases):**
- **inject-or-default client:** `this.webClient = config.webClient ?? new WebClient(config.botToken)` (`slack.ts:207`), `options?.client ?? new WebClient(...)` (`download.ts:142`), `input.clientFactory ? input.clientFactory(token) : new WebClient(...)` (`slack-search-public.ts:129`). The attr is ctor-param-fed → pry's **one-hop (`this.attr`←ctor param) catches it SEAMED**, same-file.
- **injected clock:** `input.now ?? new Date()` (pervasive — slack/agent/runtime ledgers), `function f(..., now = Date.now())` default param (`agent-runner-support.ts:169`), `now: () => new Date()` wired deps (`webhook-runtime.ts`, `main.ts`), `interface Clock { now: () => number }` (`identity-graph-store.ts`). **Clock is injected ~25% of the time** — the boundary that was the *unavoidable hard-weld* in Python.
- **injectable transport/executor interfaces:** `NotionHttpTransport`, github/notion host-executors, `executor.exec(command)` — **135** `*(Transport|Executor|Client|Gateway)` interface refs. The connector's own boundary is seamed when the transport is injected into it.

## Sample classification (two-tier F18)

| kind | population | substitution | input-sim | note |
|---|---|---|---|---|
| fs (`readFile/writeFile…`) | ~441 | WELDED ~all | YES | 119 direct `node:fs` imports, 0 injected stores → welded volume (= Python) |
| clock (`new Date()`/`Date.now()`) | **229** (excl. 59 `new Date(arg)`) | WELDED ~165 (**input-sim NO**) · **SEAMED ~64** | NO | **~25% injected** — real testability discipline; `new Date(arg)` ≠ boundary |
| env (`process.env`) | ~121 | WELDED ~all | YES | direct reads; some behind `runtimeConfigStore` |
| child_process (`spawn/exec`) | ~82 | WELDED (spawn `process.execPath`) + SEAMED (injected `executor`) | YES | host-executor abstraction = seam (but `.exec` isn't a catalogued leaf → the leaf inside is welded) |
| http (`fetch`) | ~12 | WELDED (global `fetch`) + SEAMED (notion `Transport`) | mixed | github does `fetch(request.url)` direct (welded); notion injects transport (seamed) |
| agent clients (slack/llm/calendar `.postMessage`/`.create`/`.events.*`) | ~50 calls | **majority SEAMED** (ctor-config/param client) + minority WELDED (`new OpenAI()` inline `tools/runtime.ts:61`, guardian-child module singleton) | YES | the cautilus-demand boundaries — **mostly already seamed** |

**Approx F24 metrics:** decided-fraction **~0.92** (NOT mute), welded-fraction
(substitution) **~0.89** (still **over the `[0.15,0.85]` band ceiling** — fs+env+raw-clock
volume dominates), **SEAMED population ~11–13% and real** (vs Python's ~5%, all in
3 subprocess wrappers), ambiguous low (one-hop catches same-file ctor/param DI).

## Reading — the decisive contrasts with Python, and the catch

1. **TS genuinely discriminates; Python did not.** Python was uniformly welded
   *everywhere* (clock 100% welded, zero client/clock injection — saturated glue). TS
   has a **real seamed population concentrated at the agent-demand boundaries**:
   clients injected (`config.webClient ?? new`), **clock injected ~25%**, transports
   injectable. The welded/seamed bit *carries information* here. This validates finding
   A's strategic direction: pry's thesis is **meaningful** on the TS agent surface.

2. **But the bare welded-fraction is fs-swamped in *both* languages** (~0.89 TS /
   0.95 Py, both over band). The high-volume low-value boundary (file I/O, input-
   redirectable) dominates the headline number regardless of language. This is the
   **strongest confirmation yet of the Run-3 recalibration candidate**: the bare
   welded-fraction band is the wrong GO test; the right test is **lens discrimination**
   (does the cautilus-demand subset split seamed/welded?). Under that lens test, **TS
   passes and Python fails.**

3. **The humbling catch: ceal TS is *already* testability-disciplined at its agent
   boundaries.** Because clients/clocks/transports are mostly already injected, pry's
   high-value find-rate (welded boundaries at cautilus-demand points) on ceal TS is
   **modest** — welds do NOT concentrate at demand points (low/negative cautilus-demand
   lift); they sit in the fs/env volume. pry would mostly **confirm good hygiene** and
   flag the *minority* un-seamed agent boundaries (the 3 inline `new OpenAI`, github's
   direct `fetch`, raw clocks on non-deterministic-sensitive paths) — a
   regression-guard role, not a large welded backlog.

## Catalog / model findings (carried)

- **`new Date(arg)` is NOT a clock boundary** (deterministic parsing) — only `new
  Date()`/`Date.now()` are. A TS catalog must distinguish arg-vs-no-arg, or it
  over-counts clock ~25%.
- **TS DI surfaces same-file** (ctor-param-attr, function param, lazy `??=`), so pry's
  existing leaf + 0-hop + one-hop model **transfers** — it catches the inject-or-default
  seams without needing the cross-file cliff. The architectural transport/executor
  layer shows up as *welded leaves in the impl file* (correct) + *under-counted*
  project-method wrappers (`executor.exec` — F22 rung 3, not ambiguous).
- A TS frontend is feasible on nose's model (nose supports TS), with a TS boundary
  catalog (fetch/fs/child_process/Date/timers/process.env + provider SDKs) and the
  `?? new` / default-param / ctor-config seam patterns.

## Verdict

**GO-lean under the lens criterion / formally EXTEND under the frozen criterion.**
By the *frozen* bare-welded-fraction band, ceal TS is **not a clean GO** (~0.89, over
ceiling — fs-swamped, same failure mode as Python). But the **lens** (cautilus-demand
subset) **discriminates** — TS has the mixed, DI-disciplined agent surface Python
lacked. This is a materially better result than Python's KILL·HANDOFF and **answers
the author's question: yes, the TS agent surface is where pry's thesis has traction.**
**No Rust built** (kill-cheaply holds).

The disciplined EXTEND step (not a build-commit): **re-run the (b)-gate with the
recalibrated lens-based criterion** (Run-3 candidate: GO = the cautilus-demand subset
discriminates, not the fs-swamped bare fraction), on a clean 1-by-1 TS sample, to get
a frozen GO/no-GO. Two findings temper any build decision: (1) the bare metric is
fs-swamped in TS too (fix the metric first), and (2) **ceal TS is already
well-seamed at its agent boundaries → pry's value here is regression-guard +
minority-gap-flagging, not a large backlog** — a bigger demonstration would want a
less-disciplined agent corpus.

## Refined strategic fork (needs the author)

1. **Recalibrate F24 to the lens criterion, then re-gate ceal TS** (clean sample) for
   a frozen GO → if GO, build the TS frontend. Highest-fidelity, still cheap.
2. **Build the TS frontend now** on the qualitative GO-lean signal (TS discriminates),
   accepting pry's ceal role is regression-guard + minority-gap.
3. **Find a less-disciplined agent/TS corpus** (or OSS) where agent boundaries are
   welded → a bigger backlog to demonstrate pry's find-value.
4. **Re-scope to regression-guard** — pry as a CI gate that flags *newly-welded*
   cautilus-demand boundaries (catches regressions in already-disciplined codebases
   like ceal), rather than a one-shot backlog finder.
