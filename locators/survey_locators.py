import re

from playwright.sync_api import Locator, Page


class SurveyLocators:
    """Locators for the respondent survey flow (Thread 3)."""

    CONTINUE_PATTERN = re.compile(r"^(Continue|Next|Submit|Finish|Start)$", re.I)
    COMPLETION_PATTERN = re.compile(r"thank you|complete|submitted|survey complete", re.I)

    def __init__(self, page: Page) -> None:
        self.page = page

    def continue_button(self) -> Locator:
        return self.page.get_by_role("button", name=self.CONTINUE_PATTERN)

    def completion_indicator(self) -> Locator:
        return self.page.get_by_text(self.COMPLETION_PATTERN)

    def visible_radios(self) -> Locator:
        return self.page.get_by_role("radio")

    def visible_checkboxes(self) -> Locator:
        return self.page.get_by_role("checkbox")

    def visible_textboxes(self) -> Locator:
        return self.page.get_by_role("textbox")

    def visible_textareas(self) -> Locator:
        return self.page.locator("textarea")

    def scale_buttons(self) -> Locator:
        # NPS-style numbered options (0–10)
        return self.page.get_by_role("button", name=re.compile(r"^\d{1,2}$"))
