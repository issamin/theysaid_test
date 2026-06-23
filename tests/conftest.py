from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

from auth.login import HEADLESS, assert_logged_in, ensure_logged_in, login, save_auth_state
from config import AUTH_STATE_PATH, DEFAULT_TIMEOUT, FIXTURES_DIR, OUTPUT_DIR
from helpers.page_waits import wait_for_page_load

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    return {**browser_type_launch_args, "headless": HEADLESS}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "permissions": ["clipboard-read", "clipboard-write"],
    }


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """Fresh login on every test — navigates to /login and enters credentials from .env."""
    page.set_default_timeout(DEFAULT_TIMEOUT)
    login(page)
    assert_logged_in(page)
    wait_for_page_load(page)
    ensure_logged_in(page)
    save_auth_state(page, path=AUTH_STATE_PATH)
    return page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return

    page = (
        item.funcargs.get("page")
        or item.funcargs.get("authenticated_page")
        or item.funcargs.get("respondent_page")
    )
    if page is None:
        return

    screenshot_path = OUTPUT_DIR / f"failure-{item.name}.png"
    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:
        pass
