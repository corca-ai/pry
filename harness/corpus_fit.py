"""corpus_fit.py — the app-shapedness / domain scorer (S1 of the E9 sweep).

NEW scorer, NOT repo_fit.py. repo_fit.py is a *site-count* kill-gate (does this
ONE repo have enough SZZ bug sites to power a precision study?); this scores
*app-shapedness* for **corpus selection** — "is this repo an app (route handlers
/ service layer / DB clients / env+config) rather than a single-purpose
library?" — across MANY candidate repos. What is reused from repo_fit.py is the
*discipline*: a pure, unit-testable decision function plus a PRE-REGISTERED floor
set in config.py BEFORE any candidate is scored, so the slate cannot be moved
post hoc to manufacture a result (the kill-gate / F27 "frozen before the number"
pattern, applied to corpus selection — risk R-A, selection bias).

The score is computed from cheap, gh-API-derivable features (no clone): the
target-language byte ratio, top-level backend-directory signals, recent activity,
substance (stars/size), and app-vs-library keyword signals in topics/description.
A repo enters the corpus only if it clears config.CORPUS_APP_SHAPEDNESS_FLOOR.

The scorer is deliberately blind to anything downstream of the enrichment metric
(it never reads bugfix history, weld/seam counts, or injection rate) so selection
cannot peek at the result it is meant to test.

Usage:
    python3 harness/corpus_fit.py --features <features.json>   # score + verdict
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import config

# Top-level path tokens that signal an application backend (route handlers /
# service layer / DB clients / migrations / deploy), as opposed to a library's
# flat src/ + dist/. Matched case-insensitively against top-level entries.
APP_DIR_TOKENS = (
    "server", "backend", "api", "apps", "packages", "services", "src",
    "prisma", "migrations", "migration", "db", "database", "docker-compose.yml",
    "compose.yaml", "dockerfile", "alembic", "manage.py", "wsgi.py", "asgi.py",
)

# App-vs-library keyword signals in topics + description (lowercased substring).
# Curated to be DISTINCTIVE (low false-positive): greedy short tokens like "app",
# "service", "server" are excluded because they match inside unrelated words
# ("happen", "observability"); phrase tokens like "self-hosted" are safe.
APP_KEYWORDS = (
    "self-hosted", "selfhosted", "self hosted", "platform", "alternative to",
    "alternative-to", "cms", "headless", "dashboard", "saas", "automation",
    "monitoring", "e-commerce", "ecommerce", "crm", "workflow", "collaboration",
    "no-code", "low-code", "open-source platform",
)
# Library signals. "framework" is deliberately NOT here: many genuine app
# frameworks (payload, vendure) describe themselves that way, and a real library
# is only penalized when it ALSO lacks every app signal above.
LIBRARY_KEYWORDS = (
    "library", " sdk", "sdk ", "component library", "react hooks", "react hook",
    "ui kit", "ui-kit", "toolkit", "wrapper", "bindings",
    "client library", "parser library",
)


def _has_token(entries, tokens) -> int:
    """Count distinct backend-dir tokens present among top-level entries."""
    low = {e.lower() for e in entries}
    return sum(1 for t in tokens if any(t == e or t in e for e in low))


def _kw_hit(text: str, keywords) -> bool:
    t = (text or "").lower()
    return any(k in t for k in keywords)


def score(features: dict) -> dict:
    """Pure app-shapedness score (0-100) from gh-API features. No I/O.

    features keys:
      lang_ratio        : float, target-language bytes / total bytes
      top_level         : list[str], top-level repo entries (names)
      days_since_push   : int, days since last push (activity)
      stars             : int
      size_kb           : int, repo size reported by GitHub
      topics            : list[str]
      description       : str
    """
    lr = float(features.get("lang_ratio", 0.0))
    top = features.get("top_level", []) or []
    days = features.get("days_since_push")
    stars = int(features.get("stars", 0) or 0)
    size_kb = int(features.get("size_kb", 0) or 0)
    text = " ".join(features.get("topics", []) or []) + " " + (
        features.get("description") or "")

    points = {}
    # Dominant target language (a TS app whose code is mostly .ts; a Django app
    # mostly .py). A repo whose target language is a thin shell is the wrong arm.
    points["lang_ratio"] = 30 if lr >= 0.5 else (15 if lr >= 0.3 else 0)
    # Backend structure: the single strongest app-vs-library discriminator.
    ndirs = _has_token(top, APP_DIR_TOKENS)
    points["app_structure"] = 25 if ndirs >= 2 else (12 if ndirs == 1 else 0)
    # Active (mining needs a living bugfix history).
    points["activity"] = (
        20 if (days is not None and days <= 365)
        else (8 if (days is not None and days <= 730) else 0))
    # Substantial (proxy for substantial bugfix history; the real mine floor is
    # checked downstream in S2/S3, this is only a selection proxy).
    points["substance"] = (
        15 if (stars >= 1000 or size_kb >= 3000)
        else (7 if stars >= 300 else 0))
    # App keyword signal.
    points["app_keyword"] = 10 if _kw_hit(text, APP_KEYWORDS) else 0
    # Library penalty: a pure-library signal with no app signal.
    lib = _kw_hit(text, LIBRARY_KEYWORDS) and not _kw_hit(text, APP_KEYWORDS)
    points["library_penalty"] = -20 if lib else 0

    total = sum(points.values())
    floor = config.CORPUS_APP_SHAPEDNESS_FLOOR
    return {
        "app_shapedness_score": total,
        "floor": floor,
        "passes": total >= floor,
        "components": points,
        "backend_dir_tokens": ndirs,
        "library_flagged": lib,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features", type=Path, required=True,
                    help="JSON: {id: features} or a single features object")
    args = ap.parse_args()
    data = json.loads(args.features.read_text())
    if "lang_ratio" in data:  # single object
        data = {data.get("id", "repo"): data}
    print(f"{'id':<16} {'score':>5} {'floor':>5}  pass  components")
    fails = 0
    for rid, feats in sorted(data.items()):
        r = score(feats)
        if not r["passes"]:
            fails += 1
        print(f"{rid:<16} {r['app_shapedness_score']:>5} {r['floor']:>5}  "
              f"{'YES' if r['passes'] else 'no ':>4}  {r['components']}")
    if fails:
        print(f"\n{fails} candidate(s) below floor {config.CORPUS_APP_SHAPEDNESS_FLOOR}")
        sys.exit(2)


if __name__ == "__main__":
    main()
