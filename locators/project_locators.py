import re

from playwright.sync_api import Locator, Page


class ProjectLocators:
    """Locators for the Create Project flow (Thread 1)."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def add_project_button(self) -> Locator:
        # Spec: "Add Project" — observed DOM label: "Add project"
        return self.page.get_by_role("button", name=re.compile(r"add project", re.I))

    def url_field(self) -> Locator:
        # Observed placeholder after clicking "Add link": "Add URL ..."
        return self.page.get_by_placeholder(re.compile(r"add url", re.I))

    def add_link_button(self) -> Locator:
        return self.page.get_by_role("button", name="Add link")

    def additional_information_menu(self) -> Locator:
        return self.page.locator('[data-test="teach-ai-additional-info-menu"]')

    def additional_information_field(self) -> Locator:
        return self.page.locator('[data-test="teach-ai-additional-info"] [contenteditable="true"]')

    def additional_information_save_button(self) -> Locator:
        return self.page.get_by_role("button", name="Save")

    def file_input(self) -> Locator:
        return self.page.locator('input[type="file"]')

    def add_file_button(self) -> Locator:
        return self.page.locator('[data-test="teach-ai-add-file"]').or_(
            self.page.get_by_role("button", name="Add file")
        )

    def create_modal(self) -> Locator:
        return self.page.get_by_role("dialog")

    def ai_survey_option(self) -> Locator:
        return self.create_modal().get_by_role("radio", name=re.compile(r"AI Survey", re.I))

    def create_ai_survey_button(self) -> Locator:
        return self.page.get_by_role("button", name="Create AI Survey")

    def start_with_ai_button(self) -> Locator:
        return self.page.get_by_role("button", name="Start with AI")

    def apply_ai_suggestion_button(self) -> Locator:
        # Spec: "Apply Ai Suggestion" — observed DOM label: "Apply"
        return self.page.get_by_role("button", name=re.compile(r"apply ai suggestion", re.I)).or_(
            self.page.get_by_role("button", name="Apply")
        )

    def continue_to_learning_goals_button(self) -> Locator:
        # Spec: "Continue to Learning goals" — observed DOM label: "Learning goals"
        return self.page.get_by_role(
            "button", name=re.compile(r"continue to learning goals", re.I)
        ).or_(self.page.get_by_role("button", name="Learning goals"))

    def confirm_button(self) -> Locator:
        return self.page.get_by_role("button", name="Confirm")

    def finalize_button(self) -> Locator:
        # Create Project (wizard) or Publish (project page)
        return self.page.get_by_role("button", name=re.compile(r"^(Create Project|Publish)$", re.I))

    def publish_button(self) -> Locator:
        return self.page.get_by_role("button", name="Publish")

    def create_project_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"create project", re.I))

    def copy_link_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"copy link", re.I))

    def project_link_text(self) -> Locator:
        return self.page.locator(
            'input[value*="theysaid.io"], a[href*="theysaid.io"]'
        ).first

    def project_link_candidates(self) -> Locator:
        return self.page.locator(
            'input[readonly][value*="http"], '
            'input[value*="theysaid.io"], '
            'a[href*="theysaid.io"]'
        )
