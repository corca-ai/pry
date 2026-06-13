# Critique — spec-layer0 REDESIGN (architecture correction)

- **Date:** 2026-06-13
- **Target reference:** `spec-critique` (pre-impl lock-in of an architecture correction)
- **Change:** `docs/spec-layer0.md` redesigned after the user caught an architecture error — the LLM labeling was wrongly embedded in a Python script calling the API with its own key + a cost gate (the `nose` anti-pattern, and the cause of the credential wall). Corrected to: deterministic CLI (zero intelligence) + agent-run `pry` skill + **agent-driven labeling**.
- **Execution:** ran (fresh-eye subagents). **Fresh-Eye Satisfaction:** `nested-delegated`.
- **Angles:** Jackson (problem-framing) · Weinberg (diagnostic) · Gawande (operational) + 1 counterweight.

## Central finding (all three angles converged)

The fix solved the **credential** problem but re-opened an **independence** problem: the agent now both runs `pry` and grades it. The spec went to lengths to pre-register *analyst* knobs (`T`, budget unit, mute-gate) against §13 B.1 bias, then handed the single softest knob — what counts as an error-handling fix — back to the invested agent. Borderline commits near the floor (30) are exactly where bias leaks.

## Counterweight four-bin triage

**Act Before Ship (applied):**
- C1 — blinded labeling worklist (no pry/seam/welded framing). → F10.
- C2 — frozen, contestable label transcript (verdict+reason keyed to corpus_head+sha; re-judge via `git show` without re-running the agent). → F16.
- C3 — high-confidence floor (clear ≥30 with high-confidence sites only) + verdict provenance caveat; fixed the "frozen ground truth" overclaim. → F17, F9, SC0, SC5.
- C7 — `label_io.py` emit/freeze contract specified; freeze preserves the EXACT labels.json schema szz.py/repo_fit.py consume. → Labeling protocol section.
- C8 — `freeze --model-id <id>` as the provenance source (a deterministic script can't introspect its caller). → F10/protocol.
- C9 — freeze completeness guard: refuse unless every candidate + P1b sha present, well-formed. → protocol, SC0.

**Bundle Anyway (applied):**
- C5 — borderline/low-confidence refute pass (argue NOT-count), scoped to borderline. → F17.
- C10 — `config.py` keep-list (MINING_RECALL_SAMPLE, LABEL_DIFF_CHAR_CAP, paths, floor, pathspec, regexes) vs strike-list (PRICING, LABELER_MODEL*, CHARS_PER_TOKEN, PROMPT_OVERHEAD_TOKENS, OUTPUT_TOKENS_PER_CALL). → protocol.
- C11 — `freeze` is pure schema validation, never adjudicates label correctness. → protocol.

**Over-Worry (dropped, cheaper substitute):**
- C4 — full inter-rater / inter-batch calibration study. Substitute: **forbid subagent batching for the first number — one agent labels all 166** + the borderline refute-pass (C5). The transcript (C2) makes it contestable without a labeling study.
- C6 — restructure code so the deterministic miner sets a lower bound and labeling can only subtract. Substitute: pin the monotone-subtractive property in one sentence (mine.py already produces 126 recall-oriented candidates; labeling only prunes). → F10.

**Valid but Defer (recorded):**
- C12 — exact `Cargo.lock` no-LLM dep-check command for SC2 → Deferred Decision tied to the Slice-2 reopen trigger (it's the Rust slice, not the current harness slice).

## Net

Most important fix: **C7+C8+C9** — the emit/freeze contract + completeness check is what stops a half-labeled or mis-provenanced run from silently flipping the kill gate (without it "un-wrigglable" is hollow). Biggest over-worry dropped: **C4** (inter-rater study) → forbid batching + borderline refute-pass. After the Act-Before edits + cheap bundles, the spec is close-to-ready — clause-level tightenings on an already-sound contract, not a re-redesign.
