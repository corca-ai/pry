# Floor go/kill spec — bounded fresh-eye spec-critique

Slice: `docs/spec-floor.md` + `harness/fixtures/eval/preregistration-floor.md` +
config `Floor` block (the go/kill contract for the un-killed claim channel).

**Execution:** parent-delegated fresh-eye subagents (2 angles: gaming-honesty +
problem-framing; 1 counterweight). No same-agent substitute. Target: spec-critique.
Packet Consumed: n/a (no adapter sections).

## Verdict: SOUND after one load-bearing fix (A) + zero-cost prose (E/G) + cheap bundles. Cleared to freeze.

The honesty *machinery* (prereg-before-number, git-provable, frozen config,
disclosed caveats) matched the two prior gates. The *content* had one gate-gaming
hole, now closed.

## Findings + disposition (four-bin, counterweight-triaged)

**Act Before Ship (folded before freeze):**
- **A — cheap-GO hole (the one that mattered).** Numerically demonstrated by two
  reviewers: n=3 all-genuine FLOOR-2 flags cleared *every* GO clause (precision
  1.0, Wilson-LB 0.438 ≥ 0.40 — the LB was calibrated to pass n=3); no floor on
  corpus-wide FLOOR-2 yield nor on decided-sample-n. **Fix:** added VOLUME gates
  `FLOOR_GO_MIN_DECIDED`=20 + `FLOOR_MIN_TOTAL_FLAGS`=25; demoted Wilson-LB to
  reported-only (it was redundant + mis-calibrated at realistic n).
- **E — GO over-commit (prose).** GO "build the floor [whole channel]" → "build
  the **detector** + thin owned-repo dogfood"; KILL scoped to "this 2-rule set,"
  not the floor concept.
- **G — §5 ship bar (one sentence).** GO authorizes building; does NOT retire the
  initial-plan §5 ≈zero-FP ship bar (separate later gate).

**Bundle Anyway (folded, cheap):**
- **F1** — GENUINE label must name the concrete consequence (which write is lost /
  what state goes inconsistent), per the H3 panel-over-call precedent.
- **D** — linter-survival reported as a *fraction* of GENUINE flags (the moat
  measurement), descriptive — NOT promoted to a blind GO clause.
- **B-lite** — a 2-3 flag operator sanity-glance as a GO tripwire (contradiction →
  GO provisional); generated/vendored code → FALSE-FLAG.

**Valid but Defer (recorded in spec "Deferred"):**
- **C — owned-repo/charness dogfood:** the GO follow-up, NOT this probe. kill-gate
  already showed owned repos lack the swallow shape (charness 7/126, ceal 2/26),
  so re-pointing the probe there would re-confirm a known null. Captured as a GO
  *action*, not a corpus change.
- **B-full — operator human calibration:** what a GO authorizes (the tripwire is
  the cheap proxy for the go/kill).

**Over-Worry (rejected, recorded):**
- A standalone actionability clause (F2) — folded one line into the rubric
  (generated → FALSE-FLAG) instead of a new dimension.
- Promoting linter-survival to a gate — over-constrains a probe whose point is
  that log-only swallows are exactly what linters pass.

## Sound as written (not re-litigated)
Weld-agnostic decoupling (clean — no back-door re-import of the dead map signal);
physical output separation (`pry floor` ≠ `pry map`, defuses premortem §13.B.2);
two-sided bar with WEAK band + dev-only tuning; honesty gate (3rd instance).
