# Handoff

## Workflow Trigger

**The §13 strategic fork is RESOLVED — do not re-open it as a discussion.** It was
worked live toward the user's lean (**pivot the signal**) and *reshaped well beyond*
the handoff's original "catalog swap" into a full **(b) testability-surface
re-centering**. The contract is now in [`docs/spec-layer0.md`](spec-layer0.md)
(F18–F24 + three new sections). Read those first.

**Five gate runs → first GO → first analyzer BUILT & validated.** The author's
*Python* is glue pry can't rank (Runs 1–3 → KILL); the author's *TS* agent runtime is
pry's surface (Run 5 → GO, lens criterion). The author then chose **build the minimal
TS map (staged)**, and it's done: **`pry map` (Rust + tree-sitter-typescript)
reproduces the hand-gate** — demand-subset welded **0.7352** (vs ~0.74), deterministic,
zero-LLM, tested. **First action: DECIDE what's next** — stage-2 rung-3 / gate a 2nd TS
corpus with the now-built analyzer / wire packaging (below).

**Run 3 — ceal Python (b)-gate → KILL·HANDOFF (glue)** ([`docs/ceal-b-gate.md`](ceal-b-gate.md);
[`kill-gate.md`](kill-gate.md) Run 3). N=59 sites: decided **1.00**, welded **0.95**
(out of band), substitution lift **≈1.0** (none). Procedural glue, structurally
identical to pry's own harness; ~94% input-redirectable, ~4% hard-weld (clock).

**Run 4 — ceal TypeScript (b)-gate → GO-lean / EXTEND** ([`docs/ceal-ts-gate.md`](ceal-ts-gate.md);
[`kill-gate.md`](kill-gate.md) Run 4). ceal TS is a real DI-disciplined agent runtime:
clients injected (`config.webClient ?? new`), **clock injected ~25%** (the boundary
that was 0%/hard-weld in Python), 135 injectable transport/executor interfaces. The
welded/seamed bit **carries information** — pry's thesis is **meaningful on TS**. Two
honest catches: (1) the bare welded-fraction is **fs-swamped in *both* languages**
(~0.89 TS / 0.95 Py, both over band) → the **bare-fraction band is the wrong GO test;
the lens (cautilus-demand subset) is the right one** (TS passes, Py fails); (2) ceal TS
is **already well-seamed at its agent boundaries** → pry's role there is
**regression-guard + minority-gap-flagging, not a large backlog**. pry's
leaf+0-hop+one-hop model **transfers to TS** (DI is same-file ctor/param). Catalog
finding: `new Date(arg)` ≠ clock boundary. Welded-fraction is approximate (hand-sample
+ aggregate splits) — a frozen number needs a clean 1-by-1 re-gate.

**Run 5 — ceal TS, clean re-gate under the lens criterion (F27) → GO** ([`docs/ceal-ts-gate.md`](ceal-ts-gate.md)
Run 5; [`kill-gate.md`](kill-gate.md) Run 5). Substitution-demand subset (clock/
clients/network/subprocess), classified 1-by-1: welded **~0.74** (pry leaf model,
**in band**) / ~0.55 (DI-resolved), bare-diagnostic ~0.89 (fs-swamp, excluded). The
**first GO in five runs.** Seams concentrate in the testable core (clock 6S/15W with
injected `input.now`; slack clients param/ctor-injected); welds in worker-command
stamps + inline LLM clients. pry's leaf+0-hop+one-hop model **catches** clock/client
seams (same-file DI). **EXTEND rider (evidence-backed):** pry under-detects **network
+ subprocess** seams (injected transport/executor wrappers behind non-catalogued
`.request()`/`.exec()`) → needs **F22 rung-3 wrapper detection** for TS accuracy (not
a GO blocker). Catalog finding: `new Date(arg)` ≠ clock; DB in TS = 0.

