"""Core local-file-backed tech lead preference helpers.

Exports: PREF_CATEGORY_FRONTEND, PREF_CATEGORY_BACKEND, PREF_CATEGORY_DATABASE,
         resolve_preference_category, load_preferences_for_category
"""

import logging
from pathlib import Path

from src.common.token_matching import normalize_tokens

logger = logging.getLogger(__name__)

PREF_CATEGORY_FRONTEND = "frontend"
PREF_CATEGORY_BACKEND = "backend"
PREF_CATEGORY_DATABASE = "database"

CATEGORY_KEYWORDS: list[tuple[str, set[str]]] = [
    (PREF_CATEGORY_FRONTEND, {"frontend", "front", "ui", "ux", "fe", "client", "react", "web"}),
    (PREF_CATEGORY_DATABASE, {"database", "db", "sql", "schema", "migration", "postgres", "query"}),
    (PREF_CATEGORY_BACKEND, {"backend", "back", "api", "service", "be", "server"}),
]

_RULESET_FILENAME: dict[str, str] = {
    PREF_CATEGORY_FRONTEND: "frontend-ruleset.md",
    PREF_CATEGORY_BACKEND: "backend-ruleset.md",
    PREF_CATEGORY_DATABASE: "database-ruleset.md",
}


def _config_root() -> Path:
    """Return absolute path to the project config/ directory.

    Returns:
        Path to leadsync/config/, resolved relative to this file's location.
    """
    # __file__ = src/common/prefs_core.py
    # parents[0] = src/common
    # parents[1] = src
    # parents[2] = leadsync (project root)
    return Path(__file__).parents[2] / "config"


def resolve_preference_category(labels: list[str], component_names: list[str]) -> str:
    """Resolve preference category from Jira labels/components.

    Args:
        labels: Jira issue labels.
        component_names: Jira component names.
    Returns:
        One of PREF_CATEGORY_FRONTEND, PREF_CATEGORY_BACKEND, PREF_CATEGORY_DATABASE.
    """
    tokens = normalize_tokens(labels) + normalize_tokens(component_names)
    for category, keywords in CATEGORY_KEYWORDS:
        if any(token in keywords for token in tokens):
            return category
    return PREF_CATEGORY_BACKEND


def load_preferences_for_category(category: str) -> str:
    """Load ruleset text from config/<category>-ruleset.md.

    Args:
        category: One of the PREF_CATEGORY_* constants.
    Returns:
        Ruleset file content as a string.
    Raises:
        RuntimeError: If the file is missing or empty.
    """
    filename = _RULESET_FILENAME.get(category)
    if not filename:
        raise RuntimeError(f"Unknown preference category: {category!r}")
    path = _config_root() / filename
    if not path.exists():
        raise RuntimeError(
            f"Local ruleset file not found: {path}. "
            f"Create config/{filename} with your team rules."
        )
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError(f"Local ruleset file is empty: {path}")
    logger.debug("Loaded %s ruleset from %s (%d chars)", category, path, len(text))
    return text
