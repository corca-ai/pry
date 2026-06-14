# Handoff

## Workflow Trigger

**Packaging is engineering-COMPLETE (S1–S5).** There is no single forced next
step. On pickup, either (a) run the formal `/achieve` After-phase closeout of the
packaging goal (`charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md`,
still `active` — engineering done, needs retro + disposition artifacts to flip to
`complete`), or (b) pick a follow-up below. **Discuss before building** — the
prior "Python frontend next" trigger is superseded (see Discuss).

## Current State

- **pry is now packaged + dogfood-proven.** TS/JS analyzer was already a validated
  GO (precision 88% ceal / 97% cautilus; see `docs/precision-gate.md`). This
  session wired it into charness and shipped the agent layer:
  - **S3** — `integrations/tools/pry.json` external_binary manifest in charness,
    mirroring `nose.json`. **Now on charness `main`** (`754e82ba` integrated by
    the charness side + their test fix `91d47352`; install-URL update `d7ef98ee`).
    pry surfaces as a `validation`-role tool for `quality`.
  - **S4** — F15 `pry` agent skill in this repo (`skills/pry/SKILL.md` +
    `skills/pry/scripts/rank_backlog.py`, `PRY_BIN`-honoring). Commits `5282d9c`,
    `5c25d5c`.
  - **S5** — dogfood proven: `PRY_BIN → rank_backlog.py ../ceal/packages` = **68
    welded-at-demand findings**, deterministic, matching the frozen
    `fixtures/ceal-ts-map.summary.json` on every field (fixture is current vs the
    lever'd classifier).
- **Two fresh-eye critique rounds** (S3: 3 angles + counterweight; S5 bundle: 2 +
  counterweight). All Act-Before-Close findings fixed.
- **Released: v0.1.0 on `corca-ai/pry`** (cargo-dist, nose model). `main` pushed,
  tag `v0.1.0`, GitHub Release published with `pry-installer.sh` + 4 platform
  tarballs (mac/linux × arm64/x86_64) + checksums. Config: `dist-workspace.toml`
  (shell installer; homebrew deferred — needs a tap-token secret).
- **Repo is PUBLIC; v0.1.0 installer verified end-to-end** — `curl -LsSf
  https://github.com/corca-ai/pry/releases/latest/download/pry-installer.sh | sh`
  installs a working `pry 0.1.0` (detect/healthcheck strings match the charness
  manifest). The nose-model install path now works for anyone.
- **charness wiring DONE + on `main`** — coordination complete; manifest install
  now points at the released `pry-installer.sh`; `quality` can detect/recommend pry.
- **Open (follow-ups):** `quality` does not *auto-invoke* pry yet (no dispatch path
  — agent-invoked via the F15 skill + `PRY_BIN`); Stage-2 rung-3 wrapper detection
  unbuilt (demand-welded is an upper bound); homebrew installer not yet added.

## Next Session

Pick one (none forced):
1. **quality auto-invoke** — wire a `quality` driver that runs `pry map` on TS/JS
   dirs as an advisory inventory (mirror nose's `inventory_nose_clones.py`), so pry
   runs inside standing quality, not just on-request via the F15 skill.
2. **Formal goal closeout** — `/achieve` After-phase on the packaging goal: retro
   + standalone disposition artifact → flip Status to `complete`.
3. **Deepen TS** — Stage-2 F22 rung-3 wrapper detection (closes the
   network/subprocess under-detection; sharpens demand-welded).
4. **Polish release** — homebrew installer (add tap repo + token secret), or
   Python only on a *non-glue OSS* corpus (author's repos are a recorded KILL).

## Discuss

- **The "Python frontend next" trigger is dead for the author's repos.** Both axes
  agree the author's Python is welded glue with no discrimination (`docs/kill-gate.md`
  Runs 1–3). This session the operator chose packaging over a third Python frontend.
  Only revisit Python on a *non-glue OSS* corpus.
- **Auto-invoke wiring** (quality runs `pry map` itself) is the natural next
  packaging increment if pry should run inside standing quality, not just
  on-request via the F15 skill.

## References

- `charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md` — the
  packaging goal: full slice log, user-verification commands, final-verification state.
- `docs/precision-gate.md` — validated TS precision + labeling taxonomy.
- `docs/kill-gate.md` — why TS-only (Python KILL).
- `skills/pry/SKILL.md` + `skills/pry/scripts/rank_backlog.py` — the F15 skill.
- `../charness/integrations/tools/pry.json` (on charness `main`, `d7ef98ee`) — the manifest.
