# Operator Acceptance

What a human maintainer must understand and check to take this repository over.
This is a **design-stage** repo: the deliverable so far is a thesis and a plan,
not running code, so acceptance here is about understanding and guarding the
discipline — not about a passing test suite (there is none yet).

## To take over, you should be able to

1. **State the thesis in one sentence.** Testability is the observable shadow of
   modularity; its mechanical proxy is *injectability* — is there a seam to
   substitute a failure at this boundary? (Source: `initial-plan.md` §1.3.)
2. **Name the two channels and why they differ.** Claim channels (syntactic
   floor, injection oracle) aim for ≈ zero false positives; the prediction
   channel (the map) is judged by lift over a churn baseline, never by zero
   error. Keep their outputs physically separate. (`initial-plan.md` §5.)
3. **Recite the kill gate.** Before trusting the map: does it concentrate
   error-handling defects more than a churn/LOC baseline, with a negative
   control scoring low? No lift over churn → stop or pivot. (`§8`–`§9`;
   `§7` is the central risk that motivates validating first.)
4. **Know the forced layer order.** Layer 0 (map + floor) → Layer 1 (seams) →
   Layer 2 (injection oracle). Each stands alone; do not start a later layer
   before the earlier one is stable. (`§4`, `docs/roadmap.md`.)

## Acceptance checklist for the first real milestone (Layer 0)

When Layer 0 work begins, it is "acceptable" only when **all** hold:

- [ ] The **validation harness exists before** (or alongside) the analyzer — not
      deferred. Git-history miner + LLM labeler + SZZ + churn baseline + negative
      control.
- [ ] Output is **deterministic**: byte-identical across runs, threads, and
      machines. This is a hard invariant.
- [ ] The **map** (prediction) and the **floor** (claim) are emitted as separate
      outputs/commands, with the map labeled "risk ranking, not a bug list".
- [ ] Every finding **traces to exact source lines** (tree-sitter spans).
- [ ] The **functional-core exemption** holds: clean pure code and a hexagonal /
      functional-core reference app score **low** (the negative control).
- [ ] Ambiguous boundaries land in an explicit **"ambiguous" bucket**, not in
      silence.
- [ ] A `# pry-ignore` escape hatch exists on the claim channel.
- [ ] The kill-gate number is produced on the author's own repos and the
      go/kill decision is recorded: *Z% pre-flagged vs B% churn baseline at F%
      false-flag on the negative control.*

## How this repo is operated today

- **Build target: Rust binary.** `pry` is built here as a standalone Rust binary
  and, like `nose` (`corca-ai/nose`), distributed as a prebuilt release and
  consumed by charness's `quality` skill as an `external_binary`. A maintainer
  takes over the Rust toolchain and the release/install path, not a Python
  package. (No `Cargo` surface exists yet — design stage.)
- Charness durable artifacts live under `charness-artifacts/` and are **repo
  state** — commit meaningful changes with the work they support (see
  `AGENTS.md` → Commit Discipline). The user has approved committing them.
- `charness-artifacts/gather/` records provenance for `initial-plan.md` (a
  Cloudflare-gated claude.ai artifact; the verbatim text was captured locally).
- There is no build, test, or CI surface yet. When one is added, replace this
  section with the concrete commands a maintainer runs to verify a green repo.

## Open risks a new owner inherits

- **Repo-fit, not correctness, is the most likely cause of death.** If your repo
  has no testability *gradient* or a different bug profile (LLM orchestration,
  prompt I/O) than Yuan's distributed-systems shape, change the *target*, not
  the tool. Run it on your own code first. (`initial-plan.md` §13.)
- **Conservative defaults can make it mute.** Watch for "nothing came out" — a
  too-silent tool dies as fast as a too-noisy one; that is what the ambiguous
  bucket guards against.
