# Handoff

## Workflow Trigger

**This is a discussion pickup, not a build trigger.** Packaging + release are
engineering-COMPLETE; there is no forced next step. Next session = *decide* the
next center with the operator (see Discuss), then build. The prior "Python
frontend next" trigger is dead (Python is a recorded KILL — `docs/kill-gate.md`).

## Current State

- **pry v0.1.0 is released, public, and wired.** TS/JS analyzer (validated GO;
  demand-subset precision ~88% ceal / ~97% cautilus) shipped this session:
  - **Released:** `corca-ai/pry` is PUBLIC; `v0.1.0` GitHub Release via cargo-dist
    (`pry-installer.sh` + 4 platform tarballs). Installer verified end-to-end
    (`curl … pry-installer.sh | sh` → working `pry 0.1.0`). `main` pushed.
  - **charness-wired (on `main`):** `integrations/tools/pry.json` external_binary
    manifest, install → the released installer; pry is a `validation`-role tool for
    `quality`.
  - **F15 skill (this repo):** `skills/pry/SKILL.md` + `skills/pry/scripts/rank_backlog.py`
    (`PRY_BIN`-honoring); dogfood = 68 welded-at-demand findings on ceal,
    deterministic, matches the frozen fixture.
  - Full slice/commit/critique detail lives in the goal artifact (References).
- **quality auto-invoke is now being built charness-side** (their
  `inventory_testability_surface.py` wraps `pry map` + honors `PRY_BIN`). **charness
  owns this** — not a pry-side task.

## Next Session — decide, then build (none forced)

- **Syntactic floor** — the one genuinely un-built Layer-0 deliverable (the *claim*
  channel: empty catch / swallowed error / log-and-continue on a mutating path),
  kept physically separate from the map. The strongest pry-side "deepen" candidate.
- **Stop / consolidate** — pry is released + wired + honestly documented; doing
  nothing more is a legitimate, clean end state.
- **Polish** — homebrew installer (needs a tap repo + token secret).
- **Rung-3 stage-2: DEFERRED, do not build.** Scouted on ceal → the injected
  transport/executor wrapper gap is *not material* (welds are genuine; demand-welded
  is not an overcount). A safe rule needs cross-file analysis + risks false-seaming.
  See `docs/precision-gate.md` "Rung-3 stage-2 census". (Form-A `implements I` is built.)

## Discuss

- **Is pry "done enough"?** The thesis is validated (TS GO, Python KILL), the tool
  is released + wired. The open product question is whether to invest in the
  syntactic floor (a second, zero-FP claim channel) or treat Layer-0-map as the
  shippable end and stop.
- **Python** only ever revisits on a *non-glue OSS* corpus, never the author's repos.
- **Formal goal closeout** (`/achieve` After-phase: retro + disposition → flip the
  packaging goal `active`→`complete`) is optional housekeeping, not product work.

## References

- `charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md` — packaging
  goal: full slice log, commit SHAs, user-verification commands, final-verification.
- `docs/precision-gate.md` — validated precision, labeling taxonomy, rung-3 census.
- `docs/kill-gate.md` — the go/kill record (TS GO, Python KILL).
- `skills/pry/SKILL.md` + `skills/pry/scripts/rank_backlog.py` — the F15 skill.
- `../charness/integrations/tools/pry.json` (on charness `main`) — the manifest.
