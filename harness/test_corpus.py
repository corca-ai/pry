"""test_corpus.py — unit tests for the S1 corpus scorer + validator.

Pure-logic tests (no git, no gh, no network): corpus_fit.score decision logic,
validate_corpus invariants, and a smoke test that the frozen corpus.json actually
validates against its schema.

Run:  python3 -m pytest harness/test_corpus.py -q
"""

from __future__ import annotations

import json

import config
import corpus_fit
import validate_corpus


# --- corpus_fit.score ---------------------------------------------------------

def _app_features():
    return {
        "lang_ratio": 0.9,
        "top_level": ["server", "packages", "src", "package.json", "Dockerfile"],
        "days_since_push": 10,
        "stars": 5000,
        "size_kb": 40000,
        "topics": ["self-hosted", "cms"],
        "description": "An open-source self-hosted application platform",
    }


def test_clear_app_passes_floor():
    r = corpus_fit.score(_app_features())
    assert r["passes"] is True
    assert r["app_shapedness_score"] >= config.CORPUS_APP_SHAPEDNESS_FLOOR
    assert r["backend_dir_tokens"] >= 2


def test_pure_library_is_penalized_and_can_fail():
    lib = {
        "lang_ratio": 0.95,
        "top_level": ["src", "dist", "package.json"],  # flat lib shape
        "days_since_push": 20,
        "stars": 40000,
        "size_kb": 2000,
        "topics": ["react", "hooks"],
        "description": "React Hooks library for form state management",
    }
    r = corpus_fit.score(lib)
    assert r["library_flagged"] is True
    assert r["components"]["library_penalty"] == -20


def test_stale_thin_shell_fails_floor():
    thin = {
        "lang_ratio": 0.1,            # target language is a thin shell
        "top_level": ["docs"],
        "days_since_push": 1500,      # stale
        "stars": 50,
        "size_kb": 100,
        "topics": [],
        "description": "an old experiment",
    }
    r = corpus_fit.score(thin)
    assert r["passes"] is False


def test_floor_comes_from_config():
    # The floor is the pre-registered constant, not a literal in the scorer.
    r = corpus_fit.score(_app_features())
    assert r["floor"] == config.CORPUS_APP_SHAPEDNESS_FLOOR


# --- validate_corpus ----------------------------------------------------------

def _good_repo(**over):
    base = {
        "id": "ex", "name": "owner/ex", "primary_language": "TypeScript",
        "domain": "demo", "url": "https://github.com/owner/ex.git",
        "commit": "a" * 40, "split": "dev", "arm": "ts",
        "app_shapedness_score": 80, "app_shapedness_passes": True,
    }
    base.update(over)
    return base


def _schema():
    return json.loads(config.CORPUS_SCHEMA_PATH.read_text())


def test_validator_accepts_minimal_two_split_arm():
    corpus = {
        "schema_version": "0.1.0",
        "app_shapedness_floor": 55,
        "splits": {"dev": 1, "heldout": 1},
        "repositories": [
            _good_repo(id="a", name="o/a", split="dev"),
            _good_repo(id="b", name="o/b", split="heldout"),
        ],
    }
    assert validate_corpus.validate(corpus, _schema()) == []


def test_validator_rejects_branch_ref_commit():
    corpus = {
        "schema_version": "0.1.0", "app_shapedness_floor": 55,
        "splits": {"dev": 1, "heldout": 1},
        "repositories": [
            _good_repo(id="a", name="o/a", split="dev", commit="main"),
            _good_repo(id="b", name="o/b", split="heldout"),
        ],
    }
    errs = validate_corpus.validate(corpus, _schema())
    assert any("commit" in e for e in errs)


def test_validator_requires_dev_and_heldout_per_arm():
    corpus = {
        "schema_version": "0.1.0", "app_shapedness_floor": 55,
        "splits": {"dev": 2},
        "repositories": [
            _good_repo(id="a", name="o/a", split="dev"),
            _good_repo(id="b", name="o/b", split="dev"),
        ],
    }
    errs = validate_corpus.validate(corpus, _schema())
    assert any("dev AND >=1 heldout" in e for e in errs)


def test_validator_rejects_score_below_floor_marked_passing():
    # The boolean is freeze-written; the validator must independently check the
    # numeric score clears the floor (critique #11).
    corpus = {
        "schema_version": "0.1.0", "app_shapedness_floor": 55,
        "splits": {"dev": 1, "heldout": 1},
        "repositories": [
            _good_repo(id="a", name="o/a", split="dev",
                       app_shapedness_score=3, app_shapedness_passes=True),
            _good_repo(id="b", name="o/b", split="heldout"),
        ],
    }
    errs = validate_corpus.validate(corpus, _schema())
    assert any("< floor" in e for e in errs)


def test_validator_rejects_floor_mismatch_with_config():
    corpus = {
        "schema_version": "0.1.0",
        "app_shapedness_floor": config.CORPUS_APP_SHAPEDNESS_FLOOR + 1,
        "splits": {"dev": 1, "heldout": 1},
        "repositories": [
            _good_repo(id="a", name="o/a", split="dev"),
            _good_repo(id="b", name="o/b", split="heldout"),
        ],
    }
    errs = validate_corpus.validate(corpus, _schema())
    assert any("pre-registered" in e for e in errs)


def test_validator_rejects_failed_app_shapedness():
    corpus = {
        "schema_version": "0.1.0", "app_shapedness_floor": 55,
        "splits": {"dev": 1, "heldout": 1},
        "repositories": [
            _good_repo(id="a", name="o/a", split="dev",
                       app_shapedness_passes=False),
            _good_repo(id="b", name="o/b", split="heldout"),
        ],
    }
    errs = validate_corpus.validate(corpus, _schema())
    assert errs  # const:true in schema + invariant both catch it


# --- frozen artifact smoke test ----------------------------------------------

def test_frozen_corpus_validates():
    corpus = json.loads(config.CORPUS_PATH.read_text())
    schema = _schema()
    assert validate_corpus.validate(corpus, schema) == []


def test_frozen_corpus_split_is_preregistered_shape():
    corpus = json.loads(config.CORPUS_PATH.read_text())
    ts = [r for r in corpus["repositories"] if r["arm"] == "ts"]
    dev = [r for r in ts if r["split"] == "dev"]
    # dev must include the 4 labeled seeds (pre-registered) + be small (~5).
    seed_ids = {"outline", "flowise", "continue", "librechat"}
    assert seed_ids <= {r["id"] for r in dev}
    assert len(dev) == 5
    assert all(r["app_shapedness_passes"] for r in corpus["repositories"])