**Stage-1 minimal TS map — BUILT & validated (F28)** ([`docs/ceal-ts-gate.md`](ceal-ts-gate.md)
Stage-1 section). `pry map <path>` + `pry --version`; Rust + tree-sitter-typescript;
`catalog/typescript.toml` (data); leaf + 0-hop (`??`/default-param/local-decl/param-
receiver) + one-hop (`this.attr`←ctor) classification + two-tier `inputSimulation`
tag; deterministic JSON. On ceal/packages: demand-subset welded **0.7352** (vs hand
~0.74), bare 0.8878, decided 0.9942, 457 files. Byte-deterministic (SC3), no LLM/HTTP
deps (SC2), pure I/O-free core + 3 tests (F26). Per-kind: clock 51S/135W, slack
5S/3W/**3 amb**, subprocess 2S/8W, llm 0S/3W, **network 0S/12W (leaf — rung-3 gap)**.
Frozen evidence: `fixtures/ceal-ts-map.summary.json`.

**The next decision (needs the author):**
1. **Stage 2 — F22 rung-3 wrapper detection** (transport/executor interfaces): the
   3 ambiguous slack receivers + leaf-welded network/subprocess are the evidence-backed
   rung-3 work; resolves leaf-0.74 toward the true ~0.55.
2. **Gate a 2nd TS corpus** with the now-built analyzer (cheap, analyzer-driven) — de-risk
   "is ceal idiosyncratically well-engineered?" before more building.
3. **Wire packaging** — `external_binary` manifest + the `pry` agent skill (the F15
   path), so `quality` can invoke `pry`.
4. **Product framing** — settle backlog-finder vs regression-guard (shapes the map's
   output + skill).
- **Finding C — RESOLVED 2026-06-13 (two-tier F18).** Headline SEAMED/WELDED =
  `externalSubstitution`; operand-parameterization = WELDED + `inputSimulation`-tag.
- **Finding A — CONFIRMED.** ceal Python = file/subprocess/clock glue (agent-API 0);
  ceal TS = the agent surface (clients/clock/transports, DI-disciplined).

If validation-shaped closeout is needed, route through `quality` per CLAUDE.md.

## Current State

- **(b)-gate → GO → analyzer BUILT (Runs 3–5 + Stage-1, this session).** Finding C
  resolved (two-tier F18). **Run 3 ceal Python → KILL·HANDOFF (glue)**. **Run 4 ceal
  TS → GO-lean** but surfaced the bare-fraction **fs-swamp** → **F24 recalibrated to
  the lens criterion (F27, frozen first)**. **Run 5 ceal TS clean re-gate → GO** (the
  first GO). Then **Stage-1 minimal TS map BUILT (F28)**: `pry map` (Rust +
  tree-sitter-typescript) reproduces the hand-gate (demand-subset welded **0.7352** vs
  ~0.74), byte-deterministic (SC3), zero-LLM (SC2), pure I/O-free core + 3 tests (F26).
  Evidence: `docs/ceal-b-gate.md`, `docs/ceal-ts-gate.md`, `docs/kill-gate.md` Runs
  3–5, `fixtures/ceal-ts-map.summary.json`. **First real analyzer code shipped**;
  next decision = stage-2 rung-3 / 2nd corpus / packaging.
- **Design seq #1–#5 complete and formalized** (this session): seam definition,
  catalog-recognition + analysis-depth model, extension ladder, the (b)-gate, and
  the cautilus-demand lens. All in `docs/spec-layer0.md` F18–F24 + sections
  *Seam classification & analysis depth*, *Extension ladder*, *Testability-surface
  gate*. Cross-doc updates in `kill-gate.md` and `ceal-bug-profile.md`.
- **Key reframe:** pry re-centered on **(b) testability-surface** (welded = can't
  inject a failure) as the substrate; **(a) bug-history**, error-path proximity,
  and **cautilus-demand** are pluggable lenses. Gate 0's RE-TARGET killed the
  (a)-lens for these repos, **not** pry — the (b) map was never measured.
- **cautilus is BUILT** (`../cautilus`, Go+JS, eval-slice shipping). Its 4
  verification legs (`externalSubstitution`/`triggerControl`/`inputSimulation`/
  `externalObservation`) are the concrete demand signal; ceal is its primary
  consumer. pry = the static, ahead-of-time **runner-readiness scorer** cautilus
  lacks (F23). Complementarity is non-overlapping by construction; mechanically the
  static/behavioral line = the local/whole-program line.
- **nose study (`../nose`):** tree-sitter parse-only + CST→IL→manual walk (no
  `.scm`); rules hardcoded but pry's flat catalog stays **data**; intra-fn dataflow
  + one-level import resolution are affordable; nose *omits* `self.attr`→ctor, the
  one hop pry must add (F19/F20).
- **Dogfooding decided (F25/F26):** the Python harness is a ground-truth-known
  *calibration control* — run the (b)-gate protocol on it before ceal (shakedown +
  calibration), **never as a gate corpus** (non-independent). Plus a
  **self-application invariant**: pry's own Rust implementation must be seamed by
  pry's own standard (testable by its own definition). Literal self-analysis
  deferred (pry parses Python, not Rust).
- **Pre-work done (this session):** `catalog/python.toml` (grounded seed — ceal
  Python = file I/O + subprocess + clock; agent-API is TS-side, **0 in Python**) and
  the harness dogfood control are pre-computed in `docs/dogfood-control.md`.
  Surfaced pre-scoring blockers: **finding C** (config-seam operational test) and
  **finding A** (ceal agent boundaries are TS, not Python).
- **Architecture unchanged & locked:** `pry` CLI = deterministic Rust analyzer,
  zero intelligence (nose model); intelligence in an agent-run skill; labeling
  agent-driven/blinded. Harness built/verified/committed (`harness/`).
- **Still static-only.** Behavioral correctness = cautilus's lane (`../cautilus`).

## References

- [`docs/spec-layer0.md`](spec-layer0.md) — build contract; **F18–F26** + the three
  new sections are this session's output. Canonical.
- [`catalog/python.toml`](../catalog/python.toml) — Python boundary catalog seed
  (leg-tagged; ceal Python = file I/O + subprocess + clock).
- [`catalog/typescript.toml`](../catalog/typescript.toml) + `src/` (`main.rs`,
  `lib.rs`, `catalog.rs`, `classify.rs`) + `Cargo.toml` — **the Stage-1 TS analyzer**
  (`pry map`). `tests/classify_smoke.rs`; `fixtures/ceal-ts-map.summary.json`.
- [`docs/dogfood-control.md`](dogfood-control.md) — pre-computed harness control +
  ceal Python surface scan + findings A–D (C is a pre-scoring blocker).
- [`docs/kill-gate.md`](kill-gate.md) — (a)-axis Gate 0 verdicts + **Run 3** (the
  (b)-axis gate, KILL·HANDOFF) + the cross-axis synthesis.
- [`docs/ceal-b-gate.md`](ceal-b-gate.md) — Run 3 (ceal **Python** (b)-gate): N=59
  sample table, F24 metrics under the two-tier rule, KILL·HANDOFF verdict.
- [`docs/ceal-ts-gate.md`](ceal-ts-gate.md) — Run 4 (ceal **TypeScript** (b)-gate):
  TS seam idioms, architecture, GO-lean verdict, the fs-swamp finding, refined fork.
- [`docs/ceal-bug-profile.md`](ceal-bug-profile.md) — ceal's recurring clusters +
  the grounded pivot outcome (catalog leg-tags, config-seam, cautilus 4 legs).
- `../cautilus` — built behavioral verifier; `docs/contracts/runner-verification.md`
  defines the 4 legs (the demand signal).
- `../nose` — the static-analysis sibling pry is modeled on (mechanics ground truth).
- `harness/` + `harness/README.md` — the built (a)-axis falsifier; frozen evidence
  under `harness/fixtures/`.
- [`initial-plan.md`](../initial-plan.md) §9/§13.
