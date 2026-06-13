# (b)-axis testability-surface gate — ceal Python (analyzer-free, 2026-06-13)

The F24 gate, run **analyzer-free** (hand-sample, no Rust) on the independent corpus
`ceal` @ `8238b245`. Classification rule = the **frozen two-tier F18** (finding C
resolved): headline `SEAMED/WELDED` = `externalSubstitution` (runner-swappable
provider/endpoint/client); operand-parameterization recorded on a separate
`inputSimulation`-seam tier. Numbers were frozen **before** this run (§13 B.1).

Scope (finding A): ceal Python = 461 skill scripts (`charness-public` +
`ceal-native`) + a few repo scripts — agent **tooling/automation** glue. The headline
agent boundaries (LLM/Slack/calendar) are in ceal's **TS** (out of Layer-0 scope).
**Test files excluded** (`tests/`, `test_*.py`): the gate measures product-code
testability, not test code.

## Sample (N = 59 boundary sites, stratified; non-test product code)

Rare high-value kinds sampled **exhaustively** (net 6/6, db 3/3, tz 4/4); volume
kinds sampled across files. All operands were local params / CLI args (`args.x`) /
env-derived — verified, not assumed.

| kind | n | substitution | input-sim | cautilus leg | note |
|---|---|---|---|---|---|
| network (`urllib.request.urlopen`) | 6 | WELDED 6 | YES 6 | es | url-as-data param; **confirmed welded** — `check_coverage_lib.py` must `mock.patch.object(...urlopen...)` |
| db (`sqlite3.connect(path)`) | 3 | WELDED 3 | YES 3 | es | path param → fixture/`:memory:` |
| tz (`ZoneInfo(key)`) | 4 | WELDED 4 | YES 4 | es | key param, all in `try/except ZoneInfoNotFoundError` — the ceal bug class; value-shaped failure is input-injectable |
| subprocess | 12 | **SEAMED 3**, WELDED 9 | YES 12 | tc/es | SEAMED = `command` injected as a param (generic runner wrappers); WELDED = hardcoded exe (`"git"`/`"python3"`/`"cautilus"`) |
| clock (`datetime.now`/`time.*`) | 11 | WELDED 11 | **NO 11** | es/tc | **hard welds** — no operand controls the current time; must substitute the clock |
| env (`os.environ`/`getenv`) | 7 | WELDED 7 | YES 7 | is/es | env is the canonical runner-controllable input |
| file I/O (`read_text`/`write_text`/`open`/`mkdir`/`glob`) | 16 | WELDED 16 | YES 16 | es/eo | path always param/CLI/derived; **literal-absolute-path opens = 0** (full scan) |
| **total** | **59** | **SEAMED 3 · WELDED 56 · AMBIGUOUS 0** | YES 48 · NO 11 | | |

Population checks (full non-test scan, not sampled): `self.<attr>.<boundary>(` = **0**
(no OOP DI), `open(func())`/computed-target = **0**, injected-callable params
(`runner=`/`client=`/`*_fn=`) = **1** (`ci_local_gate_parity_lib.py:146`
`yaml_loader: Callable`). ceal Python is **procedural, like pry's own harness.**

## F24 metrics (frozen rule applied)

| metric | value | frozen threshold | result |
|---|---|---|---|
| **recognizability** | ~1.0 of leaf surface | high | clears (hidden-wrapper under-count: the 3 `command`-param wrappers attribute caller boundaries to the wrapper) |
| **decided-fraction** `(S+W)/recognized` | **1.00** (59/59) | mute-gate `< 0.40` | **NOT mute** — pry sees ceal Python fully |
| **welded-fraction (substitution)** `W/decided` | **0.95** (56/59) | band `[0.15, 0.85]` | **OUT of band (high)** — bare welded bit does not discriminate |
| **ambiguous-reason histogram** | empty (0 ambiguous) | steers ladder | no extension signal |
| **cautilus-demand lift (substitution)** | ≈ **1.0** (welded% at es/tc ≈ overall, both 0.95) | > 1 | **no lift** — substitution-welded is uniform |
| **input-sim tier (two-tier, frozen F18)** | welds: **YES 45 / NO 11**; hard-weld = 11/59 = **0.19** | — | discriminates: hard-welds concentrate **100% at clock/timing** |

