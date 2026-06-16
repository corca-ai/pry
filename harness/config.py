"""Shared constants for the pry validation harness (Slice 0 — repo-fit gate).

Single source of truth for corpus paths, mining heuristics, the labeler model,
and the pre-registered repo-fit floor. Kept as plain data so the heuristics are
auditable (the catalog/moat discipline, applied to the harness side).

See docs/spec-layer0.md (F6/F9/F10, P1) for the contract these encode.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- corpus (F3) ---------------------------------------------------------
# First corpus is charness; ceal is the second data point after the number.
DEFAULT_CORPUS_REPO = Path(os.path.expanduser("~/codes/charness"))
DEFAULT_CORPUS_NAME = "charness"

# --- output locations ----------------------------------------------------
HARNESS_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = HARNESS_DIR / "fixtures"
CANDIDATES_PATH = FIXTURES_DIR / "candidates.json"   # mine.py output (frozen)
LABELS_PATH = FIXTURES_DIR / "labels.json"           # label.py output (frozen)
REPO_FIT_PATH = FIXTURES_DIR / "repo_fit.json"       # repo_fit.py output (frozen)

# --- labeling worklist (F10) --------------------------------------------
# The labeler is the CODING AGENT, not a pinned API model. There is no model
# constant, no pricing, and no cost gate (that was the retired nose anti-pattern
# that embedded intelligence + a credential in a script). label_io.py emit caps
# each diff placed in the (blinded) worklist:
LABEL_DIFF_CHAR_CAP = 8000      # max diff chars per commit in the worklist

# --- repo-fit gate (P1) --------------------------------------------------
# Pre-registered floor: below this many SZZ-attributable error-handling bug
# sites, the verdict is "underpowered/inconclusive -> re-target", NOT go/kill.
# Set here BEFORE the number is computed so it cannot be moved post hoc.
REPO_FIT_SITE_FLOOR = 30

# Mining-recall sanity (P1b): how many non-matched bugfix commits to sample and
# LLM-classify, to estimate error-handling fixes the lexical miner missed.
MINING_RECALL_SAMPLE = 40

# --- mining heuristics (auditable) --------------------------------------
# A candidate error-handling bugfix commit = bugfix-intent message
# AND a python diff that touches error-handling / boundary tokens.
# Recall-oriented on purpose: label.py is the precision filter.

# Bugfix-intent in the commit subject/body (PCRE, case-insensitive).
BUGFIX_MSG_REGEX = r"\b(fix|fixes|fixed|bugfix|hotfix|bug|regression|broke|broken|crash|incorrect)\b"

# Error-handling + boundary tokens in the diff (PCRE). The spec's named
# signal: except/catch/retry/rollback/timeout/raise + boundary call names.
# No \b on code tokens that abut punctuation; kept conservative-but-broad.
ERROR_HANDLING_DIFF_REGEX = "|".join(
    [
        # error-handling constructs
        r"except\b",
        r"\braise\b",
        r"\btry:",
        r"\bfinally:",
        r"\.rollback\b",
        r"\bretry",
        r"\btimeout\b",
        r"\btraceback\b",
        r"contextlib\.suppress",
        r"\.(error|exception|warning)\(",
        # boundary call names (Python boundary catalog, §6)
        r"\brequests\.",
        r"\bhttpx\.",
        r"\burllib",
        r"\bsocket\.",
        r"\bsubprocess\b",
        r"os\.environ",
        r"os\.getenv",
        r"datetime\.now",
        r"\btime\.time\b",
        r"\brandom\.",
        r"\bpsycopg",
        r"\bsqlite3",
        r"sqlalchemy",
        r"\bboto3",
        r"(^|[^.\w])open\(",
    ]
)

# Restrict mining to the analysis-target language (Python) for this corpus.
PYTHON_PATHSPEC = "*.py"

MINER_VERSION = "0.1.0"

# --- finding-eval harness (H3 broad-market gate, docs/spec-eval-harness.md) ----
# The unit here is a pry *finding* (a welded-at-demand boundary), not a commit.
# finding_io.py emit/reconcile/freeze is the mechanical plumbing around a
# 3-persona coding-subagent panel (E2: no LLM in scripts). Outputs live under a
# dedicated eval/ subdir so they never collide with the Slice-0 commit labels.
EVAL_DIR = FIXTURES_DIR / "eval"

# Source context placed around each finding in the (blinded) worklist. Enough to
# judge the call site without revealing pry's verdict bit (E4 weak-blinding: the
# worklist hides class/demand/input_sim; kind + location are legitimate context).
FINDING_CONTEXT_LINES = 12       # source lines shown each side of the finding
FINDING_CONTEXT_CHAR_CAP = 4000  # max context chars per finding (mirrors LABEL cap)

# The three independent panel lenses (PQ2). Two keyed to the testability taxonomy
# (pragmatic, skeptic) + one NEUTRAL "can you inject a failure here?" lens whose
# rubric never names pry/weld/seam, to break rubric-circularity (E4).
FINDING_PERSONAS = ("pragmatic", "skeptic", "neutral")

# The 4-way label vocabulary, reused verbatim from precision-gate.md (E4).
FINDING_LABELS = ("GENUINE", "FALSE-WELD", "COSMETIC", "AMBIGUOUS")

# PQ3 pre-registered sampling: non-clock demand-welds are a full census (the
# high-value, smaller set); clock demand-welds are sampled (cosmetic-heavy, large).
# Deterministic stride sampling (no RNG) keeps the worklist byte-reproducible.
FINDING_CLOCK_SAMPLE_FRACTION = 0.25   # >=25% of clock demand-welds (PQ3)
# A control sample of pry-SEAMED findings, mixed in blind, so the panel can also
# catch pry's false-*seams* (the FALSE-WELD inverse), not only grade its positives
# (E4). Sampled deterministically from the demand-seamed pool.
FINDING_SEAMED_CONTROL_FRACTION = 0.20
FINDING_SEAMED_CONTROL_FLOOR = 10      # but at least this many when the pool allows

# --- filter-recall arm (Slice 2, E5/SC3/AC3) ----------------------------------
# Filter-recall asks the inverse of precision: did a precision filter DEMOTE a
# genuine weld? The denominator is pry's pre-demand pool, so the un-labeled part is
# the DEMOTED welded pool — class=welded, demand=false, in a filter-demotable kind
# (clock/random; NOT the fileio/env diagnostic swamp, which is demand=false by
# catalog and never demoted by a filter). Any GENUINE in this pool is a recall MISS.
# Clock is the large cosmetic pool (sampled heavier); random is a known-COSMETIC
# control (lever #1 demoted it; here it doubles as a consistency cross-check).
FINDING_DEMOTED_KINDS = ("clock", "random")
FINDING_DEMOTED_CLOCK_FRACTION = 0.22   # ~22% of the demoted-clock pool
FINDING_DEMOTED_RANDOM_FRACTION = 0.10  # small control on demoted random

FINDING_HARNESS_VERSION = "0.1.0"

# --- E9 multi-repo validation sweep (harness/fixtures/eval/preregistration.md) -
# Every constant below is PRE-REGISTERED: it is committed BEFORE any enrichment
# number is computed, so a fresh closeout reviewer can prove the order from git
# (`git merge-base --is-ancestor <prereg-sha> <enrichment-sha>`). This mirrors the
# Slice-0 REPO_FIT_SITE_FLOOR "set BEFORE the number so it cannot be moved post
# hoc" + the kill-gate F27 "frozen before this run" discipline.
CORPUS_PATH = EVAL_DIR / "corpus.json"
CORPUS_SCHEMA_PATH = HARNESS_DIR / "corpus_schema.json"
PREREGISTRATION_PATH = EVAL_DIR / "preregistration.md"
DISCOVERY_FEATURES_PATH = EVAL_DIR / "corpus_discovery_features.json"
CORPUS_PRUNE_LOG_PATH = EVAL_DIR / "corpus_prune_log.md"

# S1 corpus selection (risk R-A, selection bias): a candidate enters the corpus
# only if its app-shapedness score (harness/corpus_fit.py) clears this floor. Set
# here BEFORE any candidate was scored.
CORPUS_APP_SHAPEDNESS_FLOOR = 55

# Tier-1 enrichment metric (쟁점 4). Unit = a pry finding; the two arms are
# welded-at-demand (class=welded AND demand=true) vs seamed (class=seamed). A
# finding is "bugfix-touched" iff the commit that LAST modified its source line
# (git blame at the pinned commit) is in the repo's bugfix-commit set (the miner).
# Enrichment ratio = welded_at_demand_bugfix_touch_rate / seamed_bugfix_touch_rate.
#
# DENOMINATOR = a MATCHED comparison, not a raw pool: findings are stratified by
# (file-churn tercile x site-size tercile); the matched ratio is the
# stratum-count-weighted ratio of per-stratum welded vs seamed rates (direct
# standardization). This is the only form that neutralizes confound R-B (welded
# sites simply being more numerous / larger / in hotter files). The raw pooled
# ratio is reported ALONGSIDE so the confound's size stays visible.
ENRICHMENT_CHURN_TERCILES = 3       # file-churn strata (commits touching the file)
ENRICHMENT_SITESIZE_TERCILES = 3    # enclosing-function line-count strata
ENRICHMENT_MIN_STRATUM = 5          # min findings PER ARM to use a stratum;
                                    # under-filled strata are DROPPED + LOGGED
                                    # (no silent truncation, risk R-D)
# Bugfix-commit set = the enrichment NUMERATOR, PINNED here (critique #8) so it is
# frozen WITH the denominator, not left tunable in S2. A bugfix commit = a
# non-merge commit reachable from the pinned commit whose MESSAGE matches this
# intent regex (message-intent only; NO error-handling diff filter — enrichment is
# blame-based per source line, so any bugfix counts). Reuses the frozen Slice-0
# regex so the predicate is identical to the one already in the repo's history.
ENRICHMENT_BUGFIX_MSG_REGEX = BUGFIX_MSG_REGEX

# Two-sided floor (set blind, before measuring):
ENRICHMENT_GO_FLOOR = 1.5           # matched ratio >= this => signal real (GO)
ENRICHMENT_FALSIFIER = 1.1          # matched ratio <= this (or ~1.0) => thesis
                                    # FALSIFIED for this corpus. [1.1,1.5)=weak.
# Significance (critique #7): a cluster bootstrap OVER REPOS (resample the corpus's
# repos with replacement, recompute the matched ratio) — pinned before any number,
# deterministic seed. GO requires the point floor AND the CI lower bound strictly
# above 1.0; FALSIFIED if point <= falsifier OR the CI lower bound <= 1.0 (the
# "collapses to ~1.0" condition made testable rather than eyeballed).
ENRICHMENT_BOOTSTRAP_B = 2000
ENRICHMENT_BOOTSTRAP_CI = 0.95
ENRICHMENT_BOOTSTRAP_SEED = 0
ENRICHMENT_GO_CI_LOWER_MIN = 1.0
# Simpson's-paradox guard: a pooled GO must not be carried by one repo. Of repos
# with >= this many findings per arm, a majority must show per-repo ratio > 1.
ENRICHMENT_PERREPO_MIN_FINDINGS = 20
ENRICHMENT_PERREPO_MAJORITY = 0.60

# Python (b)-gate lens GO criterion (S5) = the kill-gate F27/Run-5 LENS band on
# the substitution-demand subset welded fraction (NOT the fs-swamped bare
# fraction). `pry map` already emits summary.substitution_demand_subset.
BGATE_LENS_BAND = (0.15, 0.85)      # demand-subset welded fraction in band => GO
BGATE_MIN_DECIDED_FRACTION = 0.40   # below this the lens is MUTE (KILL, not GO)

CORPUS_SWEEP_VERSION = "0.1.0"

# --- Step-1 coverage (testability) metric -------------------------------------
# After E9 Tier-1 FALSIFIED the bug-prediction thesis, this tests pry's remaining
# honest candidate thesis: welded-at-demand is a TESTABILITY signal — a welded
# boundary has no seam to inject a failure, so its code is harder to test, hence
# LESS tested. Same corpus, same frozen sweep records, same matched machinery;
# the outcome is "untested" (the finding's file has NO test association),
# oriented so wd-more-untested => ratio>1 (the SAME direction as E9), so the E9
# two-sided floor is reused by symmetry and no new free parameter is fit to this
# outcome. Contract: harness/fixtures/eval/preregistration-coverage.md.
COVERAGE_GO_FLOOR = ENRICHMENT_GO_FLOOR        # matched untested ratio >= => GO
COVERAGE_FALSIFIER = ENRICHMENT_FALSIFIER      # <= (or CI-lo<=1) => FALSIFIED
# Test-file detection (mirrors pry's is_source test-stem heuristics).
COVERAGE_CODE_EXT_REGEX = r"\.[cm]?[jt]sx?$"
COVERAGE_TEST_BASENAME_REGEX = r"\.(test|spec|e2e|vitest|cy)\.[cm]?[jt]sx?$"
COVERAGE_TEST_DIR_REGEX = r"(^|/)(__tests__|__mocks__|tests?|e2e|cypress|spec)/"
# Module-resolution extension order for the imported-by-test arm (TS/JS standard).
COVERAGE_RESOLVE_EXTS = [".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs"]
# Frontend heuristic for the backend-only robustness cut (the named E9 file-kind
# confound: welded fetch concentrates in less-unit-tested UI code).
COVERAGE_FRONTEND_REGEX = (
    r"\.(tsx|jsx)$|(^|/)(components|pages|app|ui|views|client|frontend)/"
)
COVERAGE_RESULT_PATH = EVAL_DIR / "coverage_result.json"

# --- Step-1b: static FAILURE-test detection (preregistration-step1b.md) --------
# The SHARP redo of Step-1. Step-1's file-level coverage proxy was FALSIFIED
# (0.95) but it only asked "is the welded boundary's FILE tested at all?". Step-1b
# asks the question the testability thesis actually makes: is the welded
# boundary's own FAILURE PATH simulated by a test? Failure-testing leaves STATIC
# fingerprints (module mock + failure simulation), so it is measurable offline /
# AC4-clean on the same frozen corpus (no test suites run, no LLM, no outbound).
# Every threshold here is PRE-REGISTERED (committed before any number; git-provable
# via merge-base). Contract: harness/fixtures/eval/preregistration-step1b.md.
#
# Unit = a pry finding of a FAILURE-CAPABLE kind (clock/random/env excluded: no
# failure worth injecting). Signal arm = welded-at-demand (wd); PRIMARY contrast
# control = "rest" (seamed | welded-not-demand) — "seamed"-only is too thin to
# matched-power on FC kinds (corpus n=138, 1 eligible repo), so it is a REPORTED
# underpowered secondary, exactly as preregistration-coverage.md did. Same reuse:
# coverage.py's import-by-test graph + matched/boot_ci/per_repo, keyed on the new
# `failure_untested` outcome; the E9/Step-1 floor (1.5/1.1) reused by symmetry.
# Same failure-capable set as the Floor (FLOOR_BOUNDARY_KINDS); a literal here
# because the Floor block is defined below this one. test_step1b asserts equality.
STEP1B_FAILURE_CAPABLE_KINDS = ("network", "subprocess", "db", "fileio")

# AMENDED 2026-06-16 (operator decision, still BEFORE any number): the VERDICT is
# the ABSOLUTE wd failure-TESTED rate, two-sided; NO comparison gates it. The
# welded-vs-rest contrast (below) is REPORTED CONTEXT (weld/demand-specificity
# caveat), not a pass/fail. This removes the demand-confound + the contrast-
# reachability problem the spec-critique surfaced. Prereg §0/§5/§6.
# Two-way ABSOLUTE-rate verdict thresholds on the wd failure-TESTED rate, each
# applied under the linkage that makes it CONSERVATIVE (POSITIVE uses the generous
# L-module count; OVERSTATED uses the strict L-import count) — see prereg §6.
STEP1B_TESTED_LOW = 0.20    # wd failure-tested <= this (L-module) => dense untested
                            # targets (POSITIVE: recommender wedge by yield)
STEP1B_TESTED_HIGH = 0.40   # wd failure-tested >= this (L-import) => failure-
                            # testing is COMMON => "welded=untestable" OVERSTATED

# REPORTED-CONTEXT contrast floor (NOT a gate): reuses the E9/Step-1 matched floor
# by symmetry to label whether the reported wd-vs-rest `failure_untested` contrast
# is weld/demand-specific (>=1.5) or flat (<=1.1). A flat contrast => POSITIVE's
# targets are real but not weld-differentiated (caveat, not a different verdict).
STEP1B_CONTRAST_GO = ENRICHMENT_GO_FLOOR    # 1.5: wd >=1.5x more failure-untested
STEP1B_CONTRAST_FLAT = ENRICHMENT_FALSIFIER  # 1.1: flat contrast (reported caveat)
# Base-rate ceiling (preregistration-coverage.md §5): failure-tests are rare =>
# high untested base rate => risk ratio compressed; the reported contrast is read
# with the odds ratio when max achievable ratio (1/rest_untested_rate) < 1.5.

# Honesty guards added by the spec-critique (preregistration-step1b.md §3/§4.2):
# (1) module extraction can leave a boundary UNRESOLVED -> conservatively untested
#     -> biases toward POSITIVE (the un-robust direction), so an UNRESOLVED share
#     above this in the wd arm makes the wd number UNCOMPUTABLE (never POSITIVE).
STEP1B_UNRESOLVED_ABORT = 0.30
# (2) failure-sim matcher is PERMISSIVE: a [BRACED] construct whose paren/brace-
#     balanced window (this many chars from the token) can't be parsed is counted
#     as failure-sim PRESENT -> detection gaps over-credit tested -> bias toward
#     OVERSTATED, away from POSITIVE (POSITIVE is robust to over-crediting).
STEP1B_BRACE_WINDOW = 600
STEP1B_RESULT_PATH = EVAL_DIR / "step1b_result.json"

# --- Floor experiment (the un-killed CLAIM channel) ---------------------------
# After both MAP prediction payoffs died (E9 bugs, Step-1 coverage), this tests
# the never-built FLOOR: a syntactic error-handling bug finder whose bar is
# precision-of-a-fact (Aspirator/Yuan lineage), NOT lift-over-churn. So the go/kill
# is a precision + repo-fit gate, not a ratio-vs-1.0 gate. Rules: FLOOR-1 (swallowed
# failure-capable boundary failure: try has a network/subprocess/db/fileio call,
# catch swallows) and FLOOR-2 (FLOOR-1 + control reaches a mutation/commit after =
# the severe subclass, the headline metric). Weld-AGNOSTIC. Separate `pry floor`
# output. Contract: docs/spec-floor.md / preregistration-floor.md.
FLOOR_BOUNDARY_KINDS = ("network", "subprocess", "db", "fileio")  # failure-capable
FLOOR_LABEL_TARGET = 40           # label up to this many FLOOR-2 flags (all if fewer)
                                  # + ~10 FLOOR-1-only for context; deterministic stride
FLOOR_SAMPLE_SEED = 0
# Two-sided go/kill on FLOOR-2 (set blind, before any flag is seen). The VOLUME
# gates (min-total + min-decided) close the cheap-GO hole a Wilson-LB alone left
# open (n=3 all-genuine would otherwise clear an LB>=0.40 bar — spec-critique F-A);
# so the binding gate is precision + min-decided-n + min-total + spread, and the
# Wilson interval is REPORTED descriptively, not used as a gate.
FLOOR_MIN_TOTAL_FLAGS = 25        # corpus-wide FLOOR-2 flags required for GO-eligibility
FLOOR_GO_PRECISION = 0.60         # FLOOR-2 precision >= this ...
FLOOR_GO_MIN_DECIDED = 20         # ... over >= this many DECIDED FLOOR-2 labels ...
FLOOR_GO_MIN_GENUINE = 3          # ... with >= this many GENUINE-MEANINGFUL ...
FLOOR_GO_MIN_REPOS = 2            # ... spanning >= this many repos => GO (build detector)
FLOOR_KILL_PRECISION = 0.40       # precision <= this (or <2 genuine) => KILL
FLOOR_WILSON_CI = 0.95            # reported alongside precision, NOT a gate
FLOOR_RESULT_PATH = EVAL_DIR / "floor_result.json"
FLOOR_LABELS_PATH = EVAL_DIR / "floor-labels.json"

# --- S2 sweep engine ----------------------------------------------------------
CORPUS_CLONE_DIR = Path(os.path.expanduser("~/codes/_pry-corpus"))  # local clones
SWEEP_DIR = EVAL_DIR / "sweep"                  # per-repo sweep records (frozen)
PRY_BIN = HARNESS_DIR.parent / "target" / "release" / "pry"

# TS/JS pathspec for the net-new miner (mine.py is Python-token-only). The
# enrichment NUMERATOR is message-intent ONLY (ENRICHMENT_BUGFIX_MSG_REGEX); this
# pathspec + the TS EH regex below feed only the secondary EH-candidate record.
TS_PATHSPEC = ["*.ts", "*.tsx", "*.js", "*.jsx", "*.mts", "*.cts", "*.mjs", "*.cjs"]

# JS/TS error-handling + boundary tokens (the EH-candidate diff signal). Mirrors
# the Python ERROR_HANDLING_DIFF_REGEX shape with JS idioms (handoff S2:
# catch/throw/.catch(/reject/retry/timeout + boundary names).
ERROR_HANDLING_DIFF_REGEX_TS = "|".join(
    [
        r"\bcatch\b", r"\bthrow\b", r"\.catch\(", r"\.reject\b", r"\breject\(",
        r"\bretry", r"\btimeout\b", r"\bfinally\b", r"AbortController",
        r"\bECONN", r"\bETIMEDOUT\b", r"\bENOENT\b", r"statusCode",
        # boundary call names (TS/JS boundary catalog)
        r"\bfetch\(", r"\baxios\b", r"\bhttp\.", r"\bhttps\.", r"\bfs\.",
        r"readFile", r"writeFile", r"\bexec\(", r"\bexecSync\b", r"\bspawn\(",
        r"Date\.now", r"new Date\(", r"Math\.random", r"process\.env",
        r"\bprisma\b", r"\bmongoose\b", r"\bknex\b", r"sequelize", r"\bpg\b",
        r"\bredis\b", r"\.query\(",
    ]
)

# Site-size proxy: the enclosing brace-block (TS/JS) or indent-block (Python)
# line span around a finding, used as a matched-denominator stratum. A coarse
# tercile bucket, so a brace/indent heuristic (string/comment edge cases ignored)
# is acceptable — documented in preregistration.md.
SWEEP_VERSION = "0.1.0"
