# `pry untested` (slice 1) — fresh-eye code critique, before closeout

Slice: `pry untested` subcommand — port `harness/step1b.py`'s static failure-test
cross into the binary (the welded∧untested worklist). Contract: `docs/spec-untested.md`.
Changed: `src/untested.rs` (new), `src/main.rs`, `src/lib.rs`, `Cargo.toml` (+regex),
`README.md`.

**Execution:** one bounded fresh-eye subagent (code-critique target), two anchored
angles per the spec — (1) port fidelity vs the validated oracle, (2) worklist
false-alarm honesty. Reviewer built the tree, ran 43 tests, and dogfooded on the
real `/home/hwidong/codes/ceal` (traced `control-auto-commit.ts:133` end-to-end).
No same-agent substitute. **Fresh-Eye Satisfaction: parent-delegated.**

## Verdict: Act-Before-Ship = NONE. Port fidelity sound; worklist honest.

- **Port fidelity (angle 1) — clean.** Catalogs/regexes/binding-precedence faithful.
  The one deliberate refactor (`_FS_BARE`'s `\.rejects(?![\w(])` negative-lookahead →
  `\.rejects(?:[^\w(]|$)`, since Rust `regex` has no lookaround) verified equivalent
  for boolean presence across all 6 edge cases incl. end-of-string; reviewer grepped
  the whole catalog and confirmed it is the ONLY lookaround and there are zero
  backreferences. `VIMOCK`, `FS_NET_STATUS`, `canon_module` fs-folding, `clause_ids`,
  `mocked_modules`, the in-file-binding→bare-fetch→globalThis.fetch→UNRESOLVED
  precedence all faithful.
- **Worklist honesty (angle 2) — honest on the real target.** Traced
  `control-auto-commit.ts:133/208` (`spawnSync` from `node:child_process`): its test
  drives a real git repo in a tmpdir, never failure-sims the subprocess → flagging it
  untested is a TRUE positive. ceal: 158/579 tests simulate failures but ZERO mock a
  non-relative module (all `vi.mock("./...")` local wrappers, correctly discarded) →
  the near-empty index (1 module) is the honest reading, not a port defect. The
  UNRESOLVED-vs-worklist split is honest (7 ceal local-wrapper/script findings held
  separate, not hidden).

## Counterweight triage

- **Act Before Ship:** none.
- **Bundle Anyway → FOLDED IN.** B1: `is_test_file` was narrower than the oracle's
  `is_test` (missed `cy` stem, `.mts/.cts/.jsx` exts, `e2e/spec/cypress/__mocks__`
  dirs). Inert on ceal/craken (both nets caught 579/579 there) but on a Cypress/
  `.mts`/`__mocks__`-heavy repo it would shrink the failure-mock index → inflate false
  "untested" (and misfile `__mocks__/` as source). Since low-false-alarm is this
  slice's core promise, folded in: `is_test_file` now mirrors
  `COVERAGE_TEST_{BASENAME,DIR}_REGEX` faithfully, and `discover_split` checks test
  classification BEFORE source so `__mocks__/`/`e2e/` dir files feed the index instead
  of misfiling as source. Verified: ceal test_files 579→648, worklist UNCHANGED
  (111/5), candidates unchanged — the fold is inert-on-these-repos as predicted,
  robust elsewhere. New unit test `test_file_detection_matches_oracle`.
- **Over-Worry (dismissed):** `from_utf8_lossy` byte-shift vs tree-sitter raw-byte
  cols (bounded to a finding sharing a line with a raw invalid byte before the callee;
  mis-slice → UNRESOLVED, not a false row; `is_char_boundary`-guarded). `str::lines()`
  vs Python `splitlines()` (tree-sitter counts rows by `\n` only, so `.lines()` is
  consistent with the line numbers indexing it).
- **Valid but Defer:** the generous L-module index credits a module mocked+failed
  anywhere — repos that failure-test via a *relative wrapper* see those welds as
  UNRESOLVED, which slice-2 `.pryconfig.toml` wrapper/alias declarations resolve.
  llm/slack failure-capable kinds omitted (disclosed in `docs/spec-untested.md`).

## Lint Gate

`cargo clippy` clean on the new code; the single remaining warning
(`floor.rs:165` let-else→`?`) is pre-existing, not in this slice.
