# Handoff

## Workflow Trigger — if the operator says "계속합시다" / "continue"

Do **Next Session: Step-1b** (operator-decided 2026-06-16) via `spec` (pre-register
the metric + go/kill BEFORE any number, git-provable — the standing honesty gate),
then `impl`. It is a bounded, fully-static/offline analysis (no new binary feature
strictly required; reuses `harness/coverage.py`). Read `docs/eval-gate.md` §Step-1
(scope correction) first. The ratchet-vs-ship-as-is decision is **downstream** of
Step-1b and waits on it.

## Current State — 3 value-bridges down, BUT Step-1 was the wrong granularity

Detail/numbers in `docs/eval-gate.md`. E9 (bugs) FALSIFIED 1.05; Step-1 (coverage)
FALSIFIED 0.95 — *file-level only*; floor (claim channel) KILL 3.8% (mature OSS
swallows are mostly intentional). pry stays a **validated precise injectability
classifier** (net/subproc 100%) with no proven *defect* payoff.

**The live thread (why Step-1b exists).** "welded = the boundary's failure can't be
injected" is pry's static layer-1 finding and is solid. The sharp question — *is
that failure path actually tested?* — was only crudely approximated by Step-1's
file-level coverage. The earlier "needs npm install / unmeasured" framing was
**wrong** (operator-caught): module-mocking + failure-simulation leave **static**
fingerprints, so it is measurable offline on the same corpus.

## Next Session — Step-1b: static failure-test detection (the sharp Step-1 redo)

**Question:** for each welded, failure-capable boundary (network/subprocess/db/
fileio), is its *failure* actually simulated by a test? Fully static, offline, AC4.

**Method (reuse `coverage.py`'s import-by-test graph):** for the test files that
reference the boundary's module (+ jest/vitest config `setupFiles`/`moduleNameMapper`
+ `__mocks__/`), statically detect **(a) the module is mocked** (`vi.mock`/`jest.mock`/
`__mocks__`, `nock`, `msw`, `sinon`) and **(b) its FAILURE is simulated** —
`mockRejectedValue`, `mockImplementation(()=>{throw})`, `nock().replyWithError`, msw
error handler, `mockResolvedValue({ok:false})`, `.rejects`. **(b) is the
discriminator.** Honest hard part: linking mock-target ↔ the specific boundary
(module/symbol match) and separating (a) "mocks the module" from (b) "simulates its
failure"; report both.

**Measure (pre-register first):** fraction of welded boundaries whose failure is
mock-tested vs seamed. Two-way payoff, both worth reporting:
- welded failures rarely tested → first *positive* signal (welded = real untested
  failure paths; pry's layer-1 finding tracks actual test absence).
- welded often mock-tested → pry's "untestable" claim is overstated (record honestly).

**Why it matters (operator's framing — the real point):** this turns pry from an
*inventory* into a **point-of-use recommender**: "welded boundary whose failure is
untested anywhere → high-value: add a fault test / introduce a seam" vs "already
mock-tested → low priority." That recommendation quality is the product value, with
or without the defect-correlation that died.

## Discuss (downstream of Step-1b)

Ratchet (no-new-welds CI gate) vs ship-as-is. Defer until Step-1b: if welded
failures are genuinely untested, pry's recommender (above) becomes the wedge and
reframes both options.

## References

- `docs/eval-gate.md` — E9 + Step-1 (+ scope correction) + Floor results.
- `harness/coverage.py` — the import-by-test graph + tsconfig alias resolution to reuse.
- `src/floor.rs` + `harness/floor_worklist.py` — prior static test-file/AST patterns.
- `charness-artifacts/ideation/2026-06-16-concept-ideation.md` — wedge analysis.
- `initial-plan.md` §1.3/§5 (testability=injectability thesis, two channels).
