# spec — `pry untested` (the welded∧untested worklist subcommand)

Canonical build contract for slice 1 of the dogfood/`.pryconfig.toml` direction.
Upstream concept: `charness-artifacts/ideation/2026-06-16-pryconfig-and-dogfood.md`.
Reference oracle: `harness/step1b.py` (the validated static failure-test cross).

## Problem

`pry map` classifies boundary calls welded vs seamed. The north star (operator's
own products) needs one more cut: of the welded, failure-capable boundaries, which
ones have **no test that simulates their failure** — those are the "add a failure
test" candidates. The dogfood proved this pays off on the author's own repos
(ceal: 142 welded-FC → 114 untested), the opposite of mature OSS (~71% mock-tested).

`step1b.py` proved the cross is computable statically/offline. This slice ports the
**generous (L-module) linkage** of that cross into the binary as `pry untested`, so
the worklist is a product feature, not eval scaffolding.

## Current Slice (1a — the core worklist)

`pry untested <path>` →
1. classify source (reuse `classify::analyze_source`); candidate pool =
   `class==Welded && demand && kind ∈ FLOOR_KINDS` (network/subprocess/db/fileio).
2. discover **test** files (the inverse of `is_source`'s test exclusion) and
   fingerprint each: import bindings, mocked modules, failure-sim presence.
3. build the **L-module failure-mock index**: module token → some test mocks it
   AND simulates a failure (generous `include_bare=True` catalog).
4. per candidate: extract its module token (re-read the source line, resolve the
   callee root against the file's import map — frozen §3 binding precedence);
   `tested` iff module ∈ index (network also credited by `__NETWORK_ANY__`).
5. emit the **untested** candidates (worklist) + a summary, deterministic JSON.

## Fixed Decisions

- **Linkage = L-module generous only.** Generous-tested ⇒ conservative-untested:
  a finding lands on the worklist only if NO test anywhere mocks its module and
  simulates a failure. This is the low-false-alarm bias a worklist needs. L-import
  (tight) / strict catalog / the two-sided bracket were eval-measurement machinery
  (defensible *rate*); the product needs candidate generation, not the bracket.
- **Failure-capable set = `floor::FLOOR_KINDS`** (single source of truth, already
  `{network,subprocess,db,fileio}`). llm/slack stay omitted until the
  `.pryconfig.toml` override (slice 2) — recorded as a known gap, not silently fixed.
- **Fingerprint catalogs are ported byte-faithfully** from `step1b.py` §3/§4.1/§4.2
  (already adversarially verified). The one negative-lookahead entry (`_FS_BARE`'s
  `(?![\w(])`) is refactored to a consuming-char equivalent `(?:[^\w(]|$)` —
  faithful for boolean presence, avoids a lookaround crate.
- **Output tags `catalog: "seed"`** on every finding now, establishing the
  provenance contract the `.pryconfig.toml` slice will extend (seed vs repo-config).
- **Production filter is out of slice.** `discover` already honors `.gitignore` +
  `.pryignore`; a repo narrows scripts/bin/eval out there (the dogfood's 114→12).
  No path-based "production" heuristic baked into pry.

## Probe Questions (answered by building, not blocking)

- Does the Rust generous-untested set on ceal land near the dogfood's ~114? (parity
  sanity vs `step1b.py` logic — not byte-identical, since the binary computes its
  own findings rather than reading frozen corpus findings.)
- Is craken-agents still ~clean (few untested, all tooling)?

## Deferred Decisions

- `.pryconfig.toml` (ignore + structured per-repo `[[boundary]]` + failure-capable
  override + wrapper/alias declarations) — slice 2.
- completeness-probe mode — slice 3. LLM-judge triage — slice 4.

## Non-Goals / Deliberately Not Doing

- NOT proving coverage. "untested" = no failure-mock fingerprint (fast static
  filter), not proven-uncovered. The reason string says so.
- NOT reproducing step1b's measured *rate*, verdict, or contrast arms — that
  number is closed (WEAK, `docs/eval-gate.md`); this is a product-shape build.
- NOT a generalizable-OSS payoff claim. The 4 negatives stand.

## Constraints

- F1: deterministic, zero intelligence (no HTTP/LLM/network). `regex` crate is
  pure computation — allowed.
- F26 self-application: the analysis core stays I/O-free (`analyze_untested` takes
  injected findings + test fingerprints); the binary shell does discovery + emit.
- Deterministic output: stable sort, fixed-dp ratios (SC3), like `map`/`floor`.

## Success Criteria → Acceptance Checks

- SC1 worklist is welded∧demand∧FC∧untested → unit tests on a synthetic repo:
  a welded `fetch` with NO failure-test appears; the same with a
  `mockRejectedValue` test for its module disappears.
- SC2 fingerprint fidelity → port step1b's catalog unit tests (import bindings,
  module extraction, mocked_modules, has_failuresim FLAT/BRACED/bare, NETWORK_ANY).
- SC3 determinism → identical bytes across two runs (existing harness style).
- SC4 dogfood sanity → `pry untested` runs clean on ceal + craken-agents; ceal
  surfaces a non-trivial untested set incl. `control-auto-commit.ts`, craken-agents
  stays near-empty. (Reproduction proof, not a checked-in number.)

## Critique

Fresh-eye subagent **code-critique** required before closeout (repo discipline);
angle on fingerprint-port fidelity + worklist false-alarm honesty.

## Canonical Artifact

This file during slice 1; `untested.rs` + its unit tests are the executable contract.

## First Implementation Slice

`src/untested.rs` (port: bindings/modules/fingerprints/index/cross) + `Untested`
subcommand in `src/main.rs` + `regex` dep + unit tests, then dogfood sanity.
