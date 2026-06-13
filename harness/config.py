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
