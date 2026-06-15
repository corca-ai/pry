# Spec — the syntactic FLOOR go/kill experiment (the un-killed claim channel)

Contract for the experiment chosen after the map's prediction channel was
falsified twice (`docs/eval-gate.md` E9 + Step-1) and `ideation`
(`charness-artifacts/ideation/2026-06-16-concept-ideation.md`) reframed the wedge
as the **never-built FLOOR**. This spec is the build contract; the frozen go/kill
numbers live in `harness/fixtures/eval/preregistration-floor.md` + the `Floor`
block of `harness/config.py` (the honesty gate).

## Problem

`initial-plan.md` §5 defines two channels with different validity bases. Only the
**map (prediction)** was built, and it died (no lift over baseline on bugs or
file-coverage). The **floor (claim)** — a *sound, high-precision* error-handling
bug finder whose bar is **precision-of-a-fact**, not lift-over-churn (Aspirator /
Yuan OSDI'14: 3 syntactic rules → 100+ developer-confirmed bugs) — was never
built and is **not what failed**. Question this experiment answers, cheaply and
before full investment: **does a minimal floor flag REAL, MEANINGFUL error-handling
defects at high precision on the existing corpus?**

## Current Slice

Implement a **minimal floor** as a *separate* `pry floor` output, run it offline
on the already-cloned 25 TS/JS corpus, label a ~30-flag sample for **precision +
repo-fit**, and decide GO/KILL against a pre-registered two-sided bar.

## Fixed Decisions

1. **The rules (TS/JS only — the validated surface).** Two, the second a severe
   subclass of the first:
   - **FLOOR-1 — swallowed boundary failure.** A `try` whose body contains ≥1
     **failure-capable** boundary call, paired with a `catch` that **swallows**:
     it does not re-throw, does not `return`/`break`/`continue`/`process.exit`
     out of the flow — it is empty or only logs. (The non-empty-but-only-logs
     case is exactly what ruff/eslint pass — `initial-plan.md` §1.4.)
   - **FLOOR-2 — swallow-then-commit (the severe subclass).** FLOOR-1 **AND**
     after the try/catch, control reaches a **mutation/commit** in the same
     function (a write/persist call — `.save(`/`.update(`/`.commit(`/`.write(`/
     `.create(` on a non-boundary target, or an assignment to a param/outer
     object property). The credits-debited/charge-lost shape.
2. **Failure-capable boundary kinds only:** `network`, `subprocess`, `db`,
   `fileio`. **Exclude** `clock`/`random`/`env` (a clock read has no failure worth
   swallowing). The floor reuses pry's boundary catalog (the moat) for *which*
   calls matter.
3. **The floor is WELD-AGNOSTIC.** It does **not** gate on the map's `welded`
   bit. The defect is the *swallowed failure*, independent of injectability —
   this fully decouples the floor from the falsified map signal. (Rationale, not
   re-litigable here.)
4. **Physically separate output** (premortem §13.B.2). The floor is a new
   `pry floor <repo>` subcommand emitting its **own** deterministic JSON, labeled
   "claim (defect to fix), not a ranking." It is **never** mixed into `pry map`.
5. **Offline, AC4.** Run on `CORPUS_CLONE_DIR` clones at pinned commits; zero
   outbound; the binary and harness import no LLM/HTTP lib.
6. **Labeling protocol (offline, frozen — E8 pattern).** Label up to
   `FLOOR_LABEL_TARGET` (40) FLOOR-2 flags (all if fewer) + ~10 FLOOR-1-only for
   context (deterministic stride, seed 0), by a **fresh-eye subagent panel**
   reading local source (±window + file), into `harness/fixtures/eval/floor-labels.json`.
   Categories: `GENUINE-MEANINGFUL` (real defect — the label MUST name the concrete
   consequence: which write is lost / what state goes inconsistent / what wrong
   result ships), `BENIGN-SWALLOW` (intentional/correct — optional/best-effort/
   cleanup), `FALSE-FLAG` (rule misfired / generated / vendored), `AMBIGUOUS`.
   precision = GENUINE-MEANINGFUL / (decided), AMBIGUOUS excluded; Wilson 95% +
   linter-survival fraction reported. Same-model bias disclosed (H3 caveat); a 2-3
   flag operator sanity-glance is the GO tripwire (contradiction → GO provisional).
7. **Honesty gate.** The rules, the sample method, the labeling protocol, and the
   two-sided go/kill (below) are frozen in `preregistration-floor.md` + config
   **before** any floor number; the prereg commit must precede the first
   floor-number commit (git-provable `merge-base --is-ancestor`).

## Probe Questions (resolved in impl)

- Exact AST detection of "swallows" (re-throw / control-exit recognition in
  `catch_clause`) — refine against real cases; start conservative.
- Exact mutation/commit heuristic for FLOOR-2 (the write-call catalog +
  property-assignment shape) — reuse `value_reaches_control` / `name_used_in_*`
  dataflow-lite; tune on the dev-5 only if the first pass is WEAK.
- Whether `finally`/nested-try shapes need handling for the minimal pass.

## Deferred Decisions

- Python floor rules (bare `except`, etc.) — TS/JS first (validated surface).
- The full Aspirator rule set (over-catch→abort, TODO-in-handler) — minimal set
  first.
- Inline `// pry-ignore` per-finding hatch (roadmap floor item) — only after GO.
- SARIF emit for the floor — after GO.
- **Owned-repo / charness dogfood** — the GO follow-up (NOT this experiment;
  re-pointing this probe at owned repos would just re-confirm the kill-gate null).
- **Full operator human calibration** — what a GO authorizes, not a go/kill input
  (the 2-3 flag tripwire above is the cheap proxy for this probe).

## Non-Goals

- No map change; no precision-lever work (demoted, premise dead).
- Not a security/taint tool; not a mutation-testing replacement (`initial-plan` §2).
- No outbound; no executed test suites; no LLM in binary or harness.

## Deliberately Not Doing

- **Not gating the floor on `welded`** (decision 3) — would re-couple it to the
  dead signal.
- **Not including clock/random/env** swallows — no failure to swallow.
- **Not chasing high recall** — §5/§7: a quiet, trustworthy claim channel beats a
  noisy one; this is a *precision* experiment.

## Constraints

- Deterministic, byte-identical output (the standing pry invariant).
- AC4 zero-LLM (binary + harness); no outbound on corpus repos.
- Reuse parse/catalog/dataflow-lite already in `src/` (clap subcommand, tree-sitter,
  `value_reaches_control` et al.).

## Success Criteria

- **SC-F1 (precision/claim validity):** FLOOR-2 flags are mostly real defects.
- **SC-F2 (repo-fit/meaningfulness):** the floor finds MEANINGFUL bugs, not only
  trivial/correct swallows (the premortem §13.A death the experiment must expose).
- **SC-F3 (differentiation):** ≥1 confirmed flag is a case ruff/eslint pass.
- **SC-F4 (separation):** `pry floor` output is physically distinct from `pry map`.
- **SC-F5 (honesty gate):** prereg precedes the first number, git-provable.

## Acceptance Checks (pre-registered go/kill — frozen in config)

The VOLUME gates (min-decided + min-total) close the cheap-GO hole a Wilson-LB
alone left open (spec-critique: n=3 all-genuine clears an LB≥0.40 bar). The Wilson
interval is reported, not gated.

- **GO** (build the DETECTOR + thin owned-repo dogfood) = `FLOOR-2 precision ≥
  FLOOR_GO_PRECISION (0.60)` over `≥ FLOOR_GO_MIN_DECIDED (20)` DECIDED FLOOR-2
  labels **AND** corpus-wide FLOOR-2 `≥ FLOOR_MIN_TOTAL_FLAGS (25)` **AND** `≥
  FLOOR_GO_MIN_GENUINE (3)` GENUINE-MEANINGFUL spanning `≥ FLOOR_GO_MIN_REPOS (2)`
  repos **AND** ≥1 ruff/eslint-passes case (SC-F3). GO authorizes building the
  detector; it does **not** retire the §5 ≈zero-FP ship bar, and must be followed
  by an owned-repo/charness dogfood before trust where pry deploys.
- **KILL** (this rule set) = `precision ≤ FLOOR_KILL_PRECISION (0.40)` **OR** `< 2`
  GENUINE-MEANINGFUL total (correct-but-useless, §13.A) → fall back to **ratchet**
  or **ship-as-is**, reported honestly. KILL scopes to this minimal 2-rule set, not
  the floor concept.
- **WEAK** = between (incl. corpus-wide FLOOR-2 < 25) → ONE dev-tune / heldout-
  confirm iteration (dev-5 only; heldout never tuned on), then re-decide.
- Each criterion has a check: SC-F1/F2 via `floor-labels.json` + re-derive script
  (GENUINE labels must name the concrete lost write/inconsistent state); SC-F3 by
  the reported linter-survival fraction; SC-F4 by the separate subcommand; SC-F5 by
  `git merge-base --is-ancestor`. Operator GO-tripwire: a 2-3 flag sanity-glance;
  contradiction → GO is provisional pending full human calibration.

## Critique

Bounded fresh-eye spec-critique run (2 angles + counterweight, parent-delegated;
`charness-artifacts/critique/2026-06-16-floor-spec-critique.md`). Load-bearing
fold: the **cheap-GO hole** (n=3 all-genuine cleared every clause via a Wilson-LB
calibrated to pass n=3) → added VOLUME gates (`FLOOR_GO_MIN_DECIDED`=20 +
`FLOOR_MIN_TOTAL_FLAGS`=25), demoted Wilson-LB to reported-only. Also folded: GO
scoped to "build the **detector** + owned-repo dogfood" (not the whole channel);
KILL scoped to "this rule set"; GENUINE label must name the concrete consequence;
linter-survival reported as a **fraction** (the moat measurement); §5 ≈zero-FP
ship bar explicitly not retired by GO; operator 2-3 flag GO-tripwire. Deferred
(counterweight): full owned-repo dogfood + full human calibration are the GO
follow-up, not go/kill inputs — re-pointing this probe at owned repos would only
re-confirm the kill-gate null.

## Canonical Artifact

This file (`docs/spec-floor.md`) during implementation; the frozen numbers in
`harness/fixtures/eval/preregistration-floor.md` + `harness/config.py`; results
will land in `docs/eval-gate.md` (a new "Floor" section) + `floor_result.json`.

## First Implementation Slice

Add `pry floor` to `src/main.rs` (clap subcommand) + a `src/floor.rs` checker that
traverses `try_statement`/`catch_clause`, reuses the boundary catalog (decision 2)
and the existing dataflow-lite for FLOOR-2, and emits separate deterministic JSON.
Unit-test the rules on small fixtures (empty catch, log-only catch, rethrow =
negative, swallow-then-save = FLOOR-2). Then the harness runner + sample + labeling.
