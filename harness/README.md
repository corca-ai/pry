# pry validation harness (Python)

The falsifier for Layer 0 — built **before** the analyzer (kill-gate
discipline). See [`../docs/spec-layer0.md`](../docs/spec-layer0.md) for the
contract. The analyzer is the Rust binary; this harness is eval infra (the
nose-eval analog) and is deliberately *not* part of the shipped binary, so its
non-deterministic LLM labeling stays out of the binary's determinism contract.

## Slice 0 — the analyzer-free repo-fit gate

Can kill or re-target the project **before any Rust is written** (§9 reframe).

| step | script | spends? | output |
|------|--------|---------|--------|
| 1 | `mine.py` | no | `fixtures/candidates.json` — error-handling bugfix candidates + non-matched bugfix commits |
| 2 | `doctor.py` | no | precondition (API key) + candidate-count × est-token **cost gate** |
| 3 | `label.py` | **yes (paid LLM)** | `fixtures/labels.json` — frozen labels (+ model id, prompt hash, SHAs) + P1b mining-recall sample |
| 4 | `szz.py` | no | `fixtures/bug_sites.json` — SZZ-resolved sites (the frozen ground truth) |
| 5 | `repo_fit.py` | no | `fixtures/repo_fit.json` — site count vs floor → repo-fit verdict |

`label.py` is gated: it must not spend without explicit `--yes` confirmation,
and `doctor.py` prints the cost first. Built so far: steps 1–2.

## Run

```sh
python3 harness/mine.py            # freeze candidates.json (corpus: charness)
python3 harness/doctor.py          # cost gate — review before authorizing labeling
```

## Current numbers (charness @ 3b9a2013)

- 126 candidate error-handling bugfix commits; 78 non-matched bugfix commits.
- Labeling estimate: 166 calls (126 + 40 P1b sample), ≈$1.28 on `claude-sonnet-4-6`.

Heuristics live in `config.py` (auditable, not buried in code). All frozen
outputs sort deterministically and record the corpus HEAD so downstream scoring
is reproducible (F9).
