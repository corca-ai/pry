# Spec — Finding-Eval Harness (H3 broad-market gate) · build contract

The next build contract after Layer-0 map + precision levers. Turns pry's
*precision/recall claim* into something **measured on independent code** and
keeps every future algorithm change honest. Sibling docs:
[`spec-layer0.md`](spec-layer0.md) (the map + kill-gate harness contract),
[`precision-gate.md`](precision-gate.md) (the hand-labeled H1 precision result
this generalizes), [`kill-gate.md`](kill-gate.md) (the go/kill record).

This is the `nose` `bench/` discipline applied to pry: a frozen, panel-labeled,
dev/held-out corpus that has *rejected plausible-but-wrong ideas* — except pry's
unit is a **finding** (a welded-at-demand boundary), not a clone family.

## Problem

pry's entire value proposition — "the welded-at-demand backlog is ~88% genuine
(ceal) / ~97% (cautilus)" — rests **only on corca's own repos**: ceal, cautilus,
charness, Run 6's 7 own TS codebases, and now open-ax-day. Every number pry has
ever produced is self-corpus.

- The **H3 broad-market gate is pre-registered but unrun** (`precision-gate.md`
  Caveats: *"H3 (broad-market value test) remains the complementary unrun
  gate"*); §9 of `initial-plan.md` always named "then 20–50 OSS repos."
- Precision is **corpus-sensitive** (ceal raw 32% vs cautilus raw 70%; different
  noise classes each time) — so one more own-repo does not de-risk it.
- There is **no reusable harness** to (a) measure precision *and recall* of pry
  findings on a new corpus, or (b) gate a new filter/lever against a held-out
  generalization split. Today that work is ad-hoc, single-rater, in-session hand
  labeling.

nose closed exactly this with a 105-repo (7-lang × 15, dev 58 / heldout 47),
3-persona-panel-labeled benchmark. pry needs the finding-level analog.

## Current Slice

A **dev-time, in-repo, LLM-panel finding-eval harness** for the TS/JS analyzer:

1. `pry map` → demand-welded findings (+ the bare/diagnostic pool for recall).
2. mechanical `emit` → a **blinded** finding worklist (`{file, line, kind,
   source_context}`, pry's own verdict hidden).
3. **3 independent coding-subagent personas** label each finding
   `GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS` against the rubric.
4. mechanical `reconcile` → majority (≥2/3); 2-1 → tie-break judge; residual →
   arbiter; genuinely-undecidable marked as such. `freeze` → schema-validated,
   provenance-stamped labelset (votes retained for audit).
5. report **precision** (demand-welded) + **recall** (vs independent pool),
   per-repo and pooled, on a **third-party application-shaped** TS/JS corpus with
   a **dev/held-out** split.

The **first measurement slice runs existing pry unchanged** (no algorithm
change) to answer "does ~88% hold off-corca?" and to emit the noise taxonomy that
names the next lever.

## Fixed Decisions

- **E1 — TS/JS first.** The analyzer has a TS/JS frontend and a hand-validated
  88/97%. Python has *no frontend* and is a separate, deferred, analyzer-free
  (b)-gate phase (see Deferred). No Python frontend is built on faith.
- **E2 — dev-time intelligence only; shipped CLI unchanged.** The LLM panel
  exists *only in this repo's harness*. The `pry` binary stays **zero-LLM,
  zero-credential, deterministic** (the existing harness rule: *"No harness
  script calls an LLM or holds a credential. The intelligence is the coding
  agent"*; F10/F16). The panel is **3 coding-subagents** (personas), **not** an
  LLM-calling script; mechanical scripts only `emit` / `reconcile` / `freeze`.
  *Confirmed by the operator: LLM eval is for building the algorithm here; each
  repo running `pry map` uses no LLM.*
- **E3 — corpus = third-party, application-shaped, not libraries, not own
  repos.** Validation corpus is independent (non-corca) OSS **applications /
  services** (agent/LLM runtimes, automation/workflow apps, web services, CLIs) —
  the population pry actually deploys onto. **Excluded:** (a) general-purpose
  libraries (`date-fns`/`zod`/`hono`-style) — more DI-disciplined/seamed → wrong
  population, operator-flagged; (b) corca's own repos — the very gap being closed
  is "all validation is self-corpus." Pinned commits + generated/vendored prune
  (borrow nose `prune_corpus.py`). **dev / held-out split; tune only on dev.**
- **E4 — labels reuse the precision-gate taxonomy.** `GENUINE / FALSE-WELD /
  COSMETIC / AMBIGUOUS` (already validated in `precision-gate.md`). **Blinded** to
  pry's own verdict (F10 independence); **refute-borderline** (F17).
- **E5 — metric = precision AND recall; gate = precision↑ ∧ held-out recall
  held.** Precision on the demand-welded subset; recall against an **independent
  candidate pool** (pry's bare/diagnostic full-boundary set is a near-free pool —
  it contains what pry's filters *demote/miss*). A new lever/filter ships **only
  if** it raises dev precision **without** dropping held-out recall. Sequencing:
  precision is measured in the first slice (measuring *existing* pry, no
  algorithm change); the **recall arm comes online before any new lever ships.**
- **E6 — own repos are dogfood, not validation.** open-ax-day, ceal, cautilus,
  etc. are dogfood / dev-signal targets — valuable for surfacing candidate noise
  classes (open-ax-day surfaced the smoke-harness scope question now resolved by
  E7) — but **never** counted as the external-validity proof.
- **E7 — scope is user-controlled, not heuristic (resolves PQ4).** pry does not
  *guess* wantedness (the (c)-axis `precision-gate.md` leaves unmeasured): instead
  of auto-demoting test/smoke-harness-shaped files in `src/`, **each repo declares
  its own out-of-scope set** (operator: *"the decision belongs to each repo"*).
  Three granularities:
  (a) **`.pryignore`** — gitignore syntax, committed per-repo; near-free since the
  `ignore` crate already backs the walk (`WalkBuilder::add_custom_ignore_filename`);
  (b) **`--exclude <glob>`** — ad-hoc / CI, no commit;
  (c) **inline `// pry-ignore`** (`# pry-ignore` for future Python) — the
  per-finding escape hatch the roadmap already names for the floor, extended to the
  map. (`.gitignore` is **already** respected via the `ignore` crate.)
  **Exclude is NOT an algorithmic precision lever** — it is user scoping, **off
  during eval measurement** (third-party corpora have no `.pryignore`), so it never
  inflates the precision claim. Sequenced independently of the eval.
  **Path-level `.pryignore` + `--exclude <glob>` are BUILT** (`src/main.rs`
  `discover`; `tests/exclude_smoke.rs`; proven on open-ax-day: `--exclude
  'src/smoke-*.ts'` drops the 8 smoke-harness welds, keeps the 3 genuine
  identity/kit-runtime welds). Inline `// pry-ignore` remains future, ideally with
  the floor.

## Probe Questions

- **PQ1 — the dev corpus slate.** Scout candidates (`git clone` at a pinned
  commit + `pry map`) to confirm: real TS/JS (not thin-over-other-lang), low
  generated/vendored ratio after prune, and enough demand boundaries to measure.
  Candidate domains + named starting candidates (confirm/swap by scouting):
  agent/LLM app (`librechat`, `continue`), automation/workflow (`n8n`,
  `activepieces`), LLM-orchestration (`flowise`), web service (`outline`),
  scheduling/clock-heavy (`cal.com`). Freeze ≥3 for dev before slice 1 labeling.
- **PQ2 — panel personas + reconciliation.** 3 lenses (borrow nose's
  pragmatic/skeptic + a pry-specific *"is there a real failure to inject on a
  path worth testing, with no existing seam?"*). Define tie-break/arbiter
  mechanics. Resolved during the first labeling run.
- **PQ3 — sampling rates under cost.** Clock census vs stratified sample;
  recall-pool sample size. The panel is 3×(+tie-break) passes per finding; start
  small (dev ≥3 repos), scale to held-out once the harness is proven.
- ~~**PQ4 — test/smoke-harness scope.**~~ **RESOLVED → E7.** open-ax-day's 9/11
  demand-welds in `src/smoke-*.ts` are handled by user-controlled exclude
  (`.pryignore` / `--exclude` / inline), not a pry heuristic — pry never guesses
  wantedness, so it cannot false-demote a genuine gap.

## Deferred Decisions (each names its reopen trigger)

- **Python (b)-gate phase, then a Python frontend.** *Reopen when:* the TS/JS
  harness is stable AND a **third-party non-glue OSS Python** corpus
  (distributed-systems / data-pipeline shape, pry's original §9 target) is
  assembled. Run the analyzer-free (b)-gate first (welded/seamed hand/script
  sample, as Runs 1–5 did, no frontend); build a Python frontend **only on a
  (b)-gate GO**. *Note:* `parental-interaction-eval` (239 Py, own repo) is a
  tempting candidate but is the **own-repo glue population kill-gate already
  KILLed** — it does not test the open Python question; use independent non-glue
  OSS Python instead.
- **Held-out expansion / per-corpus client fingerprints / SARIF emit.** *Reopen
  when:* the dev gate is green and generalization or tooling needs sharpening.
- **Homebrew tap (packaging polish).** *Reopen when:* a tap repo + token exist.

## Non-Goals

- **No OSS showcase / leaderboard / outbound PRs** (operator killed the
  marketing/adoption play; this is measurement-for-the-algorithm only).
- **No LLM in the shipped binary** (E2).
- **Not** validating on general-purpose libraries, or on additional own repos
  (E3/E6).
- **Not** building the Python frontend in this slice (Deferred).

## Deliberately Not Doing (rejected, with reasons)

- **LLM-calling eval script with an embedded credential** — rejected: violates
  pry's zero-intelligence-CLI rule and is the explicit "nose anti-pattern" the
  harness README names. The panel is coding-subagents; scripts stay mechanical.
- **Precision-only metric** — rejected: pry improves precision by *filtering*, so
  a precision-only optimizer silently over-filters and craters recall (lever 3 is
  already "precision-favoring"; W1–W3 are named recall holes). Recall arm is
  required before any new lever.
- **Own-repo / library validation corpus** — rejected: representativeness
  (libraries are more seamed; pry deploys on apps) + independence (self-corpus is
  the exact gap). Own repos stay as dogfood only (E6).

## Constraints

- `pry map` stays **byte-deterministic** (existing; unchanged this slice).
- Harness scripts are **mechanical**: no LLM call, no credential, no spend
  (extends `harness/label_io.py`).
- Labels are **auditable, not byte-reproducible**: provenance = labeler model-id
  + rubric-hash (F16); the 3 votes are retained per finding (nose-style audit).
- **Held-out discipline:** tune only on dev; held-out is the generalization gate.
- **Frozen corpus:** pinned commits + prune manifest for reproducibility.

## Success Criteria

- **SC1** — a frozen, auditable finding-labelset exists for the dev corpus
  (per-finding: 3 votes + reconciled label + provenance).
- **SC2** — per-repo + pooled **precision** of demand-welded is reported on **≥3
  third-party application-shaped TS/JS repos**, answering "does ~88% hold
  off-corca?" with file:line-auditable labels.
- **SC3** — **recall** is measurable against the independent pool (genuine
  findings pry demoted/missed are identifiable), and the gate rule (precision↑ ∧
  held-out recall held) is documented and runnable.
- **SC4** — the shipped `pry` binary is unchanged: no new LLM/credential
  dependency; harness scripts contain no network/LLM call.
- **SC5** — a **noise taxonomy** names the next lever (precision-gate-style
  deliverable), with counts.

## Acceptance Checks

- **AC1 (SC1)** — `freeze` refuses (exit ≠ 0) on any incomplete/malformed verdict
  set (completeness guard, mirroring `label_io.py freeze`); the checked-in
  labelset validates against its schema.
- **AC2 (SC2)** — a precision table (precision-gate format) is checked into
  `docs/eval-gate.md`; every label is contestable via the cited `file:line`
  against the pinned corpus.
- **AC3 (SC3)** — recall is computed from the labeled bare-pool sample; a
  documented command re-derives precision/recall from the frozen labelset; the
  gate rule is stated with a worked example.
- **AC4 (SC4)** — a dependency check (`Cargo.lock` has no
  `reqwest|hyper|anthropic|openai|tonic` etc.) is empty; `rg` over `harness/`
  shows no LLM/HTTP client call from a script.
- **AC5 (SC5)** — the taxonomy section in `docs/eval-gate.md` lists each noise
  class with its count and the candidate lever it implies.

## Critique

Bounded fresh-eye critique (repo-mandated subagent; same-agent substitute
forbidden) to run before finalize — focuses: (1) likely implementer misread of
the precision/recall gate; (2) overstated acceptance (is "≥3 repos" enough to
claim generalization, or only to *start*?); (3) hidden sequencing (does the
recall arm really need the bare pool labeled, or can it piggyback the precision
pass?); (4) corpus-selection bias (do the named app candidates secretly skew
DI-disciplined like ceal?). *Pending — see First Implementation Slice.*

No forced debug interrupt reported by the risk planner for this contract.

## Canonical Artifact

This doc (`docs/spec-eval-harness.md`) is canonical during implementation.
Results land in a new **`docs/eval-gate.md`** (the H3 result doc, sibling to
`precision-gate.md`). Harness code extends `harness/` (new `finding_io.py` +
reconcile, mirroring `label_io.py`); fixtures under `harness/fixtures/eval/`.

## First Implementation Slice

1. **Scout + freeze the dev slate (PQ1):** clone ≥3 app-shaped third-party TS/JS
   candidates at pinned commits, prune, confirm fit with `pry map`. Record the
   slate (ids, commits, source_file_count, split) in `docs/eval-gate.md`.
2. **Build the mechanical harness:** `finding_io.py emit` (blinded finding
   worklist) + `reconcile`/`freeze` (majority ≥2/3, tie-break, schema-validated,
   provenance-stamped), extending the `label_io.py` pattern. No LLM in scripts.
3. **Run the 3-subagent panel** on the dev corpus demand-welded findings (+ a
   recall-pool sample).
4. **Report** per-repo + pooled precision, recall, and the noise taxonomy in
   `docs/eval-gate.md`. **No algorithm change in this slice** (measure existing
   pry); levers come after, each gated by E5.

Ready for `impl` after the bounded critique (Critique section) and operator
sign-off on the dev slate (PQ1).
