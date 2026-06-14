# Handoff

## Workflow Trigger

**Active arc: the finding-eval harness (H3 broad-market gate).** Spec finalized +
critique-clean; mechanical harness built; **the panel has now RUN on 4 third-party
repos and the H3 gate is OPENED** ([`eval-gate.md`](eval-gate.md)). The next
substantive build is **Slice 2 (filter-recall arm)**, which unblocks the named
precision levers (cosmetic-random is the clear #1). Two operator-only items remain
(human calibration; held-out/spectrum expansion) — see Next.

Canonical contract: [`spec-eval-harness.md`](spec-eval-harness.md). Result doc:
[`eval-gate.md`](eval-gate.md). Layer-0 map + packaging are engineering-COMPLETE
(prior arc; below).

## Current State

### Finding-eval harness arc (this session)
- **Spec finalized** — `docs/spec-eval-harness.md`, E1–E9 + PQ1–4 + SC1–5/AC1–5,
  bounded critique folded (FIX-FIRST, 4 BLOCKERs resolved). Core shape: dev-time
  LLM panel (3 same-model personas + human calibration) → **frozen labelset** →
  deterministic regression forever (E8); shipped binary stays zero-LLM (E2/SC4);
  corpus = third-party **app-shaped** OSS, not libraries, not own repos (E3/E6);
  SZZ is an **active dev-time structural-improvement** input, never a product
  prediction claim (E9).
- **Scope-control slice SHIPPED** (commit `dd97cad`): `.pryignore` + `--exclude
  <glob>` path-level exclusion (`src/main.rs discover`; `tests/exclude_smoke.rs`,
  5 cases). pry never guesses wantedness — each repo declares its own out-of-scope
  set (E7). Two silent footguns guarded (empty glob, leading `!`).
- **Mechanical eval harness BUILT** (this slice): `harness/finding_io.py`
  (`emit`/`reconcile`/`freeze`) + `harness/config.py` constants +
  `harness/test_finding_io.py` (8 stdlib-unittest cases, green). Unit = a pry
  *finding*; 3-persona panel → majority(≥2/3) → tie-break → arbiter; blinded
  worklist (hides the verdict bit), provenance-stamped frozen labelset, votes
  retained. **No LLM in scripts** (E2). Proven on the synthetic fixture (AC1
  refuse paths + tie-break/arbiter loops + malformed-escalation refuse +
  determinism) AND on a real `pry map` (ceal/packages: 68 demand-welded →
  41-graded + 15 seamed-control worklist). Bounded fresh-eye critique done
  (no BLOCKERs; 2 NOTEs fixed).
- **H3 PANEL RAN — gate OPENED** (commit `0587e5c`): the 3-persona panel labeled
  589 findings across 4 pinned third-party repos (outline/flowise/continue/
  librechat); frozen to `harness/fixtures/eval/*-labels.json` (votes retained).
  **Result** ([`eval-gate.md`](eval-gate.md)): network+subprocess **100%**
  (261/261), ex-cosmetic-tail **89.3%** (≈ ceal 88%), raw pooled 56.7%; the
  clock(3.8%)/random(0%) cosmetic tail is the entire drag. Levers named: (1)
  cosmetic-random filter, (2) stronger clock filter, (3) `.vitest` test-file
  heuristic, (4) **rung-3 stage-2 REOPEN** (continue surfaced the injected-
  customFetch seam). Seamed-control recall flag 13/33 → Slice 2. *Panel-labeled,
  human-calibration pending (E4); gate OPENED not CLOSED.* Corpus cloned at
  `~/codes/_pry-corpus/` (default-HEADs matched PQ1 commits exactly).
- **ceal#350 re-scoped → DONE** (the cut): whole-repo 248 → validated `packages/`
  (70 on latest `c4297fc1`), re-scope explained in the issue body + comment.
- **Testability-backlog issues filed** (dogfood, corca-owned only): ceal#350
  (re-scoped above), cautilus#48, open-ax-day#5. parental skipped (Python).

### Layer-0 + packaging arc (prior, COMPLETE)
- **pry v0.1.0 released + wired.** TS/JS analyzer (demand-subset precision ~88%
  ceal / ~97% cautilus). `corca-ai/pry` PUBLIC; `v0.1.0` GitHub Release via
  cargo-dist; charness `external_binary` manifest (`validation` role for
  `quality`); F15 skill `skills/pry/SKILL.md` + `rank_backlog.py`.

## Next — Slice 2, then the levers

The H3 gate is open and the levers are named. Build order (the spec gates levers
behind the recall arm):

1. **Slice 2 — filter-recall arm** (E5/SC3/AC3): label a bare-pool sample, compute
   baseline filter-recall, document the gate rule with a worked example. Its own
   panel run (size the sample when it starts, PQ3). **Unblocks every lever.**
2. **Cosmetic-random + test-file levers (the two EXACT, zero-cost wins):**
   `random` is 0/79 genuine and the `.vitest`/`-sol`/`sandbox` test-file leak is
   0-genuine too — demoting both lifts dev precision **56.7% → 70.3% losing zero
   genuine welds** ([`eval-gate.md`](eval-gate.md) "Projected lever impact",
   computed against the frozen labelset). They are *directly E5-gate-checkable on
   dev today* (they only demote already-labeled COSMETIC/FALSE-WELD findings, so no
   bare-pool labeling is needed for these two) — but still need the **held-out arm**
   before shipping. Build cosmetic-random first (mirror the cosmetic-clock filter
   in `src/classify.rs`); NB it changes validated fixtures (ceal 68→67) + the
   skill's cited self-test number, so do it with the operator in the loop. Then the
   harder stronger-clock + rung-3 levers (ceilings → ~95–99%) behind Slice 2.
3. **Rung-3 stage-2 REOPEN** (eval-gate.md #4): continue's injected-`customFetch`
   seam — scoped re-exam, cross-file, gate hard against the labelset + Slice 2.
4. **E9 SZZ structural-improvement** pass on an EH-bugfix-rich OSS repo (reuse
   `harness/mine.py`+`szz.py`+commit labeler) — catalog-recall + calibration.

**Operator-only (not autonomous):**
- **Human calibration set (E4):** hand-label a small subset of the 4 frozen
  labelsets to bound the panel's own error rate. Until then every eval number is
  panel-only (high agreement, but same-model → can be confidently wrong).
- **Close the gate (SC2):** add a **DI-disciplined exemplar** (high clock-injection
  — the slate is all welded-end) as dev #5, and run the **held-out arm** (target
  dev 5 / held-out 10). Scout `n8n`/`cal.com` for the disciplined end.

*Corpus note:* the 4 dev repos are cloned at `~/codes/_pry-corpus/` (pinned commits
in `eval-gate.md`); re-clone if cleaned. The shipped `pry` binary is unchanged
(zero-LLM); all panel work is dev-time only.

## Deferred (each names its reopen trigger — see spec)

- **Python (b)-gate + frontend** — reopen on a third-party non-glue OSS Python
  corpus (own-repo glue is a recorded KILL).
- **Inline `// pry-ignore`** (per-finding escape hatch) — ideally with the
  syntactic floor.
- **Syntactic floor** (zero-FP *claim* channel: empty catch / swallowed error) —
  the one un-built Layer-0 deliverable; still a legitimate alternate next center.
- **Homebrew tap; held-out expansion; SARIF emit.**

## References

- `docs/spec-eval-harness.md` — the canonical eval-harness build contract (E1–E9).
- `docs/eval-gate.md` — the H3 result doc (per-repo/kind/stratum precision +
  noise taxonomy + named levers + gate status).
- `harness/finding_io.py` + `harness/test_finding_io.py` — the mechanical panel
  plumbing. `harness/fixtures/eval/*-labels.json` — the 4 frozen labelsets.
- `docs/precision-gate.md` — validated precision, labeling taxonomy, rung-3 census.
- `docs/kill-gate.md` — the go/kill record (TS GO, Python KILL).
- `charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md` —
  packaging goal: full slice log, commit SHAs, user-verification commands.
