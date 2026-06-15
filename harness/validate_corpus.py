"""validate_corpus.py — validate the frozen E9 corpus (S1 deliverable).

Validates harness/fixtures/eval/corpus.json against corpus_schema.json (draft-07)
PLUS cross-field invariants the schema cannot express:
  * ids unique; names unique; commits are 40-hex (pinned, not a branch ref)
  * every repo's app_shapedness_passes is true (the floor was actually applied)
  * each arm (ts, python) has >= 1 dev AND >= 1 heldout repo, so the
    generalization split (쟁점 2) is actually testable per arm
  * the declared splits/counts match the repositories array

Exit 0 = valid; exit 1 = invalid (prints every violation).

Usage:
    python3 harness/validate_corpus.py
    python3 harness/validate_corpus.py --corpus <path> --schema <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

import config


def validate(corpus: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    v = jsonschema.Draft7Validator(schema)
    for e in sorted(v.iter_errors(corpus), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in e.path) or "<root>"
        errors.append(f"schema: {loc}: {e.message}")

    repos = corpus.get("repositories", [])
    ids = [r.get("id") for r in repos]
    names = [r.get("name") for r in repos]
    if len(set(ids)) != len(ids):
        errors.append(f"duplicate ids: {[i for i in ids if ids.count(i) > 1]}")
    if len(set(names)) != len(names):
        errors.append("duplicate repo names present")

    for r in repos:
        rid = r.get("id", "?")
        if not r.get("app_shapedness_passes", False):
            errors.append(f"{rid}: app_shapedness_passes is not true")
        c = r.get("commit", "")
        if not (isinstance(c, str) and len(c) == 40 and all(
                ch in "0123456789abcdef" for ch in c)):
            errors.append(f"{rid}: commit not a pinned 40-hex sha: {c!r}")

    for arm in ("ts", "python"):
        arm_repos = [r for r in repos if r.get("arm") == arm]
        if not arm_repos:
            continue  # an arm may be absent; only validate present arms
        splits = {s: sum(1 for r in arm_repos if r.get("split") == s)
                  for s in ("dev", "heldout")}
        if splits["dev"] < 1 or splits["heldout"] < 1:
            errors.append(f"arm {arm}: needs >=1 dev AND >=1 heldout; got {splits}")

    declared = corpus.get("splits", {})
    actual = {}
    for r in repos:
        actual[r.get("split")] = actual.get(r.get("split"), 0) + 1
    if declared != actual:
        errors.append(f"splits mismatch: declared {declared} != actual {actual}")

    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, default=config.CORPUS_PATH)
    ap.add_argument("--schema", type=Path, default=config.CORPUS_SCHEMA_PATH)
    args = ap.parse_args()

    for p in (args.corpus, args.schema):
        if not p.exists():
            sys.exit(f"missing: {p}")

    corpus = json.loads(args.corpus.read_text())
    schema = json.loads(args.schema.read_text())
    errors = validate(corpus, schema)

    if errors:
        print(f"INVALID — {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    repos = corpus["repositories"]
    print(f"VALID — {len(repos)} repos, splits={corpus.get('splits')}, "
          f"counts={corpus.get('counts')}")
    for arm in ("ts", "python"):
        ar = [r for r in repos if r["arm"] == arm]
        if ar:
            dev = sum(1 for r in ar if r["split"] == "dev")
            print(f"  {arm}: {len(ar)} repos (dev {dev} / heldout {len(ar)-dev})")


if __name__ == "__main__":
    main()
