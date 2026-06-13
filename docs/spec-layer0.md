# Spec — Layer 0 + Validation Harness (build contract)

Canonical implementation contract for the first `pry` deliverable. Refines
[`initial-plan.md`](../initial-plan.md) §8–§10/§13 and
[`docs/roadmap.md`](roadmap.md) into something `impl` can execute without
rediscovering the problem. Acceptance bar lives in
[`docs/operator-acceptance.md`](operator-acceptance.md); this spec ties each of
its checklist items to a concrete check.

Status: **ready for `impl`** (tightened after bounded fresh-eye critique — see
`Critique`). First slice: the **validation harness** (the falsifier), per
kill-gate discipline.

---

## Problem

We do not yet know whether `pry`'s thesis holds *on this author's own code*: that
error-handling defects concentrate in welded (un-seamed) boundaries, denser than
a churn baseline. The most likely cause of death (§13) is **repo-fit** — building
an elegant instrument for a bottleneck the repo doesn't have. So Layer 0 must,
cheaply and falsifiably, produce **one number** and a go/kill decision — and the
falsifier must be built *before* the thing it falsifies, with every analyst knob
**pre-registered**, so an invested future self cannot wriggle a "no lift" result
into a "go."

A "no lift" or null result has **two distinct meanings the verdict must keep
apart** (§13 A vs B): *repo-fit death* ("my repo has no gradient / not this bug
shape → change the target") versus *tool death* ("the map is weak or mute → fix
or kill the tool"). A single Z-vs-B number collapses them; the contract below
keeps them on separate axes.

## Current Slice

Build the pieces required to reach the **kill gate**, in forced order:

0. **Repo-fit gate (harness-only, analyzer-free).** Before any Rust is written,
   establish from git history alone that charness *has the bug shape at all*: a
   non-trivial mined+labeled error-handling bug-site set (clearing a
   pre-registered floor) and a mining-recall sanity check. If this gate fails,
   **re-target or pull `ceal` earlier — do not build the analyzer.** This is the
   cheapest possible kill (§9 reframe).
1. **Validation harness** (Python) — the falsifier. Frozen labeled set +
   SZZ-resolved bug sites + churn baseline + the analyzer-free repo-fit signals.
2. **Minimal analyzer = the MAP** (Rust + tree-sitter) — boundary catalog as
   data, conservative seamed/welded/**ambiguous** classification with a reported
   coverage denominator, deterministic emit. This is all the *number* needs.
3. **Join → the one number → go/kill** — run the map at the pre-registered
   temporal split, score lift over baselines at equal #-function budget, gate
   against the mute-map ceiling, and record the two-axis verdict.

The syntactic **floor** (claim channel), SARIF, and the `external_binary`
packaging are Layer 0 deliverables that complete **only on a "go"** — the map
must earn them by beating the baselines first. This keeps the experiment able to
*kill cheaply* and is the honest reading of operator-acceptance's floor item (it
is required for *accepted/completed* Layer 0, i.e. the go path).

## Fixed Decisions

| # | Decision | Why |
|---|----------|-----|
| F1 | **Analyzer = Rust + tree-sitter** Python bindings; spans on every node. | Roadmap/handoff; distributed like `nose` as a prebuilt binary. |
| F2 | **Harness = Python**, separate from the binary (nose-eval analog). | LLM-labeling/git-mining/SZZ glue is natural in Python; keeps non-deterministic labeling *out* of the binary's hard determinism contract. (User-confirmed.) |
| F3 | **First corpus = charness**, then **ceal** as a second corpus. | §9: own repo, ~97% Python, most honest. ceal (2804 commits) adds a second data point after the first number. (User-confirmed.) |
| F4 | **Label source = own-repo git history only** for the first number; BugsInPy deferred. | DTSTTCPW (§9): one number first. (User-confirmed.) |
| F5 | **Prediction grain = function-level**; record call-site spans as evidence; file roll-up is a trivial aggregation. | §11: method-level concentration is the literature's strong grain and matches SZZ blame resolution. Revisable by measurement. |
| F6 | **First number = single temporal split**, not per-commit replay. The split `T` is **pre-registered by a mechanical rule before any map run**: `T` = the commit at the timestamp that splits the *mined+labeled* error-handling bug-site history **70% (pre, for churn) / 30% (post, as test labels)**. The verdict must state that Z is reported at this `T`, **not** as a maximum over a `T`-sweep. | Honest (no look-ahead, no hand-picked split) **and** cheap (one analyzer run). Per-commit temporal validity (§8.2) is deferred. |
| F7 | **Equal-budget comparison is by #functions flagged**, not LOC. The map flags `K` functions; each baseline is given the **same `K`-function budget**; compare recall of post-`T` bug sites. Baselines: **(a) churn rank**, **(b) "all functions containing any catalogued boundary call"** (the decisive null — if the map cannot beat this, seam classification adds nothing), and (c) random functions (optional sanity floor). | §8 effort-aware lift. #functions is the real decision unit ("which functions do I look at"); LOC budget lets large welded I/O functions inflate Z. The any-boundary-call baseline is the honest null hypothesis. |
| F8 | **Map and floor are physically separate** outputs: distinct subcommands → distinct files. Map labeled "risk ranking, not a bug list". `pry --version` exists for `external_binary` detection (mirrors `nose`). | §13 B.2 / operator-acceptance. |
| F9 | **Frozen ground truth = the SZZ-resolved bug-site set**, not just the LLM labels. Checked in as `{repo SHA, fix commit, bug-introducing commit, file, fully-qualified function}` per site, plus labeler model id + prompt hash. The kill-gate computation reads only frozen sites — no live `git` in the scoring path. | Validation must be byte-reproducible even though labeling and live blame are not. (C11.) |
| F10 | **Labeler model = `claude-sonnet-4-6`** (pinned in config), binary classify "is this an error-handling fix?". `claude-haiku-4-5-20251001` is the cheaper fallback if cost dominates. | Precision defines ground truth; Sonnet 4.6 balances precision/cost. |
| F11 | **Join key = file path + fully-qualified function name (module-qualified), resolved at commit `T`.** SZZ blame line ranges are mapped back to `T`'s line ranges to locate the function; matching is by qualified name, never by raw line number (which drifts across the split). | The join is the load-bearing step; left implicit, impl would invent it and silently corrupt Z. (C10.) |
| F12 | **The map reports a coverage denominator and the verdict is gated on it.** Output carries `seamed`, `welded`, `ambiguous` counts and the **decided fraction** = (seamed+welded)/total catalogued boundary calls. If the **ambiguous fraction exceeds a pre-registered ceiling** (default **0.60**, revisable from the first run), the verdict is **"map is mute (P3 fired) — not a go,"** regardless of Z. | §13 B.3: a too-silent tool dies as fast as a too-noisy one; SC2's non-zero check guards only silence, not muteness. (C2.) |
| F13 | **The verdict is two-axis** (written to `docs/kill-gate.md`): a **repo-fit axis** from harness-only signals (mined+labeled bug-site count vs floor; mining-recall sanity; is the bug shape present) and a **tool axis** (given a usable gradient, does the map beat the baselines at equal budget, under the mute-gate). "No lift" routes to *change the target* vs *fix the tool* by which axis failed. | §13 A vs B must stay separable, else a weak classifier kills the thesis (or vice-versa). (C6.) |
| F14 | **SZZ uses `git blame -w` (ignore whitespace)** and records each site's resolution as kept/dropped; residual SZZ noise is acknowledged to bias Z **downward** (conservative — against the thesis, so it cannot manufacture a false "go"). | Cheap honesty hygiene without research-grade SZZ machinery. (C5, cheap substitute.) |

## Probe Questions

Answered through the build; each names where its answer is written back.

- **P1 — Does charness have the bug shape? (repo-fit, gate 0, harness-only.)**
  Answer = the mined+labeled error-handling bug-site count vs the pre-registered
  floor (**default: ≥ 30 SZZ-attributable sites**; below it the verdict is
  *underpowered/inconclusive → re-target or pull ceal*), plus the mining-recall
  sanity result (**P1b**: LLM-classify a sample of *non-matched* bugfix commits
  to estimate error-handling fixes the lexical miner missed; a low match-count
  is only "no gradient" if recall is high). Written back to
  `harness/fixtures/repo_fit.json` and the repo-fit axis of `docs/kill-gate.md`.
- **P2 — What is the churn baseline `B`?** Measured before the map is trusted;
  sets the bar. Thresholds (`N/M`) derived from it, never invented. Written back
  to `baseline.py` output (`harness/fixtures/baseline.json`).
- **P3 — How much lands in `ambiguous`?** Guarded by F12's coverage gate; the
  ambiguous set is surfaced explicitly and *is* the catalog to-do list. Written
  back to the map output's coverage block and the tool axis of the verdict.
- **P4 — Weld-depth weighting** vs a flat seamed/welded bit (§11): recorded as a
  measured ranking input, not assumed. Written back to this spec (a Deferred →
  Fixed promotion) once the first map output shows the depth distribution.

## Deferred Decisions (each names its reopen trigger)

- **Per-commit temporal predictive validity** (stronger than F6). *Reopen when:*
  the single-split number is a "go" and Layer 1 needs tighter evidence.
- **BugsInPy / cross-language (JS/TS) label sets.** *Reopen when:* the own-repo
  number is a "go" and external generalization is in question.
- **Non-circular negative control** (C9): also measure `F%` on charness functions
  demonstrably pure by an independent signal (no catalogued boundary call in the
  reachable body), beyond the hand-written hexagonal twin. *Reopen when:* `F%`
  materially drives the go/kill verdict (i.e. the decision is close on `F`).
- **Statistical confidence interval on (Z−B)** (C3, deliberately not in the first
  number — see `Deliberately Not Doing`). *Reopen when:* the first number is a
  marginal "go" near the floor and a sharper-than-raw-counts decision is needed.
- **Cross-machine/thread determinism diff** (C17): downgraded — see Constraints.
  *Reopen when:* `pry` is wired into multi-runner CI.
- **Layer 1 / Layer 2 internals**, **test-only monkeypatches as "seamed enough,"**
  **final per-language floor rule set.** *Reopen when:* the relevant layer is
  unfolded after a "go"; for monkeypatches specifically, *when* the first map run
  shows test-only patches materially change a function's seamed/welded class.
- **`external_binary` manifest + Homebrew tap + release installer** (mirror
  `integrations/tools/nose.json`). *Reopen when:* the verdict is "go."

## Non-Goals

- Not a complexity/length metric; not a security/taint tool; not a
  mutation-testing replacement (§2).
- Not OSS-corpus benchmarking yet — own repos first (§9/§13 A).
- Not Layers 1–2; not JS/TS; not the runner (Layer 0 has no runner).
- Not research-grade validation machinery for the *first* number (see below).

## Deliberately Not Doing (rejected, with reasons — so the branch stays closed)

- **All-Rust harness** — heavier git/LLM glue, no determinism benefit for
  throwaway eval infra; the binary's determinism contract is best protected by
  keeping non-deterministic labeling outside it.
- **Pull BugsInPy now** — scope creep that risks the kill-gate slipping; deferred
  cross-check.
- **Per-commit temporal replay for the first number** — expensive; single-split
  (F6) is the cheap honest first cut.
- **File-level or call-site-only as the sole prediction grain** — function-level
  is the concentration grain and matches blame; call-site kept as evidence.
- **Building the full floor before the number** — violates kill-cheaply; the map
  must earn the floor by beating the baselines.
- **Bootstrap/Wilson confidence intervals on (Z−B) for the first number** (C3) —
  research-grade for an n≈15–40 go/kill *bit*. Cheaper honest substitute:
  **report raw `n` and the raw counts behind Z and each baseline**, plus the
  pre-registered n-floor (P1) below which the verdict reads *underpowered*. CI
  math is a Deferred Decision, not a first-number requirement.
- **Full SZZ hygiene** (`-C -M`, ignore-revs files, per-site confidence scoring,
  sensitivity sweeps) — research-grade for this n. Substitute: `git blame -w` +
  the conservative-bias note (F14).
- **Per-file runnable harness for every script** (C15) — process gold-plating for
  throwaway eval glue; the per-criterion acceptance checks (SC0–SC6) pin the
  load-bearing points.

## Constraints

- **Determinism is a hard invariant on the analyzer**: byte-identical output
  across runs/threads on one machine (SC3 tests this). Cross-machine identity is
  a **code-level invariant** — no absolute paths, timestamps, or hashmap
  iteration order in output; stable-sort all findings; fixed float formatting —
  enforced by inspection, not a cross-machine diff in Layer 0 (C17).
- **Functional-core exemption is load-bearing**: only *boundary-crossing* code
  lacking a seam is flagged; a pure functional core scores low.
- **Two-channel discipline**: map = prediction (judged by lift, never zero
  error); floor = claim (target ≈ zero FP, `# pry-ignore` escape hatch).
  Physically separate outputs (F8).
- **Boundary + seam catalog is *data*** (auditable config, e.g.
  `catalog/python.toml`), not code — the moat.
- **No live `git` in the scoring path** — scoring reads frozen SZZ-resolved sites
  (F9) so `B`/`F`/`Z` are byte-reproducible.
- Toolchain present: `cargo`/`rustc` 1.93, `python3` 3.10. Labeling needs an
  Anthropic API key — gated by a doctor/precondition step (see First Slice).
- Charness durable artifacts under `charness-artifacts/` are repo state; commit
  with the work they support.

## Success Criteria

0. **Repo-fit gate runs first and is analyzer-free.** The harness produces a
   mined+labeled error-handling bug-site count and a mining-recall sanity result
   for charness *before* any analyzer code; below the pre-registered floor the
   recorded verdict is *underpowered/inconclusive → re-target*, and the analyzer
   is not built. (P1.)
1. The harness produces a **frozen, byte-reproducible** SZZ-resolved bug-site set
   (F9), a churn baseline `B`, and a negative-control score `F`.
2. The analyzer parses charness Python, classifies boundary calls
   **seamed / welded / ambiguous** conservatively, reports the **coverage
   denominator** (decided fraction), and every finding traces to exact source
   lines.
3. Output is **deterministic** (byte-identical on repeat, same machine) and the
   **map and floor are physically separate**, with the map labeled "risk
   ranking, not a bug list".
4. The **negative control** (clean hexagonal / functional-core fixture) scores
   **relatively low** and a deliberately-welded twin scores **relatively high**
   (a *discrimination* smoke test — relative, not an absolute threshold invented
   before `B` is measured).
5. The **one number** is produced with its honesty guards: *"Z% of post-`T`
   error-handling bug sites fall in the map's `K`-function flagged set, vs
   baseline recall (churn `B%`, any-boundary-call `A%`) at equal `K`-function
   budget, at `F%` on the negative control, decided-fraction `D%` (mute-gate
   `D ≥ 1 − ceiling`), n = `<count>`"* — and a **two-axis go/kill decision is
   recorded** in `docs/kill-gate.md` (F13), with `Z` reported at the
   pre-registered `T` (not a `T`-sweep max).
6. On a **go**: the syntactic floor (claim channel, ≈0 FP + `# pry-ignore`) and
   SARIF emit exist, satisfying the remaining operator-acceptance items.

## Acceptance Checks

| Criterion | Check |
|-----------|-------|
| SC0 | `harness/fixtures/repo_fit.json` exists with `{labeled_site_count, floor, mining_recall_sample}`; if `labeled_site_count < floor` the verdict line reads `underpowered/inconclusive` and no `pry`/Cargo code is required to exist. |
| SC1 | Re-running `score.py`/`baseline.py` on the frozen `bug_sites.json` reproduces byte-identical `B`/`F` (no live `git` invoked — assert by running with the repo at a different HEAD and getting identical numbers). |
| SC2 | `pry map <charness>` emits per-function findings each with `{file, qualified_function, line span, class ∈ {seamed,welded,ambiguous}}` **and** a coverage block `{seamed,welded,ambiguous,decided_fraction}`; `ambiguous` is reported (non-zero on real Python) and `decided_fraction` is computed. |
| SC3 | `pry map <path>` run twice → `diff` empty. Map and floor are separate subcommands writing separate files; map output carries the "risk ranking, not a bug list" header. |
| SC4 | On `fixtures/negative_control/` (hexagonal core) the map flags **fewer** functions than on `fixtures/welded_twin/`; asserted as a relative inequality in a harness test (not an absolute count). |
| SC5 | `score.py` joins map output (run at the pre-registered `T`, F6) against post-`T` frozen sites using the F11 key, and emits `Z`, `B`, `A` (any-boundary-call), `F`, `D` (decided fraction), `n`, applies the F12 mute-gate, and writes the **two-axis verdict** (F13) to `docs/kill-gate.md`. The emitted line names `T` and asserts it was fixed before the map ran. |
| SC6 | (go path) `pry floor <path>` emits the Aspirator-derived claims with `# pry-ignore` honored; SARIF validates against schema. Negative: an empty-`except` fixture is flagged; a `# pry-ignore`'d one is not. |

## Critique

Bounded fresh-eye critique **completed** before finalizing this contract (spec
step 7 + repo subagent-delegation policy). No forced debug interrupt was reported
by the risk planner.

- **Execution:** ran. **Fresh-Eye Satisfaction:** `nested-delegated` (spec→critique
  parent delegated to fresh-eye subagents).
- **Target:** `spec-critique` (pre-impl lock-in).
- **Angles:** Minto (structure), Jackson (problem-framing), Weinberg (diagnostic),
  Gawande (operational) + one separate counterweight pass.
- **Coherence result:** the original draft *failed* (F6 hid the split-selection
  knob; P2/P3 named no write-back; deferred items lacked reopen triggers) — **fixed
  here** (F6 pre-registration rule; every P names a write-back; every Deferred names
  a reopen trigger).
- **Acceptance-coverage result:** the original draft *failed* (the mute-map risk had
  no check) — **fixed here** (F12 coverage gate + SC2/SC5 coverage denominator).

Counterweight four-bin triage and disposition:

- **Act Before Ship (applied):** C1 pre-registered `T` (F6) · C2 mute-gate +
  coverage denominator (F12, SC2/SC5) · C4 #function budget + any-boundary-call
  baseline (F7) · C6 two-axis verdict (F13) · C7 analyzer-free repo-fit gate first
  (Slice 0, SC0, P1) · C8 mining-recall sanity (P1b) · C10 explicit join key (F11) ·
  C11 freeze SZZ-resolved sites (F9) · plus the cheap substitutes for C3 (raw n +
  n-floor) and C5 (`git blame -w` + conservative-bias note, F14).
- **Bundle Anyway (applied):** C12 labeler doctor/precondition + cost ceiling +
  resumable cached writes · C13 fixtures moved to slice 2 · C14 Cargo +
  `pry --version` + 3-line `pry map` smoke before the join.
- **Valid but Defer (recorded):** C9 non-circular negative control · C16 reopen
  triggers (added throughout) · C17 cross-machine determinism downgraded to a
  code-level invariant.
- **Over-Worry (dropped, with cheaper substitute noted in Deliberately Not Doing):**
  C3 bootstrap/Wilson CIs · C5 full SZZ hygiene · C15 per-file harness scripts.

Provenance: `charness-artifacts/critique/2026-06-13-spec-layer0.md`.

## Canonical Artifact

This file (`docs/spec-layer0.md`) is the canonical build contract during
implementation. Keep it synchronized: if `impl` discovers a fact that changes
scope or acceptance, update here, not chat. The two-axis go/kill verdict lands in
`docs/kill-gate.md`.

## First Implementation Slice

**The validation harness (the falsifier) — Python — beginning with the
analyzer-free repo-fit gate (Slice 0).** Smallest meaningful unit:

```
harness/
  doctor.py      # precondition: Anthropic API key present; print candidate
                 #   count × est. token cost and require confirm before labeling
  mine.py        # git-mine charness for error-handling bugfix commits
                 #   (diffs touching except/catch/retry/rollback/timeout/raise
                 #    + boundary call names); emit candidate set with SHAs
  label.py       # claude-sonnet-4-6 binary classify: real error-handling fix?
                 #   idempotent cached writes (resume on failure); freeze labels
                 #   + model id + prompt hash. P1b: also classify a sample of
                 #   NON-matched bugfix commits (mining-recall sanity).
  szz.py         # SZZ (git blame -w) pre-fix lines -> bug-introducing commit +
                 #   qualified function; freeze bug_sites.json (file+function+SHAs)
  baseline.py    # churn/LOC per function <= split T; any-boundary-call set;
                 #   #function-budget recall machinery -> B, A
  repo_fit.py    # Slice 0 gate: labeled_site_count vs floor + mining-recall
                 #   -> fixtures/repo_fit.json + repo-fit axis verdict
  score.py       # (slice 3) join map @ T  x  frozen sites (F11 key) -> Z/B/A/F/D/n
                 #   + F12 mute-gate + F13 two-axis verdict -> docs/kill-gate.md
  fixtures/
    repo_fit.json       # Slice 0 output (frozen)
    labels.json         # frozen LLM labels (+ model id, prompt hash, SHAs)
    bug_sites.json      # frozen SZZ-resolved sites (the ground truth for scoring)
    baseline.json       # frozen B / A
    negative_control/   # (created in slice 2) hexagonal / functional-core app
    welded_twin/        # (created in slice 2) same app, boundaries welded inline
```

**Build order:**
- **Slice 0 (repo-fit, analyzer-free — can kill before any Rust):** `doctor.py`
  → `mine.py` → `label.py` (freeze `labels.json` + run P1b mining-recall) →
  `szz.py` (freeze `bug_sites.json`) → `repo_fit.py`. If the site count is below
  floor, record *underpowered → re-target* and **stop** (or pull `ceal`).
- **Slice 1 (baseline):** `baseline.py` → `baseline.json` (`B`, `A`). Delivers the
  churn + any-boundary-call bars **before** any analyzer code — the
  pre-commitment that makes the kill gate un-wrigglable.
- **Slice 2 (minimal map — Rust):** Cargo scaffold + `pry --version` + a 3-line
  `pry map` smoke fixture *first* (prove the binary builds and is deterministic),
  then the boundary catalog (`catalog/python.toml`), seamed/welded/ambiguous
  classification with the coverage block, and the `negative_control`/`welded_twin`
  fixtures (which presuppose the seam/weld definition, so they live here, not in
  Slice 0).
- **Slice 3 (the number):** `score.py` joins map@`T` with frozen sites → the
  honesty-guarded triplet + two-axis verdict → `docs/kill-gate.md` → go/kill.
