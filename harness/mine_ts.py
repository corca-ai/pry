"""mine_ts.py — net-new TS/JS bugfix-commit miner for the E9 sweep (S2).

mine.py is Python-token-only; this is its TS/JS sibling. It produces the
enrichment NUMERATOR — the **bugfix-commit set** — under the predicate PINNED in
preregistration.md / config.ENRICHMENT_BUGFIX_MSG_REGEX:

  a bugfix commit = a non-merge commit REACHABLE FROM THE PINNED COMMIT whose
  MESSAGE matches the intent regex (message-intent only — no diff filter).

It ALSO emits a secondary EH-candidate subset (message AND a JS/TS error-handling
diff signal, config.ERROR_HANDLING_DIFF_REGEX_TS) for the record — parallel to
mine.py's `candidates` — but that subset is NOT the enrichment numerator.

Determinism (reusing mine.py's discipline): commits sorted, the pinned commit is
the rev (not a moving branch), output is sorted/stable. Re-running on the same
pinned commit yields byte-identical output.

Usage:
    python3 harness/mine_ts.py --repo PATH --name NAME --commit SHA [--out PATH]
    python3 harness/mine_ts.py --repo PATH --name NAME --commit SHA --summary
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import config
from mine import _git, _supports_perl_regex  # reuse the determinism helpers


def _shas_by_message(repo: Path, rev: str, regex: str, perl: bool) -> set[str]:
    """Non-merge commits reachable from `rev` whose MESSAGE matches `regex`.

    No pathspec restriction — the pinned predicate is message-intent only; the
    blame join (sweep.py) intersects with the mapped TS/JS source lines.
    """
    flags = ["-i", "--no-merges", "--format=%H"]
    flags += ["-P"] if perl else ["-E"]
    out = _git(repo, ["log", rev, *flags, f"--grep={regex}"])
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


def _shas_total(repo: Path, rev: str) -> int:
    out = _git(repo, ["log", rev, "--no-merges", "--format=%H"])
    return sum(1 for ln in out.splitlines() if ln.strip())


def _shas_by_diff_ts(repo: Path, rev: str, regex: str, perl: bool) -> set[str]:
    """Commits reachable from `rev` whose TS/JS diff matches the EH regex."""
    flags = ["--no-merges", "--format=%H", f"-G{regex}"]
    flags += ["-P"] if perl else ["-E"]
    out = _git(repo, ["log", rev, *flags, "--", *config.TS_PATHSPEC])
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


def mine(repo: Path, name: str, commit: str) -> dict:
    if not (repo / ".git").exists():
        sys.exit(f"error: {repo} is not a git repository")
    perl = _supports_perl_regex(repo)

    bugfix = _shas_by_message(repo, commit, config.ENRICHMENT_BUGFIX_MSG_REGEX, perl)
    eh = _shas_by_diff_ts(repo, commit, config.ERROR_HANDLING_DIFF_REGEX_TS, perl)
    eh_candidates = bugfix & eh
    total = _shas_total(repo, commit)

    return {
        "corpus": name,
        "corpus_repo": str(repo),
        "pinned_commit": commit,
        "miner_version": config.SWEEP_VERSION,
        "regex_engine": "pcre" if perl else "ere",
        "heuristics": {
            "bugfix_msg_regex": config.ENRICHMENT_BUGFIX_MSG_REGEX,
            "eh_diff_regex_ts": config.ERROR_HANDLING_DIFF_REGEX_TS,
            "pathspec": config.TS_PATHSPEC,
            "numerator": "message-intent only (eh subset is secondary record)",
        },
        "counts": {
            "commits_from_pinned": total,
            "bugfix_commits": len(bugfix),
            "eh_candidate_commits": len(eh_candidates),
        },
        # The numerator set the join consumes:
        "bugfix_shas": sorted(bugfix),
        # Secondary record (not the numerator):
        "eh_candidate_shas": sorted(eh_candidates),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--commit", required=True, help="the pinned commit (rev)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    result = mine(args.repo, args.name, args.commit)
    c = result["counts"]
    print(f"{result['corpus']} @ {args.commit[:12]} ({result['regex_engine']}): "
          f"commits={c['commits_from_pinned']} bugfix={c['bugfix_commits']} "
          f"eh_candidates={c['eh_candidate_commits']}")
    if args.summary:
        return
    out = args.out or (config.SWEEP_DIR / f"{args.name}.minets.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
