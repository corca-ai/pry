# Handoff

## Workflow Trigger

**Next step = implement the duration-record clock filter** — the remaining
high-leverage precision lever (`docs/precision-gate.md` → "duration-record
lever"). It takes cautilus's demand-welded precision ~74% → ~93%. It is **not a
simple filter**: it reopens lever 3's "arithmetic = control" call with a **sink
hop** — demote a clock subtraction (`Date.now() - started`) whose result flows
only to a field / log / return / metric, but KEEP it when the difference feeds a
relational/branch (`if (Date.now() - started > timeout)`). **Validate bi-corpus
before committing:** cautilus precision ↑ AND ceal recall = no genuine timing
demoted (`X > Date.now()`, `Date.now() + ttl`, `deadline - Date.now()` must
survive). The `lever3_clock_timing_vs_logsink` `elapsed()` expectation will need
revising — that revision *is* the design decision. Read `docs/precision-gate.md`
"Cross-corpus" + "duration-record lever" first.

## Current State

- **JS frontend shipped** (`c038487`). `is_source` (was `is_ts_source`) accepts
  `.mjs`/`.cjs`/`.js`, parsed with the SAME tree-sitter-typescript grammar — TS
  is a JS superset and node kinds are grammar-determined, so the classifier works
  unchanged. (Adding tree-sitter-javascript would REGRESS param/default seam
  detection — JS-grammar params lack the `required_parameter` wrapper.) 0 parse
  errors on 227 cautilus + ceal `.mjs`.
- **cautilus cross-corpus precision measured** — the prior handoff's next step,
  done. Full census of 92 demand-welds (cautilus `3027ba4` `scripts/`): **~70%
  raw** vs ceal's 88% post-lever. ceal's 88% does NOT directly transfer, but the
  noise is again two nameable classes. **Injected-callee subprocess lever DONE**
  (`2ba9538`: 92→87 demand-welds). The duration-record clock class (23, 25%) is
  the remaining work → the trigger above.
- **No ceal TS regression.** ceal/packages `.ts` is byte-identical (850/776,
  demand-welded 67) — confirmed three ways incl. building the freeze commit.
  Fixture re-frozen for the JS frontend (now 900; +7 of ceal's own JS files).

## Next Session

1. Implement the duration-record clock filter (sink hop) per the trigger.
2. Re-run the cautilus precision census (`docs/precision-gate.md` method); confirm
   ~74% → ~93% and that ceal recall holds.
3. (Then / parallel) **Python frontend for charness** — the THIRD corpus and the
   founding Layer-0 deliverable; new classifier, `catalog/python.toml` seeded;
   risks reproducing the Runs 1–3 "Python = glue" KILL (`docs/kill-gate.md`).

## Discuss

- **Duration-record lever first, or Python/charness next?** Lean: **lever first**
  — evidence-backed, closes the cautilus gap, reuses the TS path; charness is a
  new classifier + KILL risk.
- **Standalone packaging (nose cargo-dist model) stays deferred** until cross-
  corpus precision is settled.

## References

- `docs/precision-gate.md` — **canonical**: H1 gate, the levers, ceal ~88% +
  cautilus ~70% census + the duration-record lever design. Read first.
- `src/classify.rs` + `tests/classify_smoke.rs` — levers + guards (`lever3_*` is
  the test to revise); `src/main.rs::is_source` — the JS frontend.
- `docs/kill-gate.md` (Python-KILL), `catalog/python.toml`,
  `fixtures/ceal-ts-map.summary.json` (packages-scoped, JS-frontend re-frozen).
