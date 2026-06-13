# Handoff

## Workflow Trigger

**The §13 strategic fork is RESOLVED — do not re-open it as a discussion.** It was
worked live toward the user's lean (**pivot the signal**) and *reshaped well beyond*
the handoff's original "catalog swap" into a full **(b) testability-surface
re-centering**. The contract is now in [`docs/spec-layer0.md`](spec-layer0.md)
(F18–F24 + three new sections). Read those first.

**First action: run the (b)-axis testability-surface gate (F24) on `ceal`,
analyzer-free** (hand/script-sample, Gate-0 spirit — *no Rust yet*). Sequence:

1. Sample N≈30–50 boundary **call/acquisition sites** in ceal's Python (favor the
   cautilus-demand surface: LLM/tool dispatch, Slack/provider SDK, calendar reads,
   scheduled enqueue, subprocess worker spawn, workflow-state store, credentials).
2. Classify each **SEAMED / WELDED / AMBIGUOUS** by the F18/F19 rule (0-hop +
   one `self.attr`→same-class `__init__` hop; config-seam counts; monkeypatch never
   upgrades; every `ambiguous` gets a **reason code**).
3. Score the F24 metrics: recognizability, decided-fraction, welded-fraction,
   **ambiguous-reason histogram**, cautilus-demand lift. Apply the frozen numbers
   (mute-gate `<0.40`; welded band `[0.15,0.85]`; lift = demand-point welded% >
   overall welded%).
4. Record the **3-way verdict — GO / EXTEND / KILL·HANDOFF** — in
   `docs/kill-gate.md`. EXTEND routes to the F22 ladder by the ambiguous-reason
   shape; **no analyzer code until a (b)-gate GO.**

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
- **Architecture unchanged & locked:** `pry` CLI = deterministic Rust analyzer,
  zero intelligence (nose model); intelligence in an agent-run skill; labeling
  agent-driven/blinded. Harness built/verified/committed (`harness/`).
- **Still static-only.** Behavioral correctness = cautilus's lane (`../cautilus`).

## References

- [`docs/spec-layer0.md`](spec-layer0.md) — build contract; **F18–F24** + the three
  new sections are this session's output. Canonical.
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
