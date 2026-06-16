# Step-1b — static FAILURE-test detection — PRE-REGISTRATION

**Status: frozen. This file's git commit MUST precede the commit that writes any
Step-1b failure-test number.** A fresh reviewer proves the order from git, not
from a self-attesting line:

```
git merge-base --is-ancestor <this-commit-sha> <first-step1b-number-commit-sha>
```

Fourth honesty gate in this repo (after `preregistration.md` E9,
`preregistration-coverage.md` Step-1, `preregistration-floor.md` Floor). It
matters as much as Step-1: this is the **sharp redo** of Step-1's coarse
file-level coverage proxy. Step-1 asked "is the welded boundary's *file* tested
at all?" (FALSIFIED, 0.95). Step-1b asks the question the testability thesis
actually makes: **is the welded boundary's own FAILURE PATH actually simulated by
a test?** — fully static, offline, AC4-clean, on the same frozen corpus. The
machine-readable copy of every threshold lives in the `Step-1b` block of
`harness/config.py`; that is the source of truth the harness reads. If the two
disagree, the git history of *this file* governs.

> **Why this is measurable offline (the 2026-06-16 scope correction).** The
> earlier "needs `npm install` / executed coverage / outbound" framing was WRONG
> (operator-caught). Failure-path testing leaves **static fingerprints**: a
> module mock (`vi.mock`/`jest.mock`/`__mocks__/`, `nock`, `msw`, `sinon`) plus a
> **failure simulation** (`mockRejectedValue`, `mockImplementation(()=>{throw})`,
> `nock().replyWithError`, an msw error handler, `mockResolvedValue({ok:false})`,
> `.rejects`). So Step-1b reads test-file source at the pinned commits via the
> same git plumbing (`ls-tree` + `cat-file`) Step-1 used — zero new mining, zero
> outbound, no test suites run, no LLM.

---

## 0. What changed from the handoff framing (disclosed, set BEFORE any number)

The handoff (`docs/handoff.md`) framed the contrast as "welded ... mock-tested
**vs seamed**." Sizing the **existing frozen sweep** (pre-existing E9 data, not a
Step-1b outcome) shows the seamed arm cannot carry a matched contrast:

| failure-capable arm | corpus N | repos with ≥20 in arm |
| --- | --- | --- |
| welded-at-demand (`wd`, signal) | **1727** (net 1207 / subproc 414 / db 106 / fileio 0) | 24/25 |
| **seamed** | **138** | **1/25** (calcom only) |
| welded-not-demand (`wnd`) | 1562 | — |
| **rest** (`seamed ∪ wnd`) | 1700 | 15/25 |

A `wd`-vs-**seamed** matched ratio is **structurally underpowered** (138 findings,
one eligible repo): its CI lower bound cannot clear 1.0, so binding the verdict on
it would make a positive *unreachable* — a rigged gate, forbidden by this repo's
reachability discipline (Step-1 explicitly checked "the bar was reachable").

**AMENDED 2026-06-16 (operator decision, still BEFORE any number — the simpler,
more honest gate).** Rather than bind the verdict on *any* comparison, the verdict
is now the **ABSOLUTE failure-tested rate of the `wd` arm**, read two ways
(POSITIVE = low / OVERSTATED = high; §6). The welded-vs-other **comparison is
REPORTED CONTEXT, not a gate.** Why this is better, not weaker:

