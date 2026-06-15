# Concept Ideation — does pry have a wedge after both prediction payoffs died?
Date: 2026-06-16

Trigger: operator chose "ideation: is there a wedge?" after step-1 coverage came
back FALSIFIED (the second falsification). Question: is there ANY real product
wedge for pry given no proven *prioritization* payoff? Detail: `docs/eval-gate.md`
(E9 Tier-1 + Step-1), `docs/roadmap.md` (premise-update banner), `initial-plan.md`.

## Concept

The decisive reframe: **`initial-plan.md` defines pry as TWO channels with two
different validity disciplines (§5), and only ONE was ever built.**

- **Map (PREDICTION channel)** — the injectability risk ranking. Validity basis:
  *lift over a churn baseline* on error-handling defects (§5, §8). **This is the
  channel that just died** — E9 (bugs, matched 1.05) + step-1 (file coverage,
  0.95). This is precisely premortem §13.B.1 ("the map failed to beat the churn
  baseline") — faced, not rationalized. pry ships *only this channel today.*
- **Floor (CLAIM channel)** — the syntactic error-handling bug finder (empty
  catch; swallowed boundary error; **log-and-continue on a mutating path** →
  the credits-debited/charge-lost shape, `initial-plan.md` §1.4). Validity basis:
  *precision of a fact* (zero-FP target, §5), Aspirator lineage (Yuan OSDI'14
  found 100+ developer-confirmed bugs from 3 such rules). **Never built. NOT what
  E9/step-1 tested.** Its value does not depend on the dead prediction premise.

So "does pry have a wedge?" is mostly "is the un-built, un-killed CLAIM channel a
wedge?" — a different question than the one the validations answered.

## Product Posture

Solo research tool dogfooded through charness; distribution = a charness
`external_binary` consumed by the `quality` skill (already wired). Not a startup;
no viral/growth logic. Bets are evaluated by *evidence on the author's own repos
first* (§9/§13), under zero-LLM (AC4) + no-outbound-on-corpus constraints.

## Verified Facts

- The MAP's prioritization payoff is falsified twice, pre-registered, robust
  (E9 1.05 CI[0.96,1.18]; step-1 0.95 CI[0.88,1.02]). Source: `docs/eval-gate.md`.
- The MAP is a *precise classifier*: network/subprocess 100% (261/261) on 4
  third-party apps; ex-cosmetic-tail 89.3% ≈ human 88%. Source: eval-gate H3.
- The FLOOR is unbuilt: "Not built yet in Layer 0: the syntactic floor."
  Source: `docs/roadmap.md` "Shipped" section.
- pry's `demand` refinement adds nothing to coverage over a plain welded/seamed
  split (wd-vs-welded-not-demand 0.94). Source: step-1.
- Author's own Python = welded glue → KILLed as pry's analyzer target; TS/JS is
  the surface. Source: `docs/kill-gate.md` / precision-gate.

## Assumptions (to test, not assert)

- A1: linters miss the floor's rules — esp. *swallowed boundary error then a
  mutation commits* (ruff/eslint pass non-empty catches; `initial-plan.md` §1.4).
  Test: build the rule, find cases ruff/eslint pass that the floor flags.
- A2: the floor fires at high precision on real repos (the claim-channel bar).
  Test: implement Aspirator's 3 rules, sample ~30 flags, label precision.
- A3: the floor fires on *meaningful* bugs in a repo the author cares about
  (repo-fit, premortem §13.A — the real killer). Test: among flags, how many are
  real defects vs trivially-correct swallows.
- A4 (ratchet wedge): some teams have bought into DI discipline and want a "no
  new welded boundary" gate. Unverified demand.

## Decision Candidates (wedges), scored on problem / demand / status-quo / moat

1. **(f) Build + precision-test the syntactic FLOOR — the un-killed claim
   channel.** Problem: real (error-handling bugs are the Pareto, Yuan). Demand:
   Aspirator's 100+ confirmed bugs is third-party evidence the *pattern* matters.
   Status-quo gap: linters miss swallowed-then-commit (§1.4). Moat: the boundary
   catalog + dataflow-lite (already built for the map) — reused, not rebuilt.
   **Not premised on the dead prediction.** Risk: repo-fit (A3) + precision (A2)
   both unproven; could be correct-but-useless on the author's corpus.
2. **(c) Seam-coverage RATCHET (CI gate: "no new welded boundary").** Problem:
   architecture-conformance drift. Demand: niche — only DI-bought-in teams.
   Status-quo: ArchUnit/dependency-cruiser exist but none target welded boundary
   calls specifically. Moat: catalog + seam recognition. **Survives the
   falsification** (policy-conformance, not risk prediction) and is shippable on
   the *already-validated* 100% precision — no new validation needed. Smaller TAM.
3. **(a) Fault-test enablement / (b) testability-debt RANKER / (e) feeder to
   mutation testing.** All re-lean on "welds concentrate risk," which is the dead
   premise. (b)'s "ranker" is exactly what the critique killed. Demote.
4. **(d) Measure the open line-level coverage claim on an owned/local corpus.**
   Not a wedge — a *de-risk experiment* for a testability wedge. Subordinate:
   only run it if (a/testability) becomes the chosen direction.
5. **(0) No wedge → ship the map as-is into `quality`, stop.** Legitimate. Banks
   the validated precise classifier; makes no prioritization claim.

## Dependency Order

The upstream choice that most changes the rest: **is the bet the CLAIM channel
(floor) or a POLICY gate (ratchet) or NEITHER (stop)?** Everything else (line-
level measurement, fault-test framing) is downstream of that. The floor (f) is
the highest-information bet because it tests the half of the founding thesis that
was never tested — resolving it tells you whether pry's *original* reason to exist
holds, independent of the now-dead map.

## Recommended Current Decision

**Build a MINIMAL floor (Aspirator's 3 rules) and run a cheap, offline precision +
repo-fit test before committing to it as the direction.** Rationale: it is the
only candidate that (a) is not premised on the falsified prediction, (b) has
third-party prior evidence the pattern matters (Aspirator), (c) reuses existing
infra (parse/catalog/dataflow-lite), and (d) resolves the biggest open question in
the whole project — whether the *sound* channel pry was designed around is real.
The ratchet (c) is the fallback if the floor's repo-fit fails: it needs no new
validation and ships on existing precision.

This is NOT "the floor is a proven wedge." It is "the floor is the un-killed bet
worth the cheapest possible test before stop." Honesty tripwire (premortem §13.A):
if the floor is high-precision but fires only on trivial/correct swallows (no
meaningful bugs) on a repo the author cares about, that is a KILL for the floor →
fall back to (c) or (0), reported honestly like E9/step-1.

## Alternatives and Tradeoffs

- Ship-as-is/stop (0): lowest cost, but leaves the founding *claim* thesis
  untested — you would stop one cheap experiment short of knowing if pry's
  original reason to exist was ever valid.
- Ratchet (c): shippable now, no new validation, but bets on unverified niche
  demand (A4) and a smaller surface.
- Line-level measurement (d): only de-risks a *testability* wedge that the data
  has already made unattractive; do it only behind a chosen testability direction.

## World Model

User = a developer (first: the author) who wants real error-handling defects
surfaced that linters miss, OR a team enforcing DI discipline. Job-to-be-done for
the floor: "tell me where a boundary failure is silently swallowed and then state
is committed anyway" — a *fact*, actionable as a fix. Status quo: ruff/eslint
(miss it), Aspirator (academic, unmaintained, no TS), CodeQL/Semgrep (security,
different game). The moat is the per-language boundary catalog + the dataflow-lite
that recognizes mutation→swallow→commit.

## Truth Tests

- Floor precision: of ~30 sampled floor flags on the already-cloned corpus
  (offline), what fraction are real error-handling defects? (Claim-channel bar.)
- Repo-fit: do the flags include *meaningful* bugs, or only trivial swallows?
- Status-quo gap: pick flagged cases; confirm ruff/eslint pass them.
- (Ratchet, if pursued) demand: would any real team turn on a "no new weld" gate?

## Edge and Expansion

Edge = the catalog + dataflow-lite already exist (sunk cost reused), and the
sound-channel framing is defensible where the prediction channel was not. If the
floor lands, Layer 1 (seam PRs for floor hits) and Layer 2 (injection oracle) are
the original unfolding — but only the floor needs to be proven first.

## Agent/Human Fit

Agent-first: pry is a deterministic CLI emitting JSON, invoked by the `quality`
skill. The floor's output is a *claim* (fix this), which fits an agent's
remediation loop better than the map's *ranking* (which needs human judgment and
just failed validation). This mildly favors (f) over the map for agent-native use.

## Next Step

Route to **`spec`** for a bounded floor-precision experiment: Aspirator's 3 rules
on the already-cloned offline corpus, ~30-flag precision + repo-fit labeling,
pre-registered go/kill (high precision ∧ ≥1 meaningful bug class → build the floor;
else → ratchet (c) or ship-as-is (0)). Keep the same honesty discipline (prereg
before numbers; report a kill honestly). Hold (a)/(b)/(e); (d) only behind a
chosen testability direction.
