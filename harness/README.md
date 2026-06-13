# pry validation harness (Python mechanics + agent labeling)

The falsifier for Layer 0 — built **before** the analyzer (kill-gate
discipline). See [`../docs/spec-layer0.md`](../docs/spec-layer0.md) for the
contract.

**Two-layer architecture (the `nose` model).** The `pry` CLI (Rust, later) is a
deterministic analyzer with **zero intelligence** — it emits the map (advisory)
+ floor (claims) as data. The **intelligence is the coding agent**: an agent-run
`pry` skill consumes the CLI output and, for validation, **does the commit
labeling itself**. No harness script calls an LLM or holds a credential.

## Slice 0 — the analyzer-free repo-fit gate

Can kill or re-target the project **before any Rust is written** (§9 reframe).

| step | what runs it | spends? | output |
|------|--------------|---------|--------|
| 1 | `mine.py` (mechanical) | no | `fixtures/candidates.json` — error-handling bugfix candidates + non-matched bugfix commits |
| 2a | `label_io.py emit` (mechanical) | no | `fixtures/label_worklist.json` — **blinded** rubric + `{sha, subject, diff}` |
| 2b | **the coding agent** | no | `fixtures/label_verdicts.json` — `{sha: {is_error_handling_fix, confidence, reason}}` (single-pass, refute borderline) |
| 2c | `label_io.py freeze --model-id <m>` (mechanical) | no | `fixtures/labels.json` — frozen labels (completeness-checked, exact schema) |
| 3 | `szz.py` (mechanical) | no | `fixtures/bug_sites.json` — SZZ-resolved sites (`git blame -w` + AST, F11 key) |
| 4 | `repo_fit.py` (mechanical) | no | `fixtures/repo_fit.json` — repo-fit verdict (**high-confidence** floor, F17) |

No credential, no spend, no cost gate (the retired `label.py`/`doctor.py` were
the `nose` anti-pattern — intelligence + credential embedded in a script).

## Run

```sh
python3 harness/mine.py                       # 1. candidates.json (corpus: charness)
python3 harness/label_io.py emit              # 2a. blinded worklist
#   2b. the agent labels every sha -> fixtures/label_verdicts.json
python3 harness/label_io.py freeze --model-id <model>   # 2c. frozen labels.json
python3 harness/szz.py                        # 3. bug_sites.json
python3 harness/repo_fit.py                   # 4. repo-fit verdict
```

`label_io.py freeze` **refuses** unless every candidate + P1b sha is present and
well-formed (completeness guard) and is a **pure schema validator** — it never
judges label correctness (the agent is the only intelligence).

## Current numbers (charness @ 3b9a2013)

- 126 candidate error-handling bugfix commits; 78 non-matched bugfix commits.
- Labeling worklist: 166 commits (126 + 40 P1b mining-recall sample).

Heuristics live in `config.py` (auditable). All frozen outputs sort
deterministically and record the corpus HEAD (F9). Labels are *auditable*
(contestable via `git show <sha>` against the frozen corpus), not byte-
reproducible — provenance = model id + rubric hash (F16).
