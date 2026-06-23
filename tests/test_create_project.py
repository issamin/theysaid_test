"""
Thread 1 — Create Project Flow.

Selectors marked TODO in locators/project_locators.py should be verified against the live app.
Observed label differences from spec:
  - "Add Project" renders as "Add project"
  - "Apply Ai Suggestion" renders as "Apply"
  - "Continue to Learning goals" renders as "Learning goals"
  - File upload opens a dialog — click "Confirm" after attaching PDF
  - End of wizard: "Create Project" then "Publish" on the project page (Create Project disappears after navigation)
"""

import uuid

import bootstrap  # noqa: F401

from playwright.sync_api import Page, expect

from config import AI_GENERATION_TIMEOUT, BASE_URL, DEFAULT_TIMEOUT, PDF_PATH
from helpers.project_link import is_valid_survey_link, save_project_link
from helpers.page_waits import wait_for_page_load
from locators.project_locators import ProjectLocators
from locators.teach_ai_locators import TeachAiLocators

PROJECT_URL_BASE = "https://jsonplaceholder.typicode.com"
ADDITIONAL_INFORMATION = (
    "Thank you for taking part in this survey. We're exploring how testers, developers, "
    "and students use free mock REST APIs — like `jsonplaceholder.typicode.com` — to learn "
    "and practice API testing skills before working with real production systems.\n"
    "Your responses will help us understand which features of these sandbox APIs are most "
    "valuable, where they fall short, and whether they're effective tools for onboarding "
    "and training. This should take about 5 minutes to complete. All responses are "
    "anonymous and will be used solely to improve our testing curriculum and tooling "
    "recommendations."
)


def _unique_project_url() -> str:
    slug = uuid.uuid4().hex[:8]
    return f"{PROJECT_URL_BASE}/{slug}"


def _fill_teach_ai_context(page: Page, locators: ProjectLocators, project_url: str) -> None:
    """Steps 2–4: URL, additional information, and file attachment."""
    page.goto(f"{BASE_URL}/home/teach-ai", wait_until="domcontentloaded")
    wait_for_page_load(page)

    locators.add_link_button().click()
    locators.url_field().wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    locators.url_field().fill(project_url)
    locators.url_field().press("Enter")
    wait_for_page_load(page)

    locators.additional_information_menu().click()
    page.get_by_text("Edit", exact=True).click()
    locators.additional_information_field().wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    locators.additional_information_field().fill(ADDITIONAL_INFORMATION)
    locators.additional_information_save_button().click()
    expect(page.get_by_text("Thank you for taking part in this survey", exact=False)).to_be_visible(
        timeout=DEFAULT_TIMEOUT
    )
    wait_for_page_load(page)

    teach_ai = TeachAiLocators(page)
    if teach_ai.document_card(PDF_PATH.name).count() > 0:
        return

    locators.add_file_button().click()
    locators.file_input().set_input_files(str(PDF_PATH))
    expect(locators.confirm_button()).to_be_enabled(timeout=DEFAULT_TIMEOUT)
    locators.confirm_button().click()
    wait_for_page_load(page)


def _click_create_project_if_visible(page: Page, locators: ProjectLocators) -> None:
    """Click Create Project in the wizard when it appears (before Publish)."""
    create_btn = locators.create_project_button()
    publish = locators.publish_button()
    expect(create_btn.or_(publish)).to_be_visible(timeout=AI_GENERATION_TIMEOUT)
    if not create_btn.is_visible():
        return
    create_btn.click()
    wait_for_page_load(page, timeout=AI_GENERATION_TIMEOUT)


def _publish_project(page: Page, locators: ProjectLocators) -> None:
    """Wait for and click Publish on the project page."""
    publish = locators.publish_button()
    publish.wait_for(state="visible", timeout=AI_GENERATION_TIMEOUT)
    publish.click()
    wait_for_page_load(page, timeout=AI_GENERATION_TIMEOUT)


def _select_ai_survey_and_create(page: Page, locators: ProjectLocators) -> None:
    """Select AI Survey in the create modal and confirm."""
    locators.ai_survey_option().click()
    expect(locators.create_ai_survey_button()).to_be_visible(timeout=DEFAULT_TIMEOUT)
    locators.create_ai_survey_button().click()
    wait_for_page_load(page)


def _read_link_from_locator(locator) -> str | None:
    try:
        if not locator.is_visible():
            return None
        tag_name = locator.evaluate("el => el.tagName")
        if tag_name == "A":
            href = locator.get_attribute("href")
            if href and is_valid_survey_link(href):
                return href.strip()
        if tag_name == "INPUT":
            value = locator.input_value()
            if value and is_valid_survey_link(value):
                return value.strip()
        text = locator.inner_text().strip()
        if text and is_valid_survey_link(text):
            return text
    except Exception:
        pass
    return None


def _capture_project_link(page: Page, locators: ProjectLocators) -> str:
    """Prefer visible theysaid.io link in DOM; fall back to clipboard after Copy link."""
    for index in range(locators.project_link_candidates().count()):
        link = _read_link_from_locator(locators.project_link_candidates().nth(index))
        if link:
            return link

    link = _read_link_from_locator(locators.project_link_text())
    if link:
        return link

    clipboard = page.evaluate("() => navigator.clipboard.readText()").strip()
    if is_valid_survey_link(clipboard):
        return clipboard

    raise AssertionError(
        "Could not capture a theysaid.io survey URL from the page or clipboard. "
        f"Clipboard contained: {clipboard!r}"
    )


def test_create_project_flow(authenticated_page: Page) -> None:
    page = authenticated_page
    locators = ProjectLocators(page)
    project_url = _unique_project_url()

    page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
    wait_for_page_load(page)

    # Step 1: Click "Add Project"
    locators.add_project_button().click()
    locators.create_modal().wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    expect(locators.ai_survey_option()).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Steps 2–4: URL (unique slug), additional information, and file attachment
    _fill_teach_ai_context(page, locators, project_url)

    page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
    wait_for_page_load(page)

    locators.add_project_button().click()
    locators.create_modal().wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    expect(locators.ai_survey_option()).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Step 5: Choose AI Survey and click "Create AI Survey"
    _select_ai_survey_and_create(page, locators)
    expect(locators.start_with_ai_button()).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Step 6: Click "Start with AI"
    locators.start_with_ai_button().click()
    wait_for_page_load(page)
    expect(locators.apply_ai_suggestion_button()).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Step 7: Click "Apply Ai Suggestion"
    locators.apply_ai_suggestion_button().click()
    wait_for_page_load(page)
    expect(locators.continue_to_learning_goals_button()).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Step 8: Click "Continue to Learning goals" and wait for next step
    locators.continue_to_learning_goals_button().click()
    wait_for_page_load(page, timeout=AI_GENERATION_TIMEOUT)

    # Step 9–10: Create Project (wizard) then Publish (project page)
    _click_create_project_if_visible(page, locators)
    _publish_project(page, locators)
    expect(locators.copy_link_button()).to_be_visible(timeout=AI_GENERATION_TIMEOUT)

    # Step 11: Click "Copy link" and persist the URL
    locators.copy_link_button().click()
    wait_for_page_load(page)
    project_link = _capture_project_link(page, locators)
    save_project_link(project_link)
    expect(locators.copy_link_button()).to_be_visible()