**Extrapolated to the full ~1130-site surface** (by-kind proportion; file I/O ~865
dominates): welded ≈ 0.98, SEAMED < 0.02, hard-weld (clock 41) ≈ **0.036**,
input-sim-redirectable welded ≈ 0.94.

## Reading

1. **The bare (b)-map does NOT discriminate on ceal Python.** ~95% welded, no
   substitution lift → as a standalone seamed/welded *ranker* the map ≈ the
   any-boundary baseline (flag-every-boundary). This fails the frozen GO criterion
   ("welded in band").
2. **It is a *saturated-welded / glue* outcome, NOT an *undecidable* one.** decided =
   1.00 (the F24 KILL·HANDOFF rationale is "injectability not statically decidable" —
   here it is the **opposite**: fully decidable, uniformly welded). This is a **fourth
   outcome F24 did not enumerate** (its EXTEND/KILL branches are both muteness-keyed).
3. **The frozen two-tier lens recovers one real, small signal.** 45/56 welds are
   cheaply **input-redirectable** (fixtures/CLI/env — exactly how ceal's own tests
   work; `mock.patch` appears only for net/urlopen where input-redirection can't
   reach). Only 11/56 (~4% of the full surface) are **hard welds** — all clock/timing
   — = the genuine cautilus `externalSubstitution`/`triggerControl` demand. That set
   is tiny and trivially found (`grep datetime.now`); a Rust analyzer is overkill for
   it.
4. **ceal Python ≈ the harness in shape** (decided 1.0, welded ~1.0, procedural). The
   "independent" gate corpus did not present a *different* shape — it **confirmed the
   glue shape**. Third convergent signal that the author's agent-tooling repos are
   glue in Python; the interesting agent surface is TS (finding A).

## Verdict

**KILL · HANDOFF (substitution-ranker), "saturated-welded / glue" variant.** By the
frozen headline criteria (welded out of band; no substitution lift) ceal Python is
**not a GO**; closest frozen label is KILL·HANDOFF, qualified (decidable, not
undecidable). **No Rust analyzer is built** (the kill-cheaply discipline holds across
both gate axes). Convergent with the (a)-gate RE-TARGET.

**Anti-wriggle (§13 B.1):** the input-sim tier (a *frozen* secondary metric) does
discriminate, but it does **not** flip the headline verdict — it informs the handoff
and the recalibration candidates below. The verdict rests on the frozen headline
criteria, not on a metric promoted after seeing the result.

## Recalibration candidates (F24, for *between-runs* tuning only — never this run)

- F24's verdict taxonomy needs a **fourth branch**: *decided-high but
  welded-saturated (no lift)* — distinct from mute-EXTEND and undecidable-KILL.
- The **welded-band `[0.15,0.85]` tests the bare bit**, which the substrate+lens
  model (F25) says is *not* the product. A glue corpus will always breach it. The GO
  test for the (b)-axis arguably should be **lens discrimination** (does a *frozen*
  lens — input-sim tier / cautilus-demand / error-path — separate actionable from
  not?), not bare-bit discrimination. Candidate F24 revision.

## Strategic fork (needs the author — the (b)-axis analogue of kill-gate.md's fork)

1. **TS frontend** — go where ceal's real agent boundaries (LLM/Slack/calendar) live
   (finding A); nose supports TS; reopens the language scope Layer-0 deferred.
2. **OSS non-glue Python corpus** (§9: distributed systems / data pipelines) where
   boundaries are genuinely *mixed* welded/seamed and the bare bit discriminates.
3. **Re-scope pry's product on glue** from "welded/seamed ranker" to the **two-tier
   lens output** — the hard-weld (clock) extractor + cautilus-handoff list +
   input-sim cheap-test list — accepting the bare-bit ranker thesis does not fit glue.
