"""Standalone script to run the TheySaid login flow. Credentials are loaded from .env."""

import bootstrap  # noqa: F401

from pathlib import Path

from playwright.sync_api import sync_playwright

from auth.login import HEADLESS, assert_logged_in, login, save_auth_state

AUTH_STATE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "auth_state.json"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        login(page)
        assert_logged_in(page)
        save_auth_state(page, path=AUTH_STATE_PATH)
        print(f"Logged in successfully: {page.url}")
        browser.close()


if __name__ == "__main__":
    main()
