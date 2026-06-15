# S1 slice review packet — E9 corpus discovery + freeze + pre-registration

## Intent
Build a frozen, pinned, split-honest corpus + the pre-registration honesty gate
for the E9 multi-repo validation sweep, BEFORE any enrichment number exists.
Answer-questions downstream: 쟁점 4 (does welded-at-demand predict defects?) and
쟁점 2 (does it generalize?). S1 itself measures nothing — it only selects +
freezes + pre-registers.

## Changed files / surfaces
- `harness/config.py` (+E9 block): pre-registered constants — CORPUS_APP_SHAPEDNESS_FLOOR=55,
  ENRICHMENT_GO_FLOOR=1.5, ENRICHMENT_FALSIFIER=1.1, churn×site-size terciles,
  ENRICHMENT_MIN_STRATUM=5, Simpson guard, BGATE_LENS_BAND=[0.15,0.85].
- `harness/fixtures/eval/preregistration.md` — human-readable contract.
- `harness/corpus_fit.py` — NEW app-shapedness scorer (pure, unit-tested).
- `harness/corpus_schema.json` + `harness/validate_corpus.py` — schema + validator.
- `harness/corpus_freeze.py` — gh-API discovery → score → pin → freeze.
- `harness/check_ac4.py` — AC4 zero-LLM denylist runner.
- `harness/test_corpus.py` — 10 unit tests.
- `harness/fixtures/eval/corpus.json` — 33 repos (25 TS dev5/heldout20 + 8 Python
  dev2/heldout6), pinned commits.
- `harness/fixtures/eval/corpus_discovery_features.json` — per-repo scoring inputs.
- `harness/fixtures/eval/corpus_prune_log.md` — discovery→selection funnel + exclusions.

## Commits (ordering matters)
- `037e5bc` preregister(E9) — the honesty-gate anchor (must precede any enrichment commit).
- `50f06cb` S1 corpus + tooling.

## Expected invariants
- Corpus validates against schema; pinned 40-hex commits; each arm has dev AND heldout.
- Pre-registration commit precedes first enrichment-number commit (git-provable).
- dev includes the 4 labeled H3 seeds + medusa (non-AI); heldout never tuned on.
- AC4: zero LLM/HTTP client in binary + harness (gh discovery the single surfaced exception).

## Tests / proof
- `python3 harness/validate_corpus.py` → VALID.
- `python3 harness/check_ac4.py` → AC4 PASS.
- `python3 -m pytest harness/test_corpus.py` → 10 passed.
- `cargo test` → green (no Rust changed).

## Non-claims (S1)
- No enrichment number yet. No causal claim. No Python frontend yet. License
  recorded per-repo (copyleft included deliberately — analysis is local read-only).

## Out of scope for this pass
- S2 miner/join, S3 enrichment math execution, S5 (b)-gate run. (The metric
  *definition* in preregistration.md IS in scope to stress now.)

## Reviewer questions (the load-bearing ones)
1. R-A: Is the slate genuinely stratified, or silently clustered at the
   disciplined/low-injection end? Is the dev/heldout split genuinely
   pre-registered (not chosen after a peek)? Is dev's AI-lean a problem?
2. R-B: Does the pre-registered matched-comparison denominator (file-churn ×
   site-size terciles, direct standardization) actually neutralize the confound?
   Is the blame-based "bugfix-touched" definition sound? Are floor=1.5 /
   falsifier=1.1 honest and not gameable?
3. Scorer/freeze/AC4: Does corpus_fit.py measure app-shapedness as claimed (or
   is the floor set to admit everything)? Is the gh-AC4 exception a smuggled
   network dependency or genuinely benign? Schema/validator/repro gaps?
