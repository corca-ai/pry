# DI-seam recognition (slice 2) — fresh-eye code critique, before closeout

Slice: teach `classify.rs` to recognize the dependency-injection seam
`const spawn = deps.spawnSync ?? spawnSync; … spawn(…)` → SEAMED (was a false weld).
Motivation: dogfood found this idiom is ceal's #1 testability seam (188×) and pry
mis-classified it welded, polluting the `pry untested` worklist with false alarms.
Changed: `src/classify.rs` (`callee_injected` helper + one call-site edit),
`tests/classify_smoke.rs` (`local_di_binding_callee_is_seamed`).

**Execution:** one bounded fresh-eye subagent (code-critique target), two anchored
angles — (1) precision safety / false-seam risk, (2) consistency & completeness.
Reviewer independently re-ran the corpus map diff and spot-checked all 7 ceal flips.
No same-agent substitute. **Fresh-Eye Satisfaction: parent-delegated.**

## Verdict: SHIP. Act-Before-Ship = NONE.

The change is a **measured precision no-op on the validated corpus** —
independently re-verified **0 welded→seamed flips across all 1882 network/subprocess
findings in 33 repos** (the H3 precision asset is preserved by construction) — and a
clean **7→0 false-weld fix on ceal**, where every flip is a genuine DI seam (one
carries an explicit `// Seam: … injectable so failure paths can be exercised`).

## Counterweight triage

- **Act Before Ship:** none.
- **Bundle Anyway → FOLDED IN.** Documented the `find_local_binding` outer-scan
  scoping caveat in `callee_injected`'s doc comment (the body scan can match a
  *sibling*-nested binding of the same name; needs a sibling DI-binding the same
  catalog name + a free use at the call site → 0 corpus occurrences).
- **Over-Worry (dismissed, corpus 0-flips dominates):**
  - blind `??` false-seam (`classify_rhs` seams any `??` RHS regardless of operands)
    — pre-existing behavior inherited verbatim from `classify_receiver`'s receiver
    path, not introduced here; 0 such callee shapes in the corpus.
  - non-catalog alias invisibility (`const run = deps.x ?? y; run(…)` produces no
    finding) — pre-existing recall property of literal-name matching; the call was
    never welded before, so the worklist is unchanged. Not a soundness regression.
- **Valid but Defer:**
  - sibling-scope leak (the documented edge) — real mechanism, 0 corpus footprint.
  - member-call subprocess DI (`const cp = deps.cp ?? cjs; cp.spawnSync(…)`) is NOT
    given `callee_injected` treatment — but ceal uses only the bare-identifier idiom,
    and that receiver shape is already partly covered by `classify_receiver`. Defer.
  - bringing `classify_receiver` up to closure-aware parity — additive recall, later.

## Precision evidence

- corpus before/after (`pry map` on 33 repos): 1882 net/subproc findings, **0 class
  flips**. The DI idiom is ceal's own discipline (188×); OSS doesn't share it at the
  callee position, so the change is inert there.
- ceal: candidates 140→133, UNRESOLVED bucket 7→0 (all 7 were DI seams). Worklist
  unchanged at 111 (those are genuine direct-call welds).
- 29 tests pass incl. the new closure-aware + 2-guardrail regression test.

## Lint Gate

`cargo clippy` clean on the change; the single remaining warning (`floor.rs:165`
let-else→`?`) is pre-existing.
