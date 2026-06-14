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
  - **S3** — `integrations/tools/pry.json` external_binary manifest in charness
    (commit `754e82ba`, **local, not pushed**), mirroring `nose.json` honestly
    (experimental / manual / `PRY_BIN`, no fake release). pry now surfaces as a
    `validation`-role tool for `quality`. All 7 charness pre-commit gates green.
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
- **Open after release:**
  - **Repo is PRIVATE** → the `curl | sh` installer 404s anonymously. The
    nose-model public installer needs the repo to go **public** (operator's call).
  - **charness `pry.json` NOT updated** — still says manual/no-release/`PRY_BIN`.
    Update its install to the real `pry-installer.sh` URL only after (a) the repo
    is public AND (b) charness-side coordination (the S3 commit `754e82ba` is
    still local/unpushed, held for that coordination per operator).
  - **quality does not auto-invoke pry** (no dispatch path — agent-invoked via the
    F15 skill + `PRY_BIN`); Stage-2 rung-3 wrapper detection unbuilt (demand-welded
    is an upper bound).
- charness working tree also carries unrelated uncommitted `validate_debug_artifact`
  work (not ours; left untouched).

## Next Session

Pick one (none forced):
1. **Make `corca-ai/pry` public** (if intended) → then the `curl | sh` installer
   works anonymously; then update charness `pry.json` install to it (post-coordination).
2. **charness coordination** — loop in the charness side on the held-local S3
   commit (`754e82ba`); decide push + manifest install-URL update together.
3. **Formal goal closeout** — `/achieve` After-phase on the packaging goal: retro
   + standalone disposition artifact → flip Status to `complete`.
4. **Deepen TS** — Stage-2 F22 rung-3 wrapper detection (closes the
   network/subprocess under-detection; sharpens demand-welded). Or homebrew
   installer (add tap + token). Or Python only on a *non-glue OSS* corpus (author's
   repos are a recorded KILL).

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
- `../charness/integrations/tools/pry.json` (commit `754e82ba`, local) — the manifest.
