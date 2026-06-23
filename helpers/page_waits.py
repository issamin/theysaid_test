from playwright.sync_api import Page

from config import DEFAULT_TIMEOUT


def wait_for_page_load(page: Page, timeout: int | None = None) -> None:
    """Wait until the page has finished loading (DOM + network idle)."""
    timeout = timeout or DEFAULT_TIMEOUT
    page.wait_for_load_state("domcontentloaded", timeout=timeout)
    page.wait_for_load_state("networkidle", timeout=timeout)
