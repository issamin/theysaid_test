"""Read/write the survey link produced by Thread 1 for Thread 3."""

import re
from pathlib import Path

import pytest

from config import PROJECT_LINK_PATH

# Respondent survey links live on a theysaid.io host (evo.dev, production, etc.)
SURVEY_URL_PATTERN = re.compile(r"^https?://([a-z0-9-]+\.)*theysaid\.io/", re.I)


def is_valid_survey_link(url: str) -> bool:
    return bool(SURVEY_URL_PATTERN.match(url.strip()))


def save_project_link(link: str, path: Path | None = None) -> Path:
    """Write the survey URL to a plain-text file (one line, overwritten each run)."""
    path = path or PROJECT_LINK_PATH
    cleaned = link.strip()
    if not cleaned.startswith("http"):
        raise ValueError(f"Expected an http(s) URL, got: {cleaned!r}")
    if not is_valid_survey_link(cleaned):
        raise ValueError(f"Expected a theysaid.io survey URL, got: {cleaned!r}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{cleaned}\n", encoding="utf-8")
    return path


def load_project_link(path: Path | None = None) -> str:
    """Load the survey URL written by test_create_project_flow."""
    path = path or PROJECT_LINK_PATH
    if not path.is_file():
        pytest.fail(
            f"Project link file not found at {path}. "
            "Run Thread 1 first: pytest tests/test_create_project.py"
        )

    link = path.read_text(encoding="utf-8").strip()
    if not link:
        pytest.fail(
            f"Project link file is empty at {path}. "
            "Run Thread 1 first: pytest tests/test_create_project.py"
        )
    if not is_valid_survey_link(link):
        pytest.fail(
            f"Stored link is not a theysaid.io survey URL: {link!r}. "
            "Re-run Thread 1: pytest tests/test_create_project.py"
        )
    return link
