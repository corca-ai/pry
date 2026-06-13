# Gathered: pry design spec (claude.ai public artifact)

- **Source:** https://claude.ai/public/artifacts/d3a23d3b-4bc9-4a9f-a462-95f89e59397e
- **Canonical Asset:** `initial-plan.md` (repo root) — full verbatim document
- **Freshness:** captured 2026-06-13
- **Access Mode:** content captured into the repo; live URL is Cloudflare-gated (see Open Gaps)
- **Source Identity:** Claude artifact `d3a23d3b-4bc9-4a9f-a462-95f89e59397e`

## What this is

The artifact is the founding design document for **pry** — a proposed static
analysis tool that makes the *injectability* (testability) of code visible by
finding boundary calls (network, file I/O, clock, etc.) "welded" into business
logic with no seam to inject a failure, concentrating on error-handling paths
where defects cluster (Yuan et al., OSDI 2014). It is structured in three layers
(Layer 0 static map + syntactic floor; Layer 1 seam generation; Layer 2
injection oracle), with a kill-gate validation strategy (beat a churn baseline
on error-handling defects) and a Klein premortem.

The complete verbatim text lives in `initial-plan.md`. Do not re-summarize from
this note when the primary asset is present — read `initial-plan.md`.

## Access Mode detail (why content is local, not re-fetched live)

- Direct `curl` to the page and to `/api/(public/)artifacts/<id>` returns
  Cloudflare's managed "Just a moment..." challenge (HTTP 403).
- `agent-browser` (headless chromium, no display / no Xvfb on this host) is
  detected by Cloudflare Turnstile and never clears the challenge — the Ray ID
  re-issues on each attempt. Stealth launch args and a clicked Turnstile
  checkbox did not pass.
- The harness `WebFetch` backend reaches the page but only returns a small-model
  *paraphrase* (two calls produced two different summaries/titles), so it is not
  a faithful source for a durable asset.
- The verbatim document was therefore captured into `initial-plan.md` directly.

## Open Gaps

- Live re-fetch from the URL requires a Cloudflare-trusted browser session
  (headed/real Chrome, or `agent-browser --cdp <port>` connected to an existing
  trusted browser). On this headless host, refresh by updating `initial-plan.md`
  from a trusted source rather than re-scraping the URL.
