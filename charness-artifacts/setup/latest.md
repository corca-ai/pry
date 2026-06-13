# Setup — pry

- **Date:** 2026-06-13
- **Mode at start:** GREENFIELD (git initialized; only `initial-plan.md` and
  gather provenance present)
- **Mode after:** NORMALIZE (core operating surfaces created)

## What setup created

- `AGENTS.md` — deterministic charness operating contract (Project orientation,
  Skill Routing, Commit Discipline, Subagent Delegation), via
  `normalize_host_docs.py --execute`.
- `CLAUDE.md` — symlink → `AGENTS.md`.
- `README.md` — repo story / orientation, grounded in `initial-plan.md`.
- `docs/roadmap.md` — ordered priorities (Layer 0 + validation first, kill gate,
  then Layers 1–2).
- `docs/operator-acceptance.md` — hand-written first draft (no checks exist yet
  to synthesize from); design-stage acceptance + Layer 0 milestone checklist.

`docs/handoff.md` intentionally NOT created (no baton-pass needed).

## Concept source

No ideation pass was needed: `initial-plan.md` is already a rich, honest concept
surface. All scaffolded docs are derived from it.

## Commit policy

User approved tracking `charness-artifacts/` in git; AGENTS.md → Commit
Discipline records charness-artifacts as repo state.

## Fresh-eye review (setup delegation contract)

Three bounded `Explore` reviewers ran (host policy, operator takeover, surface
consistency):
- Host policy: PASS (minor non-blocking markdown spacing in machine-generated
  block; left as generator output).
- Surface consistency: PASS.
- Operator takeover: ISSUES → one accuracy fix applied (kill-gate citation
  corrected from `§7`–`§9` to `§8`–`§9` in `operator-acceptance.md`).

## Next step

Begin Layer 0 per `docs/roadmap.md`, validation harness first.
