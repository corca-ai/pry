# Handoff

## Workflow Trigger

**The §13 strategic fork is RESOLVED — do not re-open it as a discussion.** It was
worked live toward the user's lean (**pivot the signal**) and *reshaped well beyond*
the handoff's original "catalog swap" into a full **(b) testability-surface
re-centering**. The contract is now in [`docs/spec-layer0.md`](spec-layer0.md)
(F18–F24 + three new sections). Read those first.

**Four gate runs done; a clear map. The author's *Python* is glue pry can't rank
(Runs 1–3); the author's *TS* agent runtime is the surface where pry's (b)-thesis has
traction (Run 4 = GO-lean).** Finding C RESOLVED (two-tier F18). **First action:
DECIDE the refined fork** (below) with the author — needs a human call. **No analyzer
code until a corpus clears the (recalibrated) gate.**

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

**The refined fork to decide (needs the author):**
1. **Recalibrate F24 to the lens criterion, then re-gate ceal TS** (clean sample) for
   a *frozen* GO/no-GO → build the TS frontend only on a GO. Highest-fidelity, cheap.
2. **Build the TS frontend now** on the qualitative GO-lean signal, accepting pry's
   ceal role is regression-guard + minority-gap.
3. **Find a less-disciplined agent/TS corpus** (or OSS) where agent boundaries are
   welded → a bigger backlog to demonstrate pry's find-value.
4. **Re-scope to regression-guard** — pry as a CI gate flagging *newly-welded*
   cautilus-demand boundaries (fits already-disciplined codebases like ceal).

- **F24 recalibration candidate (carried, Runs 3+4):** the bare welded-fraction band
  `[0.15,0.85]` is **fs-swamped** (file I/O volume dominates in any codebase) → the
  (b)-axis GO test should be **lens discrimination** (does the cautilus-demand subset
  split seamed/welded?), not the bare fraction. *Between-runs* tuning only (§13 B.1).
- **Finding C — RESOLVED 2026-06-13 (two-tier F18).** Headline SEAMED/WELDED =
  `externalSubstitution`; operand-parameterization = WELDED + `inputSimulation`-tag.
- **Finding A — CONFIRMED.** ceal Python = file/subprocess/clock glue (agent-API 0);
  ceal TS = the agent surface (clients/clock/transports, DI-disciplined).

If validation-shaped closeout is needed, route through `quality` per CLAUDE.md.

## Current State

- **(b)-gate RUN on both languages (Runs 3+4, this session).** Finding C resolved
  (two-tier F18, frozen first). **Run 3 ceal Python → KILL·HANDOFF (glue)** (welded
  0.95, no lift). **Run 4 ceal TS → GO-lean / EXTEND** (mixed surface, seams at agent
  boundaries, clock injected ~25%) — the (b)-thesis has traction on the TS agent
  runtime. Four runs converge: author's Python = glue pry can't rank; author's TS =
  pry's surface, but already DI-disciplined (→ regression-guard role). The bare
  welded-fraction is fs-swamped in both → recalibrate F24 to the lens criterion.
  Evidence: `docs/ceal-b-gate.md`, `docs/ceal-ts-gate.md`, `docs/kill-gate.md` Runs
  3+4. The refined fork is the open decision. **No analyzer code built.**
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
- [`catalog/python.toml`](../catalog/python.toml) — the grounded boundary catalog
  **seed** (leg-tagged; ceal Python = file I/O + subprocess + clock).
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
