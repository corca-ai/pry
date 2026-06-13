# Dogfood control + ceal Python surface (pre-work, 2026-06-13)

Pre-computed for the next session: the (b)-gate's **harness dogfood control** (F25)
and a grounding scan of **ceal's Python boundary surface** for the catalog seed
(`catalog/python.toml`). Done by-hand from source (no analyzer — Layer-0 rule). The
point of doing the control on code we wrote: shake down the protocol + catalog
*before* the ceal gate run, on code with perfect ground truth.

## Harness dogfood control (the protocol shakedown)

Hand-classified every Layer-0-recognizable boundary site in `harness/*.py` under
F18/F19. The harness is procedural (no classes / `self.attr` / factories), so
**ambiguous = 0** — pry sees it fully.

| site | boundary | target origin | strict (F18 pre-config-seam) | with config-seam |
|---|---|---|---|---|
| `mine._git` / `szz._git` / `label_io._diff`: `subprocess.run(["git", "-C", str(repo), …])` | subprocess | exe `"git"` hardcoded; `repo` param | WELDED | WELDED (exe hardcoded) |
| fs ops on `args.out/.labels/.candidates`, `repo` (`read_text/write_text/exists/mkdir`) — ~15 sites | fileio | path from argparse/CLI (`--out` …) | WELDED | **config-seam → SEAMED** (runner redirects to fixtures/temp; bad path injects failure) |
| `config.py`: `os.path.expanduser`, `Path(__file__).resolve()` (module-level) | env/fileio | hardcoded | WELDED | WELDED |
| `repo_fit.assess(...)` | — | pure decision core | **EXEMPT** (functional core) | EXEMPT |
| `szz.ast.parse`, `label_io.hashlib.sha256` | — | pure computation | not a boundary | not a boundary |
| ~15× `_git(...)` call sites (szz) | subprocess (hidden) | wrapped behind `_git` | **UNDER-COUNTED** (L0 doesn't follow the wrapper) | under-counted |

**(b)-gate metrics on the control** (recognizability high; decided-fraction = 1.0,
ambiguous = 0 — clears the mute-gate trivially):

| reading | substitution welded-frac | inputSimulation-seam | band? |
|---|---|---|---|
| **two-tier (FROZEN, F18; finding C)** | ~21/21 ≈ **1.0** | ~14/21 input-redirectable (fs-on-args, git-repo-arg) | substitution OUT of band (all-welded) — but this is a **control**, welded-but-fine (F25); ceal carries the band |
| ~~loose "any param = seam"~~ (rejected = option 2) | ~6/21 ≈ 0.29 | — | its discrimination was an artifact of the harness's *hardcoded-git* anchor; collapses to ~0 on anchor-free glue → rejected |

The harness under the frozen rule is the textbook two-tier shape: **substitution-welded
1.0** (no provider/endpoint/client is parameterized — git exe hardcoded, fs is builtin)
yet **input-sim-seam high** (most welds redirect to fixture/temp paths). That is the
honest picture of throwaway CLI glue — *can't substitute boundary behavior, can redirect
inputs* — and it directly confirms substrate+lens (F25): welded-but-fine, with the weak
input-sim tier as the cheapest test path.

### Calibration lessons (what the control proves)

1. **config-seam is load-bearing — RESOLVED two-tier (finding C, frozen F18).** A
   loose "any parameterized target = seam" rule swallows everything on glue (the
   monkeypatch trap's mirror); the harness's apparent 0.29 discrimination was an
   artifact of its *hardcoded-git* anchor and would collapse on anchor-free glue.
   Frozen resolution: the headline SEAMED/WELDED bit = **externalSubstitution**
   (runner can swap the boundary's provider/endpoint/client), and operand-
   parameterization is recorded on a **separate `inputSimulation` tier**, never folded
   into the headline. So the harness is honestly substitution-welded 1.0 with a high
   input-sim tier — the lens, not the bit, makes a weld actionable.
2. **Functional-core exemption works.** `repo_fit.assess` (docstring: "unit-testable
   without git or the agent") is pure → correctly unflagged. Right answer.
3. **Hidden-wrapper under-count is real and visible.** `_git` wraps `subprocess.run`;
   L0 recognizes the 1 call inside `_git`, not its ~15 call sites → honest
   under-count = exactly F22 rung 3 (deferred). The harness demonstrates it.
4. **welded ≠ bad (confirms F25 / substrate+lens).** Even strict-100%-welded glue is
   *welded-but-fine* — nobody needs to failure-inject git in a throwaway eval. Raw
   welded is uninformative; only the lens (would anyone test this failure?) makes it
   actionable.

## ceal Python boundary surface (catalog grounding)

Scan of ceal Python (472 files; ceal is 472 py / 797 ts / 536 js):

| boundary | signal (file counts) | kind |
|---|---|---|
| **file I/O** | `.read_text` 189, `.exists` 81, `.write_text` 75, `.mkdir` 74, `.glob` 50, `.open` 24, `open(` 12 | fileio (largest) |
| **subprocess** | `subprocess.run` 107, check_output 2, Popen 1 | subprocess |
| **env** | `os.environ` 41 | env |
| **clock** | `datetime.now`/`.now(` 33, `time.sleep` 3, `time.time` 1 | clock |
| network | `urllib.request`/`urlopen` 7, `socket` 2 | network (small) |
| tz | `zoneinfo`/`ZoneInfo` 4 | clock (the profile's bug) |
| db | `sqlite3.connect` 3 | db (tiny) |
| dynamic dispatch | `getattr(` 15, `importlib.import_module` 4, `exec(` 1 | (modest) |
| **agent-API** | openai/anthropic/slack/boto3/calendar = **0** | → TS/JS side |

### Findings carried to the next session

- **A (scope, headline).** ceal's *agent-API* boundaries (LLM dispatch, Slack,
  calendar, provider SDKs) — the surface the "pivot the signal" reshaping centered
  on — are **0 in Python; they live in TS/JS**, out of Layer-0 scope. ceal **Python**
  is file I/O + subprocess glue + clock. So for the Python subset the catalog
  reverts toward the *classic* boundary set (file/subprocess/clock), and the
  cautilus-demand overlap is **subprocess worker-spawn (tc/es) + file/db/clock
  substitution**, NOT LLM substitution. Open: is pry-Python the right surface for
  ceal's *interesting* boundaries, or does the agent surface need a **TS frontend**
  (reopens language scope; nose supports TS; deferred)?
- **B (catalog mechanics).** File I/O — ceal Python's biggest surface — is
  **method-on-receiver** (`.read_text()`), unrecognizable by dotted-module
  fingerprint. nose-grade has no type inference, so the catalog uses receiver-blind
  `[[method]]` fingerprints (FP risk accepted). Validate the FP rate on the gate.
- **C (seam-definition) — RESOLVED 2026-06-13 (two-tier / leg-relative, frozen F18).**
  The headline SEAMED/WELDED bit tracks **externalSubstitution** (a param that selects
  a runner-swappable provider/endpoint/client — `OpenAI(base_url=cfg)`, `[cfg.bin,…]`);
  a param that steers only the *operand/data* of a fixed real boundary (`open(path)`,
  `urlopen(url)`) is WELDED for substitution but tagged **`inputSimulation`-seam** (a
  separate weaker tier). Litmus: *can you make the boundary fail in arbitrary ways via
  this param?* This kills the degeneracy (the loose reading), stays consistent with the
  monkeypatch ruling, and lets the gate report **per-leg lift**. Applied to the ceal
  gate below.
- **D (extend-vs-ceiling).** Dynamic dispatch in ceal Python is modest (`getattr` 15,
  `importlib` 4) → if the gate goes mute, ambiguous is more likely
  same-file-factory/`self.attr` (→ EXTEND rung 1) than runtime/dynamic (→ ceiling).
