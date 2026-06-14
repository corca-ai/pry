# Handoff

## Workflow Trigger

**Next step = generalize the precision result to ../cautilus and ../charness.**
But pry only parses **TypeScript**, and neither target has any: **cautilus** is Go
+ ~4200 `.mjs` (JavaScript); **charness** is ~2000 `.py` (Python). So `pry map`
returns *empty* on both today — do **not** just run it and report zero. The real
next step is: **add a frontend for the target language, then re-run the precision
hand-sample gate** (`docs/precision-gate.md` protocol) on that corpus to test
whether ceal's ~88% precision holds or was ceal-tuned. Read `docs/precision-gate.md`
first.

## Current State

- **Session pivot: "packaging" → "make pry reliably useful" (operator call).** The
  original packaging goal (charness `external_binary` manifest) was **abandoned**:
  wrong scope (real packaging = pry *standalone* release, deferred) and charness is
  occupied by a concurrent agent. The committed goal artifact
  `charness-artifacts/goals/2026-06-14-pry-packaging-ceal-revalidation.md` is
  superseded; its ceal-revalidation half is done (below).
- **pry is now reliably useful on ceal — measured, not asserted.** The H1
  **precision gate** hand-labeled the welded-at-demand backlog; three classifier
  levers raised precision **~32% → ~88%** (demand-welded 174→67): (1) cosmetic
  clock/random filter, (2) F22 rung-3 wrapper/factory detection + 2 0-hop seam bug
  fixes, (3) one-hop clock dataflow (timing math kept, record/log sinks demoted).
  5 tests green, byte-deterministic. Full method + per-finding evidence:
  **`docs/precision-gate.md`**.
- **ceal re-validated** at `cdd31884` (pulled this session, was `8238b245`);
  fixture re-frozen (`fixtures/ceal-ts-map.summary.json`). The 4 new error-handling
  files added zero boundaries — pry stable across the corpus move.
- **The one big caveat: precision is measured on a SINGLE corpus (ceal,
  DI-disciplined).** Cross-corpus generalization is unproven — that is exactly
  what the next step exists to test. (pry measures testability-surface — genuine
  failure paths with no seam to inject a failure — not bug prediction.)

## Next Session

1. **Pick the frontend** (Discuss below): JavaScript (cautilus) reuses most of the
   TS classifier but loses the type-only rung-3 signals (`implements` / typed-const
   have no JS analog) → likely lower precision there. Python (charness) is the
   original Layer-0 deliverable and has a `catalog/python.toml` seed, but is a new
   classifier — **and may reproduce the Runs 1–3 "Python = glue" KILL**
   (`docs/kill-gate.md`; charness is the author's Python harness, the shape that
   failed Gate 0).
2. Add the chosen frontend (`tree-sitter-javascript` or `-python`), wiring it like
   the TS path in `src/` (catalog stays data; reuse `classify.rs` levers where the
   grammar allows).
3. Run the **precision hand-sample gate** (`docs/precision-gate.md` method:
   classify demand-welded, hand-label a sample, report precision + noise taxonomy)
   on the new corpus.
4. Record the cross-corpus precision in `docs/precision-gate.md` (does ~88% hold?).

## Discuss

- **Which frontend first — JS/cautilus or Python/charness?** JS reuses more code
  and is a cleaner precision generalization test; Python tests the founding thesis
  but risks re-confirming the glue-KILL. (Lean: JS first as the precision check,
  Python second as the thesis check.)
- **Standalone packaging (nose cargo-dist model) stays deferred** — revisit after
  cross-corpus precision is known.

## References

- `docs/precision-gate.md` — **canonical**: the H1 gate, the 3 levers, 32%→88%
  method + evidence. Read first.
- `src/classify.rs` + `tests/classify_smoke.rs` — the levers and their guards;
  `catalog/python.toml` — Python boundary seed (for the charness path).
- `docs/kill-gate.md` / `docs/ceal-ts-gate.md` / `docs/ts-cross-corpus.md` — Runs
  3–6 history. `docs/spec-layer0.md` F18–F28. `fixtures/ceal-ts-map.summary.json`
  — frozen ceal evidence at `cdd31884`.
