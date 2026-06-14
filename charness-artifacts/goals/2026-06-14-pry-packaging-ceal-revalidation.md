# Achieve Goal: pry packaging (external_binary + F15 skill) + ceal re-validation

Status: active
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: S3 — charness `integrations/tools/pry.json` external_binary manifest + lock.
- Current slice intent: wire packaging into charness so `quality` can detect/invoke
  `pry map`, mirroring `nose.json`. S1 (build/smoke) + S2 (ceal re-validate/re-freeze)
  are DONE and committed. Spans the charness manifest commit (+ any lock/index regen).
- Next action: write `pry.json` in charness mirroring `nose.json`; validate against
  `manifest.schema.json`; run charness integrations validation test.
- Verification cadence: cheap deterministic checks at commit boundaries
  (`cargo build --release`, `cargo test`, JSON determinism diff); fresh-eye
  critique + manifest schema validation at slice boundaries; the end-to-end
  packaged dogfood loop at the final bundle boundary.
- Gate cadence: per-slice `cargo test` + schema validation; final bundle proof =
  the PRY_BIN dogfood loop (quality / F15 skill invokes `pry map`) over a sample.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make `pry` a tool the charness `quality` skill can actually invoke, and prove the
built Stage-1 TS analyzer still holds up on a *current* ceal main — closing
handoff decision #2 ("Wire packaging") with a real dogfood loop.

Two concrete outcomes:

1. **Packaging** — a schema-valid `integrations/tools/pry.json` external_binary
   manifest (+ lock) committed into the charness repo, mirroring `nose.json`, so
   `quality` can detect and invoke `pry map`; plus the F15 `pry` agent skill (the
   intelligence layer that consumes `pry map` JSON and produces the
   backlog-finder ranking), shipped in *this* repo and honoring a local `PRY_BIN`
   override for dogfooding.
2. **ceal re-validation** — run the built `pry map` on a freshly-pulled ceal main
   (now at `cdd31884`, which added new slack/agent **error-handling** files), and
   either reproduce or explain-then-re-freeze `fixtures/ceal-ts-map.summary.json`,
   so the frozen evidence is honest against the corpus it actually describes.

## Non-Goals

- **No real GitHub release / publish.** Dogfood via a local `cargo --release`
  build + `PRY_BIN` override only (operator decision). A published installer like
  nose's is a deliberate later goal; this run claims no outward-facing release.
