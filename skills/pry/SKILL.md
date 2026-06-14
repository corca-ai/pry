---
name: pry
description: "Use when reviewing the testability/injectability of TypeScript/JavaScript code, or when `quality` wants pry's testability backlog. Runs the pry static analyzer (honoring PRY_BIN), ranks the welded-at-demand findings (boundary calls with no seam to inject a failure), and labels each GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS. Emits a risk ranking, not a bug list. TS/JS only — Python is a recorded KILL."
---

# pry (F15 intelligence skill)

`pry` the binary is deterministic and dumb (spec F1): `pry map <path>` emits
every boundary finding classified seamed / welded / ambiguous, with the
substitution-demand flag and the cosmetic-clock + duration-record filters
already applied. **This skill is the intelligence layer the CLI defers to**: it
runs the binary, ranks the *welded-at-demand* backlog, and labels each finding.
The output is advisory — a testability backlog, never a bug list, and it must
never fail standing `quality`.

## When to use

- A user asks "is this TS/JS testable?", "where are the un-injectable boundaries?",
  or wants the welded-at-demand / injectability backlog.
- `quality` wants pry's advisory testability inventory for a TS/JS path.

Not for Python: the author's Python is welded glue with no discrimination — a
recorded KILL (`docs/kill-gate.md`). pry analyzes `.ts/.tsx/.js/.mjs/.cjs` only.

## Prerequisite: the binary

pry has no published release yet. Resolve it in this order (the consumer does
this for you):

1. `PRY_BIN=/abs/path/to/pry/target/release/pry` (maintainer-local override).
2. `pry` on `PATH`.
3. a `target/release/pry` build inside the pry checkout.

If none exist: `cargo build --release` in the pry repo, then set `PRY_BIN`.

## Workflow: run → rank → label

**1. Run + rank** (the prescribed command — reproduce exactly):

```bash
PRY_BIN=/abs/path/to/pry/target/release/pry \
  python3 skills/pry/scripts/rank_backlog.py <ts-or-js-path> [--top N] [--json]
```

This projects the **welded-at-demand backlog** = findings where `demand=true`
and `class="welded"`, sorted high-precision-kind first
(subprocess → llm → db → network → slack → clock → random; order from the
`docs/precision-gate.md` census) then by `file:line`. It is deterministic
(byte-identical across runs). `fileio`/`env` are the diagnostic swamp and are
excluded from the demand subset by design.

**2. Label** each backlog finding by reading its `file:line` (the binary cannot —
this is the skill's job). Use the `docs/precision-gate.md` taxonomy:

- **GENUINE** — real weld, on/near a failure path, no seam to inject a failure,
  worth making injectable. *(This is the actionable backlog.)*
- **FALSE-WELD** — actually already seamed via an injected interface/factory/param
  pry's leaf model missed (a rung-3 gap). Report as a pry recall gap, not a code gap.
- **COSMETIC** — real weld but outside the thesis: a display/record value
  (`new Date().toISOString()` as a field, temp-name randomness) with no failure to inject.
- **AMBIGUOUS** — local context can't decide control-vs-record use.

**3. Report** the GENUINE findings as the testability backlog (file:line, kind,
why no seam, suggested injection seam). State precision honestly: cite how many
were GENUINE vs noise. Advisory only.

## Self-test

The prescribed command above, run against any TS path with boundaries, is the
skill's self-test: it must emit a deterministic `WELDED-AT-DEMAND BACKLOG`
ranking. Validated against `../ceal/packages` (68 findings, matches the frozen
`fixtures/ceal-ts-map.summary.json`).

## Degraded behavior

No binary → the consumer returns `status: degraded` with a build/PRY_BIN hint and
exit 1. Quality keeps its deterministic gates authoritative and omits the
testability backlog; do not claim a testability review succeeded without a
healthy binary.

## References

- `docs/precision-gate.md` — the labeling taxonomy + per-kind precision census.
- `docs/kill-gate.md` — why TS/JS only (Python KILL).
- `skills/pry/scripts/rank_backlog.py` — the PRY_BIN-honoring consumer.
- `../charness/integrations/tools/pry.json` — the charness external_binary manifest.
