"""Tests for local-file-backed preference loading."""
from pathlib import Path
from unittest.mock import patch
import pytest

from src.common.prefs_core import (
    PREF_CATEGORY_BACKEND,
    PREF_CATEGORY_DATABASE,
    PREF_CATEGORY_FRONTEND,
    load_preferences_for_category,
    resolve_preference_category,
)


def test_resolve_preference_category_backend():
    assert resolve_preference_category(["backend"], []) == PREF_CATEGORY_BACKEND


def test_resolve_preference_category_frontend():
    assert resolve_preference_category(["frontend"], []) == PREF_CATEGORY_FRONTEND


def test_resolve_preference_category_database():
    assert resolve_preference_category([], ["database"]) == PREF_CATEGORY_DATABASE


def test_resolve_preference_category_defaults_to_backend():
    assert resolve_preference_category([], []) == PREF_CATEGORY_BACKEND


def test_load_preferences_reads_local_file(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "backend-ruleset.md").write_text("# Backend Rules\n- rule one\n")
    monkeypatch.setattr(
        "src.common.prefs_core._config_root",
        lambda: config_dir,
    )
    result = load_preferences_for_category(PREF_CATEGORY_BACKEND)
    assert "rule one" in result


def test_load_preferences_raises_if_file_missing(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    monkeypatch.setattr("src.common.prefs_core._config_root", lambda: config_dir)
    with pytest.raises(RuntimeError, match="not found"):
        load_preferences_for_category(PREF_CATEGORY_BACKEND)


def test_load_preferences_raises_if_file_empty(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "backend-ruleset.md").write_text("   ")
    monkeypatch.setattr("src.common.prefs_core._config_root", lambda: config_dir)
    with pytest.raises(RuntimeError, match="empty"):
        load_preferences_for_category(PREF_CATEGORY_BACKEND)
