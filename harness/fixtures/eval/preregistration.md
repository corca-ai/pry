# E9 sweep — PRE-REGISTRATION (split + denominator + floor + falsifier)

**Status: frozen. This file's git commit MUST precede the commit that writes any
enrichment number.** A fresh closeout reviewer proves the order from git, not from
a self-attesting line:

```
git merge-base --is-ancestor <this-commit-sha> <first-enrichment-number-commit-sha>
```

This is the load-bearing honesty gate for the E9 sweep (handoff "Honesty gates";
goal Boundaries C2). It mirrors the Slice-0 `REPO_FIT_SITE_FLOOR` and the
kill-gate F27 "frozen before this run" discipline: the split, the metric
denominator, and the two-sided floor are all fixed **before** any number exists,
so none can be moved post hoc to manufacture (or rescue) a result.

The machine-readable copy of every threshold below lives in `harness/config.py`
(the `E9 multi-repo validation sweep` block) and the corpus/split in
`harness/fixtures/eval/corpus.json`. This document is the human-readable contract;
config.py is the single source of truth the harness reads. If the two ever
disagree, that is a bug, and the git history of *this file* governs.

---

## 1. The corpus and the dev|heldout split (쟁점 2)

Frozen in `corpus.json` (33 repos: 25 TS/JS + 8 Python), pinned commits,
schema-validated. The split below is chosen **now, before any mining or
enrichment number exists** — it is not chosen after a peek (risk R-A). Tuning
rule: **any threshold is tuned on `dev` only; `heldout` is reported separately
and never tuned on.**

**TS/JS arm — dev (5):** `outline`, `flowise`, `continue`, `librechat` (the 4
already-mapped H3 seeds) + `medusa` (a non-AI e-commerce app, added so `dev` is
not all-AI).
**TS/JS arm — heldout (20):** directus, payload, strapi, n8n, nocodb, budibase,
umami, formbricks, calcom, twenty, immich, karakeep, linkwarden, openstatus,
docmost, vendure, midday, novu, seerr, rocketchat.

**Python arm — dev (2):** `paperless-ngx`, `saleor`.
**Python arm — heldout (6):** netbox, searxng, mealie, healthchecks, redash,
changedetection.

The Python split is pre-registered here too; it is inert (harmless) if the S5
(b)-gate KILLs the Python branch.

## 2. The unit, the arms, and "bugfix-touched"

> **Amendment A (2026-06-15, pre-measurement, power-motivated — NOT an outcome
> peek).** Before computing ANY bugfix-touch rate, a power check on the 4 already-
> cloned seeds showed the `class=="seamed"` arm is ~14× thinner than welded-at-
> demand (seeds: seamed 3/16/15/28 vs welded@demand 135/149/237/354). Only **arm
> SIZES** were observed — no bugfix-touch outcome. A seamed-ONLY control is badly
> underpowered under the matched denominator (≥5/arm/stratum). So the **PRIMARY
> control is changed to "rest"** (every other decided boundary finding), which is
> well-powered; `seamed` and `welded-not-demand` are retained as pre-registered
> SECONDARY breakdowns so nothing is hidden. This amendment is committed before any
> enrichment number; the honesty-gate ancestry test uses this commit.

- **Unit:** one pry *finding* (a boundary call classified by `pry map`).
- **Signal arm — welded-at-demand:** findings with `class == "welded" AND
  demand == true`.
- **PRIMARY control — "rest":** every other **decided** boundary finding, i.e.
  `class == "seamed"` OR (`class == "welded"` AND `demand == false`). (Ambiguous
  findings — no decided class/demand — are in NEITHER arm.) This tests the
  actionable claim: *are the sites pry flags as welded-at-demand bugfix-enriched
  relative to every other boundary site pry sees?*
- **SECONDARY breakdowns (reported, not the verdict):** welded-at-demand vs
  `seamed`-only (the injectability contrast, flagged underpowered if thin) and
  welded-at-demand vs `welded-not-demand`-only (isolates the *demand* bit holding
  "welded" fixed). The two-sided floor/falsifier applies to the PRIMARY.
- **Bugfix-commit set (the NUMERATOR), PINNED HERE — not deferred to S2:** a
  bugfix commit = a **non-merge commit reachable from the repo's pinned commit
  whose MESSAGE matches `config.ENRICHMENT_BUGFIX_MSG_REGEX`** (= the frozen
  Slice-0 `BUGFIX_MSG_REGEX`: `fix|fixes|fixed|bugfix|hotfix|bug|regression|
  broke|broken|crash|incorrect`, case-insensitive). **Message-intent only — NO
  error-handling diff filter** (the EH-diff filter is for Slice-0 *mining*;
  enrichment is blame-based per line, so any bugfix counts). This is the single
  most outcome-sensitive knob, so it is frozen WITH the denominator (critique #8):
  S2's miner *implements* this predicate, it does not get to *choose* it.
- **Bugfix-touched (the observed outcome):** a finding is bugfix-touched **iff
  the commit that LAST modified its source line — `git blame` at the repo's
  pinned commit — is in that repo's bugfix-commit set** (above). This is a
  deterministic last-touch proxy. It undercounts older bugfixes, and the
  undercount is **plausibly LARGER for the welded arm** (welded code is, by the
  thesis, hotter / more recently churned, so an original bugfix is more likely to
  have been overwritten by a later non-bugfix commit). The matched denominator
  (churn stratum) *reduces* but does not *eliminate* this asymmetry, so the
  matched ratio is a **conservative LOWER bound** on the true enrichment — the
  proxy can only *understate* a real signal, never manufacture one. (A full
  per-line modification history is out of scope — see Non-Claims.)

## 3. The metric and its DENOMINATOR (쟁점 4 + confound R-B)

- **Per-arm bugfix-touch rate** = (# bugfix-touched findings in arm) / (# findings
  in arm).
- **Raw (pooled) enrichment ratio** = welded_at_demand_rate / rest_rate (PRIMARY
  control). Reported, but NOT the verdict metric — it is confounded by R-B (welded
  sites may simply be more numerous, larger, or in hotter files).
- **MATCHED enrichment ratio = THE verdict metric** (signal = welded-at-demand,
  control = "rest"). Findings are stratified by
  `(file-churn tercile × site-size tercile)`:
  - *file-churn* = number of commits that touched the finding's file (proxy for
    "hot file"), cut into terciles **across all findings in the corpus arm
    pool** (`ENRICHMENT_CHURN_TERCILES = 3`).
  - *site-size* = line count of the enclosing function/method containing the
    finding (proxy for "big site"), cut into terciles
    (`ENRICHMENT_SITESIZE_TERCILES = 3`).
  - Within each of the ≤9 strata, compute the welded-at-demand rate and the
    control ("rest") rate. A stratum is **used only if it has ≥
    `ENRICHMENT_MIN_STRATUM` (5) findings in EACH arm**; under-filled strata are
    **dropped and the drop is LOGGED** (no silent truncation, risk R-D).
  - **Matched ratio** = directly standardized:
    `Σ_s w_s·welded_rate_s / Σ_s w_s·rest_rate_s`, where `w_s` = total findings
    in stratum `s` (both arms). This is the form that neutralizes R-B.

