# Roadmap

Ordered by dependency, following the design in
[`../initial-plan.md`](../initial-plan.md). The sequence is forced, not chosen:
injection needs seams, seams come from the map, the map needs the catalog. Stop
at any layer and the result still stands.

## Now — Layer 0 + validation, on this author's own repos

The first experiment's real job is **not** "is the tool accurate" but **"does my
repo even have this bottleneck"** (a testability gradient and the swallowed-
boundary-failure bug shape). Build the validation harness *before* the analyzer
so the thesis can actually be falsified.

1. **Validation harness first** (the `nose-eval` analog). Git-history miner for
   error-handling bugfix commits → LLM labeler → SZZ trace to bug-introducing
   commit → churn/LOC baseline → negative control (clean hexagonal / functional-
   core reference apps must score low). Reuse BugsInPy for Python.
2. **Parse.** `pry` is a **Rust** binary; parse Python (TS/TSX later) via
   tree-sitter's Rust bindings. Spans on every node so every finding traces to
   exact lines.
3. **Boundary + seam catalog as data** (auditable config, not code) — the moat.
   Start from the Python boundary list in the spec (`requests`/`httpx`, `open`,
   `socket`, `subprocess`, `os`/`os.environ`, `datetime.now`/`time.time`,
   `random`, DB drivers, `boto3`). Enforce the functional-core exemption: only
   flag *boundary-crossing* code that lacks a seam.
4. **Dataflow-lite.** Classify each boundary call **seamed vs welded**,
   conservatively (§7 central risk). Surface an explicit **"ambiguous" bucket**
   rather than going silent. Record weld depth as a *measured* ranking input.
5. **Syntactic floor** (Aspirator-derived): empty catch; catch-all → abort/
   continue; log-and-continue on a mutating path; swallowed error; Python bare
   `except`; un-handled `await` in `try`. High precision + `# pry-ignore`.
6. **Emit.** Deterministic JSON + a human risk map + SARIF for CI. Determinism
   is a hard invariant (byte-identical across runs/threads/machines). Keep the
   map (prediction) and the floor (claim) in **physically separate** outputs.

### Kill gate (write the line down before measuring)

Produce one number: *"Z% of error-handling bugfix commits touched code the map
pre-flagged, vs a churn baseline of B%, at F% false-flag on the negative
control."* **Real lift over churn → unfold Layer 1. No lift → stop or pivot the
signal.** Do not set N/M/K thresholds a priori; set them from the measured churn
baseline.

## Next — Layer 1 (only after Layer 0 is stable and validated)

Seam generation: propose a port/adapter refactoring for the highest-risk
boundaries; output is a human-reviewed PR. Propose seams only where the map's
risk is high enough that the PR sells itself — never refactor for purity's sake.

## Later — Layer 2 (only after seams exist)

Injection oracle: inject failures at seams, check invariants, measure the
escaped-injection rate; the map score should correlate inversely with it.

## Deliberately deferred

Internals of Layers 1–2, map **granularity** (call-site vs function vs file),
weld-depth weighting, whether test-only monkeypatches count as "seamed enough",
and the final per-language floor rule set. These are resolved by measuring on
real repos, not decided now.

## Adoption guardrails (so it survives)

- Wire into CI / pre-commit so it runs by default — "remember to run it" = dies.
- Label the map "risk ranking, not a bug list" from the first pixel.
- Keep Layer 0 small enough that it pays for itself in week one.
- Ship as an `external_binary` consumed by the charness **`quality`** skill,
  mirroring `nose` (`integrations/tools/nose.json`): a prebuilt Rust release
  (installer + Homebrew tap), detected by `pry --version`, with a quality-side
  consumer/inventory script. This is §10's "packaging option" made concrete —
  not a Python charness skill.
