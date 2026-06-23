import re

from playwright.sync_api import Locator, Page


class TeachAiLocators:
    """Locators for the Teach AI upload flow (Thread 2)."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def teach_ai_nav(self) -> Locator:
        return self.page.get_by_role("link", name="Teach AI")

    def add_file_button(self) -> Locator:
        return self.page.locator('[data-test="teach-ai-add-file"]').or_(
            self.page.get_by_role("button", name="Add file")
        )

    def upload_dialog_file_input(self) -> Locator:
        return self.page.locator('input[type="file"]')

    def confirm_button(self) -> Locator:
        return self.page.get_by_role("button", name="Confirm")

    def cancel_button(self) -> Locator:
        return self.page.get_by_role("button", name="Cancel")

    def generating_data_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"generating data", re.I))

    def document_card(self, filename: str) -> Locator:
        return self.page.locator('[data-test="teach-ai-data-source-card"]').filter(
            has_text=filename
        )