## 4. The two-sided floor / FALSIFIER (set blind)

On the **matched** ratio, with a **cluster bootstrap over repos** (resample the
corpus's repos with replacement, `ENRICHMENT_BOOTSTRAP_B = 2000`, deterministic
`ENRICHMENT_BOOTSTRAP_SEED = 0`, `ENRICHMENT_BOOTSTRAP_CI = 0.95` percentile
interval). Bootstrapping over *repos* (not findings) respects the
non-independence of findings within a repo (critique #7). The CI is pinned now,
before any number, so it cannot be added post hoc to rescue a result:
- **GO — signal real (쟁점 4 confirmed):** matched point ratio ≥
  `ENRICHMENT_GO_FLOOR = 1.5` **AND** the 95% CI lower bound strictly above
  `ENRICHMENT_GO_CI_LOWER_MIN = 1.0` (the enrichment is significantly > 1, not a
  thin-stratum point estimate).
- **FALSIFIED for this corpus:** matched point ratio ≤ `ENRICHMENT_FALSIFIER =
  1.1` **OR** the 95% CI lower bound ≤ 1.0 (the "collapses to ~1.0" condition,
  made testable). **This is a valid, honest outcome to report, not a failure to
  hide** (the nose `rate-match ≠ precision` lesson made a contract).
- **WEAK / inconclusive:** anything between (point in `(1.1, 1.5)`, or point ≥1.5
  but CI lower bound ≤ 1.0).

**Simpson's-paradox guard (S3, per-repo distribution):** a pooled GO must not be
carried by one repo. Among repos with ≥ `ENRICHMENT_PERREPO_MIN_FINDINGS = 20`
findings per arm, **a majority (≥ `ENRICHMENT_PERREPO_MAJORITY = 0.60`) must show
a per-repo ratio > 1.0.** The per-repo distribution is reported, not only the
pooled number.

## 5. Python (b)-gate lens criterion (S5) — set blind

The Python branch builds a frontend **only on a (b)-gate GO**, and the lens runs
**only after S3+S4 have a recorded verdict** (sequencing gate, goal C6).
- **GO:** the analyzer-free substitution-demand subset
  (`summary.substitution_demand_subset.welded_fraction_LENS_GO_METRIC`, the
  clock/clients/network/subprocess subset — NOT the fs-swamped bare fraction)
  lands **inside the band `BGATE_LENS_BAND = [0.15, 0.85]`** (kill-gate F27 /
  Run 5).
- **KILL:** the subset is out of band, OR the lens is **mute**
  (`decided_fraction < BGATE_MIN_DECIDED_FRACTION = 0.40`). On KILL, no frontend
  is built; the analyzer-free result is recorded.

## 6. Standing non-claims (restated at closeout)

- **Correlation, never causation.** The matched enrichment is a directly-observed
  correlation; pry never ships "welded *causes* bugs."
- **One-directional.** A seamed-no-bugfix site is NOT evidence the seam prevented
  a bug (it may be younger/colder code). We claim only that welded-at-demand
  sites are *enriched* among bugfix-touched sites — never that seams are safe.
- **Residual confound NOT neutralized: file-KIND** (critique #5). The matched
  denominator balances file-churn and site-size, but NOT file *kind*: network /
  DB / subprocess modules are independently bug-prone *by type* regardless of
  churn or size, and welded boundary calls concentrate there. Churn is measured
  at the pinned commit (`git log --oneline -- <file> | wc -l`). We do not claim
  the matched ratio is confound-free — only that the two numerosity/size/hotness
  confounds (R-B as originally stated) are neutralized; the file-kind residual is
  named, un-neutralized, and works against a clean causal reading (so the
  correlation is reported as exactly that — a correlation).
- **No SZZ Tier 2** (operator-dropped): no bug-linked gold, no LLM-panel audit.
- **No per-line full history**, no per-repo precision panel on heldout, no
  provider/live/release proof, no outbound on corpus repos.

---

*Frozen at S1. Downstream slices read config.py; they do not re-derive these
numbers. Changing any threshold above after an enrichment number exists voids the
honesty gate and must be called out explicitly in the closeout.*
