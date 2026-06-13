"""doctor.py — preconditions + cost gate before paid LLM labeling.

Slice 0 of the pry validation harness (docs/spec-layer0.md, C12/F10). This is
the gate the spec requires *before* label.py spends money: it checks the
Anthropic API key is present and prints the candidate-count x estimated-token
cost so a human can authorize (or decline) labeling ~hundreds of commits.

doctor.py never calls the API and never spends. It measures the real diff sizes
of the mined candidates (capped at LABEL_DIFF_CHAR_CAP, exactly what label.py
will send) and converts to a token/$ estimate with a documented heuristic.
label.py is the step that actually labels and must refuse to run without an
explicit confirmation flag.

Usage:
    python3 harness/doctor.py [--candidates PATH] [--repo PATH]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import config


def _diff_chars(repo: Path, sha: str, cap: int) -> int:
    """Bytes of the unified *.py diff for `sha`, capped at `cap` chars."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "show", "--format=", "--unified=3",
             sha, "--", config.PYTHON_PATHSPEC],
            check=True, capture_output=True, text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return 0
    return min(len(out), cap)


def _estimate(commit_count: int, total_diff_chars: int) -> dict:
    """Token + cost estimate across `commit_count` labeling calls."""
    input_tokens = (
        total_diff_chars / config.CHARS_PER_TOKEN
        + commit_count * config.PROMPT_OVERHEAD_TOKENS
    )
    output_tokens = commit_count * config.OUTPUT_TOKENS_PER_CALL

    costs = {}
    for model, rate in config.PRICING.items():
        costs[model] = round(
            input_tokens / 1_000_000 * rate["input"]
            + output_tokens / 1_000_000 * rate["output"],
            4,
        )
    return {
        "calls": commit_count,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "cost_usd": costs,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", type=Path, default=config.CANDIDATES_PATH)
    ap.add_argument("--repo", type=Path, default=config.DEFAULT_CORPUS_REPO)
    args = ap.parse_args()

    # --- precondition: API key ------------------------------------------
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY")
                   or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    print("=== preconditions ===")
    print(f"  ANTHROPIC_API_KEY present: {has_key}")
    if not has_key:
        print("  -> set ANTHROPIC_API_KEY (or run `ant auth login`) before label.py")

    if not args.candidates.exists():
        sys.exit(f"\nerror: {args.candidates} not found — run mine.py first")

    data = json.loads(args.candidates.read_text())
    candidates = data["candidates"]
    non_matched = data["non_matched_bugfix"]

    # P1b mining-recall sample: first N non-matched bugfix commits (deterministic;
    # candidates.json is already sorted by (date, sha)).
    sample = non_matched[: config.MINING_RECALL_SAMPLE]

    print("\n=== labeling workload (charness @ "
          f"{data['corpus_head'][:12]}) ===")
    print(f"  candidates to label:            {len(candidates)}")
    print(f"  mining-recall sample (P1b):     {len(sample)}")
    print(f"  diff char cap per commit:       {config.LABEL_DIFF_CHAR_CAP}")

    to_measure = candidates + sample
    total_chars = sum(
        _diff_chars(args.repo, c["sha"], config.LABEL_DIFF_CHAR_CAP)
        for c in to_measure
    )

    est = _estimate(len(to_measure), total_chars)

    print("\n=== cost estimate (heuristic, no API spend) ===")
    print(f"  labeling calls:    {est['calls']}")
    print(f"  est input tokens:  ~{est['input_tokens']:,}")
    print(f"  est output tokens: ~{est['output_tokens']:,}")
    print(f"  (assumes ~{config.CHARS_PER_TOKEN} chars/token, "
          f"+{config.PROMPT_OVERHEAD_TOKENS} prompt tokens/call)")
    for model, cost in est["cost_usd"].items():
        tag = " (default labeler)" if model == config.LABELER_MODEL else " (fallback)"
        print(f"  ~${cost:>7.4f}  {model}{tag}")

    print("\n=== gate ===")
    print("  doctor.py spent $0. Authorize label.py before it spends the above.")
    print("  Next: `python3 harness/label.py --yes` (gated; not run by doctor).")


if __name__ == "__main__":
    main()
