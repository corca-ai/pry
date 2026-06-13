"""mine.py — git-mine the corpus for error-handling bugfix candidates.

Slice 0 of the pry validation harness (docs/spec-layer0.md). Analyzer-free:
this runs on git history alone and produces the candidate set the LLM labeler
(label.py) will then filter for precision.

A *candidate error-handling bugfix commit* = a commit whose message shows
bugfix intent AND whose Python diff touches error-handling / boundary tokens
(config.ERROR_HANDLING_DIFF_REGEX). The mining is recall-oriented; label.py is
the precision filter.

Also emits `non_matched_bugfix`: bugfix-intent commits that touch Python but do
NOT match the error-handling diff signal. This is the population P1b
(mining-recall sanity) samples from — to estimate error-handling fixes the
lexical miner missed (the §13 A.2 "wrong bug profile" guard).

Output is deterministic given the corpus HEAD: commits are sorted by
(date, sha), and the frozen corpus SHA is recorded so downstream scoring is
reproducible (F9).

Usage:
    python3 harness/mine.py [--repo PATH] [--name NAME] [--out PATH]
    python3 harness/mine.py --summary   # print counts only, no write
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import config

_SEP = "\x01"  # field separator unlikely to appear in subjects
_REC = "\x02"  # record marker for name-only parsing


def _git(repo: Path, args: list[str]) -> str:
    """Run a git command in `repo`, returning stdout (raises on failure)."""
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def _supports_perl_regex(repo: Path) -> bool:
    """Probe whether this git build accepts -P (PCRE). Falls back to ERE."""
    try:
        subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "-P", "--grep", "x", "--format=%H"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _shas_by_message(repo: Path, regex: str, perl: bool) -> set[str]:
    """Commits whose message matches `regex` (bugfix intent), touching *.py."""
    flags = ["-i", "--no-merges", "--format=%H"]
    flags += ["-P"] if perl else ["-E"]
    out = _git(repo, ["log", *flags, f"--grep={regex}", "--", config.PYTHON_PATHSPEC])
    return {line.strip() for line in out.splitlines() if line.strip()}


def _shas_by_diff(repo: Path, regex: str, perl: bool) -> set[str]:
    """Commits whose *.py diff adds/removes lines matching `regex`."""
    flags = ["--no-merges", "--format=%H", f"-G{regex}"]
    flags += ["-P"] if perl else ["-E"]
    out = _git(repo, ["log", *flags, "--", config.PYTHON_PATHSPEC])
    return {line.strip() for line in out.splitlines() if line.strip()}


def _commit_meta(repo: Path) -> dict[str, dict]:
    """Map sha -> {date, subject} for every *.py-touching non-merge commit."""
    fmt = f"%H{_SEP}%cI{_SEP}%s"
    out = _git(
        repo,
        ["log", "--no-merges", f"--format={fmt}", "--", config.PYTHON_PATHSPEC],
    )
    meta: dict[str, dict] = {}
    for line in out.splitlines():
        if _SEP not in line:
            continue
        sha, date, subject = line.split(_SEP, 2)
        meta[sha] = {"date": date, "subject": subject}
    return meta


def _commit_py_files(repo: Path) -> dict[str, list[str]]:
    """Map sha -> sorted list of *.py files it changed."""
    fmt = f"{_REC}%H"
    out = _git(
        repo,
        [
            "log",
            "--no-merges",
            "--name-only",
            f"--format={fmt}",
            "--",
            config.PYTHON_PATHSPEC,
        ],
    )
    files: dict[str, list[str]] = {}
    cur: str | None = None
    for line in out.splitlines():
        if line.startswith(_REC):
            cur = line[len(_REC):].strip()
            files[cur] = []
        elif cur and line.strip() and line.endswith(".py"):
            files[cur].append(line.strip())
    return {sha: sorted(set(fs)) for sha, fs in files.items()}


def mine(repo: Path, name: str) -> dict:
    if not (repo / ".git").exists():
        sys.exit(f"error: {repo} is not a git repository")

    head = _git(repo, ["rev-parse", "HEAD"]).strip()
    perl = _supports_perl_regex(repo)

    meta = _commit_meta(repo)
    bugfix = _shas_by_message(repo, config.BUGFIX_MSG_REGEX, perl) & meta.keys()
    eh_diff = _shas_by_diff(repo, config.ERROR_HANDLING_DIFF_REGEX, perl) & meta.keys()

    candidate_shas = bugfix & eh_diff
    non_matched_shas = bugfix - eh_diff

    files = _commit_py_files(repo)

    def _sort_key(sha: str) -> tuple[str, str]:
        return (meta[sha]["date"], sha)

    candidates = [
        {
            "sha": sha,
            "date": meta[sha]["date"],
            "subject": meta[sha]["subject"],
            "py_files": files.get(sha, []),
        }
        for sha in sorted(candidate_shas, key=_sort_key)
    ]
    non_matched = [
        {
            "sha": sha,
            "date": meta[sha]["date"],
            "subject": meta[sha]["subject"],
        }
        for sha in sorted(non_matched_shas, key=_sort_key)
    ]

    return {
        "corpus": name,
        "corpus_repo": str(repo),
        "corpus_head": head,
        "miner_version": config.MINER_VERSION,
        "regex_engine": "pcre" if perl else "ere",
        "heuristics": {
            "bugfix_msg_regex": config.BUGFIX_MSG_REGEX,
            "error_handling_diff_regex": config.ERROR_HANDLING_DIFF_REGEX,
            "pathspec": config.PYTHON_PATHSPEC,
        },
        "counts": {
            "py_commits": len(meta),
            "bugfix_commits": len(bugfix),
            "error_handling_diff_commits": len(eh_diff),
            "candidates": len(candidates),
            "non_matched_bugfix": len(non_matched),
        },
        "candidates": candidates,
        "non_matched_bugfix": non_matched,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=config.DEFAULT_CORPUS_REPO)
    ap.add_argument("--name", default=config.DEFAULT_CORPUS_NAME)
    ap.add_argument("--out", type=Path, default=config.CANDIDATES_PATH)
    ap.add_argument("--summary", action="store_true", help="print counts, do not write")
    args = ap.parse_args()

    result = mine(args.repo, args.name)
    counts = result["counts"]

    print(f"corpus: {result['corpus']} @ {result['corpus_head'][:12]}")
    print(f"regex engine: {result['regex_engine']}")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    if args.summary:
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {counts['candidates']} candidates + "
          f"{counts['non_matched_bugfix']} non-matched bugfix commits -> {args.out}")


if __name__ == "__main__":
    main()
