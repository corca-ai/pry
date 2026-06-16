"""floor_worklist.py — build the labeling worklist for the floor go/kill.

Runs `pry floor` on the 25 TS/JS clones (offline), collects ALL FLOOR-2 flags +
a deterministic stride sample of FLOOR-1, and emits a self-contained worklist with
embedded source context + a `catch_empty` bit (eslint `no-empty` catches ONLY
empty catches, so non-empty = the linter-survival/differentiation signal). The
panel labels this worklist; nothing here computes a verdict.

Usage: python3 harness/floor_worklist.py
"""

from __future__ import annotations

import json
import subprocess

import config
import enrichment

CTX_BEFORE = 4
CTX_AFTER = 3


def run_floor(repo) -> list[dict]:
    out = subprocess.run([str(config.PRY_BIN), "floor", str(repo)],
                         capture_output=True, text=True)
    out.check_returncode()
    return json.loads(out.stdout)["findings"]


def context(repo, file, line, catch_line, commit_line) -> str:
    path = repo / file
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return "(unreadable)"
    hi = max(line, catch_line, commit_line or 0)
    lo = max(0, line - 1 - CTX_BEFORE)
    end = min(len(lines), hi + CTX_AFTER)
    numbered = [f"{n+1:>5}| {lines[n]}" for n in range(lo, end)]
    return "\n".join(numbered)


def main() -> None:
    recs = enrichment.load_records()
    floor2, floor1 = [], []
    for rid in sorted(recs):
        repo = config.CORPUS_CLONE_DIR / rid
        for f in run_floor(repo):
            ctx = context(repo, f["file"], f["line"], f["catch_line"],
                          f.get("commit_line"))
            entry = {
                "id": f"{rid}:{f['file']}:{f['line']}",
                "repo": rid, "file": f["file"], "line": f["line"], "col": f["col"],
                "rule": f["rule"], "kind": f["kind"],
                "catch_line": f["catch_line"], "commit_line": f.get("commit_line"),
                "catch_empty": f["catch_empty"], "context": ctx,
            }
            (floor2 if f["rule"] == "FLOOR-2" else floor1).append(entry)

    # ALL FLOOR-2 (<= label target), + deterministic stride sample of FLOOR-1
    n_f1 = min(len(floor1), 10)
    stride = max(1, len(floor1) // n_f1) if n_f1 else 1
    f1_sample = floor1[::stride][:n_f1]
    worklist = floor2 + f1_sample
    dest = config.EVAL_DIR / "floor-worklist.json"
    dest.write_text(json.dumps({
        "n_floor2_total": len(floor2), "n_floor1_total": len(floor1),
        "labeled": {"floor2": len(floor2), "floor1": len(f1_sample)},
        "items": worklist,
    }, indent=2) + "\n")
    print(f"FLOOR-2 total={len(floor2)} (all labeled), FLOOR-1 total={len(floor1)} "
          f"(sampled {len(f1_sample)})")
    print(f"FLOOR-2 catch_empty: {sum(e['catch_empty'] for e in floor2)}/{len(floor2)} "
          f"(empty = eslint no-empty WOULD catch; non-empty = linter passes)")
    print(f"wrote {dest} ({len(worklist)} items)")


if __name__ == "__main__":
    main()
