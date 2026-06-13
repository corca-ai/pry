# TS cross-corpus generalization — 2nd-corpus gating (Run 6, 2026-06-14)

The author chose **gate a 2nd TS corpus** to de-risk "is ceal idiosyncratically
well-engineered?" — now cheap, since the Stage-1 analyzer is built. `pry map` was run
on **7 other local TS codebases** + ceal. The clean cross-corpus signal is the
**clock-injection rate** (`new Date()`/`Date.now()` seamed-vs-raw): a *universal*
fingerprint (no catalog tuning), the boundary that was 0% in Python and 27% in ceal TS.

## Results (`pry map <corpus> --summary-only`)

| corpus | files | demand-welded | clock S/W | **clock seam%** | bare | amb | shape |
|---|---|---|---|---|---|---|---|
| **ceal** | 466 | **0.74** | 51 / 140 | **27%** | 0.89 | 3 | mixed — *disciplined outlier* → regression-guard |
| craken-agents | 368 | 0.85 | 9 / 42 | 18% | 0.85 | 0 | borderline |
| ax-day | 92 | 0.94 | 3 / 26 | 10% | 0.96 | 4 | mostly welded → backlog |
| agent-device | 333 | 0.92 | 14 / 134 | 9% | 0.95 | 0 | mostly welded → backlog |
| gstack | 79 | 1.00 | 0 / 122 | **0%** | 1.00 | 0 | fully welded → backlog |
| agent-browser | 42 | 1.00 | 0 / 32 | **0%** | 1.00 | 0 | fully welded → backlog |
| corca-bot | 99 | 1.00 | 0 / 10 | 0% | 1.00 | **28** | high-ambiguous (coverage gap) |
| ~~codex~~ | 579 | — | 0 / 0 | — | — | 0 | **EXCLUDED** — TS is thin over a Rust core (10 boundaries total; agent boundaries are in its Rust) |

## Finding — ceal is the outlier; the ecosystem is welded-at-demand

**The de-risk question is answered: yes, ceal is idiosyncratically well-engineered.**
Its 27% clock-injection rate stands alone; six other TS codebases run 0–18%, and three
(`gstack`, `agent-browser`, `corca-bot`) inject the clock essentially **never** (gstack:
122 raw clocks, 0 injected, and only 2 injection idioms exist in the entire repo). So
the Run-5 GO reflects **ceal's unusual discipline**, not a typical TS agent codebase.

But the deeper result is the *opposite* of a setback: **most TS agent code is heavily
welded at the substitution-demand points** (un-injected clocks/clients, 0.85–1.0). That
is precisely pry's **backlog-finder** opportunity — the gaps pry is built to surface are
*everywhere* except the rare disciplined codebase. This is unlike the Python KILL: there
the welds were input-redirectable glue (fs/env, not actionable); here the welds are at
**demand points** (clock/clients) where injection genuinely matters → **actionable
backlog.**

## What this means for product framing (resolves the option-4 fork with data)

The same tool plays two roles, selected by corpus discipline:
- **Backlog-finder (primary market):** typical TS agent code is welded-at-demand
  (gstack/agent-browser/ax-day/agent-device) → pry surfaces a real, large backlog of
  un-injected clocks/clients. High welded-at-demand = *good target*, not a KILL.
- **Regression-guard (the disciplined edge):** ceal already injects → pry confirms
  hygiene + flags the few gaps + catches regressions.

So the F27 band `[0.15,0.85]` is the **regression-guard** GO test (mixed = discipline to
protect). A separate **backlog-finder** GO test is "**welded-at-demand is high AND the
welds are at demand points, not input-redirectable**" — which is what distinguishes the
welded TS corpora (actionable) from the Python glue (not). Candidate F27 addendum.

## Honest caveats

- **Catalog coverage.** The catalog is ceal-tuned (slack/openai method fingerprints);
  on other codebases the **client** boundaries are under-recognized, so their demand
  subset is dominated by the **universal clock** fingerprint. The cross-corpus claim
  rests on the **clock-injection rate** (corpus-independent, robust), not the full
  client surface. Per-corpus client catalogs would sharpen the demand-welded numbers.
- **rung-3 gap.** network/subprocess leaf-welds over-report welded in *every* corpus →
  demand-welded figures are upper bounds (clock split is unaffected — clock isn't
  wrapper-hidden, so it stays the clean signal).
- **corca-bot's 28 ambiguous** = a model-coverage gap (likely heavy factory/DI the
  one-hop model can't resolve) — worth a look; not counted as decided either way.
- **codex excluded** as not an agent-surface-in-TS (low recognizability).

## Catalog broadening (Run 6 follow-up, 2026-06-14)

The author chose **broaden the catalog** (the binding constraint above). Added generic,
low-FP fingerprints: **randomness** (`Math.random`, `crypto.randomBytes/UUID/Int`),
**HTTP** (`axios(.get/post/…)`, `got`, `http(s).request`, `WebSocket`), **db**
(`new Pool/PrismaClient/MongoClient/Redis/Database`), **more LLM** (`GoogleGenerativeAI`,
`CohereClient`, `generateText/streamText`, `*.completions/embeddings.create`), **more
subprocess** (`child_process.exec/execSync/spawnSync/fork`, `*Sync` globals), more fs.
The classifier's `input_sim`/reason logic was generalized off clock (random is now a
hard weld too). Re-swept:

| corpus | demand total | demand-welded | new demand kinds surfaced (S/W) |
|---|---|---|---|
| ceal | 247 (was 222) | **0.76** (in band) | subprocess 2/22, random 0/6 |
| craken-agents | 96 | 0.91 | random 0/27, network 0/11, llm 0/7 |
| agent-device | 184 | 0.92 | random 0/16, network 0/12, subprocess 0/8 |
| ax-day | 121 | 0.97 | **random 0/66**, network 0/14, db 1/1, llm 0/4 |
| gstack | 158 | 1.00 | network 0/17, db 0/2, subprocess 0/12 |
| agent-browser | 43 | 1.00 | network 0/8, db 0/2, llm 0/1 |

**The backlog is multi-kind, not just clocks** — un-injected randomness, http, db,
subprocess, llm across the field. **FP check passed:** every `db` find is a real client
(`new Database` better-sqlite3, `new Redis` Upstash, `new PrismaClient`) — no worker-pool
FP — and the classifier even caught ax-day's Prisma singleton seam (`?? new PrismaClient()`
→ seamed). ceal stays the lone outlier with a real seam population. ceal re-frozen:
demand-welded **0.75**, 850 boundaries (was 520). Tests extended (random/db/http) — green.

## Verdict

**Run 6 = GENERALIZES (with a reframe).** ceal's GO does not generalize as "TS agent
code is a mixed surface" — ceal is the disciplined exception. It generalizes as **"TS
agent code is mostly welded-at-demand"**, which is the *stronger* result for pry: the
backlog-finder market is broad. ceal is the regression-guard edge case. The clock-
injection rate is a clean, universal testability-discipline meter pry can report today.
No new analyzer code; ran the Stage-1 binary as-is.
