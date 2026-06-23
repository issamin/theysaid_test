"""
Thread 2 — Teach AI Upload Document Flow.

Upload uses set_input_files() on the hidden file input — do not click "Upload file"
(that opens the native OS file picker). If PDF.pdf is already listed, the test
waits for any in-progress generation to finish and passes without re-uploading.
"""

import bootstrap  # noqa: F401

from playwright.sync_api import Page, expect

from auth.login import ensure_logged_in, goto_authenticated
from config import (
    AI_GENERATION_TIMEOUT,
    BASE_URL,
    DEFAULT_TIMEOUT,
    PDF_PATH,
    TEACH_AI_UPLOAD_TIMEOUT,
)
from locators.project_locators import ProjectLocators
from locators.teach_ai_locators import TeachAiLocators


def _ensure_project_exists(page: Page) -> None:
    """Ensure at least one project exists so Teach AI can be used in context."""
    goto_authenticated(page, f"{BASE_URL}/projects")
    if page.locator("table tbody tr").count() > 0:
        return

    locators = ProjectLocators(page)
    locators.add_project_button().click()
    locators.create_modal().wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    locators.ai_survey_option().click()
    locators.create_ai_survey_button().click()
    page.wait_for_load_state("networkidle")
    ensure_logged_in(page)
    locators.start_with_ai_button().click()
    page.wait_for_load_state("networkidle")
    ensure_logged_in(page)
    locators.apply_ai_suggestion_button().click()
    page.wait_for_load_state("networkidle")
    ensure_logged_in(page)
    locators.continue_to_learning_goals_button().click()
    page.wait_for_load_state("networkidle", timeout=AI_GENERATION_TIMEOUT)
    ensure_logged_in(page)
    locators.create_project_button().wait_for(state="visible", timeout=AI_GENERATION_TIMEOUT)
    locators.create_project_button().click()
    page.wait_for_url("**/projects/**", timeout=AI_GENERATION_TIMEOUT)
    page.wait_for_load_state("networkidle", timeout=AI_GENERATION_TIMEOUT)
    ensure_logged_in(page)


def _wait_for_generation_to_finish(page: Page, teach_ai: TeachAiLocators) -> None:
    generating = teach_ai.generating_data_text()
    if generating.count() == 0:
        return
    try:
        generating.first.wait_for(state="visible", timeout=10_000)
    except Exception:
        pass
    expect(generating.first).to_be_hidden(timeout=TEACH_AI_UPLOAD_TIMEOUT)


def _assert_pdf_listed(teach_ai: TeachAiLocators) -> None:
    expect(teach_ai.document_card(PDF_PATH.name).first).to_be_visible(
        timeout=DEFAULT_TIMEOUT
    )


def _is_pdf_already_uploaded(teach_ai: TeachAiLocators) -> bool:
    return teach_ai.document_card(PDF_PATH.name).count() > 0


def test_teach_ai_upload_document(authenticated_page: Page) -> None:
    page = authenticated_page
    ensure_logged_in(page)
    _ensure_project_exists(page)
    ensure_logged_in(page)

    teach_ai = TeachAiLocators(page)

    # Step 1: Open Teach AI
    goto_authenticated(page, f"{BASE_URL}/home/teach-ai")
    expect(teach_ai.add_file_button()).to_be_visible()

    # Already uploaded from a previous run — wait for any processing, then assert
    if _is_pdf_already_uploaded(teach_ai):
        _wait_for_generation_to_finish(page, teach_ai)
        _assert_pdf_listed(teach_ai)
        return

    # Step 2: Click "Add file" (opens upload dialog)
    teach_ai.add_file_button().click()
    teach_ai.upload_dialog_file_input().wait_for(state="attached", timeout=DEFAULT_TIMEOUT)

    # Step 3–4: Attach PDF via hidden input (no "Upload file" / OS dialog)
    teach_ai.upload_dialog_file_input().set_input_files(str(PDF_PATH))
    expect(teach_ai.confirm_button()).to_be_enabled(timeout=DEFAULT_TIMEOUT)

    # Step 5: Click "Confirm"
    teach_ai.confirm_button().click()

    # Step 6–7: Wait for "Generating data" to finish
    _wait_for_generation_to_finish(page, teach_ai)

    # Step 8: Assert uploaded file appears in the document list
    _assert_pdf_listed(teach_ai)
