# Corpus prune / exclusion log (S1)

Risk R-D contract: **log what was pruned or excluded — no silent truncation.** A
multi-repo sweep can quietly drop candidates and read as "covered everything."
This records the discovery → selection funnel so a fresh reviewer can see what
was considered and why each excluded candidate was dropped.

Reference date: 2026-06-15. Discovery tool: `gh search repos` (authed locally,
handoff step 1) across stratified domain queries; per-finalist features via
`gh api repos/...` (`/languages`, `/contents`, `/commits/<branch>`). No clones in
S1 (clones happen in S2).

## Discovery method (anti-clustering, risk R-A)

Searched **~20 TS/JS domains** (knowledge-base, project-mgmt, headless-cms,
ecommerce, automation, uptime, notes, forum/chat, scheduling, analytics,
bookmarks, forms, media, internal-tools/low-code, feed-reader, password-manager,
dashboard, invoicing, …) and **8 Python domains** (document-mgmt, ecommerce,
monitoring, workflow, search, recipe-webapp, ipam/network, analytics). Stratifying
by domain — rather than by "well-tested" or "clean code" — is the guard against
clustering the slate at the disciplined/low-injection end (the PQ1 gap: the 4 H3
seeds are all 0–5% clock-injection). The slate spans 17+ distinct domains.

## Scorer prunes

`corpus_fit.py` pruned **0 of 33 finalists** — every curated finalist cleared the
pre-registered app-shapedness floor (`CORPUS_APP_SHAPEDNESS_FLOOR = 55`; scores
ranged 75–100, see `corpus_discovery_features.json`). This is expected: the
finalists were curated FROM the stratified search as known applications, and the
scorer's role here is **auditable validation of that curation against a
floor that was fixed before any score was computed**, not blind rediscovery. The
floor would have rejected a library-shaped or stale candidate had one reached the
finalist stage.

## Notable EXCLUSIONS (candidate surfaced in discovery, deliberately not frozen)

### Excluded — libraries / frameworks / components, NOT apps (wrong shape)
The single most common exclusion class. pry needs boundary-welding *applications*
(route handlers / service layer / DB clients / env+config), not single-purpose
libraries whose boundary surface is thin or absent:
- `react-hook-form/react-hook-form`, `jaredpalmer/formik`,
  `rjsf-team/react-jsonschema-form`, `alibaba/formily`, `logaretm/vee-validate`,
  `yiminghe/async-validator` — form *libraries*.
- `cookpete/react-player`, `yocontra/react-responsive`,
  `QwikDev/partytown`, `Vanilagy/mediabunny`, `vuestorefront/storefront-ui`,
  `alibaba/x-render` — UI/media component libraries.
- `puppeteer/puppeteer`, `microsoft/playwright`, `apify/crawlee` — automation
  *libraries*, not self-hosted apps.

### Excluded — backend is NOT TS/JS (would starve pry's server welds)
pry analyzes TS/JS; an app whose backend (where DB/subprocess/network welds live)
is another language would contribute mostly thin frontend welds to the TS arm:
- `appsmithorg/appsmith` (Java/Spring backend), `makeplane/plane` (Python/Django
  apiserver — a *Python*-arm candidate, not picked to avoid over-weighting one
  source), `grafana/grafana` (Go), `apache/superset` (Python).

### Excluded — AI/LLM clustering avoidance (risk R-A)
The 3 AI seeds (flowise, continue, librechat) already represent the AI/LLM
domain. To avoid clustering the slate there, these app-shaped AI candidates were
deliberately **not** added: `langgenius/dify`, `langfuse/langfuse`,
`simstudioai/sim`, `onlook-dev/onlook`, `nocobase/nocobase` (AI no-code).

### Excluded — Python giants, dropped for sweep tractability
Real non-glue apps, but too large to mine within the sweep budget; smaller real
apps were preferred so the per-repo mine+map+join is tractable:
- `getsentry/sentry`, `apache/airflow`, `mlflow/mlflow`, `PrefectHQ/prefect`.

### Excluded — desktop-first / non-server-backed
- `siyuan-note/siyuan` (Go kernel), `toeverything/AFFiNE` (heavy; has a server but
  deprioritized), `TriliumNext/Trilium` (server exists; deprioritized for slate
  size).

## Kept slate (frozen in corpus.json)

25 TS/JS apps (dev 5 / heldout 20) + 8 Python apps (dev 2 / heldout 6) = 33,
spanning knowledge-base, AI, ecommerce, headless-cms, automation, low-code,
analytics, surveys, scheduling, crm, photo-management, bookmarks,
uptime-monitoring, wiki, finance, notifications, media-requests, team-chat
(TS) and document-management, ecommerce, ipam/dcim, metasearch, recipe-webapp,
cron-monitoring, data-analytics, web-monitoring (Python). License mix is recorded
per-repo (permissive + copyleft); inclusion of copyleft repos is intentional —
excluding all copyleft would itself bias the slate (many self-hosted apps are
AGPL), and analysis is **local, read-only, zero-outbound, no redistribution**, so
copyleft terms are not triggered (consistent with the BSL seed `outline`).
