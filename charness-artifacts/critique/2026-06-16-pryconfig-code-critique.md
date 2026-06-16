# `.pryconfig.toml` (slice 3) — fresh-eye code critique, before closeout

Slice: per-repo `.pryconfig.toml` consumed by `pry untested`/`map`/`floor`. v1 fields:
`[scope].exclude` (production filter) + `[untested].failure_capable_add` (opt in
llm/slack). Changed: `src/pryconfig.rs` (new loader/parser), `src/main.rs`
(`resolve_config_and_exclude`, `effective_failure_capable`, wiring + summary block),
`src/untested.rs` (`analyze_untested` failure-capable param), `src/lib.rs`,
`tests/pryconfig_smoke.rs` (4 integration tests). Contract: `docs/spec-untested.md`.

**Execution:** one bounded fresh-eye subagent (code-critique target), two anchored
angles — (1) correctness & safety, (2) design honesty & consistency. Reviewer built,
ran all tests, and exercised the binary live (empty/`!`/whitespace config globs;
inert-kind add; dedup determinism). No same-agent substitute.
**Fresh-Eye Satisfaction: parent-delegated.**

## Verdict: SHIP. Act-Before-Ship = NONE.

All ANGLE-1 traps verified safe:
- config-exclude globs hit the SAME `build_walk` empty/`!` guards as `--exclude`
  (merged into one vector at `resolve_config_and_exclude`) — no silent-misbehave path.
- `failure_capable_add` can only *remove* files or *widen* eligible kinds within the
  existing catalog — it cannot inject catalog entries (no `[[boundary]]` handling), so
  it structurally cannot dilute the validated precision number. `catalog:"seed"` stays
  hardcoded (honest, provenance deferred). An inert kind (`clock`) add is harmless
  (classify never emits a welded-demand clock candidate).
- dedup deterministic (FLOOR_KINDS first, dedup append); lifetime threading clean.
- missing file → defaults, malformed → hard error (correct: silent-ignore is worse).

## Counterweight triage — folds applied

- **Act Before Ship:** none.
- **Bundle Anyway → ALL FOLDED IN:**
  1. Spec was stale (listed `.pryconfig.toml` as Deferred while shipping it) →
     `docs/spec-untested.md` updated: a "SHIPPED (slice 3)" section; only the
     `[[boundary]]` extension + provenance tag remain deferred.
  2. No user-facing exclusion-precedence doc → README gained a `.pryconfig.toml`
     section + an explicit 4-way precedence paragraph
     (`.gitignore` → `.pryignore` → `--exclude` → `[scope].exclude`, all additive
     removals; only `.pryignore` does `!` re-include).
  3. Exclude-glob error message misattributed config globs to `--exclude` →
     genericized to source-agnostic "exclude glob (--exclude / [scope].exclude)".
- **Over-Worry (raised & dismissed, verified):** guard bypass (doesn't happen),
  precision dilution (structurally impossible), dedup non-determinism (deterministic),
  lifetime smell (clean).
- **Valid but Defer:** (#8) `[scope].exclude` is partly redundant with `.pryignore` —
  the redundancy reads as ceremony WITHOUT the consolidation story; now that the spec
  + README precedence docs land, it is defensible single-home convenience justified by
  `failure_capable_add` (which `.pryignore` cannot express). (#9) `map`/`floor` apply
  config but don't emit a `config` summary block (only `untested` does) — a fair
  transparency follow-up, not ship-blocking.

## Verification

- 56 tests pass (3 pryconfig unit + 4 integration + the rest). clippy clean (only the
  pre-existing `floor.rs:165` warning).
- dogfood: ceal worklist 111→11 via `[scope].exclude=["scripts/**"]`; +2 llm +2 slack
  via `failure_capable_add` (effective set network/subprocess/db/fileio/llm/slack).
