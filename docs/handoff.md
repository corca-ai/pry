# Handoff

## Workflow Trigger

**Active arc: the finding-eval harness (H3 broad-market gate).** Spec is
finalized + critique-clean; the zero-LLM mechanical plumbing is BUILT and tested.
The next step is **operator-gated, not auto-runnable** (see Next). This is a
*decide-then-run* pickup, not an autonomous build trigger — the remaining work
spends LLM budget and pins a corpus, both of which the operator gates.

Canonical contract: [`spec-eval-harness.md`](spec-eval-harness.md). Layer-0 map +
packaging are engineering-COMPLETE (prior arc; below).

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
- **Testability-backlog issues filed** (dogfood, corca-owned only): ceal#350,
  cautilus#48, open-ax-day#5. parental skipped (Python). *Caveat:* ceal#350 is
  whole-repo (248) vs the validated `packages/`-only subset (68) — can be
  re-scoped if the operator wants the validated cut.

### Layer-0 + packaging arc (prior, COMPLETE)
- **pry v0.1.0 released + wired.** TS/JS analyzer (demand-subset precision ~88%
  ceal / ~97% cautilus). `corca-ai/pry` PUBLIC; `v0.1.0` GitHub Release via
  cargo-dist; charness `external_binary` manifest (`validation` role for
  `quality`); F15 skill `skills/pry/SKILL.md` + `rank_backlog.py`.

## Next — operator-gated, then run (none auto-runnable)

The mechanical harness is slate-agnostic and done. What remains needs operator
input or spends budget:

1. **Operator sign-off (blocks the panel run):** the **dev slate (PQ1)** —
   librechat `8154a31` / continue `eaa23c5` / flowise `f4e2794` / outline
   `d85ead5`, all welded-end (clock-inj 0–5%); **needs one higher-injection
   exemplar** to span the spectrum (scout `n8n`/`cal.com`) — and the
   **pre-registered corpus target (SC2): dev 5 / held-out 10**.
2. **Slice 1 step 3 — run the 3-persona panel** (the gated LLM spend; E8
   one-time). PQ3 sampling: non-clock demand-welds census, clock ≥25% sample +
   seamed-control. **Pilot 1 repo first** to measure real cost (PQ3). Produce the
   **frozen labelset** → precision (per-repo/stratum/pooled + CI) + noise taxonomy
   in a new **`docs/eval-gate.md`** (SC2/SC5/AC2/AC5). Opens — does not close —
   the H3 gate.
3. **Slice 2 — filter-recall arm** (E5/SC3/AC3) before any lever ships.
4. **E9 SZZ structural-improvement** pass on an EH-bugfix-rich OSS repo (reuse
   `harness/mine.py`+`szz.py`+commit labeler) — catalog-recall + calibration.
5. **Then levers**, each gated deterministically against the frozen labelset
   (dev precision↑ ∧ held-out filter-recall held).

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
- `harness/finding_io.py` + `harness/test_finding_io.py` — the mechanical panel
  plumbing (built this slice).
- `docs/precision-gate.md` — validated precision, labeling taxonomy, rung-3 census.
- `docs/kill-gate.md` — the go/kill record (TS GO, Python KILL).
- `charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md` —
  packaging goal: full slice log, commit SHAs, user-verification commands.
