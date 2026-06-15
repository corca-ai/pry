"""sweep.py — the deterministic per-repo sweep + join engine (E9 S2).

The nose `run_corpus.sh` analog, but byte-deterministic and zero-LLM (the
acceptance contract). Per repo: clone@pinned -> `pry map` -> mine bugfix commits
(mine_ts.py) -> JOIN each finding to the bugfix history via `git blame`, and
attach the matched-denominator covariates (file-churn + enclosing-site-size).

For each finding it records, under the PINNED pre-registration:
  * arm: "wd" (welded-at-demand: class=welded AND demand) | "rest" (every other
    decided boundary: seamed OR welded-not-demand) | None (ambiguous/undecided)
  * subarm: "seamed" | "wnd" (welded-not-demand) — for the secondary breakdowns
  * bugfix_touched: the commit that LAST modified this source line (git blame at
    the pinned commit) is in the repo's message-intent bugfix set
  * file_churn: commits touching the file up to the pinned commit
  * site_size: enclosing brace-block (TS/JS) line span (matched-denominator proxy)

No enrichment RATIO is computed here — that is S3. This slice only produces the
joined per-repo records. Re-running on the same pinned commit is byte-identical.

Usage:
    python3 harness/sweep.py --repo PATH --name NAME --commit SHA --split SPLIT
    python3 harness/sweep.py --corpus            # orchestrate the whole TS corpus
    python3 harness/sweep.py --corpus --only id1,id2   # subset
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import config
import mine_ts
from mine import _git

_SHA_LINE = re.compile(r"^([0-9a-f]{40}) \d+ (\d+)")


# --- site-size proxy ----------------------------------------------------------

def enclosing_block_size(text: str, lineno: int) -> int:
    """Line span of the innermost brace block enclosing `lineno` (1-indexed).

    A coarse tercile proxy (string/comment braces ignored, per preregistration.md);
    returns 1 when the line is at top level (no enclosing block found.)
    """
    pairs = []          # (open_line, close_line)
    stack = []          # open line numbers
    line = 1
    for ch in text:
        if ch == "\n":
            line += 1
        elif ch == "{":
            stack.append(line)
        elif ch == "}":
            if stack:
                pairs.append((stack.pop(), line))
    enclosing = [(o, c) for (o, c) in pairs if o <= lineno <= c]
    if not enclosing:
        return 1
    o, c = max(enclosing, key=lambda p: p[0])   # innermost = largest open line
    return c - o + 1


# --- git joins ----------------------------------------------------------------

def blame_line_commits(repo: Path, commit: str, relpath: str) -> dict[int, str]:
    """Map final-line-number -> last-modifying commit sha (blame at `commit`)."""
    try:
        out = _git(repo, ["blame", "--line-porcelain", commit, "--", relpath])
    except subprocess.CalledProcessError:
        return {}
    result: dict[int, str] = {}
    for ln in out.splitlines():
        m = _SHA_LINE.match(ln)
        if m:
            result[int(m.group(2))] = m.group(1)
    return result


def file_churn(repo: Path, commit: str, relpath: str) -> int:
    """Number of commits touching `relpath` up to (and including) `commit`."""
    try:
        out = _git(repo, ["log", commit, "--format=%H", "--", relpath])
    except subprocess.CalledProcessError:
        return 0
    return sum(1 for ln in out.splitlines() if ln.strip())


# --- arm assignment (the pinned pre-registration) -----------------------------

def arm_of(finding: dict) -> tuple[str | None, str | None]:
    cls = finding.get("class")
    demand = finding.get("demand")
    if cls == "welded" and demand:
        return "wd", None
    if cls == "seamed":
        return "rest", "seamed"
    if cls == "welded" and not demand:
        return "rest", "wnd"
    return None, None          # ambiguous / undecided


# --- per-repo sweep -----------------------------------------------------------

def pry_map(repo: Path) -> dict:
    out = subprocess.run([str(config.PRY_BIN), "map", str(repo)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"pry map failed on {repo}: {out.stderr[:200]}")
    return json.loads(out.stdout)


def sweep_repo(repo: Path, name: str, commit: str, split: str,
               bugfix_shas: set[str]) -> dict:
    mapped = pry_map(repo)
    findings = mapped["findings"]

    # group by file so blame / churn / read happen once per file
    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    joined = []
    counts = {"wd": 0, "rest": 0, "seamed": 0, "wnd": 0, "neither": 0,
              "wd_bugfix": 0, "rest_bugfix": 0, "seamed_bugfix": 0,
              "wnd_bugfix": 0}
    for relpath in sorted(by_file):
        fpath = repo / relpath
        try:
            text = fpath.read_text(errors="replace")
        except OSError:
            text = ""
        blame = blame_line_commits(repo, commit, relpath)
        churn = file_churn(repo, commit, relpath)
        for f in by_file[relpath]:
            arm, sub = arm_of(f)
            line = f["line"]
            touch_sha = blame.get(line)
            touched = bool(touch_sha and touch_sha in bugfix_shas)
            joined.append({
                "file": relpath, "line": line, "col": f.get("col"),
                "kind": f.get("kind"),
                "class": f.get("class"), "demand": f.get("demand"),
                "arm": arm, "subarm": sub, "bugfix_touched": touched,
                "file_churn": churn,
                "site_size": enclosing_block_size(text, line),
            })
            if arm is None:
                counts["neither"] += 1
            else:
                counts[arm] += 1
                if touched:
                    counts[arm + "_bugfix"] += 1
                if sub:
                    counts[sub] += 1
                    if touched:
                        counts[sub + "_bugfix"] += 1

    joined.sort(key=lambda r: (r["file"], r["line"], r["col"] or 0,
                               r["kind"] or "", r["class"] or ""))
    return {
        "corpus": name, "split": split, "pinned_commit": commit,
        "arm": "ts", "sweep_version": config.SWEEP_VERSION,
        "n_findings": len(findings),
        "n_bugfix_commits": len(bugfix_shas),
        "counts": counts,
        "findings": joined,
    }


# --- orchestration ------------------------------------------------------------

def ensure_clone(rid: str, url: str, commit: str) -> Path:
    dest = config.CORPUS_CLONE_DIR / rid
    if (dest / ".git").exists():
        # un-shallow: the seed clones were depth-1, which has no history for
        # blame/mining (file_churn would be 1 and the bugfix set ~empty).
        if (dest / ".git" / "shallow").exists():
            print(f"  un-shallowing {rid} ...", flush=True)
            subprocess.run(["git", "-C", str(dest), "fetch", "--unshallow", "-q"],
                           check=False)
        head = _git(dest, ["rev-parse", "HEAD"]).strip()
        if head != commit:
            subprocess.run(["git", "-C", str(dest), "fetch", "--all", "-q"],
                           check=False)
            subprocess.run(["git", "-C", str(dest), "checkout", "-q", commit],
                           check=True)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  cloning {url} ...", flush=True)
    subprocess.run(["git", "clone", "-q", url, str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "-q", commit], check=True)
    return dest


def sweep_one(rid: str, name: str, url: str, commit: str, split: str) -> dict:
    repo = ensure_clone(rid, url, commit)
    mined = mine_ts.mine(repo, name, commit)
    bugfix = set(mined["bugfix_shas"])
    rec = sweep_repo(repo, name, commit, split, bugfix)
    rec["id"] = rid
    rec["mine_counts"] = mined["counts"]
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path)
    ap.add_argument("--name")
    ap.add_argument("--commit")
    ap.add_argument("--split", default="dev")
    ap.add_argument("--corpus", action="store_true",
                    help="orchestrate all arm=ts repos from corpus.json")
    ap.add_argument("--only", default="", help="comma-separated ids subset")
    ap.add_argument("--force", action="store_true", help="re-sweep existing records")
    args = ap.parse_args()
    config.SWEEP_DIR.mkdir(parents=True, exist_ok=True)

    if args.corpus:
        corpus = json.loads(config.CORPUS_PATH.read_text())
        only = {x for x in args.only.split(",") if x}
        repos = [r for r in corpus["repositories"] if r["arm"] == "ts"
                 and (not only or r["id"] in only)]
        print(f"sweeping {len(repos)} ts repos -> {config.SWEEP_DIR}")
        for r in repos:
            out = config.SWEEP_DIR / f"{r['id']}.json"
            if out.exists() and not args.force:
                print(f"  skip {r['id']} (record exists)")
                continue
            try:
                rec = sweep_one(r["id"], r["name"], r["url"], r["commit"],
                                r["split"])
            except Exception as e:                       # noqa: BLE001
                print(f"  FAIL {r['id']}: {e}", file=sys.stderr)
                continue
            out.write_text(json.dumps(rec, indent=2) + "\n")
            c = rec["counts"]
            print(f"  OK {r['id']:<14} {r['split']:<8} findings={rec['n_findings']:>5} "
                  f"wd={c['wd']:>4} rest={c['rest']:>5} "
                  f"wd_bug={c['wd_bugfix']:>4} rest_bug={c['rest_bugfix']:>5}")
        return

    if not (args.repo and args.name and args.commit):
        sys.exit("need --repo/--name/--commit, or --corpus")
    mined = mine_ts.mine(args.repo, args.name, args.commit)
    rec = sweep_repo(args.repo, args.name, args.commit, args.split,
                     set(mined["bugfix_shas"]))
    out = config.SWEEP_DIR / f"{args.name.replace('/', '_')}.json"
    out.write_text(json.dumps(rec, indent=2) + "\n")
    c = rec["counts"]
    print(f"{args.name}: findings={rec['n_findings']} wd={c['wd']} rest={c['rest']} "
          f"wd_bugfix={c['wd_bugfix']} rest_bugfix={c['rest_bugfix']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
