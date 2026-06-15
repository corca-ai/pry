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

## 2. The unit, the two arms, and "bugfix-touched"

- **Unit:** one pry *finding* (a boundary call classified by `pry map`).
- **Welded-at-demand arm:** findings with `class == "welded" AND demand == true`.
- **Seamed arm:** findings with `class == "seamed"`.
  (Findings that are welded-but-not-demand, or ambiguous, are in NEITHER arm.)
- **Bugfix-touched (the observed outcome):** a finding is bugfix-touched **iff
  the commit that LAST modified its source line — `git blame` at the repo's
  pinned commit — is in that repo's bugfix-commit set** produced by the miner
  (S2). This is a deterministic last-touch proxy: it undercounts older bugfixes,
  but it undercounts BOTH arms identically, so the *ratio* is unbiased by the
  proxy. (The proxy is the honest, tractable form; a full per-line modification
  history is out of scope — see Non-Claims.)

## 3. The metric and its DENOMINATOR (쟁점 4 + confound R-B)

- **Per-arm bugfix-touch rate** = (# bugfix-touched findings in arm) / (# findings
  in arm).
- **Raw (pooled) enrichment ratio** = welded_at_demand_rate / seamed_rate.
  Reported, but NOT the verdict metric — it is confounded by R-B (welded sites may
  simply be more numerous, larger, or in hotter files).
- **MATCHED enrichment ratio = THE verdict metric.** Findings are stratified by
  `(file-churn tercile × site-size tercile)`:
  - *file-churn* = number of commits that touched the finding's file (proxy for
    "hot file"), cut into terciles **across all findings in the corpus arm
    pool** (`ENRICHMENT_CHURN_TERCILES = 3`).
  - *site-size* = line count of the enclosing function/method containing the
    finding (proxy for "big site"), cut into terciles
    (`ENRICHMENT_SITESIZE_TERCILES = 3`).
  - Within each of the ≤9 strata, compute the welded-at-demand rate and the
    seamed rate. A stratum is **used only if it has ≥ `ENRICHMENT_MIN_STRATUM`
    (5) findings in EACH arm**; under-filled strata are **dropped and the drop is
    LOGGED** (no silent truncation, risk R-D).
  - **Matched ratio** = directly standardized:
    `Σ_s w_s·welded_rate_s / Σ_s w_s·seamed_rate_s`, where `w_s` = total findings
    in stratum `s` (both arms). This is the only form that neutralizes R-B.

## 4. The two-sided floor / FALSIFIER (set blind)

On the **matched** ratio:
- **GO — signal real (쟁점 4 confirmed):** matched ratio ≥
  `ENRICHMENT_GO_FLOOR = 1.5` (welded-at-demand sites ≥1.5× as likely to be
  bugfix-touched as seamed, after matching).
- **FALSIFIED for this corpus:** matched ratio ≤ `ENRICHMENT_FALSIFIER = 1.1`
  (or collapses to ~1.0). **This is a valid, honest outcome to report, not a
  failure to hide** (the nose `rate-match ≠ precision` lesson made a contract).
- **WEAK / inconclusive:** `1.1 < matched ratio < 1.5`.

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
- **No SZZ Tier 2** (operator-dropped): no bug-linked gold, no LLM-panel audit.
- **No per-line full history**, no per-repo precision panel on heldout, no
  provider/live/release proof, no outbound on corpus repos.

---

*Frozen at S1. Downstream slices read config.py; they do not re-derive these
numbers. Changing any threshold above after an enrichment number exists voids the
honesty gate and must be called out explicitly in the closeout.*
