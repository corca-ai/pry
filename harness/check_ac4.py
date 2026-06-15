"""check_ac4.py — the AC4/SC4 zero-LLM-binary denylist runner.

docs/spec-eval-harness.md AC4: the shipped `pry` binary is zero-LLM and the eval
/sweep harness is mechanical. This asserts:

  1. Cargo.lock has none of the HTTP/gRPC/LLM client crates
     (reqwest|hyper|ureq|isahc|surf|curl|awc|tonic|anthropic|openai).
  2. src/*.rs has no std::process::Command shelling to curl / an LLM CLI.
  3. harness/*.py import none of openai|anthropic|httpx|requests|urllib3|aiohttp.
  4. harness/*.py make no raw subprocess HTTP call (curl|wget|urllib).

Exception, surfaced (not hidden): the operator-approved GitHub corpus-discovery
bootstrap (handoff step 1; goal Boundaries) shells to the `gh` CLI in
corpus_freeze.py. `gh` is the GitHub CLI — not an LLM, not an HTTP-fetch client
library, and its credential lives in gh's own config and never enters the binary
or any sweep output. This is the ONE network-touching tool, it is one-time
selection (not part of the byte-deterministic sweep), and it is reported below so
a reviewer sees it is deliberate. Any OTHER subprocess HTTP call fails AC4.

Exit 0 = AC4 holds; exit 1 = a real violation.

Usage:
    python3 harness/check_ac4.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "harness"

CARGO_DENY = ("reqwest", "hyper", "ureq", "isahc", "surf", "curl", "awc",
              "tonic", "anthropic", "openai")
PY_IMPORT_DENY = ("openai", "anthropic", "httpx", "requests", "urllib3", "aiohttp",
                  # stdlib network clients also count (critique #9): a harness
                  # script must not open its own socket/HTTP/mail/ftp connection.
                  "socket", "http.client", "ftplib", "smtplib")
PY_SUBPROC_HTTP = ("curl", "wget", "urllib.request", "urlopen")
# The single operator-approved network CLI (GitHub corpus discovery).
APPROVED_CLI = "gh"
APPROVED_FILES = {"corpus_freeze.py"}


def check_cargo_lock() -> list[str]:
    p = ROOT / "Cargo.lock"
    if not p.exists():
        return ["Cargo.lock missing"]
    bad = []
    for m in re.finditer(r'(?m)^name = "([^"]+)"', p.read_text()):
        crate = m.group(1).lower()
        if any(d == crate or crate.startswith(d) for d in CARGO_DENY):
            bad.append(f"Cargo.lock: denylisted crate '{m.group(1)}'")
    return bad


def check_src() -> list[str]:
    bad = []
    for rs in (ROOT / "src").rglob("*.rs"):
        txt = rs.read_text()
        if "Command::new" in txt and re.search(r'Command::new\(\s*"(curl|wget)"', txt):
            bad.append(f"{rs.relative_to(ROOT)}: shells to curl/wget")
        if re.search(r'Command::new\([^)]*(openai|anthropic|llm)', txt, re.I):
            bad.append(f"{rs.relative_to(ROOT)}: shells to an LLM CLI")
    return bad


def check_harness() -> tuple[list[str], list[str]]:
    bad, notes = [], []
    for py in sorted(HARNESS.glob("*.py")):
        rel = py.name
        if rel == "check_ac4.py":
            continue  # the checker necessarily contains the denylist tokens
        txt = py.read_text()
        for dep in PY_IMPORT_DENY:
            if re.search(rf'(?m)^\s*(import|from)\s+{re.escape(dep)}\b', txt):
                bad.append(f"harness/{rel}: imports denylisted '{dep}'")
        for tok in PY_SUBPROC_HTTP:
            if tok in txt:
                bad.append(f"harness/{rel}: raw subprocess/HTTP token '{tok}'")
        # subprocess shelling to the approved gh CLI: allowed only in approved files
        if re.search(r'["\[]\s*["\']?gh["\']', txt) or '"gh"' in txt:
            if rel in APPROVED_FILES:
                notes.append(f"harness/{rel}: uses approved '{APPROVED_CLI}' "
                             f"discovery CLI (operator-approved, one-time, "
                             f"not part of the deterministic sweep)")
            else:
                bad.append(f"harness/{rel}: shells to '{APPROVED_CLI}' outside "
                           f"the approved discovery tool {sorted(APPROVED_FILES)}")
    return bad, notes


def main() -> None:
    violations = []
    violations += check_cargo_lock()
    violations += check_src()
    hbad, notes = check_harness()
    violations += hbad

    for n in notes:
        print(f"  note: {n}")
    if violations:
        print(f"\nAC4 FAIL — {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    print("AC4 PASS — zero-LLM binary held (Cargo.lock + src/ + harness scripts).")


if __name__ == "__main__":
    main()
