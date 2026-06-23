import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from config import DEFAULT_TIMEOUT
from helpers.page_waits import wait_for_page_load

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://evo.dev.theysaid.io")
EMAIL = os.getenv("THEYSAID_EMAIL", "")
PASSWORD = os.getenv("THEYSAID_PASSWORD", "")
AUTH_STATE_PATH = Path(__file__).resolve().parent.parent / "auth_state.json"
LOGIN_TIMEOUT = 60_000


def env_bool(name: str, default: bool = True) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


HEADLESS = env_bool("HEADLESS", default=True)


def is_login_required(page: Page) -> bool:
    """True when the browser was redirected to the login / AuthKit flow."""
    url = page.url
    return "authkit" in url or url.rstrip("/").endswith("/login")


def login(page: Page, email: str | None = None, password: str | None = None) -> None:
    """Sign in to TheySaid via WorkOS AuthKit (email + password)."""
    email = email or EMAIL
    password = password or PASSWORD

    if not email or not password:
        raise ValueError("THEYSAID_EMAIL and THEYSAID_PASSWORD must be set in .env")

    if not is_login_required(page):
        page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")

    # AuthKit pages never reach networkidle — wait for the email field instead
    email_input = page.get_by_placeholder("Your email address")
    email_input.wait_for(state="visible", timeout=LOGIN_TIMEOUT)
    email_input.fill(email)
    page.get_by_role("button", name="Continue").click()

    page.wait_for_url("**/password**", timeout=LOGIN_TIMEOUT)
    password_input = page.locator('input[type="password"]')
    password_input.wait_for(state="visible", timeout=LOGIN_TIMEOUT)
    password_input.fill(password)
    password_input.press("Enter")

    page.wait_for_url(
        lambda url: "evo.dev.theysaid.io" in url and "authkit" not in url,
        timeout=LOGIN_TIMEOUT,
    )
    wait_for_page_load(page, timeout=LOGIN_TIMEOUT)


def ensure_logged_in(page: Page, email: str | None = None, password: str | None = None) -> None:
    """Run the full login flow if the page is on AuthKit or /login."""
    if is_login_required(page):
        login(page, email, password)
        assert_logged_in(page)


def goto_authenticated(page: Page, url: str, timeout: int | None = None) -> None:
    """Navigate to a URL and log in again if the app redirects to AuthKit."""
    page.goto(url, wait_until="domcontentloaded")
    if is_login_required(page):
        ensure_logged_in(page)
    wait_for_page_load(page, timeout=timeout or DEFAULT_TIMEOUT)


def assert_logged_in(page: Page) -> None:
    """Verify the user is authenticated in the app."""
    expect(page.get_by_text(EMAIL, exact=False)).to_be_visible(timeout=15_000)


def save_auth_state(page: Page, path: Path | None = None) -> Path:
    """Persist browser cookies/localStorage for reuse across tests."""
    path = path or AUTH_STATE_PATH
    page.context.storage_state(path=str(path))
    return path
