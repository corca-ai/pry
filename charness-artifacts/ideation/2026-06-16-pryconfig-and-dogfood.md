# Ideation — pry's real home: dogfood on the author's own repos, via a per-repo `.pryconfig.toml`
Date: 2026-06-16 (captured before a context compaction; impl resumes after)

Trigger: after Step-1b came back WEAK (4th measurement negative), the operator
reframed the actual north star and we dogfooded pry on real repos. This note pins
the conclusion + the `.pryconfig.toml` design + the impl plan so nothing is lost.

## The operator's actual north star (the reframe that reorients everything)

"내 제품들에서, 경계에 있고 테스트하기 어려워서 잘 안 테스트되던 곳을 pry가 드러내
→ 잘 테스트되게 한다." The 25-repo corpus work was **instrumental** (to sharpen pry's
suggestions), NOT the goal. So the 4 pre-registered negatives (E9 bugs, Step-1 file-
coverage, Floor, Step-1b failure-test) refute a **generalizable prioritization claim
on mature OSS** — they do NOT refute "pry is useful on the author's own repos."

## Dogfood result (the evidence the reframe is right) — craken-agents + ceal

Pipeline: `pry map` → welded∧demand∧failure-capable → live failure-test cross
(step1b.py logic on the working tree) → production filter.

- **craken-agents**: 22 welded FC boundaries → 6 untested, **all in `bin/*.mjs` tooling**
  → ~0 production gaps (this repo's boundaries are fairly well tested).
- **ceal**: 142 welded FC → **114 untested** (vs only 4 own-file-tested). Filter to
  production = **12** (102 were scripts/eval tooling). Read 4: `control-auto-commit.ts:133`
  (real gap — git auto-commit failure branches, untested), slack connector (likely real),
  `sandbox.ts:258` taskkill (intentional best-effort), `observability.ts:58` git probe
  (mostly intentional). → **~5-6 genuine "add a failure test" gaps.**

**Key contrast:** mature OSS = ~71% module-fail-mocked somewhere (wedge dead); ceal
(own, less-mature) = 114/142 untested. **pry pays off exactly where the operator
aimed it — own products, not generalizable OSS.** The corpus was the harsh test.

**Honest limit:** the last mile (real gap vs intentional best-effort) needs judgment;
on own repos that judgment CAN use an LLM judge (AC4 only bound the corpus).

## How pry finds targets (mechanism, confirmed from source — for the design below)

Pure **syntactic AST matching**, no LLM/types: tree-sitter parse → match each
call/construct node against a hand-curated **boundary catalog** (`catalog/typescript.toml`,
~63 entries / 9 kinds, structured `[[boundary]]` fingerprints: form + ctor/callee/method
+ require_root) → welded/seamed classify (local 0-/1-hop dataflow) → `demand` subset.
TWO whitelists: (1) the catalog (what's a boundary), (2) hardcoded **failure-capable** =
`{network, subprocess, db, fileio}` (clock/random/env excluded as input-shaped; **llm/slack
are failure-capable but currently OMITTED — a gap**). Completeness is bound by the catalog
(seed `0.1.0`); wrapped/aliased calls → UNRESOLVED/missed.

## DECISION — consolidate into `.pryconfig.toml` + per-repo catalog extension (AGREED)

Replace the separate `.pryignore` (E7 repo-scope exclude) with a `.pryconfig.toml`
that carries **ignore rules + per-repo boundary extensions + overrides**, populated by
the repo's coding agent. Verdict: **strongly agreed** — fixes the catalog-completeness
limit at the right layer, fits pry's agent-native distribution, and matches the
dogfood/ratchet (opt-in, config-based) product shape the operator wants.

**Two non-negotiables (else pry's only validated asset — precision — dies):**
1. **Structured catalog ENTRIES, not loose "keywords."** Repo config adds the SAME
   `[[boundary]]` schema (form/object/method/require_root) so AST-shape matching (and the
   100% net/subproc precision) is preserved. A substring-keyword list (`client`, `query`)
   would explode noise.
2. **Seed-vs-repo PROVENANCE tagged in output.** pry's validated precision is the *seed*
   catalog's; agent-added entries are outside that guarantee. Tag each finding
   `seed` vs `repo-config` so agent config can't silently dilute the validated number.
   Config must be committed + reviewed.

**Refinements:**
- First/highest-value config type = **wrapper/alias declarations** (`./fetch`, `httpClient`
  → network) — directly closes the UNRESOLVED-wrapper gap seen in ceal.
- Let a repo **override the failure-capable set** (e.g. ceal opts in `llm`/`slack`).
- Add a **completeness-probe mode**: pry emits "looks boundary-ish but matches no catalog
  entry" → the agent proposes config additions → closes under-inclusion by *detection*,
  not assumption. This is the agent feedback loop.

**Strategic framing:** this moves pry from "drop on any repo, seed catalog" → "repo
declares its boundaries, pry surfaces welded∧untested against that declaration." That IS
the dogfood/ratchet (opt-in) home, and it fits the north star.

## Impl plan (post-compaction; operator deferred execution)

1. **`pry untested` subcommand (Rust)** — NOT a separate tool; port step1b.py's failure-
   test cross into the pry binary (it already has tree-sitter + the catalog + welded
   classification; add test-file mock/failure-sim fingerprinting + import linkage). Emit
   the welded∧untested∧production worklist. step1b.py = the validated reference/oracle.
2. **`.pryconfig.toml`** — ignore + structured per-repo `[[boundary]]` extensions +
   failure-capable override; seed-vs-repo provenance tag; wrapper/alias declarations first.
3. **completeness-probe** mode (boundary-ish-but-uncatalogued).
4. **LLM-judge triage** (real-gap vs intentional) — own-repo only; turns the ~12 into ~5-6.
5. Optionally: write the failure tests for ceal's confirmed gaps (control-auto-commit, …).

## Non-claims / honest guards (carry forward)
- "untested" = no failure-mock fingerprint (fast static filter), not proven-uncovered;
  confirm the ones that matter with real coverage (own repos can run tests — no AC4).
- pry stays a *precise injectability classifier*; the dogfood value is "candidate
  generator + agent/LLM triage on YOUR repos," not a generalizable defect/coverage payoff.
- The 4 measurement negatives stand (docs/eval-gate.md); this is a product-shape pivot,
  not a re-opening of the dead theses.
