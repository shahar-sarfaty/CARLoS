import os
from carlos.config import IndexingConfig, CIVITAI_API_KEY_ENV


def test_resolved_civitai_key_prefers_explicit_over_env(monkeypatch):
    monkeypatch.setenv(CIVITAI_API_KEY_ENV, "ENVKEY")
    cfg = IndexingConfig(civitai_key_str=" ARGKEY ")
    assert cfg.resolved_civitai_key() == "ARGKEY"


def test_resolved_civitai_key_uses_env_if_no_explicit(monkeypatch):
    monkeypatch.setenv(CIVITAI_API_KEY_ENV, "ENVKEY")
    cfg = IndexingConfig(civitai_key_str=None)
    assert cfg.resolved_civitai_key() == "ENVKEY"


def test_resolved_civitai_key_none_if_missing(monkeypatch):
    monkeypatch.delenv(CIVITAI_API_KEY_ENV, raising=False)
    cfg = IndexingConfig(civitai_key_str=None)
    assert cfg.resolved_civitai_key() is None