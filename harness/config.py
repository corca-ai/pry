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

FINDING_HARNESS_VERSION = "0.1.0"
