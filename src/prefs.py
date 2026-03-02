"""
src/prefs.py
Local-file-backed tech lead preference resolution helpers.
Exports: resolve_preference_category, load_preferences_for_category,
         PREF_CATEGORY_FRONTEND, PREF_CATEGORY_BACKEND, PREF_CATEGORY_DATABASE
"""

from src.common.prefs_core import (
    PREF_CATEGORY_BACKEND,
    PREF_CATEGORY_DATABASE,
    PREF_CATEGORY_FRONTEND,
    load_preferences_for_category,
    resolve_preference_category,
)

__all__ = [
    "PREF_CATEGORY_FRONTEND",
    "PREF_CATEGORY_BACKEND",
    "PREF_CATEGORY_DATABASE",
    "resolve_preference_category",
    "load_preferences_for_category",
]
