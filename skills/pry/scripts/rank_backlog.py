#!/usr/bin/env python3
"""Rank pry's welded-at-demand testability backlog — the F15 intelligence consumer.

The pry CLI is deterministic and dumb (spec F1): `pry map <path>` emits every
boundary finding classified seamed / welded / ambiguous, with a
substitution-demand flag and the classifier's cosmetic/duration filters already
applied. This script is the thin plumbing the `pry` agent skill defers to: it
resolves the binary (PRY_BIN override first, the nose-model maintainer override),
runs `pry map`, and projects the *welded-at-demand* subset — the actionable
testability backlog — into a ranked advisory report.

It adds NO intelligence beyond projection + a documented sort: labeling each
finding GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS is the agent's job (see the
sibling SKILL.md and docs/precision-gate.md). The output is a risk ranking, not
a bug list.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PRY_TIMEOUT_SECONDS = 300

# Kind order = descending typical genuine-gap precision from a full census
# (docs/precision-gate.md): subprocess 88% / llm 100% lead; network 58% /
# slack 67% mid; clock / random are the cosmetic-prone tail even after the
# classifier's cosmetic-clock + duration-record filters. This is the F15 skill's
# ranking judgment, not binary logic.
KIND_RANK = {
    "subprocess": 0,
    "llm": 1,
    "db": 2,
    "network": 3,
    "slack": 4,
    "provider": 5,
    "clock": 6,
    "random": 7,
}


def resolve_pry_bin() -> str | None:
    """PRY_BIN override first (maintainer-local dogfood), then PATH, then a
    release build inside this checkout (so the dogfood loop works pre-release)."""
    override = os.environ.get("PRY_BIN")
    if override:
        return override
    found = shutil.which("pry")
    if found:
        return found
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "target" / "release" / "pry"
        if candidate.is_file():
            return str(candidate)
    return None


def run_pry_map(pry_bin: str, target: Path) -> dict[str, Any]:
    command = [pry_bin, "map", str(target)]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PRY_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return {"status": "missing-binary", "command": command}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "command": command, "timeout_s": PRY_TIMEOUT_SECONDS}
    if completed.returncode != 0:
        return {
            "status": "error",
            "command": command,
            "exit_code": completed.returncode,
            "stderr": completed.stderr.strip()[:2000],
        }
    try:
        parsed = json.loads(completed.stdout) if completed.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        return {"status": "bad-json", "command": command, "detail": str(exc)}
    return {"status": "ok", "command": command, "map": parsed}


def rank_backlog(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The welded-at-demand subset = the ranked testability backlog."""
    backlog = [
        f for f in findings
        if f.get("demand") is True and f.get("class") == "welded"
    ]
    backlog.sort(
        key=lambda f: (
            KIND_RANK.get(f.get("kind", ""), 99),
            f.get("file", ""),
            f.get("line", 0),
            f.get("col", 0),
        )
    )
    return backlog


def payload_for_args(args: argparse.Namespace) -> dict[str, Any]:
    target = args.path.resolve()
    pry_bin = resolve_pry_bin()
    if pry_bin is None:
        return {
            "tool": "pry",
            "note": "risk ranking, not a bug list",
            "status": "degraded",
            "reason": (
                "No pry binary found. Set PRY_BIN=/abs/path/to/target/release/pry, "
                "put `pry` on PATH, or `cargo build --release` in the pry checkout."
            ),
            "target": str(target),
            "backlog": [],
        }
    run = run_pry_map(pry_bin, target)
    if run["status"] != "ok":
        return {
            "tool": "pry",
            "note": "risk ranking, not a bug list",
            "status": "degraded",
            "reason": f"`pry map` did not produce a map ({run['status']}).",
            "detail": {k: v for k, v in run.items() if k != "map"},
            "pry_bin": pry_bin,
            "target": str(target),
            "backlog": [],
        }
    pry_map = run["map"]
    summary = pry_map.get("summary", {})
    if summary.get("files_scanned", 0) == 0:
        # No source scanned: almost always a wrong/typo'd path. `pry map` exits 0
        # with an empty map either way, so guard here — never report a false
        # "all clear" for a path that scanned nothing.
        return {
            "tool": "pry",
            "note": "risk ranking, not a bug list",
            "status": "degraded",
            "reason": (
                f"No source files scanned at {target}. Check the path — pry analyzes "
                ".ts/.tsx/.js/.mjs/.cjs and skips test dirs."
            ),
            "pry_bin": pry_bin,
            "target": str(target),
            "backlog": [],
        }
    findings = pry_map.get("findings", [])
    backlog = rank_backlog(findings)
    if args.top is not None:
        backlog = backlog[: max(0, args.top)]
    by_kind: dict[str, int] = {}
    for f in backlog:
        kind = f.get("kind", "?")
        by_kind[kind] = by_kind.get(kind, 0) + 1
    return {
        "tool": "pry",
        "note": "risk ranking, not a bug list",
        "status": "ok",
        "pry_bin": pry_bin,
        "target": str(target),
        "summary": summary,
        "backlog_size": len(backlog),
        "backlog_by_kind": dict(sorted(by_kind.items())),
        "backlog": backlog,
    }


def print_human(payload: dict[str, Any]) -> None:
    print(f"pry — {payload['note']}")
    if payload["status"] == "degraded":
        print(f"DEGRADED: {payload['reason']}")
        if payload.get("detail"):
            print(f"  detail: {payload['detail']}")
        return
    summary = payload.get("summary", {})
    demand = summary.get("substitution_demand_subset", {})
    print(f"binary: {payload['pry_bin']}")
    print(f"target: {payload['target']}")
    print(
        f"scanned {summary.get('files_scanned', '?')} files, "
        f"{summary.get('total_boundaries', '?')} boundaries; "
        f"demand-welded fraction {demand.get('welded_fraction_LENS_GO_METRIC', '?')} "
        f"(band {demand.get('band', '?')})"
    )
    print(
        f"WELDED-AT-DEMAND BACKLOG: {payload['backlog_size']} "
        f"({payload['backlog_by_kind']})"
    )
    print("  (label each GENUINE / FALSE-WELD / COSMETIC / AMBIGUOUS — see SKILL.md)")
    for f in payload["backlog"]:
        print(f"  [{f['kind']:>10}] {f['file']}:{f['line']}:{f['col']}  {f.get('reason', '')}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rank pry's welded-at-demand testability backlog for a TS/JS path."
    )
    parser.add_argument("path", type=Path, help="File or directory of TS/JS to analyze.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human text.")
    parser.add_argument("--top", type=int, default=None, help="Limit to the top N findings.")
    args = parser.parse_args()
    payload = payload_for_args(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
