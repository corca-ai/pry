# Achieve Goal: E9 — nose-style multi-repo validation sweep (does welded-at-demand predict bugs + generalize)

Status: complete
Created: 2026-06-15
Completed: 2026-06-15
Activation: `/goal @charness-artifacts/goals/2026-06-15-e9-multi-repo-validation-sweep.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **CLOSEOUT** — S1–S5 all DONE + critiqued + committed. Next:
  quality validation recommendation, Final Verification, retro, disposition review.
- S5 result: Python (b)-gate **KILL** (welded-saturated 0.902, out of band;
  net+subproc 0.765 in-band but clock-driven saturation; kill-gate Run 7). No
  frontend built (KILL + moot given FALSIFIED enrichment).
- **MAIN RESULT (recorded):** 쟁점 4 **FALSIFIED** for this corpus — welded-at-demand
  matched enrichment vs rest = **1.05, CI [0.96,1.18]** across 25 TS apps (dev 0.93,
  heldout 1.11 weak/not-refuted but far below the 1.5 GO bar; vs seamed 0.90). The
  structural signal is a testability classifier, NOT a defect predictor on this
  corpus. Honest negative (nose-retraction discipline).
- **Honesty-gate anchor (closeout proof):** the final frozen pre-registration is
  commit `47eeb633` (numerator + CI + control-amendment pinned). The first
  enrichment-number commit is `6a19e3d`. Proven:
  `git merge-base --is-ancestor 47eeb633 6a19e3d` → OK.
- Next action: S5 — run `python3 harness/bgate_lens.py --corpus`; record GO/KILL in
  `docs/eval-gate.md` / `docs/kill-gate.md`; build frontend only on GO.
- Verification cadence: cheap deterministic checks at commit boundaries (corpus
  schema, mine/map determinism, cargo build+test, AC4 denylist); fresh-eye
  critique at slice boundaries (corpus-bias, enrichment soundness, Python
  frontend gating); the cross-corpus Tier-1 enrichment result is the bundle
  boundary. No external/live proof in scope (observational git mining on local
  clones).
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Prove pry's core thesis with **independent, multi-repo evidence** before any more
precision polish (the levers' assumption is unverified). Answer the two
load-bearing questions the precision levers *assume*:

1. **쟁점 4 — does welded-at-demand actually predict real defects?** Tier 1, the
   directly-observed bugfix-**enrichment** result (nose's G1 analog): across a
   broad corpus, are welded-at-demand sites touched by bugfix commits at a higher
   rate than seamed sites? Pure git + map join, no per-site gold → robust.
2. **쟁점 2 — does the signal generalize beyond the 4 H3 apps?** A pre-registered
   `dev`/`heldout` split: tune any threshold on `dev` only, report `heldout`
   separately.

Modeled on nose's `eval/hazard/` **PATTERN** (`run_corpus.sh` + `corpus.json` +
mining), **reusing the pattern, NOT nose's repos** (nose's corpus is
15-per-language *libraries* — the wrong shape; pry needs boundary-welding
*apps*). The corpus self-selects app-shaped TS/JS OSS from GitHub (operator-
approved). Folds in the **full Python branch**: discover non-glue Python apps,
run the analyzer-free (b)-gate lens, and — on a (b)-gate GO — build the Python
frontend (`catalog/python.toml` exists) and fold Python into the sweep.

## Non-Goals

- **No Tier 2 — SZZ bug-linked gold + LLM-panel precision audit (operator-
  dropped, 2026-06-15 interview Q3).** The handoff's "fragile cherry" is out of
  scope: no `szz.py` port to tree-sitter-typescript, no LLM-panel ~11% audit.
  SZZ bug-linked gold becomes a separate future goal. (Why dropped: nose built
  the same auto bug-linked gold, an LLM-judge audit found it only ~11% precise,
  and they RETRACTED the "validated against bug-linked harm" claim. The robust
  result is Tier 1; pry skips the fragile cherry this goal.)
- **No causal / prediction claim shipped.** Tier 1 is a directly-observed
  **correlation** (an enrichment ratio), never "welded *causes* bugs." The
  shipped `pry` binary stays testability-only — "risk ranking, NOT a bug list"
  (the dropped kill-gate (a)-axis). Enrichment is dev-time evidence that the
  structural signal is worth trusting, not a product metric.
- **No LLM / credential in the shipped binary** (E2/SC4). Tier 1 needs **no LLM**
  (git + map join). The (b)-gate lens is dev-time, analyzer-free (hand/script
  sample, as Runs 1–5 did). Harness scripts stay mechanical (AC4 denylist).
- **No outbound on third-party repos.** No PRs / issues / disclosure on the swept
  OSS apps — corca-owned dogfood only. Off-goal defects in pry itself are filed
  via `issue`; nothing is filed against the corpus repos.
- **No full precision-panel re-labeling of the whole ≈15+ heldout arm.** Tier 1
  enrichment is the *cheap* generalization signal (no per-repo LLM panel). The
  broad corpus exists *because* Tier 1 needs no labeling. Expanding the 3-persona
  precision panel to every heldout repo is out-of-scope-by-default (a sampled
  subset or a follow-up only) — this goal does not move the SC2 precision
  gate-close on its own.
- **No two-directional safety claim from the seamed arm.** Absence of a historical
  bugfix ≠ "the seam prevented a bug" — the signal is one-directional (a
  seamed-no-bugfix site may just be younger / colder / less-exercised code). Tier 1
  claims only that **welded sites are enriched among bugfix-touched sites**, never
  that seams are safe; "welded vs seamed" is not a verified clean control (E9 SZZ
  caveat — absence-of-bugfix is uninformative).
- **No Python analyzer breadth beyond the (b)-gate fold-in.** If S5 GO-builds the
  Python frontend, its scope is *exactly* "enough `catalog/python.toml` coverage to
  run `pry map` on the discovered Python apps and fold them into the enrichment" —
  NOT catalog parity with the TS frontend, NOT a shippable Python release, NOT new
  Python-specific levers. Frontend-completeness for its own sake is a separate goal.
- **No marketing / leaderboard / showcase / outbound adoption play** (operator
  killed it; this is measurement-for-the-algorithm only).

## Boundaries

- **Corpus = third-party, app-shaped, pinned.** ≈20–25 independent (non-corca)
  TS/JS OSS *applications/services* (route handlers / service layer / DB clients /
  env+config — NOT single-purpose libraries), split **dev 5 / heldout 15+**;
  PLUS a stratified set (~5–8) of **non-glue Python apps** for the (b)-gate
  branch. Real error-handling + substantial bugfix history (for mining),
  permissive license, active, NOT corca. Seed = the 4 H3 apps (outline / flowise
  / continue / librechat — already app-shaped, mapped, frozen-labeled). **Write** an
  app-shapedness/domain scorer (`harness/repo_fit.py` is a site-count/recall
  *gate*, NOT a domain scorer — reuse its pre-registered-floor *discipline*, not
  its function), stratify by domain (and TS/JS by clock-injection rate, the
  discipline fingerprint), **pin commits**, prune vendored/generated/`.vitest`
  (reuse nose's prune discipline). Freeze to a `corpus.json` whose **schema file +
  validator are S1 deliverables** (neither exists yet), modeled on nose's
  `bench/goldens/corpus.json` shape — note nose's hazard `run_corpus.sh` itself
  hardcodes its repo list and reads no corpus.json; the schema is borrowed from
  nose's *separate* dedup benchmark, not the sweep pattern.
- **Pre-register before measuring — git-provable, not honor-system (honesty gate,
  like the kill-gate floor):** the `dev|heldout` split, the Tier-1 **metric
  denominator** (= a **matched comparison**: welded vs seamed sites matched on
  file-churn + site-size — the only form that neutralizes confound R-B, "welded
  sites are simply more numerous/larger/in hotter files"), and the **enrichment
  floor + its symmetric falsifier** are committed to a **separate pre-registration
  artifact** (`harness/fixtures/eval/preregistration.md` or a `config.py`-style
  constant — mirroring `REPO_FIT_SITE_FLOOR` "set BEFORE the number so it cannot be
  moved post hoc" + the F27 "frozen before this run" discipline) whose **git commit
  must precede the commit that writes any enrichment number**, so a fresh closeout
  reviewer can *prove* the order from git rather than trust a self-attesting line
  inside `corpus.json`. The floor is **two-sided**: a "signal real ≥ X" bar **and**
  a pre-committed **FALSIFIER** — "if the matched-denominator enrichment ratio ≤ Y
  or collapses to ~1.0, the welded-at-demand thesis is FALSIFIED for this corpus"
  (the nose `rate-match ≠ precision` lesson: a floored ratio can look real and be a
  pure confound artifact). `log`/report whatever is pruned or excluded — no silent
  truncation.
- **External fetches route through `gather`** (CLAUDE.md). GitHub discovery uses
  `gh` / the GitHub API (authed locally; approved as handoff step 1). Discovery
  reads repo structure (read-only); clones are local.
- **Sweep fan-out via the Workflow orchestration tool** (the handoff names it):
  per repo clone@pinned → `pry map` → mine bugfix commits → join. Parallel +
  incremental (skip already-mined). Dev-time, local clones only.
- **Python frontend build is CONDITIONAL on a (b)-gate GO, and sequenced AFTER the
  TS result.** The **(b)-gate GO criterion = the LENS criterion** (kill-gate.md
  F27/Run 5): the **substitution-demand subset** (clock/clients/network/subprocess)
  welded-fraction lands in band **`[0.15, 0.85]`** — **NOT** the bare welded-
  fraction (retired as fs-swamped ~0.9 in both languages, the *wrong* test). A
  **KILL** (lens-subset out of band, or mute: decided-fraction < 0.40) closes the
  Python branch at the analyzer-free lens result — **no frontend is built** (the
  kill-gate discipline: build a frontend only on a per-corpus GO). **Sequencing
  gate:** S5's frontend build may **not begin until S3 (Tier-1 enrichment) and S4
  (dev/heldout) have a recorded verdict in `docs/eval-gate.md`** — on an early GO
  the GO is *recorded and queued*, not started, so the heavy frontend cannot starve
  the load-bearing TS result. The frontend is the one heavy analyzer-capability
  addition and it is gated both ways.
- **Local commits only by default.** No `git push` / PR for any repo unless the
  operator explicitly asks at closeout. Remote push is a phase-scoped approval
  not yet granted.
- **Shipped binary stays byte-deterministic and zero-LLM** (SC4/AC4); the only
  analyzer change in scope is the *conditional* Python frontend (a new frontend,
  not an LLM/credential dependency). Third-party corpora are **read-only**.
- The standard external-side-effect rule applies: any later approved
  publish/push/CI/apply is phase-scoped and does not carry forward.

Discuss before activation: RESOLVED — four consequential defaults were settled in
the Before-phase (handoff + the 2026-06-15 interview) and need no further
discussion. (a) External GitHub corpus discovery + third-party local clones are
approved (handoff step 1 explicitly: "corpus discovery from GitHub IS approved").
(b) Building a Python frontend (analyzer capability growth) is operator-chosen
(interview Q2 = "Full Python branch incl. frontend") but **conditional on a
(b)-gate GO**; on KILL it does not build. (c) Tier-1 enrichment is an
observational correlation, never shipped as a causal/prediction claim — a
proof-level non-claim the final report must restate (the nose-retraction
discipline). (d) No outbound on the third-party corpus repos. No open
consequential discussion remains.

## User Acceptance

What the user can do to verify completion directly:

- `cat corpus.json` (or `harness/fixtures/eval/corpus.json`) → ≈20–25 TS/JS app
  repos + ~5–8 Python apps, each with `id/name/primary_language/domain/url/
  commit/split` (schema-validated), pinned commits; the `dev|heldout` split +
  matched-comparison denominator + floor + falsifier live in a **separate
  pre-registration artifact whose git commit precedes** the first
  enrichment-number commit (`git merge-base --is-ancestor` provable, not a
  self-attesting line).
- The sweep harness runs deterministically per repo: clone@pinned → `pry map` →
  mine bugfix commits → join; re-running the mine yields byte-identical output.
- `docs/eval-gate.md` carries a **Tier-1 enrichment** section: welded-at-demand
  bugfix-touch rate vs seamed bugfix-touch rate across the corpus, the
  pre-registered floor, and the verdict (signal real / not), every number
  contestable against the pinned corpus.
- **Generalization (쟁점 2):** the enrichment is reported `dev` vs `heldout`
  separately; any tuned threshold is tuned on `dev` only.
- **Python branch:** the (b)-gate lens result (GO/KILL) is recorded; if GO, the
  Python frontend exists (`pry map` runs on a Python app) and Python repos fold
  into the enrichment; if KILL, the analyzer-free result is recorded and no
  frontend ships.
- The shipped binary is unchanged on the zero-LLM axis: the AC4 denylist passes
  (`Cargo.lock` has no HTTP/LLM client; harness scripts import no LLM/HTTP client).

## Agent Verification Plan

### Low-Cost Checks

- `corpus.json` validates against its (S1-deliverable) schema; the **separate
  pre-registration artifact** (split + matched-comparison denominator + floor +
  falsifier) exists.
- **Pre-registration commit-ordering proof:** the pre-registration artifact's
  commit is an ancestor of / precedes the first enrichment-number commit
  (`git merge-base --is-ancestor <prereg-sha> <enrichment-sha>`) — the git-provable
  closeout proof that split + floor + denominator were fixed before measuring.
- **Result existence + leak guard (the two load-bearing claims):** a grep-able
  assertion that `docs/eval-gate.md`'s Tier-1 section is present with a
  welded-vs-seamed rate line, a numeric pre-registered floor, and a verdict token;
  that `dev` and `heldout` enrichment appear as **separate** arms; and that no
  threshold was fit on `heldout` rows (tuning reads `dev` only).
- Sweep determinism: re-run the mine on one repo twice → byte-identical; `pry map`
  twice on one repo → byte-identical (existing invariant).
- `cargo build --release` + `cargo test` green (incl. any new Python-frontend
  tests if S5 builds it).
- **AC4 denylist** — `Cargo.lock` has none of
  `reqwest|hyper|ureq|isahc|surf|curl|awc|tonic|anthropic|openai`; `src/` shells
  to no `curl`/LLM CLI; harness scripts import none of
  `openai|anthropic|httpx|requests|urllib3|aiohttp` and make no subprocess HTTP
  call (the zero-LLM-binary guard the spec pins).
- `check_goal_artifact.py` passes before any status flip.

### High-Confidence Checks

- Fresh-eye slice critique (per the Subagent Delegation policy — bounded
  reviewer, no same-agent substitute) on: (1) **corpus selection bias** — is the
  slate stratified, not silently clustered at the disciplined/low-injection end;
  is the `dev|heldout` split genuinely pre-registered, not chosen after a peek;
  (2) **Tier-1 enrichment soundness** — is the welded-vs-seamed bugfix-touch join
  free of obvious confounds (welded sites simply being more numerous / larger /
  in hotter files); is the pre-registered floor honest; (3) the **(b)-gate lens +
  any Python frontend** — is the lens analyzer-free as claimed, and is the
  frontend gated on a real GO.
- `quality` validation-recommendation routing for the closeout (per CLAUDE.md), to
  pick the right gate/HITL surface rather than self-asserting.

### External Or Live Proof

- **None by design.** The result is observational git mining on **local clones** —
  no provider roundtrip, no publish, no remote CI, no outbound on corpus repos.
  The Workflow fan-out is local. The final report must name these as skipped
  proof levels and claim only the local cross-corpus enrichment + generalization
  result.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Corpus discovery + freeze + pre-registration | Everything downstream joins against a frozen, pinned, split-honest corpus; pre-registering the split + denominator + floor first is the load-bearing honesty gate | `corpus.json` + its **schema file + validator** (S1 deliverables); a **new** app-shapedness/domain scorer (NOT `repo_fit.py`, the site-count gate); the **separate pre-registration artifact** (split + matched-comparison denominator + two-sided floor/falsifier) committed BEFORE any measurement; a `log` of what was pruned/excluded | **DONE** (`50f06cb`/`3d173e1`) |
| S2 | Deterministic sweep harness (nose `run_corpus.sh` analog) | The reusable engine: per repo clone@pinned → `pry map` → mine bugfix commits → join bugfix-touched lines with pry findings; Workflow fan-out, incremental. (Tier 1 is *labeling*-cheap but *mining*-bearing — the per-repo mine+join+prune × ~25–33 is the long pole) | Per-repo sweep outputs; a **net-new TS/JS miner** (new pathspec + EH-token regex `catch`/`throw`/`.catch(`/`reject`/`retry`/`timeout` + boundary names + output schema, reusing `mine.py`'s determinism discipline; `mine.py` is Python-token-only today); Python repos use the native `mine.py`; deterministic mine x2 | **DONE** (`678ccae`; mine_ts.py+sweep.py; 25/25 swept; byte-identical x2) |
| S3 | Tier 1 — directly-observed enrichment (THE main result, 쟁점 4) | Pure git + map join, no per-site gold → robust; answers "does welded-at-demand predict defects?" | Enrichment table in `docs/eval-gate.md`: welded-at-demand vs seamed bugfix-touch rate **under the pre-registered matched-comparison denominator**, vs the two-sided floor/falsifier, with the verdict; **per-repo distribution reported, not only pooled** (Simpson's-paradox guard) | **DONE** (`6a19e3d` — matched 1.05, CI [0.96,1.18] → **FALSIFIED**) |
| S4 | Generalization (쟁점 2) — dev/heldout | Absorbs the old "corpus-expansion / SC2 gate" queue item; the held-out arm is the generalization gate | Enrichment reported `dev` vs `heldout` separately; any threshold tuned on `dev` only; held-out number stated honestly | **DONE** (`6a19e3d` — dev 0.93 / heldout 1.11 weak; no tuning needed) |
| S5 | Python branch — (b)-gate lens → conditional frontend → fold-in | The recorded reopen; cheap analyzer-free lens first, heavy frontend only on a GO **and only after S3+S4 have a recorded verdict** | (b)-gate GO/KILL on the Python apps **by the lens criterion (demand-subset in band `[0.15,0.85]`, not bare fraction)**; IF GO → Python frontend built (`catalog/python.toml`), `pry map` runs on a Python app, Python folds into the S3/S4 `eval-gate.md` table (assign Python repos' dev/heldout split here); IF KILL → analyzer-free result recorded, no frontend | **DONE** — **KILL** (welded-saturated 0.902, kill-gate Run 7); no frontend |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the closeout floors below; `find-skills` owns *which* skill answers a
boundary. Fill during the run:

Routing: find-skills routed each phase — impl ran the S1–S5 slices, critique ran each slice's bounded fresh-eye review, quality gave the closeout validation recommendation, gather/gh did corpus discovery (issue/release n/a).

- **Routing** — implementation slices (S1–S5) route through `impl`; the closeout
  gate through `quality`'s validation recommendation; each slice's fresh-eye
  critique through `critique` with a bounded reviewer; the Workflow orchestration
  tool drives the S2 sweep fan-out. Confirm the concrete `find-skills` route per
  phase at each boundary; do not treat this anticipated list as the hard-coded
  map.
- **Gather step** — external GitHub discovery (repo search + structure reads) and
  any repo metadata fetched from a URL route through `gather` per CLAUDE.md;
  record the concrete `Gather:` reference(s) at closeout (local git clones
  themselves are not external-URL gathers, but GitHub-API/URL reads are).
- **Release step** — anticipated `Release: n/a` — no version bump and no generated
  install manifest this goal. Watch item: if S5 builds the Python frontend, that
  is analyzer capability gated by tests, **not** a release surface this goal; a
  real pry release that ships the Python frontend is a separate release goal.
- **Issue closeout step** — anticipated `Issue closeout: n/a` — this goal resolves
  no tracked GitHub issue. Defects found in pry during the sweep are filed via
  `issue` and listed in Off-Goal Findings, not closed by this goal; nothing is
  filed against the third-party corpus repos.

## Slice Log

### S1 — corpus discovery + freeze + pre-registration (DONE, 2026-06-15)

Commits: `468eb7e` (critique packet) → `037e5bc` (pre-registration honesty gate)
→ `50f06cb` (corpus + tooling) → `3d173e1` (critique folds; final prereg anchor).

**Built:** `harness/corpus_fit.py` (NEW app-shapedness scorer, pure + unit-tested,
floor pre-registered; library veto + curation do app-vs-library, the floor is a
substantiveness gate — recorded honestly), `corpus_schema.json` +
`validate_corpus.py` (schema + validator with floor cross-check), `corpus_freeze.py`
(gh-API discovery → score → pin → freeze; `--reseed` guard), `check_ac4.py` (AC4
runner), `test_corpus.py` (12 tests). Frozen `corpus.json` = **33 repos: 25 TS
(dev 5 / heldout 20) + 8 Python (dev 2 / heldout 6)**, pinned 40-hex commits,
stratified across 17+ domains. `corpus_discovery_features.json` (re-derivable
scores) + `corpus_prune_log.md` (discovery→selection funnel + exclusions, R-D).

**Pre-registration (`preregistration.md` + config.py constants, frozen at
`3d173e1`):** dev|heldout split (per-arm); welded-at-demand vs seamed arms;
NUMERATOR pinned (`ENRICHMENT_BUGFIX_MSG_REGEX`, message-intent only); matched
denominator (churn × site-size terciles, direct standardization); two-sided floor
(GO point≥1.5 AND 95% bootstrap-CI lower>1.0; FALSIFIER point≤1.1 OR CI≤1.0);
Simpson per-repo guard; (b)-gate band [0.15,0.85].

**Verification:** `validate_corpus.py` VALID; `check_ac4.py` AC4 PASS;
`pytest test_corpus.py` 12 passed; `cargo test` green (no Rust touched); git
ordering `037e5bc`/`3d173e1` precede any enrichment number (none exists yet).

**Slice critique (fresh-eye, parent-delegated):** 3 angle subagents
(corpus-bias R-A · metric-soundness R-B · scorer/freeze/AC4 correctness) + 1
counterweight. Dispositions:
- ACT (folded): #8 pin enrichment numerator into frozen prereg; #6 fix the false
  "undercounts both arms identically" claim → conservative lower-bound; #7
  pre-register repo-cluster bootstrap CI before any number.
- BUNDLE (folded): #5 name file-KIND residual confound; #9 deepen AC4 denylist;
  #11 validator floor cross-check + tests; #12 freeze `--reseed` guard; #3 record
  the honest finding that the floor does NOT auto-discriminate mature libraries
  (proved by scoring rejected libs) → added library veto; #4 conservative-bias
  framing.
- DEFER: #12 done early (cheap); #13 unreachable edge cases recorded.
- OVER-WORRY (no action): #1 dev AI-lean (heldout is the diverse generalization
  arm), #2 monoculture (rebutted — Next/Nest/Vue/Svelte, stars 8k–192k), #10
  `_has_token` substring FPs (0 verdict flips). Packet:
  `charness-artifacts/critique/2026-06-15-s1-corpus-packet.md`.

### S2 — deterministic sweep harness (DONE, 2026-06-15)

Commits: `<S2 harness>` (mine_ts.py+sweep.py+tests) → `678ccae` (25 sweep records
+ enrichment_result). **Built:** `mine_ts.py` (net-new TS/JS bugfix-commit miner,
message-intent numerator + JS-EH-token candidate record), `sweep.py` (per-repo
clone@pinned → `pry map` → mine → `git blame` join; arms wd/rest + subarms
seamed/wnd; covariates file_churn + enclosing site_size; un-shallows depth-1 seeds;
`--corpus` orchestrator, incremental, `--reseed` guard), `test_sweep.py` (8 tests).
**Swept all 25 TS repos** (parallelized via 2 workers; clone+mine+blame). Byte-
deterministic verified x2 (umami sweep + mine_ts). The Workflow tool was considered
for fan-out but a deterministic Python orchestrator was chosen because the per-repo
work is mechanical and the acceptance criterion is *byte-identical re-runs* (LLM
subagents would be non-deterministic) — recorded as an honest engineering call.

### S3 + S4 — Tier-1 enrichment + generalization (DONE, 2026-06-15)

Commits: `6a19e3d` (eval-gate verdict) → `<critique folds>`. **MAIN RESULT —
쟁점 4 FALSIFIED for this corpus:** welded-at-demand vs rest matched ratio **1.05,
95% CI [0.96,1.18]** across 25 TS apps → trips the pre-registered falsifier.
**쟁점 2:** dev 0.93 (FALSIFIED), heldout 1.11 (CI [1.02,1.29] — weak, not-refuted,
but far below the 1.5 GO bar); no threshold tuned (none needed). Secondary vs
seamed 0.90, vs welded-not-demand 1.05. Simpson guard 17/25 repos >1 (direction
positive, magnitude negligible). `enrichment.py` re-derives every number from the
frozen records; seeded bootstrap byte-reproducible. **Honest negative** (nose-
retraction discipline): welded-at-demand is a testability classifier, NOT a defect
predictor on this corpus → lever #4 precision polish is not justified by a
bug-prediction payoff.

**Slice critique (fresh-eye, parent-delegated, bundle boundary):** 3 angle
subagents (blame-join correctness · statistical soundness · arm/coverage integrity)
+ 1 counterweight. **All three independently verified the FALSIFIED negative is
SOUND, not a harness bug** (blame join hand-checked 4 findings + 0/171 file
failures; direct-standardization planted-confound test raw 2.32→matched 0.93;
bootstrap indices/seed-stable, 9/9 strata full; arms partition exactly, 25/25
coverage; the thesis fails under EVERY framing — seamed rate 0.437 > wd 0.394).
Dispositions: ACT (folded, honesty-of-disclosure) — base-rate-ceiling caveat
(bugfix regex matches ~48% of commits, compressing the ratio toward 1.0), explicit
"heldout not-refuted, just below the bar" sentence; BUNDLE — frontend+backend
tier-pooling caveat. OVER-WORRY (no action) — "rest" framing (thesis fails under
all framings), outline.json missing in-record id (cosmetic). Packet:
`charness-artifacts/critique/2026-06-15-s3-enrichment-packet.md`.

### S5 — Python (b)-gate lens → KILL, no frontend (DONE, 2026-06-15)

Commits: `761e305` (lens KILL) → `<S5 critique folds>`. Sequencing gate honored
(S3+S4 verdict `6a19e3d` is git-ancestor of the S5 commit). **Built:**
`bgate_lens.py` (analyzer-free `ast` lens, zero-LLM, byte-deterministic) + 7 tests.
**Verdict: KILL** — full demand-subset welded-fraction **0.902** (out of band
[0.15,0.85], decided 0.737 = not mute). Idiomatic Python app code reaches
boundaries module-directly (no injection seam); confirms the prior ceal-Python
KILL on **independent non-glue apps** (not a glue artifact). Decomposition: the
KILL is clock-driven (clock 62% of welds, 0-seam by construction); net+subproc
alone 0.765 (in-band, ~24% seams) — a genuine Python-vs-TS clock-culture
difference. Only mealie (FastAPI DI) GOes (0.564), which also proves the lens
detects seams (no detect-nothing bug). **No frontend built** — two honest reasons:
(b)-gate KILL + moot given the FALSIFIED TS enrichment (folding Python in cannot
resurrect a falsified thesis). A definitive 1-by-1 hand-gate + a real Python
frontend = a separate future goal. R-C (no faith-built frontend) satisfied: zero
`src/` changes, no `catalog/python.toml` touch.

**Slice critique (fresh-eye, parent-delegated):** 2 angles (lens-KILL soundness ·
no-frontend honesty/R-C) + counterweight. Both confirm the KILL is SOUND and the
no-frontend decision correctly gated + honestly recorded. Folded 2 Bundle items:
dotdir skip (.semgrep//.claude/ fixtures, 0.906→0.902, verdict unchanged) + the
clock-vs-net/subproc decomposition disclosure. Honesty note: the first lens run was
an artifactual mute (greedy substring lexicon); fixed with a boundary-VERB gate.
Packet/reviewers inline. AC4 made call-aware so the analyzer's detection-pattern
strings (`urlopen`) aren't false positives.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct the
originating context by following them in order:

1. `docs/handoff.md` — the originating workflow trigger; the "▶ NEXT ACTION — E9:
   nose-style multi-repo validation SWEEP" section is this goal's mandate (6
   steps; honesty gates; the decisive nose lesson). The strategic redirect
   (pause precision polish to prove 쟁점 4 + 쟁점 2) is operator-chosen 2026-06-15.
2. `docs/spec-eval-harness.md` — the canonical build contract; **E9** (SZZ as a
   dev-time structural-improvement input), E5 (precision AND filter-recall), E8
   (LLM once → deterministic forever), and the SC/AC. The E1–E9 critique is
   already DONE (FIX-FIRST, 4 blockers folded — see that doc's Critique).
3. `docs/eval-gate.md` — H3 results, per-kind/stratum precision, the named
   levers, the calibration ruleset R1–R7; the Slice-2 filter-recall arm.
4. nose `~/codes/nose/eval/hazard/` — the PATTERN to reuse: `run_corpus.sh`
   (sweep driver), `mine.py` (bugfix mining), `audit_sample.py` + the G2 11%
   retraction (`RESULTS.md`), the prune discipline. Reuse the pattern, NOT the
   repos.
5. pry `harness/` — `mine.py` + `szz.py` + `repo_fit.py` (the Python-native
   kill-gate versions to adapt: `mine.py` needs JS EH tokens for TS repos;
   `repo_fit.py` scores app-shapedness for S1); `finding_io.py` + `filter_recall.py`
   + `config.py` + frozen `fixtures/eval/*-labels.json` (the H3 surfaces).
6. `catalog/python.toml` + `catalog/typescript.toml` — the analyzer frontends;
   `python.toml` is the seed for the conditional Python frontend (S5).
7. `docs/kill-gate.md` — the (b)-gate discipline (analyzer-free welded/seamed
   sample) + the TS GO / Python KILL record that S5's lens re-runs on
   independent non-glue Python apps.
8. The 4 H3 seed repos (`~/codes/_pry-corpus/{outline,flowise,continue,librechat}`
   at the pinned commits) — already app-shaped, mapped, frozen-labeled; the dev
   seed the corpus expands from.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- **Mode (stated, not asked).** Artifact-only shaping vs implementation-
  continuation. **Assumed: artifact-only** — the operator said "achieve 로 goal
  만듭시다" (make a goal), the Before-phase verb; `/achieve` shapes, `/goal`
  pursues. No slices execute until the explicit `/goal` activation. axis:
  single-point — `/achieve` is shape-only by contract.
- **Q1 — Corpus size.** Options: {≈15 dev5/heldout10 (the pre-registered SC2
  target)} / {≈10 dev5/heldout5 (lean)} / {≈20–25 dev5/heldout15+ (broad)}.
  **Chosen: ≈20–25, dev 5 / heldout 15+.** Rationale: Tier-1 enrichment needs no
  per-site gold (git + map join), so a broader corpus is *cheap* for the main
  result and maximizes generalization evidence (쟁점 2). Rejected the ≈15/≈10
  options because the labeling cost that made them attractive does not apply to
  the Tier-1 result, and a larger held-out arm is the stronger generalization
  test. axis: single-point — corpus size is a per-goal measurement choice, not a
  host/profile axis.
- **Q2 — Python branch.** Options: {defer to a follow-up goal} / {include the
  cheap (b)-gate lens only} / {full Python branch incl. frontend}. **Chosen:
  full Python branch incl. frontend** — discover non-glue Python apps, run the
  (b)-gate lens, and on a GO build the Python frontend and fold Python in.
  Rejected the defer/lens-only options because the operator wants the recorded
  reopen answered end-to-end this goal; the frontend build stays **conditional on
  a (b)-gate GO** so a KILL closes the branch cheaply (no faith-built frontend).
  axis: single-point for this goal's scope.
- **Q3 — SZZ Tier 2.** Options: {Tier 1 load-bearing, Tier 2 conditional stretch}
  / {include Tier 2 fully} / {drop Tier 2 entirely}. **Chosen: drop Tier 2
  entirely** — ship Tier 1 (directly-observed enrichment) + the dev/heldout
  generalization only; SZZ bug-linked gold becomes a separate future goal.
  Rejected including it because the handoff itself calls SZZ "the fragile cherry,
  illustration not load-bearing," and nose retracted the analogous auto gold at
  ~11% precision — the robust deliverable is Tier 1, and the szz-port +
  LLM-audit cost buys an explicitly non-load-bearing illustration. axis:
  single-point.

## Plan Critique Findings

A bounded fresh-eye **spec critique RAN at shaping time** (2026-06-15, before
activation): 4 angle subagents (Minto/structure · Jackson/problem-framing ·
Weinberg/measurement-validity · Gawande/operational) + 1 separate counterweight
pass. Fresh-Eye Satisfaction: parent-delegated. Verdict: *do not activate as-is —
small local edits required.* All Act-Before-Ship + Bundle findings were folded
into this artifact (see "This-critique folds" below). The S1/S3 per-slice
critique still runs during the run on the live corpus + data; it is not replaced
by this plan pass.

Inherited + pre-registered risks:

- **Inherited (spec E1–E9 critique, DONE).** The eval-harness contract already
  passed a FIX-FIRST fresh-eye critique with four blockers folded (filter-recall
  vs detection-recall naming; the open-vs-close SC2 split; panel mis-cost +
  near-circular blinding; DI-discipline stratification). This goal does not
  re-open those; it consumes their resolution.
- **New risk R-A — corpus selection bias.** A self-selected GitHub slate can
  silently cluster at the disciplined/low-injection end (the PQ1 gap: the 4 H3
  seeds are all 0–5% clock-injection). **Folded:** S1 stratifies by domain (+
  TS/JS by clock-injection rate) and the dev/heldout split is **pre-registered
  before measuring**; the S1 critique angle verifies the split was not chosen
  after a peek.
- **New risk R-B — Tier-1 enrichment confounds.** "Welded sites are touched by
  bugfixes more" can be an artifact of welded sites simply being more numerous,
  larger, or in hotter files rather than the weld itself mattering. **Folded
  (hardened by this critique):** the metric denominator is pre-registered as a
  **matched comparison** (welded vs seamed matched on file-churn + site-size — the
  only form that neutralizes this confound), pinned in S1 *before* measuring, not
  invented at S3; the floor is two-sided (a real falsifier); the S3 critique angle
  + the per-repo distribution (Simpson's guard) interrogate what remains; the
  result is stated as a correlation, never causal, and never two-directional.
- **New risk R-C — premature Python frontend.** Building a frontend on faith is
  the exact kill-gate anti-pattern. **Folded:** S5's frontend is **gated on a
  (b)-gate GO**; a KILL closes the branch at the analyzer-free lens with no
  frontend.
- **New risk R-D — silent truncation.** A multi-repo sweep can quietly drop
  repos/commits and read as "covered everything." **Folded:** the honesty gate
  requires `log`/report of every prune/exclusion (no silent truncation), carried
  into S1's expected evidence.

### This-critique folds (2026-06-15 spec critique → applied before activation)

Act-Before-Ship + Bundle findings, each folded into the artifact above:

- **C2 (highest-leverage) — pre-registration was honor-system.** Split + floor
  provenance lived inside `corpus.json` (self-attesting; an agent could
  peek-then-backdate). **Folded:** Boundaries now require a *separate*
  pre-registration artifact committed *before* the enrichment commit, with a
  `git merge-base --is-ancestor` commit-ordering proof at closeout (mirrors the
  repo's `config.py` `REPO_FIT_SITE_FLOOR` + F27 "frozen before" pattern).
- **C1 — (b)-gate GO criterion was undefined.** **Folded:** the GO criterion is
  now stated verbatim (demand-subset welded-fraction in band `[0.15,0.85]` per
  kill-gate F27/Run 5; bare fraction is retired/fs-swamped) in Boundaries + the S5
  row, so the heavy frontend isn't gated on a contract reconstructed from a doc.
- **C3 + C4 — denominator fork + missing falsifier.** **Folded:** the Tier-1
  denominator is pinned as a *matched comparison* (file-churn + site-size) in the
  S1 pre-registration, and the floor is two-sided with a pre-committed FALSIFIER
  (ratio ≤ Y or ~1.0 under the matched denominator → thesis falsified) — the nose
  `rate-match ≠ precision` lesson made a contract.
- **C6 — S5 could starve the TS result.** **Folded:** a sequencing gate — S5's
  frontend build may not begin until S3+S4 have a recorded verdict; early GO =
  record + queue, not start.
- **C5 / C7 — directionality + frontend-depth non-claims.** **Folded:** two new
  Non-Goals (no two-directional safety claim from the seamed arm; no Python
  analyzer breadth beyond the fold-in).
- **C8 — two load-bearing claims were folklore.** **Folded:** a grep-able
  existence+leak Low-Cost Check (Tier-1 section/floor/verdict present; dev|heldout
  separate; no heldout-fit threshold).
- **C9 / C10 — mislabeled reuse.** **Folded:** `repo_fit.py` relabeled (site-count
  gate, not a domain scorer → scorer is net-new); the TS/JS miner relabeled net-new
  (not "mine.py adapted"); the corpus.json schema+validator named S1 deliverables;
  the nose two-surface conflation corrected (`run_corpus.sh` hardcodes its repos;
  the schema is from nose's separate dedup benchmark).

Over-worry (raised, NOT folded — recorded so a fresh session doesn't re-raise):
C11 AC4 needs a runner (the denylist tokens are already pinned; a `.sh` vs inline
grep is slice-execution detail); C12 S5 write-back (obvious continuation; an
implementer who built the S3/S4 table won't invent a second); C13 S1 stopping rule
(corpus counts ≈20–25/~5–8 *are* the stop rule); C15 AC4 transitive deps for the
Python frontend (the `Cargo.lock` scan is transitive by construction; a tree-sitter
frontend won't pull an HTTP client). Settled-decision dismissals confirmed:
Python-as-scope-bomb, slide-into-precision/SZZ/outbound, ≈20–25-vs-spec-SC2, and
Workflow/git-log determinism (nose `run_corpus.sh` + `mine.py` already mechanical).

Valid-but-defer (real, recorded as slice notes — not activation blockers): C14
mining-cost honesty note (folded into the S2 "Why Now"); C16 per-repo distribution
(folded into the S3 row); C17 Python repos' dev/heldout split assignment (folded
into the S5 row, resolved at the GO branch).

## Off-Goal Findings

- **No pry binary defects found** during the sweep (pry map ran cleanly on all 25
  TS repos incl. huge monorepos — twenty 12,622 files — with no crashes). Nothing
  filed via `issue`.
- **Cosmetic, not a defect:** `corpus.json` records `calcom` as `calcom/cal.com`
  while GitHub rebranded the repo to `cal.diy`; the frozen `url`+`commit` track the
  rename (clone succeeded), so the name is stale-but-harmless — noted in
  `docs/eval-gate.md`, not worth re-freezing the corpus.
- **Two reusable harness lessons** (recorded in the retro, not issues): shallow
  (depth-1) clones silently break git-history mining (fixed via ensure_clone
  un-shallow); greedy-substring token classifiers saturate/mute (fixed via the
  boundary-verb gate in `bgate_lens.py`).

## Final Verification

Canonical closeout-evidence markers (plain lines for the closeout checker):

Retro: charness-artifacts/retro/2026-06-15-e9-sweep-session.md
Host log probe: charness-artifacts/retro/2026-06-15-e9-multi-repo-validation-sweep-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-06-15-e9-closeout-disposition-review.md
Gather: gh / GitHub API (gh search repos across ~20 TS + 8 Python domains, gh api per-repo metadata/structure/commit) for corpus discovery — handoff step 1; local clones are not external-URL gathers
Release: n/a — no version bump and no install manifest; the conditional Python frontend was NOT built (b-gate KILL), so there is no release surface created by this goal
Issue closeout: n/a — no tracked GitHub issue was resolved; no pry defects were found during the sweep; nothing is filed against the third-party corpus repos

Detail (each marker above, expanded):

- **Self-verification (쟁점 4 + 쟁점 2):** DONE. 쟁점 4 **FALSIFIED** — matched
  enrichment 1.05, 95% CI [0.96,1.18] ≤ the pre-registered falsifier (≤1.1 OR
  CI-lower≤1.0), under the matched (churn×site-size) denominator. 쟁점 2: dev 0.93
  / heldout 1.11 (weak, CI [1.02,1.29] excludes 1.0 but far below the 1.5 GO bar);
  no threshold tuned. Python (b)-gate **KILL** (welded-saturated 0.902) → no
  frontend. Evidence: `docs/eval-gate.md` Tier-1 section + `docs/kill-gate.md`
  Run 7 + `harness/fixtures/eval/enrichment_result.json` +
  `harness/fixtures/eval/bgate_lens_result.json`.
- **Broad gate + commit-ordering proof:** DONE. `cargo test` green (lib 0/main
  2/classify_smoke 10/exclude_smoke 5); `python3 harness/check_ac4.py` AC4 PASS;
  `python3 harness/validate_corpus.py` VALID (33 repos); `python3 -m pytest
  harness/` 42 passed; sweep + mine + enrichment + lens all byte-identical x2
  (`pry map` deterministic). Pre-registration ordering proven:
  `git merge-base --is-ancestor 47eeb633 6a19e3d` → OK (prereg precedes the first
  enrichment number).
- **Retro:** DONE — `charness-artifacts/retro/2026-06-15-e9-sweep-session.md`
  (+ recent-lessons + lesson-selection-index).
- **Host log probe:** DONE — `probe_host_logs.py` (retro/scripts) reports claude
  host detected; token_count available, duration/tool_call/turn derivable from the
  session jsonl (`goal_metric_window: not_requested` — no scoped window declared).
- **Disposition review:** DONE — bounded fresh-eye disposition review artifact
  `charness-artifacts/critique/2026-06-15-e9-closeout-disposition-review.md`:
  verdict **HONEST and COMPLETE, no integrity gaps, cleared for completion** (7/7
  axes HONEST).
- **Residual risks + non-claims:** restated in `docs/eval-gate.md` Tier-1
  non-claims — no causal claim; **no two-directional safety claim from the seamed
  arm** (the seamed control was in fact bugfix-touched *more*, 0.437 > 0.394); no
  provider/live/release proof; no outbound on corpus repos; no full heldout
  precision-panel; base-rate ceiling + file-kind + tier-pooling residuals named.
  **The FALSIFIER fired and is reported as a valid, honest result** (the
  nose-retraction discipline), not a failure to report.

### Closeout routing (Coordination Cues)
- **Routing:** S1–S5 implemented via the `impl`-class slices; each slice
  fresh-eye-critiqued via `critique` (bounded subagents, parent-delegated, no
  same-agent substitute); the sweep fan-out ran as a deterministic Python
  orchestrator (chosen over the Workflow LLM-subagent tool because byte-identical
  re-runs are the acceptance criterion — recorded honestly in the S2 Slice Log).
- **Gather:** GitHub discovery used `gh` / the GitHub API (authed locally; handoff
  step 1) — `gh search repos` across ~20 TS + 8 Python domains + `gh api` per-repo
  metadata/structure/commit reads. Local git clones are not external-URL gathers.
- **Quality (closeout validation recommendation):** `quality` adapter absent
  (defaults); the validation-role recommendation surfaced `cautilus` (evaluator-
  backed *behavior* review) — **not applicable by design**: the deliverable is a
  zero-LLM *measurement*, so there is no LLM behavior to evaluate; validity rests
  on the deterministic re-derivation + the adversarial fresh-eye critiques (3+1 on
  the enrichment, 2+1 on S5), all done.
- **Release:** `n/a` — no version bump, no install manifest (the Python frontend
  was NOT built; KILL).
- **Issue closeout:** `n/a` — no tracked issue resolved; no pry defects found; no
  outbound on the third-party corpus repos.

## User Verification Instructions

Run these to verify completion directly (filled now; results recorded at
closeout):

1. Corpus is frozen + split-honest:
   `cat harness/fixtures/eval/corpus.json` → ≈20–25 TS/JS apps + ~5–8 Python
   apps, pinned commits, `dev|heldout` split, pre-registration provenance line.
2. Sweep is deterministic:
   re-run the mine on one repo twice → byte-identical; `pry map <repo>` twice →
   byte-identical.
3. Tier-1 enrichment (쟁점 4):
   the `docs/eval-gate.md` Tier-1 section shows welded-at-demand vs seamed
   bugfix-touch rate + the pre-registered floor + the verdict; every number is
   contestable against the pinned corpus.
4. Generalization (쟁점 2):
   the same section reports `dev` vs `heldout` separately; thresholds tuned on
   `dev` only.
5. Python branch:
   the (b)-gate GO/KILL is recorded; on GO, `pry map <python-app>` runs and the
   Python repos appear in the enrichment.
6. Zero-LLM binary held:
   the AC4 denylist passes (`Cargo.lock` + `src/` + harness scripts).

Skipped proof levels (by design): no published release, no remote push/CI, no
provider roundtrip, no outbound on the corpus repos, no full heldout
precision-panel labeling. The result is a local, observational cross-corpus
enrichment + generalization measurement.

## Auto-Retro

Retro: charness-artifacts/retro/2026-06-15-e9-sweep-session.md. Per-improvement
dispositions (all shipped this goal):

applied: ensure_clone (sweep.py) now un-shallows depth-1 clones, and "assert full git history before mining" is the standing workflow lesson recorded in the retro Sibling Search
applied: the deterministic zero-LLM corpus-study engine (corpus_fit/freeze/validate + mine_ts + sweep + enrichment + bgate_lens) is committed as a reusable asset for future corpus studies
applied: the FALSIFIED verdict, the base-rate ceiling, and the Python clock-culture difference are written durably into docs/eval-gate.md and docs/kill-gate.md Run 7
applied: the bgate_lens greedy-substring classifier noise is fixed via a boundary-verb gate, and check_ac4 is made call-aware so analyzer detection-pattern strings are not false positives
