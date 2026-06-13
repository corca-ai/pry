# Handoff

## Workflow Trigger

**The §13 strategic fork is RESOLVED — do not re-open it as a discussion.** It was
worked live toward the user's lean (**pivot the signal**) and *reshaped well beyond*
the handoff's original "catalog swap" into a full **(b) testability-surface
re-centering**. The contract is now in [`docs/spec-layer0.md`](spec-layer0.md)
(F18–F24 + three new sections). Read those first.

**Both gate axes are now run on the author's repos and both say "not pry's
corpus."** Finding C is RESOLVED (two-tier F18) and the (b)-gate has been run on
`ceal` → **Run 3 = KILL·HANDOFF (saturated-welded / glue)**. **First action: DECIDE
the (b)-axis strategic fork** (below) with the author — it is the (b)-analogue of the
(a)-gate fork and needs a human call. **No analyzer code until a corpus clears a
gate** (still true on both axes).

**(b)-gate result** (full evidence: [`docs/ceal-b-gate.md`](ceal-b-gate.md);
verdict in [`docs/kill-gate.md`](kill-gate.md) Run 3). N=59 non-test boundary sites:
decided-fraction **1.00** (fully decidable, NOT mute), welded-fraction **0.95** (OUT
of the `[0.15,0.85]` band — bare bit non-discriminating), ambiguous **0**,
substitution lift **≈1.0** (none). ceal Python is procedural agent-tooling glue —
zero `self.attr`-DI, zero computed-targets, *structurally identical to pry's own
harness*. The two-tier lens recovers one small real signal: ~4% hard welds (all
clock) = genuine cautilus substitution-demand; the other ~94% are cheaply
input-redirectable (already testable the way ceal's own tests are). This is
**decided-but-saturated-welded** — a fourth outcome F24 didn't enumerate (its
EXTEND/KILL branches are muteness-keyed); recorded as an F24 recalibration candidate,
NOT used to flip the verdict (§13 B.1 anti-wriggle).

**The strategic fork to decide (needs the author):**
1. **TS frontend** — go where ceal's *real* agent boundaries (LLM/Slack/calendar)
   live (finding A — they are 0 in Python, all in TS); nose supports TS; reopens the
   language scope Layer-0 deferred.
2. **OSS non-glue Python corpus** (§9: distributed systems / data pipelines) where
   boundaries are genuinely *mixed* welded/seamed and the bare bit discriminates.
3. **Re-scope pry's product on glue** — from "welded/seamed ranker" to the **two-tier
   lens output** (hard-weld/clock extractor + cautilus-handoff list + input-sim
   cheap-test list), accepting the bare-bit ranker thesis does not fit glue code.

- **Finding C — RESOLVED 2026-06-13 (two-tier / leg-relative, frozen F18).** Headline
  SEAMED/WELDED = `externalSubstitution` (runner-swappable provider/endpoint/client);
  operand-parameterization = WELDED + separate `inputSimulation`-seam tag. Frozen
  before Run 3.
- **Finding A — CONFIRMED by Run 3.** ceal Python (461 skill scripts) is file I/O +
  subprocess + clock glue; the agent-API surface is TS. cautilus substitution-demand
  in Python = the tiny clock hard-weld sliver only.

If validation-shaped closeout is needed, route through `quality` per CLAUDE.md.

## Current State

- **(b)-gate RUN (Run 3, this session): KILL·HANDOFF (glue).** Finding C resolved
  (two-tier F18, frozen first), then the analyzer-free (b)-gate run on ceal → welded
  0.95 / decided 1.0 / no lift. Both pry axes now agree the author's Python repos are
  uniformly welded glue (3 of 3 signals). Evidence: `docs/ceal-b-gate.md`,
  `docs/kill-gate.md` Run 3. The strategic fork (TS frontend / OSS corpus / re-scope)
  is the open decision. **No analyzer code built.**
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
- [`docs/ceal-b-gate.md`](ceal-b-gate.md) — the (b)-gate run on ceal: N=59 sample
  table, F24 metrics under the two-tier rule, verdict, and the strategic fork.
- [`docs/ceal-bug-profile.md`](ceal-bug-profile.md) — ceal's recurring clusters +
  the grounded pivot outcome (catalog leg-tags, config-seam, cautilus 4 legs).
- `../cautilus` — built behavioral verifier; `docs/contracts/runner-verification.md`
  defines the 4 legs (the demand signal).
- `../nose` — the static-analysis sibling pry is modeled on (mechanics ground truth).
- `harness/` + `harness/README.md` — the built (a)-axis falsifier; frozen evidence
  under `harness/fixtures/`.
- [`initial-plan.md`](../initial-plan.md) §9/§13.
