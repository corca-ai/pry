"""szz.py — trace each confirmed fix to its bug-introducing commit + function.

Slice 0 of the pry validation harness (docs/spec-layer0.md, F9/F11/F14). For
every commit the labeler confirmed as an error-handling fix, find the lines the
fix changed, `git blame -w` (whitespace-ignoring, F14) the PRE-fix versions of
those lines to the commit(s) that last touched them (the SZZ heuristic), and
resolve the enclosing Python function at the bug-introducing commit via the
stdlib `ast` module (no tree-sitter — that is the analyzer's job; the corpus is
Python so the harness can use Python's own parser).

Output (frozen, F9): one bug *site* per (file, qualified_function) with its fix
and bug-introducing SHAs — the ground truth the kill-gate join (F11) reads. Join
key is file path + qualified function name resolved at the bug-introducing
commit, never a raw line number (which drifts).

Residual SZZ noise (cosmetic/rename hops) biases the eventual map hit-rate Z
*downward* (conservative, against the thesis) — see F14. `git blame -w` removes
the whitespace-only class cheaply; we do not add per-site confidence scoring
(deliberately out of scope, see spec Deliberately Not Doing).

Usage:
    python3 harness/szz.py                       # consume labels.json
    python3 harness/szz.py --probe <fix_sha>     # trace one commit, print sites
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import config

BUG_SITES_PATH = config.FIXTURES_DIR / "bug_sites.json"

_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")


def _git(repo: Path, args: list[str]) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          check=True, capture_output=True, text=True).stdout


def _changed_py_files(repo: Path, sha: str) -> list[str]:
    out = _git(repo, ["show", "--format=", "--name-only", sha, "--",
                      config.PYTHON_PATHSPEC])
    return sorted({l.strip() for l in out.splitlines()
                   if l.strip().endswith(".py")})


def _prefix_lines(repo: Path, sha: str, path: str) -> list[int]:
    """Pre-fix line numbers that the fix deleted/modified (the SZZ targets)."""
    diff = _git(repo, ["show", "-w", "--format=", "--unified=0", sha, "--", path])
    lines: list[int] = []
    old_ln = 0
    for raw in diff.splitlines():
        m = _HUNK.match(raw)
        if m:
            old_ln = int(m.group(1))
            continue
        if raw.startswith("-") and not raw.startswith("---"):
            lines.append(old_ln)
            old_ln += 1
        elif raw.startswith(" "):
            old_ln += 1
    return lines


def _blame_commit(repo: Path, fix_sha: str, path: str, line: int) -> str | None:
    """Bug-introducing commit: who last touched `line` *before* the fix."""
    try:
        out = _git(repo, ["blame", "-w", "-l", "-L", f"{line},{line}",
                          f"{fix_sha}~1", "--", path])
    except subprocess.CalledProcessError:
        return None
    return out.split(" ", 1)[0].lstrip("^") if out.strip() else None


def _qualified_function(repo: Path, sha: str, path: str, line: int) -> str:
    """Enclosing def/class.def at (sha, path, line) via stdlib ast, else '<module>'."""
    try:
        src = _git(repo, ["show", f"{sha}:{path}"])
        tree = ast.parse(src)
    except (subprocess.CalledProcessError, SyntaxError):
        return "<unparseable>"

    best: str | None = None
    best_span = None

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack: list[str] = []

        def _maybe(self, node, name):
            nonlocal best, best_span
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            if start <= line <= end:
                qual = ".".join(self.stack + [name])
                span = end - start
                if best_span is None or span < best_span:
                    best, best_span = qual, span

        def visit_FunctionDef(self, node):
            self._maybe(node, node.name)
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

    V().visit(tree)
    return best or "<module>"


def trace(repo: Path, fix_sha: str) -> list[dict]:
    """Resolve a fix commit to its (file, function, bug_sha) sites."""
    sites: dict[tuple, dict] = {}
    for path in _changed_py_files(repo, fix_sha):
        for line in _prefix_lines(repo, fix_sha, path):
            bug_sha = _blame_commit(repo, fix_sha, path, line)
            if not bug_sha:
                continue
            func = _qualified_function(repo, bug_sha, path, line)
            key = (path, func)  # F11 join key: file + qualified function
            site = sites.setdefault(key, {
                "file": path,
                "qualified_function": func,
                "fix_commit": fix_sha,
                "bug_commits": set(),
            })
            site["bug_commits"].add(bug_sha)
    # finalize (sets -> sorted lists for deterministic, JSON-able output)
    out = []
    for (path, func), s in sorted(sites.items()):
        out.append({**s, "bug_commits": sorted(s["bug_commits"])})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--labels", type=Path, default=config.LABELS_PATH)
    ap.add_argument("--out", type=Path, default=BUG_SITES_PATH)
    ap.add_argument("--repo", type=Path, default=config.DEFAULT_CORPUS_REPO)
    ap.add_argument("--probe", metavar="FIX_SHA",
                    help="trace a single commit and print sites (no labels needed)")
    args = ap.parse_args()

    if args.probe:
        for s in trace(args.repo, args.probe):
            print(f"  {s['file']}::{s['qualified_function']}  <- bug "
                  f"{','.join(c[:10] for c in s['bug_commits'])}")
        return

    if not args.labels.exists():
        sys.exit(f"{args.labels} not found — run label.py first")

    labels = json.loads(args.labels.read_text())
    fixes = sorted(sha for sha, v in labels["labels"].items()
                   if v["group"] == "candidate" and v["is_error_handling_fix"])
    print(f"tracing {len(fixes)} confirmed error-handling fixes...")

    all_sites = []
    for i, fix_sha in enumerate(fixes, 1):
        all_sites.extend(trace(args.repo, fix_sha))
        if i % 20 == 0 or i == len(fixes):
            print(f"  {i}/{len(fixes)} traced")

    # dedupe sites by (file, function); a function fixed by >1 commit is one site
    by_key: dict[tuple, dict] = {}
    for s in all_sites:
        k = (s["file"], s["qualified_function"])
        agg = by_key.setdefault(k, {**s, "fix_commits": set(), "bug_commits": set()})
        agg["fix_commits"].add(s["fix_commit"])
        agg["bug_commits"].update(s["bug_commits"])
    sites = []
    for (path, func), s in sorted(by_key.items()):
        sites.append({
            "file": path,
            "qualified_function": func,
            "fix_commits": sorted(s["fix_commits"]),
            "bug_commits": sorted(s["bug_commits"]),
        })

    args.out.write_text(json.dumps({
        "corpus": labels["corpus"],
        "corpus_head": labels["corpus_head"],
        "labeler_model": labels["labeler_model"],
        "site_count": len(sites),
        "sites": sites,
    }, indent=2, sort_keys=True) + "\n")
    print(f"\n{len(sites)} distinct (file, function) bug sites -> {args.out}")


if __name__ == "__main__":
    main()
