# Handoff

## Workflow Trigger

**Next step = the Python frontend (third corpus, founding Layer-0 deliverable).**
The two cross-corpus precision levers are done; the TS/JS path ships at ceal ~88%+ /
cautilus 97%. Python is the next frontier AND the founding charness deliverable. It is
**not** a free reuse of the JS path: `analyze_source` is hardwired to the
tree-sitter-*typescript* grammar and TS/JS node kinds (`required_parameter`,
`variable_declarator`, `member_expression`, `binary_expression`…). Python needs
tree-sitter-python + a Python-aware classifier branch. `catalog/python.toml` is
already seeded (215 lines) — read it first. The live risk is **reproducing the Runs
1–3 "Python = glue" KILL** (`docs/kill-gate.md`): if Python repos are mostly glue with
no demand-welded error-handling surface, the corpus is a KILL, not a frontend bug.
**Scout before building:** hand-census a charness/Python repo's boundary density and
demand-weld shape against the kill-gate criteria BEFORE writing the classifier.

## Current State

- **Duration-record clock lever shipped** (`2157ccc`, `000d6dc`, `024d1c0`). The
  sink hop demotes a clock that is the *minuend* of a `-` whose result only records
  (field/log/return/call-arg), keeps it when it feeds a relational/branch. Recall
  guards (`X > Date.now()`, `Date.now()+ttl`, `deadline - Date.now()`) untouched.
  Bi-corpus validated: **cautilus demand-welded 87→66, precision 74%→97%** (21
  duration-records, full census); **ceal recall held** — 3 demotions, all
  log-durations (precision gain, no genuine timing). Deterministic. 8 tests green.
- **Fresh-eye critique run** — caught + fixed a stack-overflow blocker (self-ref
  declarator `const d = Date.now() - d`; `MAX_BINDING_HOPS` cap). 3 dormant recall
  holes (W1–W3) documented as known limitations, not yet in any corpus.
- **Both cross-corpus noise classes now filtered** (injected-callee + duration-record);
  pry no longer corpus-sensitive on the TS/JS path.

## Next Session

1. Scout a charness/Python repo against `docs/kill-gate.md` (boundary density +
   demand-weld error-handling shape) — confirm it is NOT a "Python = glue" KILL.
2. If it survives: tree-sitter-python frontend + Python classifier branch in
   `src/classify.rs` (seam/cosmetic/duration logic re-expressed for Python AST kinds),
   driven by `catalog/python.toml`. Census precision the same way (`docs/precision-gate.md`).
3. (Deferred) standalone packaging (nose cargo-dist model) — once the third corpus settles.

## Discuss

- **Python KILL risk is real and pre-registered.** Lean: scout-then-build, and be
  willing to record a KILL rather than force a third frontend. The TS/JS result already
  validates the thesis on two corpora.
- W1–W3 (dormant duration-record recall holes) — promote to filters only if a third
  corpus surfaces them; don't pre-build.

## References

- `docs/precision-gate.md` — **canonical**: H1 gate, all levers, ceal ~88% + cautilus
  74%→97% census, "After the duration-record lever" + known-limitations. Read first.
- `docs/kill-gate.md` — the Python-KILL criteria. Read before scouting.
- `catalog/python.toml` (seeded), `catalog/typescript.toml` — boundary catalogs.
- `src/classify.rs` (TS/JS-hardwired classifier; lever3 + sink hop + `MAX_BINDING_HOPS`),
  `tests/classify_smoke.rs`, `src/main.rs::is_source`/`run_map` (TS-grammar parser).
- `fixtures/ceal-ts-map.summary.json` (re-frozen, demand-subset 145→142).