- It answers the **product** question directly ("are there dense untested failure
  targets the recommender can point at?") — a rate, fully powered (`wd` N=1727).
- It **removes two problems** a binding comparison carried: (i) the only
  well-powered control, `rest`, is ~92% `welded-not-demand`, so a binding contrast
  would really be a *demand* test (demand already died in Step-1, 0.94) — not the
  weld/seam claim; (ii) failure-tests are rare → near-ceiling base rates →
  the contrast's CI-lo may be unreachable regardless of reality (Open Item §7.5).
- **Comparisons are still computed and reported** (`wd` vs `rest`, `seamed`,
  `wnd`; matched ratio + odds ratio + rate difference + base-rate ceiling, the
  full §5 machinery) — as **honest context** on whether the untested-ness is
  *weld-specific*, NOT as a pass/fail. The `seamed` arm is flagged underpowered.

So the headline is a **rate with a two-sided reading**; the comparison tells us
whether `welded`/`demand` *differentiates* the targets (a reported caveat, not a
verdict). Frozen here, before any failure-test number exists.

## 1. Corpus, split, data source — REUSED from E9/Step-1, no new mining

Identical to E9/Step-1 (`corpus.json`): **25 TS/JS apps**, dev 5 / heldout 20,
pinned commits. **Zero new mining, zero outbound.** The frozen E9 sweep records
(`sweep/*.json`) supply the finding set, arms, `file_churn`, `site_size`. Step-1b
**adds** two things, both read from the clones at the SAME pinned commit via
`git ls-tree` + `git cat-file`: (i) each boundary's **module token** (re-read at
its `file:line`, §3), and (ii) per-test-file **mock + failure-sim fingerprints**
(§4). The E9 sweep records are NOT mutated. Step-1b reuses `coverage.py`'s
tsconfig-alias resolution + test-file detection **substrate**, and re-runs its
import scan **retaining the `(test, source)` edge** that `build_coverage`
currently discards (plus a net-new per-module test index) — see §4.3. The
substrate is reused; the two linkage indices are net-new plumbing on it, not a
verbatim call.

## 2. Unit and arms — REUSED from E9/Step-1, restricted to failure-capable kinds

- **Unit:** one pry *finding* (a boundary call) whose `kind ∈
  STEP1B_FAILURE_CAPABLE_KINDS = {network, subprocess, db, fileio}`. Clock /
  random / env are EXCLUDED — an RNG/timer/env-read has no failure worth
  injecting (the cosmetic tail; `random` 0/79, `clock` ≈3/130 genuine). This is
  the same failure-capable set the Floor used (`FLOOR_BOUNDARY_KINDS`).
- **Signal arm — welded-at-demand (`wd`):** `class=="welded" AND demand==true AND
  kind∈FC`. The population pry actually surfaces and recommends on (operator-
  ratified primary, 2026-06-16). N=1727 on this corpus.
- **PRIMARY contrast control — `rest`:** every other FC finding (`class=="seamed"`
  OR (`class=="welded" AND demand==false`)). Well-powered (§0).
- **REPORTED secondaries (not the binding verdict):** `wd` vs `seamed`-only (the
  injectability bit; underpowered, §0); `wd` vs `welded-not-demand`-only (does
  `demand` add anything to failure-testedness — the Step-1 decomposition); the
  **all-welded** FC pool (the full recommender population).
- A finding inside a test file is out of scope (dropped, as Step-1 does).

## 3. The boundary's MODULE TOKEN (the linkage key) — frozen extraction

The sweep records do NOT carry the boundary's module. Step-1b re-reads the source
blob at the boundary's `file` (at the pinned commit) and resolves the call site's
callee to a **module token** `M` by a frozen, deterministic rule. `M` is what a
test must mock to fake this boundary. By kind:

- **network:** bare `fetch(`/`globalThis.fetch` → `M = "__global_fetch__"`
  (a global — faked by `vi.stubGlobal('fetch')` / assigning `global.fetch` / or a
  network-level mocker `nock`/`msw`, which are URL/host-based and module-agnostic).
  An imported HTTP client → its import specifier: `axios`, `got`, `node-fetch`,
  `undici`, `ky`, `superagent`, `request`, `node:http`/`http`, `node:https`/
  `https`. Resolved from the nearest `import`/`require` binding of the callee's
  root identifier in the boundary file.
- **subprocess:** `M = "child_process"` (or `node:child_process`) for
  `exec/execSync/spawn/execFile/execFileSync/fork`; `M = "execa"` for `execa`.
- **db:** the client's import specifier at the construction/call: `ioredis`/
  `redis`, `pg`, `mongodb`, `mongoose`, `@prisma/client`/`prisma`, `mysql`/
  `mysql2`, `knex`, `sequelize`, `typeorm`.
- **fileio:** `M = "fs"` family (`fs`, `node:fs`, `fs/promises`, `node:fs/promises`).
  (On this corpus `wd` fileio N=0, so fileio matters only for `rest`.)

**Binding-precedence rule (frozen, deterministic — closes the `fetch`/alias
ambiguity).** The callee's root identifier `id` at the call site is resolved by a
fixed precedence over a single-file static scan:
1. If the call is a member access `X.m(` (the callee is preceded by `.`), resolve
   `X`'s binding (recurse on the receiver's root id), never a global.
