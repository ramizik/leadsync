"""
tests/test_prefs.py
Unit tests for src/prefs.py — local-file-backed team preferences.
"""

import pytest


def test_resolve_preference_category_frontend_from_label():
    from src.prefs import resolve_preference_category

    category = resolve_preference_category(labels=["frontend"], component_names=[])
    assert category == "frontend"


def test_resolve_preference_category_database_from_component():
    from src.prefs import resolve_preference_category

    category = resolve_preference_category(labels=[], component_names=["db-migrations"])
    assert category == "database"


def test_resolve_preference_category_defaults_to_backend():
    from src.prefs import resolve_preference_category

    category = resolve_preference_category(labels=["priority-high"], component_names=["ops"])
    assert category == "backend"


def test_load_preferences_for_category_returns_string(tmp_path, monkeypatch):
    """load_preferences_for_category reads from the config/ directory and returns text."""
    import src.common.prefs_core as prefs_core

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "backend-ruleset.md").write_text("Keep APIs thin.\nPrefer REST.", encoding="utf-8")

    monkeypatch.setattr(prefs_core, "_config_root", lambda: config_dir)

    from src.prefs import load_preferences_for_category

    result = load_preferences_for_category("backend")
    assert "Keep APIs thin" in result


def test_load_preferences_for_category_raises_for_unknown_category():
    from src.prefs import load_preferences_for_category

    with pytest.raises(RuntimeError, match="Unknown preference category"):
        load_preferences_for_category("unknown")


def test_load_preferences_for_category_raises_when_file_missing(tmp_path, monkeypatch):
    import src.common.prefs_core as prefs_core

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    monkeypatch.setattr(prefs_core, "_config_root", lambda: config_dir)

    from src.prefs import load_preferences_for_category

    with pytest.raises(RuntimeError, match="not found"):
        load_preferences_for_category("frontend")


def test_load_preferences_for_category_raises_when_file_empty(tmp_path, monkeypatch):
    import src.common.prefs_core as prefs_core

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "database-ruleset.md").write_text("   ", encoding="utf-8")
    monkeypatch.setattr(prefs_core, "_config_root", lambda: config_dir)

    from src.prefs import load_preferences_for_category

    with pytest.raises(RuntimeError, match="empty"):
        load_preferences_for_category("database")


def test_prefs_exports_expected_symbols():
    """Verify __all__ exports the correct set of symbols."""
    import src.prefs as prefs_mod

    assert "PREF_CATEGORY_FRONTEND" in dir(prefs_mod)
    assert "PREF_CATEGORY_BACKEND" in dir(prefs_mod)
    assert "PREF_CATEGORY_DATABASE" in dir(prefs_mod)
    assert "resolve_preference_category" in dir(prefs_mod)
    assert "load_preferences_for_category" in dir(prefs_mod)
    assert not hasattr(prefs_mod, "resolve_doc_id")
    assert not hasattr(prefs_mod, "append_preference")
