"""corpus_freeze.py — discover features, score, pin, and freeze the E9 corpus.

S1 of the E9 sweep. Given the curated, domain-stratified finalist slate below
(operator-approved GitHub discovery, handoff step 1), this fetches cheap
gh-API features per repo (no clone), runs the app-shapedness scorer
(corpus_fit.py) against the PRE-REGISTERED floor (config.CORPUS_APP_SHAPEDNESS_
FLOOR), pins each commit, and freezes corpus.json + a discovery-features record +
a prune log. Selection bias (R-A) is held off two ways: the slate is stratified
across many domains (not clustered at the disciplined/low-injection end), and the
dev|heldout split is fixed HERE, before any mining or enrichment number exists.

The split is pre-registered, not peeked: dev = the 4 already-mapped H3 seeds + 1
non-AI app (medusa) so dev is not all-AI; everything else is heldout. Python
repos carry a pre-registered split too (harmless if the S5 (b)-gate KILLs the
Python branch).

Usage:
    python3 harness/corpus_freeze.py            # fetch + score + freeze
    python3 harness/corpus_freeze.py --dry-run  # print scores, write nothing
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import config
import corpus_fit

# Reference date for "days since push" (the currentDate of this S1 run). Fixed so
# scoring is reproducible from the frozen features record.
REFERENCE_DATE = date(2026, 6, 15)

# Seeds: the 4 H3 apps, already mapped + frozen-labeled, pinned at their local
# commits (docs/handoff.md "Current state").
SEED_COMMITS = {
    "outline": "d85ead5a461e66e124d2419284d59a267c6e57a6",
    "flowise": "f4e2794f6a576b94578f2fdafbf49c2fb304626c",
    "continue": "eaa23c5a9de86049dff765f635c18f61d1d043bb",
    "librechat": "8154a31d2d16a0628e9612d8bcd1b48885710d9a",
}

# (id, name, domain, arm, split, is_seed). Stars/license/commit/etc. are fetched.
SLATE = [
    # --- dev (5 TS): the 4 labeled seeds + 1 non-AI app -----------------------
    ("outline", "outline/outline", "knowledge-base", "ts", "dev", True),
    ("flowise", "FlowiseAI/Flowise", "ai-workflow-builder", "ts", "dev", True),
    ("continue", "continuedev/continue", "ai-dev-assistant", "ts", "dev", True),
    ("librechat", "danny-avila/LibreChat", "ai-chat", "ts", "dev", True),
    ("medusa", "medusajs/medusa", "ecommerce", "ts", "dev", False),
    # --- heldout (20 TS), stratified across domains ---------------------------
    ("directus", "directus/directus", "headless-cms", "ts", "heldout", False),
    ("payload", "payloadcms/payload", "headless-cms", "ts", "heldout", False),
    ("strapi", "strapi/strapi", "headless-cms", "ts", "heldout", False),
    ("n8n", "n8n-io/n8n", "automation", "ts", "heldout", False),
    ("nocodb", "nocodb/nocodb", "database-ui", "ts", "heldout", False),
    ("budibase", "Budibase/budibase", "low-code", "ts", "heldout", False),
    ("umami", "umami-software/umami", "web-analytics", "ts", "heldout", False),
    ("formbricks", "formbricks/formbricks", "surveys", "ts", "heldout", False),
    ("calcom", "calcom/cal.com", "scheduling", "ts", "heldout", False),
    ("twenty", "twentyhq/twenty", "crm", "ts", "heldout", False),
    ("immich", "immich-app/immich", "photo-management", "ts", "heldout", False),
    ("karakeep", "karakeep-app/karakeep", "bookmarks", "ts", "heldout", False),
    ("linkwarden", "linkwarden/linkwarden", "bookmarks", "ts", "heldout", False),
    ("openstatus", "openstatusHQ/openstatus", "uptime-monitoring", "ts", "heldout", False),
    ("docmost", "docmost/docmost", "wiki", "ts", "heldout", False),
    ("vendure", "vendurehq/vendure", "ecommerce", "ts", "heldout", False),
    ("midday", "midday-ai/midday", "finance-invoicing", "ts", "heldout", False),
    ("novu", "novuhq/novu", "notifications", "ts", "heldout", False),
    ("seerr", "seerr-team/seerr", "media-requests", "ts", "heldout", False),
    ("rocketchat", "RocketChat/Rocket.Chat", "team-chat", "ts", "heldout", False),
    # --- Python (8), non-glue apps, stratified; split pre-registered ----------
    ("paperless-ngx", "paperless-ngx/paperless-ngx", "document-management", "python", "dev", False),
    ("saleor", "saleor/saleor", "ecommerce", "python", "dev", False),
    ("netbox", "netbox-community/netbox", "ipam-dcim", "python", "heldout", False),
    ("searxng", "searxng/searxng", "metasearch", "python", "heldout", False),
    ("mealie", "mealie-recipes/mealie", "recipe-webapp", "python", "heldout", False),
    ("healthchecks", "healthchecks/healthchecks", "cron-monitoring", "python", "heldout", False),
    ("redash", "getredash/redash", "data-analytics", "python", "heldout", False),
    ("changedetection", "dgtlmoon/changedetection.io", "web-monitoring", "python", "heldout", False),
]

TARGET_LANGS = {
    "ts": {"TypeScript", "JavaScript", "TSX", "JSX", "Vue", "Svelte"},
    "python": {"Python"},
}


def _gh_json(path: str):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout)


def _days_since(pushed_at: str) -> int:
    d = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")).date()
    return (REFERENCE_DATE - d).days


def fetch_features(name: str, arm: str) -> dict:
    meta = _gh_json(f"repos/{name}")
    langs = _gh_json(f"repos/{name}/languages")
    try:
        contents = _gh_json(f"repos/{name}/contents")
        top_level = [c["name"] for c in contents]
    except RuntimeError:
        top_level = []
    total = sum(langs.values()) or 1
    tgt = sum(v for k, v in langs.items() if k in TARGET_LANGS[arm])
    lic = (meta.get("license") or {})
    return {
        "lang_ratio": round(tgt / total, 4),
        "top_level": top_level,
        "days_since_push": _days_since(meta["pushed_at"]),
        "stars": meta.get("stargazers_count", 0),
        "size_kb": meta.get("size", 0),
        "topics": meta.get("topics", []) or [],
        "description": meta.get("description") or "",
        "default_branch": meta.get("default_branch"),
        "license": lic.get("spdx_id") or lic.get("key"),
        "url": meta.get("clone_url"),
        "language_bytes": langs,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reseed", action="store_true",
                    help="allow overwriting an already-frozen corpus.json; "
                         "without it, re-running refuses so a re-fetch cannot "
                         "silently re-pin the corpus to newer HEADs (critique #12)")
    args = ap.parse_args()

    if (not args.dry_run and not args.reseed and config.CORPUS_PATH.exists()):
        sys.exit(f"refusing to overwrite frozen {config.CORPUS_PATH} — re-running "
                 f"would re-pin non-seed repos to current HEAD. Pass --reseed to "
                 f"deliberately re-freeze, or --dry-run to preview.")

    repositories = []
    features_record = {}
    pruned = []

    for rid, name, domain, arm, split, is_seed in SLATE:
        try:
            feats = fetch_features(name, arm)
        except RuntimeError as e:
            pruned.append((rid, name, f"fetch failed: {e}"))
            print(f"  PRUNE {rid}: {e}", file=sys.stderr)
            continue
        verdict = corpus_fit.score(feats)
        features_record[rid] = {**feats, "score": verdict}
        if not verdict["passes"]:
            pruned.append((rid, name,
                           f"app_shapedness {verdict['app_shapedness_score']} "
                           f"< floor {verdict['floor']}"))
            print(f"  PRUNE {rid}: below floor "
                  f"({verdict['app_shapedness_score']})", file=sys.stderr)
            continue
        commit = SEED_COMMITS.get(rid)
        if not commit:
            commit = _gh_json(
                f"repos/{name}/commits/{feats['default_branch']}")["sha"]
        repositories.append({
            "id": rid,
            "name": name,
            "primary_language": "TypeScript" if arm == "ts" else "Python",
            "domain": domain,
            "url": feats["url"],
            "commit": commit,
            "default_branch": feats["default_branch"],
            "license": feats["license"],
            "stars": feats["stars"],
            "split": split,
            "arm": arm,
            "is_seed": is_seed,
            "app_shapedness_score": verdict["app_shapedness_score"],
            "app_shapedness_passes": True,
        })
        tag = "seed" if is_seed else "    "
        print(f"  OK {rid:<16} {arm:<7} {split:<8} score={verdict['app_shapedness_score']:>3} "
              f"{tag} {commit[:10]} {feats['license']}")

    repositories.sort(key=lambda r: (r["arm"], r["split"] != "dev", r["id"]))
    splits = {}
    for r in repositories:
        splits[r["split"]] = splits.get(r["split"], 0) + 1
    corpus = {
        "schema_version": "0.1.0",
        "description": ("E9 multi-repo validation sweep corpus: app-shaped "
                        "third-party OSS (route handlers / service layer / DB "
                        "clients / env+config), NOT single-purpose libraries. "
                        "Stratified by domain; dev|heldout split pre-registered "
                        "before any mining. Cloned locally for mining, never "
                        "vendored."),
        "generated_for": "E9 nose-style multi-repo validation sweep (쟁점 4 + 쟁점 2)",
        "reference_date": REFERENCE_DATE.isoformat(),
        "app_shapedness_floor": config.CORPUS_APP_SHAPEDNESS_FLOOR,
        "splits": splits,
        "counts": {
            "ts": sum(1 for r in repositories if r["arm"] == "ts"),
            "python": sum(1 for r in repositories if r["arm"] == "python"),
            "total": len(repositories),
        },
        "repositories": repositories,
    }

    print(f"\n{len(repositories)} repos kept ({corpus['counts']['ts']} TS + "
          f"{corpus['counts']['python']} Python); {len(pruned)} pruned; "
          f"splits={splits}")
    if args.dry_run:
        print("(dry-run: nothing written)")
        return

    config.CORPUS_PATH.write_text(json.dumps(corpus, indent=2) + "\n")
    config.DISCOVERY_FEATURES_PATH.write_text(
        json.dumps(features_record, indent=2, sort_keys=True) + "\n")
    print(f"wrote {config.CORPUS_PATH}")
    print(f"wrote {config.DISCOVERY_FEATURES_PATH}")
    if pruned:
        lines = ["# Corpus prune / exclusion log (S1, risk R-D: no silent truncation)\n",
                 f"Reference date: {REFERENCE_DATE.isoformat()}\n",
                 "Each candidate considered but NOT frozen into corpus.json, with reason.\n"]
        for rid, name, reason in pruned:
            lines.append(f"- `{rid}` ({name}): {reason}")
        config.CORPUS_PRUNE_LOG_PATH.write_text("\n".join(lines) + "\n")
        print(f"wrote {config.CORPUS_PRUNE_LOG_PATH}")


if __name__ == "__main__":
    main()
