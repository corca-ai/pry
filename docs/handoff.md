# Handoff

## Workflow Trigger

**The §13 strategic fork is RESOLVED — do not re-open it as a discussion.** It was
worked live toward the user's lean (**pivot the signal**) and *reshaped well beyond*
the handoff's original "catalog swap" into a full **(b) testability-surface
re-centering**. The contract is now in [`docs/spec-layer0.md`](spec-layer0.md)
(F18–F24 + three new sections). Read those first.

**First action: DECIDE finding C, then run the (b)-axis gate (F24) on `ceal`,
analyzer-free** (hand/script-sample, *no Rust yet*). Pre-work is done — the catalog
seed (`catalog/python.toml`) and the harness dogfood control are pre-computed in
[`docs/dogfood-control.md`](dogfood-control.md). Two pre-decisions it surfaced must
be settled *before scoring*:

- **Finding C (blocker) — config-seam operational test (F18).** On CLI/script glue
  almost every boundary *target* is param-driven; a loose config-seam rule
  degenerates (all-seamed = the monkeypatch trap's mirror). Decide: does a bad
  parameterized *path/url* count as a seam (failure-injectable), or must
  substitution be at the *client/dependency* level? The harness control swings from
  welded 1.0 → 0.29 on this choice.
- **Finding A (scope) — ceal's agent-API boundaries (LLM/Slack/calendar) are TS/JS,
  0 in Python.** ceal Python is file I/O + subprocess + clock glue. Sample the
  *real* Python surface; the headline agent surface needs a TS frontend (deferred).
  cautilus-demand overlap in Python = **subprocess worker-spawn + file/db/clock**.

Then run the gate on ceal (the independent corpus that carries the verdict):

1. Sample N≈30–50 boundary **call/acquisition sites** in ceal's Python — the real
   surface: file I/O (`read_text`/`write_text`/`exists`…), `subprocess.run`
   worker-spawn, clock (`datetime.now`), `os.environ`, small net/db/tz.
2. Classify each **SEAMED / WELDED / AMBIGUOUS** by the F18/F19 rule (0-hop +
   one `self.attr`→same-class `__init__` hop; config-seam counts; monkeypatch never
   upgrades; every `ambiguous` gets a **reason code**).
3. Score the F24 metrics: recognizability, decided-fraction, welded-fraction,
   **ambiguous-reason histogram**, cautilus-demand lift. Apply the frozen numbers
   (mute-gate `<0.40`; welded band `[0.15,0.85]`; lift = demand-point welded% >
   overall welded%).
4. Record the **3-way verdict — GO / EXTEND / KILL·HANDOFF** — in
   `docs/kill-gate.md` (ceal carries the verdict; the harness pass is calibration
   only — never clears the gate, F25). EXTEND routes to the F22 ladder by the
   ambiguous-reason shape; **no analyzer code until a (b)-gate GO.**

If validation-shaped closeout is needed, route through `quality` per CLAUDE.md.

## Current State

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
- [`docs/kill-gate.md`](kill-gate.md) — Gate 0 (a)-axis verdicts + the re-centering
  note (the (b)-gate is the next experiment).
- [`docs/ceal-bug-profile.md`](ceal-bug-profile.md) — ceal's recurring clusters +
  the grounded pivot outcome (catalog leg-tags, config-seam, cautilus 4 legs).
- `../cautilus` — built behavioral verifier; `docs/contracts/runner-verification.md`
  defines the 4 legs (the demand signal).
- `../nose` — the static-analysis sibling pry is modeled on (mechanics ground truth).
- `harness/` + `harness/README.md` — the built (a)-axis falsifier; frozen evidence
  under `harness/fixtures/`.
- [`initial-plan.md`](../initial-plan.md) §9/§13.
