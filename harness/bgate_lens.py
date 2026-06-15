"""bgate_lens.py — analyzer-free Python (b)-gate lens (E9 S5).

Runs the kill-gate F27/Run-5 LENS criterion on the corpus's Python apps WITHOUT a
Rust frontend (the frontend is built ONLY on a GO, and only after S3+S4 record a
verdict — the sequencing gate). It classifies substitution-demand boundary call
sites (clock / clients-network / subprocess) as welded vs seamed by a
deterministic `ast` heuristic, then computes the demand-subset welded-fraction +
decided-fraction.

  GO   = welded-fraction in config.BGATE_LENS_BAND ([0.15,0.85]) AND
         decided-fraction >= config.BGATE_MIN_DECIDED_FRACTION (0.40).
  KILL = out of band, OR mute (decided < floor) -> NO frontend is built.

Heuristic (documented, analyzer-free — this is NOT the shipped analyzer):
  * WELDED: a boundary reached through a directly-imported module
    (`requests.get`, `datetime.now()`, `subprocess.run`, `os.system`) — no seam.
  * SEAMED: a boundary reached through an INJECTED receiver — a function
    parameter, or a `self.<attr>` whose attr was assigned from an __init__
    parameter — when the receiver/attr name is client-ish (a lexicon). This is the
    seam-counting mechanism that keeps the demand-subset welded-fraction from
    saturating at ~1.0 (the kill-gate's "fs-swamped" lesson).
  * UNDECIDED: client-ish method calls on local variables (possible
    welded-construction) we cannot classify cheaply -> lowers decided-fraction.

The hand/script-sample discipline of kill-gate Runs 1-5: a sample of classified
sites is emitted for spot hand-validation. No LLM, no network at classify time.

Usage:
    python3 harness/bgate_lens.py --repo PATH --name NAME
    python3 harness/bgate_lens.py --corpus     # all arm=python repos in corpus.json
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

import config

# Module-direct boundary calls (the WELDED side of the demand subset).
CLOCK_MOD = {"datetime": {"now", "utcnow", "today"}, "date": {"today"},
             "time": {"time", "monotonic", "perf_counter", "time_ns"}}
NET_MODS = {"requests", "httpx", "urllib", "socket", "aiohttp", "boto3",
            "psycopg2", "psycopg", "redis", "pymongo", "smtplib", "ftplib",
            "paramiko", "http", "urllib3"}
SUBPROC = {"subprocess": {"run", "call", "Popen", "check_output", "check_call",
                          "getoutput", "getstatusoutput"},
           "os": {"system", "popen", "execv", "execvp", "execve", "spawnv"}}

# UNAMBIGUOUS boundary VERBS: a method call is only a demand-subset boundary
# candidate if its method name is one of these. This replaces the earlier
# CLIENT_LEX substring heuristic, which was far too noisy (it matched `dict.get`,
# `list.append`, `request.session.pop`, Django `signal.connect` via greedy
# substrings like "es"/"session"), inflating "undecided" into an ARTIFACTUAL mute.
# Verbs chosen so the call is almost certainly a real network/db/subprocess I/O.
BOUNDARY_VERBS = {"execute", "executemany", "fetchone", "fetchall", "fetchmany",
                  "cursor", "request", "urlopen", "sendmail", "check_output",
                  "check_call", "popen", "hget", "hset", "hgetall", "scan",
                  "get_object", "put_object", "download_file", "upload_file",
                  "send_email", "query"}
# Receiver roots that are module-level globals / framework singletons -> welded
# (no injectable seam in scope), distinct from a constructed/injected receiver.
GLOBAL_RECEIVERS = {"connection", "connections", "op", "engine", "db"}

SKIP_DIR_TOKENS = ("test", "tests", "migration", "migrations", "vendor",
                   "node_modules", "__pycache__", ".venv", "site-packages",
                   "fixtures", "examples", "docs", "scripts")


def _dotted(func: ast.AST) -> list[str]:
    parts = []
    cur = func
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    parts.reverse()
    return parts


def _module_boundary_kind(parts: list[str]) -> str | None:
    """Classify a module-direct boundary call (welded side). None if not one."""
    if not parts:
        return None
    root, attr = parts[0], (parts[1] if len(parts) > 1 else "")
    last = parts[-1]
    if root in CLOCK_MOD and last in CLOCK_MOD[root]:
        return "clock"
    if root == "datetime" and last in {"now", "utcnow", "today"}:
        return "clock"
    if root in NET_MODS:
        return "network"
    if root in SUBPROC and (attr in SUBPROC[root] or last in SUBPROC[root]):
        return "subprocess"
    return None


def _receiver_kind(parts: list[str]) -> str:
    """Heuristic boundary kind for an injected receiver, from its name."""
    name = parts[0] if parts else ""
    attr = parts[1] if len(parts) > 1 else ""
    for tok in (name, attr):
        if any(c in tok.lower() for c in ("redis", "cache")):
            return "network"
        if any(c in tok.lower() for c in ("conn", "db", "cursor", "pool",
                                          "engine", "session", "repo", "store")):
            return "network"
        if any(c in tok.lower() for c in ("client", "http", "s3", "bucket",
                                          "gateway", "api", "queue", "channel",
                                          "socket", "ftp", "smtp", "mail")):
            return "network"
        if any(c in tok.lower() for c in ("exec", "runner", "subproc")):
            return "subprocess"
    return "network"


def _injected_attrs(cls: ast.ClassDef) -> set[str]:
    """self.X attrs assigned from an __init__ parameter (injected deps)."""
    out = set()
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            params = {a.arg for a in node.args.args}
            for n in ast.walk(node):
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Name) \
                        and n.value.id in params:
                    for t in n.targets:
                        if isinstance(t, ast.Attribute) and \
                                isinstance(t.value, ast.Name) and t.value.id == "self":
                            out.add(t.attr)
    return out


def classify_file(text: str) -> list[dict]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    # map each function to its param names + enclosing-class injected attrs
    parents: dict[int, set] = {}
    class_inj: dict[int, set] = {}

    def visit(node, params: set, injected: set):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                inj = _injected_attrs(child)
                visit(child, params, inj)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                p = {a.arg for a in child.args.args}
                visit(child, p, injected)
            elif isinstance(child, ast.Call):
                parents[id(child)] = (params, injected)
                visit(child, params, injected)
            else:
                visit(child, params, injected)

    visit(tree, set(), set())

    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        parts = _dotted(node.func)
        if not parts:
            continue
        params, injected = parents.get(id(node), (set(), set()))
        kind = _module_boundary_kind(parts)
        if kind:
            found.append({"line": node.lineno, "kind": kind,
                          "class": "welded", "expr": ".".join(parts)})
            continue
        # A method call is a demand-subset boundary candidate ONLY if its method
        # name is an unambiguous boundary VERB (so dict.get / list.append /
        # signal.connect are excluded — the noise that caused the false mute).
        if len(parts) < 2 or parts[-1] not in BOUNDARY_VERBS:
            continue
        root = parts[0]
        bkind = _receiver_kind(parts)
        if root in params and root != "self":
            cls = "seamed"            # injected via a parameter -> a real seam
        elif root == "self" and parts[1] in injected:
            cls = "seamed"            # injected via __init__ -> a real seam
        elif root in GLOBAL_RECEIVERS:
            cls = "welded"            # module/framework global -> no seam in scope
        else:
            cls = "undecided"         # local var: welded-construction vs injected
        found.append({"line": node.lineno, "kind": bkind, "class": cls,
                      "expr": ".".join(parts)})
    return found


def _is_source(p: Path) -> bool:
    low = str(p).lower()
    return not any(f"/{t}/" in low or low.endswith(f"/{t}") for t in SKIP_DIR_TOKENS) \
        and not p.name.startswith("test_") and not p.name.endswith("_test.py")


def lens_repo(repo: Path, name: str) -> dict:
    welded = seamed = undecided = 0
    by_kind: dict[str, dict] = {}
    sample = []
    for py in sorted(repo.rglob("*.py")):
        if not _is_source(py):
            continue
        try:
            text = py.read_text(errors="replace")
        except OSError:
            continue
        for f in classify_file(text):
            k = f["kind"]
            bk = by_kind.setdefault(k, {"welded": 0, "seamed": 0, "undecided": 0})
            bk[f["class"]] += 1
            if f["class"] == "welded":
                welded += 1
            elif f["class"] == "seamed":
                seamed += 1
            else:
                undecided += 1
            if len(sample) < 40:
                sample.append({"file": str(py.relative_to(repo)), **f})
    decided = welded + seamed
    total = decided + undecided
    wf = (welded / decided) if decided else None
    df = (decided / total) if total else None
    band = config.BGATE_LENS_BAND
    if df is not None and df < config.BGATE_MIN_DECIDED_FRACTION:
        verdict = "KILL (mute)"
    elif wf is None:
        verdict = "KILL (no decided sites)"
    elif band[0] <= wf <= band[1]:
        verdict = "GO (in band)"
    else:
        verdict = f"KILL (out of band {'high' if wf > band[1] else 'low'})"
    return {
        "corpus": name, "welded": welded, "seamed": seamed,
        "undecided": undecided, "decided": decided, "total": total,
        "welded_fraction": wf, "decided_fraction": df,
        "band": list(band), "min_decided": config.BGATE_MIN_DECIDED_FRACTION,
        "by_kind": by_kind, "verdict": verdict, "sample": sample,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path)
    ap.add_argument("--name")
    ap.add_argument("--corpus", action="store_true")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    if args.corpus:
        corpus = json.loads(config.CORPUS_PATH.read_text())
        pyrepos = [r for r in corpus["repositories"] if r["arm"] == "python"]
        results = []
        for r in pyrepos:
            dest = config.CORPUS_CLONE_DIR / r["id"]
            if not (dest / ".git").exists():
                print(f"  cloning {r['url']} ...", flush=True)
                subprocess.run(["git", "clone", "-q", "--depth", "1", r["url"],
                                str(dest)], check=True)
                # depth-1 is fine: the lens only reads source at the pinned tree,
                # no history needed (unlike the enrichment mine/blame).
                subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--depth",
                                "1", "origin", r["commit"]], check=False)
                subprocess.run(["git", "-C", str(dest), "checkout", "-q",
                                r["commit"]], check=False)
            res = lens_repo(dest, r["name"])
            res["id"] = r["id"]
            res["split"] = r["split"]
            results.append(res)
            print(f"  {r['id']:<16} welded={res['welded']:>4} seamed={res['seamed']:>4} "
                  f"undec={res['undecided']:>4} wf={_f(res['welded_fraction'])} "
                  f"df={_f(res['decided_fraction'])} -> {res['verdict']}")
        # pooled lens
        W = sum(r["welded"] for r in results)
        S = sum(r["seamed"] for r in results)
        U = sum(r["undecided"] for r in results)
        dec = W + S
        wf = W / dec if dec else None
        df = dec / (dec + U) if (dec + U) else None
        band = config.BGATE_LENS_BAND
        pooled_verdict = ("KILL (mute)" if (df is not None and df < config.BGATE_MIN_DECIDED_FRACTION)
                          else "GO (in band)" if (wf is not None and band[0] <= wf <= band[1])
                          else f"KILL (out of band)")
        out = {"per_repo": results,
               "pooled": {"welded": W, "seamed": S, "undecided": U,
                          "welded_fraction": wf, "decided_fraction": df,
                          "band": list(band), "verdict": pooled_verdict}}
        dest = args.out or (config.EVAL_DIR / "bgate_lens_result.json")
        dest.write_text(json.dumps(out, indent=2) + "\n")
        print(f"\nPOOLED: welded={W} seamed={S} undecided={U} "
              f"wf={_f(wf)} df={_f(df)} -> {pooled_verdict}")
        print(f"wrote {dest}")
        return

    if not (args.repo and args.name):
        sys.exit("need --repo/--name or --corpus")
    res = lens_repo(args.repo, args.name)
    print(json.dumps({k: v for k, v in res.items() if k != "sample"}, indent=2))


def _f(x):
    return f"{x:.3f}" if isinstance(x, (int, float)) else "n/a"


if __name__ == "__main__":
    main()