2. Else if `id` has ANY in-file `import`/`require` binding (default, named,
   namespace, aliased `import {get as g}`, or destructured `const {exec} =
   require('child_process')`), `M` = that binding's source specifier. **An in-file
   import binding ALWAYS wins** — so `import fetch from 'node-fetch'` → `node-fetch`,
   never `__global_fetch__`.
3. Else if `id == "fetch"` (or `globalThis.fetch`/`global.fetch`) with NO in-file
   binding → `M = "__global_fetch__"`.
4. Else (a local wrapper / re-export / param with no catalog-module binding) →
   `M = "UNRESOLVED"`.

A boundary with `M = "UNRESOLVED"` is **conservatively `failure_untested`** under
every linkage (it cannot match a mock). Because UNRESOLVED biases toward untested
→ toward POSITIVE — the one direction the gate is NOT otherwise robust to — it is
governed by a **pre-registered abort**, not just disclosed:

- The UNRESOLVED fraction is **reported PER ARM** (`wd`, `rest`, `seamed`).
- **Abort clause:** if `unresolved_fraction(wd) > STEP1B_UNRESOLVED_ABORT` (0.30),
  the `wd` failure-test number is declared **UNCOMPUTABLE** (module extraction too
  weak on this corpus) and reported as a **null/inconclusive result, never a
  POSITIVE**. Set blind, before any extraction is run.
- Below the abort, a POSITIVE must additionally survive the **drop-UNRESOLVED-`wd`
  re-cut** (recompute the rate over only resolved `wd` boundaries; §6).

## 4. The OUTCOME — `failure_tested` (frozen detection catalogs)

For a boundary `B` (file `F`, module `M`), define three mutually-exclusive states
over its **linkage set** of test files (§4.3):

- **`failure_tested`** — ∃ test `T` in the linkage set with BOTH (a) a mock of `M`
  AND (b) a failure simulation, co-occurring in `T` (§4.4 pairing).
- **`mocked_only`** — `T` mocks `M` but NO failure simulation: the module is faked
  happy-path; the **failure path is still untested**.
- **`failure_untested`** — neither (= `mocked_only ∪ no-mock`). The binary metric
  outcome (oriented so `wd`-more-untested → ratio>1, the SAME direction as
  E9/Step-1, so their two-sided floor + machinery apply unchanged).

`failure_tested_rate(arm) = mean(failure_tested over arm)` is the **absolute-rate
metric** (the two-way headline). The **catalogs below are FROZEN families**: the
detector implements exactly these; adding a construct after a number exists voids
the gate and must be disclosed (the Floor-rule discipline). Within a family,
spelling variants (`Once` suffixes, whitespace) are implementation detail.

### 4.1 Mock-of-`M` detection (a) — frozen family