- **No Stage-2 / F22 rung-3 wrapper detection** (handoff decision #1). The known
  network/subprocess under-detection (leaf-0.74) stays as-is; the demand-welded
  number remains an upper bound. Separate goal.
- **No analyzer capability growth** beyond what re-validation forces. No new
  catalog kinds, no classifier changes unless the ceal delta exposes a defect
  (and even then: file via `issue`, do not silently expand scope).
- **No writes to the ceal repo.** ceal is a read-only validation corpus.
- **No pry self-analysis** (pry parses TypeScript, not its own Rust — F26 invariant
  is satisfied by design review, not by literal self-application this run).
- **No dedicated charness *public-skill* registration for pry** beyond the
  manifest's `supports_public_skills` wiring. The F15 intelligence skill ships in
  the pry repo this run; promoting it into a standalone charness public skill is a
  follow-up if wanted.

## Boundaries

- **Two repos in scope:** `pry` (this repo — binary, F15 skill, re-frozen fixture,
  goal artifact) and `charness` (sibling — the external_binary manifest + lock).
  The charness commit is operator-approved (interview Q1 = "pry + charness
  manifest"). ceal is read-only.
- **Local commits only by default.** No `git push` / PR for either repo unless the
  operator explicitly asks at closeout. Remote push is a phase-scoped approval not
  yet granted.
- **No publish / release / remote CI** (interview Q2 = local `PRY_BIN`). The
  delivery mechanism is a maintainer-local override; the *consuming* side (F15
  skill / any quality reference script) must read `PRY_BIN` — charness's `NOSE_BIN`
  is consumer-script-specific (`inventory_nose_clones.py`), not a generic host
  resolver, so pry's consumer must honor `PRY_BIN` itself.
- **Re-freeze is operator-sanctioned** (interview Q3). Changing the committed
  ground-truth fixture is allowed *only* with a recorded provenance line (new ceal
  SHA) and a written delta explanation; silent number changes are forbidden.
- The standard external-side-effect rule still applies: any approved
  publish / push / remote-CI / apply is phase-scoped and does not carry forward;
  done-early test-only continuation is local by default.

Discuss before activation: RESOLVED — three consequential defaults were settled
in the Before-phase interview and need no further discussion. (a) Cross-repo
commit into charness is approved (Q1). (b) Skipping live/release/remote-CI proof
in favor of a local `PRY_BIN` dogfood is approved, and the final report must name
those skipped proof levels (Q2). (c) Re-freezing the committed
`ceal-ts-map.summary.json` fixture is approved under the provenance+delta
discipline above (Q3). No open consequential discussion remains.

## User Acceptance

What the user can do to verify completion directly:

- `cargo build --release && ./target/release/pry --version` → prints a `pry`
  version line; `./target/release/pry map --help` → mentions "risk ranking".
- `cat fixtures/ceal-ts-map.summary.json` → shows numbers re-frozen at ceal
  `cdd31884`, with a provenance line naming that SHA and a one-line delta note vs
  the prior freeze.
- In the charness repo: `integrations/tools/pry.json` exists, validates against
  `integrations/tools/manifest.schema.json`, and the integrations validation test
  passes; `supports_public_skills` lists `quality`.
- `PRY_BIN=$(pwd)/target/release/pry` + the F15 skill (or a quality reference)
  produces a welded-at-demand backlog ranking for a TS path — the end-to-end
  dogfood loop runs without a published binary.

## Agent Verification Plan

### Low-Cost Checks

- `cargo build --release` and `cargo test` green (existing classify smoke tests).
- `pry --version` exit 0 + stdout contains `pry`; `pry map --help` exit 0 +
  stdout contains `risk ranking` (these are exactly what the manifest detect /
  healthcheck assert — verify the strings match before writing the manifest).
- JSON determinism: run `pry map <sample> --summary-only` twice, diff = empty.
- charness: validate `pry.json` against `manifest.schema.json`; run the charness
  `control_plane/test_integrations_validation` (+ tool-lifecycle / recommendation
  tests if they enumerate tools) green.
- `check_goal_artifact.py` passes before any status flip.

### High-Confidence Checks

- Fresh-eye slice critique (per Subagent Delegation policy — bounded reviewer, no
  same-agent substitute) on: (1) the cross-repo manifest correctness + schema +
  intent_triggers/recommendation_role choices, (2) the re-freeze delta
  explanation (is the number move actually accounted for by the new files, or is
  it a classifier regression?).
- `quality` validation-recommendation routing for the closeout (per CLAUDE.md), to
  pick the right gate/HITL surface rather than self-asserting.

### External Or Live Proof

- **None by design.** No publish, no remote CI, no provider roundtrip. The final
  report must explicitly name these as skipped proof levels and claim only the
  *local* PRY_BIN dogfood loop. The end-to-end loop (slice S5) is the strongest
  proof this goal carries.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Build the release binary + confirm the detect/healthcheck surface | Everything downstream (manifest strings, validation, dogfood) depends on a green binary and the exact `--version` / `map --help` stdout | `cargo build --release` + `cargo test` green; captured `pry --version` and `pry map --help` output | planned |
| S2 | ceal re-validation + re-freeze | The headline ask; ceal moved `8238b245→cdd31884` adding error-handling files — re-run on the moved corpus, explain the delta, re-freeze | New `pry map ../ceal/packages --summary-only` JSON; delta note vs prior freeze; updated `fixtures/ceal-ts-map.summary.json` with `cdd31884` provenance | planned |
| S3 | charness `integrations/tools/pry.json` manifest + lock | Closes "wire packaging" so `quality` can invoke `pry map`; mirror `nose.json` exactly | Schema-valid manifest committed in charness; integrations validation test green; lock/index regenerated per charness process | planned |
| S4 | F15 `pry` agent skill (this repo) | The intelligence layer the CLI defers to — consumes `pry map` JSON → ranks welded-at-demand; honors `PRY_BIN` | A lean SKILL/skill-doc + consumer that reads `PRY_BIN` and emits the backlog ranking; documented run→rank→label mechanics | planned |
| S5 | End-to-end dogfood proof (bundle boundary) | Prove the *whole packaged loop* works locally without a release | `PRY_BIN=…/target/release/pry` → quality / F15 skill produces a welded-at-demand ranking for a TS sample; recorded transcript | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — implementation slices (S1–S4) route through `impl`; the closeout
  gate through `quality`'s validation recommendation; slice critique through
  `critique` with a bounded fresh-eye reviewer. Record the concrete `find-skills`
  route per phase here as the run proceeds. (Anticipated; confirm via
  `find-skills` at each boundary, do not treat this as the hard-coded map.)
- **Gather step** — `Gather: n/a — all context sources are local repos/files
  (ceal, nose, charness, this repo's docs), reached via git/filesystem, not an
  external URL/Slack/Notion/Docs/Drive surface.`
- **Release step** — `Release: n/a — no version bump and no generated install
  manifest; delivery is a local PRY_BIN override (interview Q2). Watch item: if
  adding pry.json forces a charness integrations index/lock regen, that regen is
  a charness-internal process step, not a pry release surface.`
- **Issue closeout step** — `Issue closeout: n/a — this goal resolves no tracked
  GitHub issue. Defects found during re-validation are filed via issue and listed
  in Off-Goal Findings, not closed by this goal.`

## Slice Log

### Slice 1: Build + confirm detect/healthcheck surface

- Objective: Green release binary + capture the exact strings the charness manifest will assert
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: cargo build --release (ok), cargo test (3/3 classify_smoke pass), pry --version -> 'pry 0.1.0', pry map --help -> 'risk ranking, NOT a bug list'. Both manifest detect/healthcheck strings confirmed present.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: ceal re-validation + re-freeze

- Objective: Run pry map on fresh ceal main (cdd31884) and re-freeze the fixture with an explained delta
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Deterministic (run x2 byte-identical). Corpus moved 8238b245->cdd31884: files_scanned 457->461 (+4 new non-test src files), ALL boundary counts unchanged (850 total, demand-welded 0.75). Verified the 4 new error-handling files have ZERO boundary-pattern hits (grep: Date/fetch/fs/random/exec/http/crypto/setTimeout) -> 0-new-boundaries is correct, not a silent miss. Fixture re-frozen with _provenance block.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Slice 3: charness pry.json external_binary manifest

- Objective: Wire pry as a quality-advisory external_binary in charness so it is discoverable/doctor-checkable; mirror nose.json honestly given no published release.
- Why this approach: Mirror nose.json (external_binary) not cautilus (external_binary_with_skill): pry's F15 skill ships in the pry repo, so charness only needs the binary manifest. Honest pre-release shape (experimental/manual/PRY_BIN) over a fake release installer.
- Commits: charness 754e82ba (local, no push)
- What changed: NEW integrations/tools/pry.json (+plugin mirror); +pry in dependencies.json (+mirror); regenerated plugin mirror (sync_root_plugin_manifests.py) + find-skills inventory (latest.json/.md). 6 files, 237 insertions.
- Alternatives rejected: Rejected access_modes=[binary,env,degraded] (env forces capability_requirements.env_vars, over-asserts the PRY_BIN crutch as first-class) -> kept [binary,degraded] mirroring nose. Rejected external_binary_with_skill (skill ships in pry repo).
- Targeted verification: validate_integrations exit0 (13 manifests/7 deps); validate_current_pointer_freshness exit0; check_staged_mirror_drift exit0; pytest control_plane/test_integrations_validation 15 passed; all 7 charness pre-commit gates passed. detect/healthcheck strings confirmed vs real binary (pry 0.1.0; 'risk ranking').
- Test duplication pressure:
- Critique: full: 3 fresh-eye angle subagents (schema/cascade=PASS; honesty; wiring) + 1 counterweight. Acted: dropped unevidenced 'db' from summary boundary-kinds (DB-in-TS=0); reworded host_note implying quality already invokes pry. Deferred: access_modes aspirational (revisit at real release). Over-worry: dead corca-ai/pry link (neutralized by experimental+notes).
- Off-goal findings: charness working tree carries unrelated uncommitted changes (scripts/validate_debug_artifact.py + mirror, tests/test_debug_artifact.py) from commit a930cc5f line; left untouched/unstaged.
- Lessons carried forward: Adding a tool manifest cascades to: plugin mirror (sync_root_plugin_manifests.py) AND find-skills inventory (latest.json freshness check) -> both must regen or pre-commit gates fail. No per-tool lock needed (nose has none).
- Metrics: S3 makes pry discoverable + doctor-checkable; it does NOT make quality auto-invoke pry. No quality dispatch/driver code path ships in either repo (S4 ships the F15 skill + consumer, not a quality auto-invoke). The dogfood loop is "F15 skill + consumer via PRY_BIN"; auto-invoke-from-quality is a deliberate, unbuilt deferral.

### Slice 4: Slice 4: F15 pry agent skill (PRY_BIN-honoring)

- Objective: Ship the F15 intelligence layer in the pry repo: a SKILL doc + a PRY_BIN-honoring consumer that runs pry map and projects the welded-at-demand backlog, leaving GENUINE/FALSE-WELD/COSMETIC labeling to the agent.
- Why this approach: CLI is dumb (F1); intelligence in the skill. Consumer mirrors nose's resolve_*_bin override pattern (PRY_BIN -> PATH -> in-repo target/release fallback for dogfooding). SKILL.md prescribes the exact reproducible command (prescribed-path-self-test).
- Commits: (this commit)
- What changed: NEW skills/pry/SKILL.md (run->rank->label workflow, labeling taxonomy, advisory framing, TS/JS-only scope); NEW skills/pry/scripts/rank_backlog.py (PRY_BIN resolver, pry map runner, welded-at-demand projection, deterministic kind-ordered ranking, degraded handling).
- Alternatives rejected: Rejected a Rust subcommand for ranking (would put intelligence in the binary, violating F1). Rejected baking labeling into the script (labeling needs to read source = agent's job).
- Targeted verification: Consumer run on ../ceal/packages: 68 welded-at-demand findings (subprocess 16, network 9, clock 37, llm 3, slack 2, random 1), deterministic (byte-identical x2). Live pry map summary == frozen fixtures/ceal-ts-map.summary.json on EVERY field incl by_kind -> fixture is current vs the lever'd classifier, not stale. Degraded path + exit codes exercised.
- Test duplication pressure:
- Critique: deferred to S5 bundle-boundary full fresh-eye critique (per goal verification cadence: end-to-end dogfood loop is the final bundle boundary). S4 is a verified consumer + prompt surface; reviewed together with the dogfood proof + user-verification at closeout.
- Off-goal findings:
- Lessons carried forward: The F15 demand-welded backlog on ceal is 68 (down from precision-gate's pre-lever 174) -> the cosmetic-clock + duration-record levers are doing the precision work end-to-end through the packaged consumer.
- Metrics: ceal demand-welded: 68 (clock 37 / subprocess 16 / network 9 / llm 3 / slack 2 / random 1); lens fraction 0.4892.

### Slice 5: Slice 5: end-to-end dogfood proof + bundle critique

- Objective: Prove the packaged loop locally (PRY_BIN -> F15 skill/consumer -> welded-at-demand ranking) and run the final bundle critique over the F15 skill + proof.
- Why this approach: Final bundle boundary per the goal's verification cadence.
- Commits: (this commit)
- What changed: Bundle-critique fixes: rank_backlog.py guards files_scanned==0 (kill false all-clear on bad path), clamps negative --top, by_kind uses .get; SKILL.md degraded note no longer implies quality has pry omit-logic; goal S3 metrics corrected (no quality auto-invoke driver shipped).
- Alternatives rejected: Rejected flipping goal to complete while the artifact still implied a delivered quality driver (honesty gate).
- Targeted verification: DOGFOOD PROVEN: PRY_BIN -> rank_backlog.py ../ceal/packages = 68 welded-at-demand findings (subprocess 16/network 9/clock 37/llm 3/slack 2/random 1), deterministic (byte-identical x2), live pry map == frozen fixture on every field. Post-fix: bad path now degrades exit1 (was false all-clear); --top -1 -> 0; py_compile clean.
- Test duplication pressure:
- Critique: full bundle (2 fresh-eye angle subagents: consumer-correctness + SKILL-honesty/proof; 1 counterweight). Act-before-close: A2 false-all-clear guard + B2a goal honesty (no quality driver delivered) -> both applied. Bundled: A1/A4 hygiene + B2b SKILL reword -> applied. Over-worry: none. This bundle critique also serves as the goal's closeout fresh-eye disposition review (angle B reviewed final-proof + user-acceptance honesty).
- Off-goal findings:
- Lessons carried forward: Discoverable != invocable: a tool manifest + an agent skill make pry usable BY AN AGENT via PRY_BIN, but NOT auto-invoked by quality (no dispatch path). Keep that distinction explicit in every closeout claim.
- Metrics: Dogfood loop = F15 skill + consumer via PRY_BIN (proven). Auto-invoke-from-quality = unbuilt, deliberately deferred.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct the
originating context by following them in order:

1. `docs/handoff.md` — the originating workflow trigger; decision #2 ("Wire
   packaging") is this goal's mandate; Run 5/6 are the prior validation baseline.
2. `docs/spec-layer0.md` F15 (packaging contract: external_binary + pry agent
   skill, CLI dumb / intelligence in the skill) + F25/F26/F28.
3. `../charness/integrations/tools/nose.json` — the exact external_binary manifest
   template pry's must mirror; `manifest.schema.json` is the validation target.
4. `../charness/skills/public/quality/scripts/inventory_nose_clones.py:32` — shows
   `NOSE_BIN` is a consumer-script override, not a generic host resolver (the
   reason pry's consumer must read `PRY_BIN` itself).
5. `fixtures/ceal-ts-map.summary.json` + `docs/ceal-ts-gate.md` + `docs/ts-cross-corpus.md`
   — the frozen evidence being re-validated and the backlog-finder framing.
6. `src/main.rs`, `src/classify.rs`, `catalog/typescript.toml` — the built
   analyzer surface (`pry map`, `pry --version`).
7. ceal at `cdd31884` (pulled this session; was `8238b245`) — the live validation
   corpus.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- **Q1 — Repo scope.** Options: {pry + charness manifest} / {pry-only, manifest
  staged} / {pry-only, defer manifest}. **Chosen: pry + charness manifest** — the
  full dogfood loop, two commits across two repos. Rejected the pry-only paths
  because handoff decision #2 explicitly wants `quality` able to invoke `pry map`,
  which requires the manifest to actually land in charness; staging it as a file
  would leave the loop unproven.
- **Q2 — Binary delivery.** Options: {local `PRY_BIN` override} / {cut a real
  GitHub release}. **Chosen: local `PRY_BIN` override** — dogfood against the
  `cargo --release` build, no publishing, fully reversible. Rejected the real
  release because pry is still Layer-0/Stage-1; an outward-facing published
  installer is premature and a separate, heavier, irreversible-leaning step.
- **Q3 — Validation bar.** Options: {re-freeze + explain delta} / {exact
  reproduction}. **Chosen: re-freeze + explain delta** — ceal main moved and added
  files, so the corpus genuinely changed; pass = deterministic run + the delta is
  accounted for by the new files + re-freeze at the new SHA. Rejected exact
  reproduction because it would falsely flag an expected corpus change as a
  regression; the regression discipline instead lives in *explaining* the delta.

## Plan Critique Findings

Not yet run. Recommended first action at activation (or fold into S1): a bounded
fresh-eye plan critique focused on the two highest-leverage risks —
(1) cross-repo manifest correctness (will the charness integrations validation /
recommendation tests accept a new tool with `recommendation_role: validation` and
`supports_public_skills: [quality]`, or does adding a tool require touching a
registry/index that this plan under-scopes?), and (2) the re-freeze guardrail
(does the slice plan make a classifier regression *distinguishable* from an
expected corpus delta, rather than rubber-stamping any number move?). Record
blockers folded + reviewer provenance here when run.

## Off-Goal Findings

(none yet)

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`.

Retro: TODO — run `retro` at closeout
Host log probe: TODO — `retro`'s `probe_host_logs.py`, or skip with reason
Disposition review: TODO — fresh-eye disposition review at closeout

## User Verification Instructions

(filled at closeout — will mirror User Acceptance with concrete commands + the
observed re-frozen numbers and the charness commit SHA.)

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
