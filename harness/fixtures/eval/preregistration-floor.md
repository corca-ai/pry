# Floor experiment — PRE-REGISTRATION (rules + sample + labeling + go/kill)

**Status: frozen. This file's git commit MUST precede the commit that writes any
floor number.** Git-provable:

```
git merge-base --is-ancestor <this-commit-sha> <first-floor-number-commit-sha>
```

Third honesty gate in this repo (after `preregistration.md` E9 and
`preregistration-coverage.md` Step-1). The floor is the *claim* channel, evaluated
by **precision-of-a-fact**, not lift-over-churn — so unlike E9/Step-1 the bar is a
precision/repo-fit gate, not a ratio-vs-1.0 gate. Contract: `docs/spec-floor.md`.
Machine source of truth: the `Floor` block of `harness/config.py`.

## 1. The rules (frozen)

TS/JS only. Failure-capable boundary kinds only: **network, subprocess, db,
fileio** (clock/random/env excluded). **Weld-agnostic** (NOT gated on the map's
`welded` bit — the defect is the swallowed failure, independent of injectability).

- **FLOOR-1 (swallowed boundary failure):** a `try` containing ≥1 such boundary
  call + a `catch` that swallows (no re-throw, no return/break/continue/exit out;
  empty or log-only).
- **FLOOR-2 (swallow-then-commit, severe subclass):** FLOOR-1 AND control reaches
  a mutation/commit after the try/catch (write/persist call or property
  assignment to a param/outer object). **FLOOR-2 is the headline metric.**

## 2. The corpus, sample, and labeling (frozen)

- Corpus: the already-cloned 25 TS/JS repos (`corpus.json`), pinned commits,
  offline. Output via the separate `pry floor` subcommand.
- Sample: a deterministic stride sample of ~30 flags (seed 0), weighted toward
  FLOOR-2 (target ≥20 FLOOR-2 + the rest FLOOR-1-only), spanning as many repos as
  the stride yields. The sampling rule is fixed here; the flags are not seen first.
- Labeling: a fresh-eye subagent panel reads local source (window + file) and
  labels up to `FLOOR_LABEL_TARGET` (40) FLOOR-2 flags (all if fewer) + ~10
  FLOOR-1-only for context, into `floor-labels.json`:
  - `GENUINE-MEANINGFUL` — real defect; the label MUST name the concrete
    consequence (which write is lost / which invariant or state goes inconsistent
    / what wrong result ships). A generic "could be bad" is not enough.
  - `BENIGN-SWALLOW` — intentional/correct (optional read, best-effort, cleanup,
    already-compensated).
  - `FALSE-FLAG` — rule misfired (not a swallowed boundary failure / not
    failure-capable / catch does handle it / **generated or vendored code**).
  - `AMBIGUOUS` — undecidable from the code.
- **precision = GENUINE-MEANINGFUL / (GENUINE-MEANINGFUL + BENIGN-SWALLOW +
  FALSE-FLAG)**; AMBIGUOUS excluded. Wilson 95% interval **reported** alongside.
- **Linter-survival (differentiation, reported not gated):** the fraction of
  GENUINE-MEANINGFUL flags that survive a real `eslint`/`ruff` run (i.e. that the
  status quo passes). This number IS the moat measurement (§1.4); it is descriptive,
  not a blind GO clause (adding it as a gate would over-constrain a probe whose
  whole point is that log-only swallows are what linters miss).
- Disclosed caveat: the panel is the same model family that built the floor
  (same-model bias, as in the H3 panel). **Operator GO-tripwire:** a 2-3 flag
  operator sanity-glance on the GENUINE subset; if the operator contradicts the
  panel on a spot-checked GENUINE, the GO is **provisional** pending full human
  calibration (the H3 calibration pattern). A *full* operator audit is what a GO
  authorizes, not a precondition of the go/kill.

## 3. The two-sided go/kill (set blind, before any flag is seen)

On **FLOOR-2** (the headline). The VOLUME gates close the cheap-GO hole that a
Wilson-LB alone left open (n=3 all-genuine would clear an LB≥0.40 bar):

- **GO (build the DETECTOR + thin owned-repo dogfood):** precision ≥
  `FLOOR_GO_PRECISION` (0.60) AND over ≥ `FLOOR_GO_MIN_DECIDED` (20) DECIDED
  FLOOR-2 labels AND corpus-wide FLOOR-2 total ≥ `FLOOR_MIN_TOTAL_FLAGS` (25) AND
  ≥ `FLOOR_GO_MIN_GENUINE` (3) GENUINE-MEANINGFUL spanning ≥ `FLOOR_GO_MIN_REPOS`
  (2) repos AND ≥1 ruff/eslint-passes case (SC-F3). **GO authorizes building the
  detector; it does NOT retire the initial-plan §5 "≈zero false positives" ship
  bar (a separate later gate), and it must be followed by a thin owned-repo /
  charness dogfood before the floor is trusted where pry actually deploys** (the
  OSS corpus has the swallow shape; `docs/kill-gate.md` shows the author's own
  repos largely do NOT — charness 7/126, ceal 2/26 — so a GO here proves the
  *detector*, not the deploy-target payoff).
- **KILL (this rule set; fall back to ratchet / ship-as-is):** precision ≤
  `FLOOR_KILL_PRECISION` (0.40) OR < 2 GENUINE-MEANINGFUL total (the §13.A "correct
  but useless" death). KILL scopes to **this minimal 2-rule set**, not the floor
  *concept* (the deferred Aspirator rules stay unexplored). A valid, honest outcome.
- **WEAK (between, incl. corpus-wide FLOOR-2 < 25):** ONE dev-tune (dev-5) /
  heldout-confirm iteration permitted (e.g. loosen the rule if it is too sparse to
  reach the min-total), then re-decide. Any tuning is dev-only; heldout is never
  tuned on.

Rationale for the 0.60 bar: a *first* minimal rule will not hit the §5 "≈zero FP"
ideal, but a claim channel worth investing in must be majority-correct over a
non-trivial sample (≥20 decided, ≥25 corpus-wide), AND clear repo-fit (meaningful,
generalizing) — all, not any. The bar is set now, blind, and cannot move post hoc.

## 4. Standing non-claims

- Precision is panel-labeled (same-model caveat); a GENUINE label is "a competent
  reader, given the code, judges this a real swallowed-failure defect," not a
  reproduced failure.
- No recall claim (this is a precision/repo-fit experiment; the floor is
  deliberately conservative, §7).
- No causation; no executed proof that the swallow ships a bug in production.
- Offline structural analysis only; no outbound; no LLM in binary or harness.

---

*Frozen for the floor experiment. The harness reads config.py; changing any
threshold after a floor number exists voids the gate and must be called out.*