`T` mocks `M` iff any of:
- `vi.mock(<s>)` / `jest.mock(<s>)` / `vi.doMock` / `jest.doMock` where `<s>`
  resolves to `M` (relative `<s>` resolved like a normal import to the same target;
  bare `<s>` matched against `M`'s package name / a leading subpath).
- a manual mock file `**/__mocks__/<M>.*` exists in the repo (implemented), OR a
  jest/vitest config `moduleNameMapper` / `setupFiles` entry that names `M`
  (**DEFERRED — immaterial, disclosed 2026-06-16:** the config-parsing arm is not
  implemented; the verification sweep found **zero** FC-module config mocks on this
  corpus — e.g. n8n's `moduleNameMapper` is ts-jest path aliases, `setupFilesAfterEnv`
  is `jest-expect-message` — so it would credit nothing here, and its absence
  *under*-credits `failure_tested`, i.e. biases away from OVERSTATED, the safe
  direction. Recorded so the frozen catalog and the impl do not silently disagree).
- network-level (kind=network only, module-agnostic): `nock(` (import + call) or
  `msw` (`setupServer`/`rest.`/`http.`/`HttpResponse`) present in `T`.
- `sinon.stub(` / `sinon.mock(` on `M`'s binding; `jest.spyOn(X,…)` / `vi.spyOn(X,…)`
  where `X` is `M`'s imported binding.
- for `M=="__global_fetch__"`: `vi.stubGlobal('fetch'…)`, `global.fetch =`,
  `globalThis.fetch =`, or a network-level mocker (`nock`/`msw`).

### 4.2 Failure-simulation detection (b) — frozen family, THE discriminator

`T` simulates a failure iff any of the following. Each entry carries a frozen
**matcher granularity**: `[FLAT]` = the token's presence in the blob suffices;
`[BRACED]` = needs the call's argument / callback span, read with a paren/brace-
balanced window capped at `STEP1B_BRACE_WINDOW` (600 chars) from the token.
**Permissive rule (frozen):** a `[BRACED]` entry whose window cannot be parsed
deterministically is counted as **failure-sim PRESENT** (over-credit). This makes
every detection gap over-credit `failure_tested` → bias toward OVERSTATED and
**away from POSITIVE** — inverting the under-count direction the critique flagged
(POSITIVE is robust to over-crediting; OVERSTATED is separately guarded by the
strict linkage + strict re-pairing §4.4 + the §6 bare-assertion exclusion).

- `[FLAT]` `.mockRejectedValue(` / `.mockRejectedValueOnce(`
- `[BRACED]` `.mockImplementation(` / `.mockImplementationOnce(` whose callback
  body contains `throw` OR `Promise.reject` OR `reject(`
- `[BRACED]` `.mockReturnValue(` / `.mockResolvedValue(` / `.mockResolvedValueOnce(`
  whose argument denotes failure: `Promise.reject`, `{ ok: false`, `{ status:`
  with a 4xx/5xx literal, `{ statusCode:` 4xx/5xx, `new Error`, `{ error:`
- `nock(…).replyWithError(` `[FLAT]` OR `nock(…).reply(` with a 4xx/5xx status
  literal in the window `[BRACED]`
- msw error: `HttpResponse.error()` `[FLAT]`, `new
  HttpResponse(null,{status:<4xx/5xx>})` `[BRACED]`, `res(ctx.status(<4xx/5xx>))`
  `[BRACED]`, `res.networkError(` `[FLAT]`
- `[FLAT]` `sinon` `.rejects(` / `.throws(`
- `[BRACED]` a mock factory (`vi.mock(M,()=>…)` / `jest.mock(M,()=>…)` /
  `__mocks__/M`) whose body `throw`s or returns a rejecting / `ok:false` / 4xx-5xx
  value
- `[FLAT, DESCRIPTIVE-ONLY]` a bare `.rejects.` / `expect(…).rejects` / `.toThrow(`
  assertion with NO mock-of-`M` wired to it. **Weakest signal.** It IS counted in
  the permissive `failure_tested` rate (over-credits tested → safe for POSITIVE),
  but is **EXCLUDED from the strict count that decides OVERSTATED** (§6) and from
  the §4.4 strict re-pairing, because a pure-logic `.rejects` is not evidence
  *this boundary's* failure is tested. Reported separately.

### 4.3 Linkage set — frozen, BRACKETED (the linkage hard part)

Reported under two linkages that bracket the truth; the gate (§6) uses each on the
side it is conservative for:

- **L-import (TIGHT — under-credits; used for the OVERSTATED direction):** test
  files `T` such that `F` is import-linked to `T` by re-running `coverage.py`'s
  import scan **retaining the `(test, source)` edge** (a resolved relative/alias
  import of `F` in `T`; `build_coverage` currently keeps only the covered-source
  set and discards `T`, so this is a net-new index on the same resolver) OR `T` is
  `F`'s mirror-stem test, AND `T` satisfies (a) for `M`. Misses tests that mock
  `M` while exercising a higher-level unit that imports `F` only transitively →
  under-credits `failure_tested`.
- **L-module (LOOSE — over-credits; used for the POSITIVE direction):** a net-new
  per-module test index — ANY test file `T` in the repo (plus repo-level
  `__mocks__/M`, `setupFiles`, `moduleNameMapper`) that satisfies (a)∧(b) for `M`
  → credit ALL FC welds of module `M`. Over-credits (one `axios` failure test
  credits every `axios` weld).

### 4.4 The (a)∧(b) pairing — frozen, with a strict sensitivity

Primary pairing = **file-level co-occurrence**: (a) and (b) both appear in the
same test file `T`. This does not prove the failure-sim is wired to `M`'s mock
specifically (only that `T` mocks `M` and simulates *a* failure) → it
**over-credits `failure_tested`**, which biases toward OVERSTATED. So:
- a POSITIVE (low `failure_tested`) is **robust** to this over-credit;
- an OVERSTATED must **survive a strict re-pairing** (the failure-sim attaches to
  `M`'s own mock handle / same statement / same `nock`/`msw` scope) — reported as
  a sensitivity (§6).

## 5. The metric machinery — REUSED from coverage.py, keyed on `failure_untested`

- **THE VERDICT METRIC — `failure_tested_rate(wd)`** per arm, under L-import and
  L-module, with per-kind breakdown (network/subprocess/db). This absolute rate is
  the **gate** (§6, two-sided). Fully powered (`wd` N=1727).
- **REPORTED CONTEXT (not a gate — §0 amendment): matched `failure_untested`
  ratio** = (`wd` untested rate)/(control untested rate), direct standardization
  over `(file-churn tercile × site-size tercile)` strata (`ENRICHMENT_MIN_STRATUM`
  =5 per arm; dropped strata logged), repo-cluster bootstrap 95% CI
  (`ENRICHMENT_BOOTSTRAP_B`=2000, `SEED`=0). Reuses `coverage.py`'s `matched` /
  `boot_ci` / `per_repo` verbatim, keyed on the new outcome. Controls reported:
  `rest`, `seamed` (underpowered), `wnd`. **Tells whether the untested-ness is
  weld/demand-specific — a caveat on the verdict, not the verdict.**
- **Companion effect sizes (reported):** matched **odds ratio** + **raw rate
  difference** next to the risk ratio (robust to high-untested base-rate
  compression). The **base-rate ceiling** (`1 / rest_untested_rate`) is reported so
  a compressed risk ratio is read with the odds ratio, not over-interpreted.
- **dev vs heldout reported separately.** Nothing is tuned on dev — every
  threshold is frozen here.
- **Simpson guard** on the reported contrast (`ENRICHMENT_PERREPO_MIN_FINDINGS`=20,
  majority `ENRICHMENT_PERREPO_MAJORITY`=0.60).
- **UNRESOLVED fraction reported PER ARM** (`wd`/`rest`/`seamed`). The §3 abort
  (`unresolved_fraction(wd) > STEP1B_UNRESOLVED_ABORT`=0.30 → `wd` number
  UNCOMPUTABLE, never POSITIVE) is checked **before** any verdict is read.

## 6. The verdict — ABSOLUTE rate, two-sided (set blind, before any flag is seen)

The verdict is the **`wd` failure-tested rate** against two frozen thresholds
(`STEP1B_TESTED_LOW`=0.20, `STEP1B_TESTED_HIGH`=0.40), each read under the linkage
that makes it **conservative** (opposite linkages — see end of section). **No
comparison gates the verdict** (§0 amendment); the §5 contrast is reported as a
weld/demand-specificity caveat only.

- **POSITIVE (dense untested-failure targets — a recommender wedge by yield):**
  `failure_tested_rate(wd, L-module) ≤ STEP1B_TESTED_LOW` — ≤20% of welded FC
  failures are mock-tested **even under the generous (over-crediting) linkage**, so
  the recommender has dense, real untested targets. Must survive the
  drop-UNRESOLVED-`wd` re-cut (§3) and clear the §3 abort.
  **Reported caveat (not a gate):** the §5 `wd`-vs-`rest` contrast says whether the
  targets are *weld/demand-specific*. If that contrast is **flat** (matched ≤
  `ENRICHMENT_FALSIFIER`=1.1 / OR≤~1.1 / CI-lo≤1), the targets are real but **not
  differentiated** from any FC boundary — a plain boundary inventory would surface
  them too (Step-1's demand-null, in a new guise). Reported alongside POSITIVE, it
  does not change the verdict; it scopes the *claim* to yield, not classification.
- **OVERSTATED (untestability claim too strong):**
  `failure_tested_rate(wd, L-import) ≥ STEP1B_TESTED_HIGH` — ≥40% of welded FC
  failures are mock-tested **even under the strict (under-crediting) linkage** and
  the **strict deciding catalog** = (a)∧(b) **excluding the bare-assertion family**
  (§4.2 `DESCRIPTIVE-ONLY`). Must survive the strict (a)∧(b) re-pairing (§4.4).
  Recorded honestly: pry's "welded = can't inject a failure" overstates real-world
  untestability (module-mocking tests these failures without a code seam); the
  recommender must down-rank already-failure-tested welds. This is the
  **informative / hard-to-reach** direction — failure-tests are rare, so a high
  rate is a genuine surprise, not a base-rate artifact.
- **WEAK / inconclusive:** `STEP1B_TESTED_LOW < failure_tested_rate(wd) <
  STEP1B_TESTED_HIGH`, or `wd` UNCOMPUTABLE (§3 abort).

Rationale for the thresholds: 0.40 = "failure-testing is *common*, not the
exception" → the untestability framing cannot stand; 0.20 = "failure-testing is
the *exception*" → the recommender has dense real targets. **Opposite linkages**
(L-module for POSITIVE, L-import for OVERSTATED; `L-module ≥ L-import` always) make
each direction conservative, and **deliberately widen the WEAK band** (a wider "we
don't know" is the honest cost of double-conservatism). POSITIVE and OVERSTATED
are provably **mutually exclusive** (both would need `L-import ≥ 0.40` AND
`L-module ≤ 0.20`, contradicting `L-module ≥ L-import`), so the gate cannot
self-contradict. **Honest read of POSITIVE:** because failure-tests are rare, a
low `wd` rate is *expected*; POSITIVE confirms the recommender has targets (a real
product fact) but is the *less surprising* outcome — the reported contrast + the
OVERSTATED arm carry the discriminating information.

## 7. What this measures — wedge EXISTENCE, not product value (the real point)

Step-1b tests whether a **point-of-use recommender wedge EXISTS** — i.e. whether
welded FC failure paths are actually untested. It does **NOT** establish
recommender *product value*: a static co-occurrence rate cannot show that adding a
recommended fault-test catches real defects (E9, dead) or that these untested
paths *matter* (the metric is explicitly one-directional, §8: untested ≠ buggy).
The earned claim stops at wedge existence (yield), with the §5 contrast as the
weld/demand-specificity caveat.
- POSITIVE → the wedge exists by yield: "demand-welded FC boundary whose failure
  is untested → candidate to add a fault test / introduce a seam; already
  failure-tested → lower priority." A *targeting* signal, not a defect or
  product-value claim — and **if the reported contrast is flat, the targets are
  not weld/demand-differentiated** (a plain FC-boundary inventory would surface
  them too; reported, not gated).
- OVERSTATED → no wedge in this framing: module-mocking already tests these
  failures, so "untestable" is the wrong pitch; record honestly.
Either way the result is reportable and directly shapes whether the ratchet-vs-
ship-as-is decision (`docs/handoff.md` Discuss) has a recommender wedge under it.

## 7.5 Open Items (recorded, deliberately NOT resolved here)

- **Reported-contrast reachability (critique C3).** With near-ceiling untested
  base rates (failure-tests are rare), the odds-ratio's tail cells are small, so
  the repo-cluster bootstrap CI-lower may not clear 1.0 even at a large OR point
  estimate. Post-amendment (§0) the contrast no longer gates the verdict, so this
  only affects how confidently the **weld/demand-specificity caveat** can be
  stated — not whether POSITIVE/OVERSTATED is reached. **Recorded, NOT
  pre-rescued.** The closeout reports the observed base rates + whether the
  contrast's CI-lo>1 was reachable; if not, the specificity caveat is reported as
  "underpowered to determine," not forced either way.

## 8. Standing non-claims (restated at closeout)

- **Static fingerprint, not executed proof.** "failure simulated by a test" = the
  presence of a frozen failure-sim construct in a linked test file, NOT a proven
  executed failing assertion. No test suites run; no LLM; no outbound (AC4-clean).
- **File-level (a)∧(b) pairing** does not prove the failure-sim is wired to `M`'s
  mock (over-credits `failure_tested`); OVERSTATED needs the strict re-pairing.
- **Linkage is a bracket, not a point:** L-import under-credits (transitive
  imports), L-module over-credits (module-global). The truth is between; the gate
  uses each on its conservative side.
- **Module extraction is best-effort;** UNRESOLVED is conservatively untested and
  reported; POSITIVE must survive dropping UNRESOLVED `wd`.
- **`nock`/`msw` are URL/host-based,** credited to all in-scope network welds in a
  test file (module-agnostic over-credit, disclosed).
- **Correlational**, never causal; one-directional (a failure-tested weld is not
  "safe"; an untested one is not proven buggy — only untested).
- **Frontend/backend file-kind residual** (named in E9/Step-1) is reported via a
  backend-only contrast cut, not fully neutralized.

---

*Frozen at Step-1b. The harness reads `config.py`; it does not re-derive these
numbers. Changing any threshold, catalog family, linkage, or arm definition above
after a Step-1b number exists voids the honesty gate and must be called out
explicitly in the closeout.*
