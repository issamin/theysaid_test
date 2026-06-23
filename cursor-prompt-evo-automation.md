# Cursor Prompt — E2E Automation for evo.dev.theysaid.io

Paste everything below into Cursor (Agent/Composer mode) inside your test repo.

---

## Context

We are building Playwright (Python) end-to-end tests for `https://evo.dev.theysaid.io/`.

Login is already implemented and working — **do not touch login code, do not include a login flow**. Assume an authenticated session/storage state is already available (e.g. via an existing `auth.json` storage state or an existing login fixture). If no such fixture exists yet, create a minimal `conftest.py` fixture that loads a pre-saved Playwright `storage_state` from `./fixtures/auth_state.json` and reuse it across all three test threads below — do not write new login steps.

Build **three independent, parallelizable test files**, each runnable on its own (`pytest -n auto` / `pytest-xdist` should be able to run them in parallel with no shared mutable state between them). Each thread gets its own file, its own fixtures, and its own test data — they must not depend on each other's output, except where explicitly noted (Thread 2 produces a project link that Thread 2 itself must persist; Threads do not need each other's projects to run).

## Repository conventions to use

- Test file layout: `tests/test_create_project.py`, `tests/test_teach_ai_upload.py` (plus a third file if you split further — see Thread 3 placeholder below)
- Shared fixture file: `tests/conftest.py`
- Sample file used for all uploads: `./fixtures/PDF.pdf` (already exists in the repo — reference it by relative path, do not hardcode an absolute path)
- Output directory: `./output/` (create if missing)
- Project link from Thread 2 must be saved to `./output/project-link.txt` (plain text, one line, overwrite on each run; create the `./output/` directory if it doesn't exist)
- Use Python 3.10+, `pytest`, `pytest-playwright`, type hints on helper functions, and `pathlib.Path` for all file paths (no hardcoded OS-specific separators)
- Base URL `https://evo.dev.theysaid.io/` should live in `pytest.ini` / `playwright.config` or a `BASE_URL` constant in `conftest.py`, not inlined in every test

## IMPORTANT — selector discovery step (do this first, before writing test code)

The exact selectors, button text, and DOM structure for this app are not provided to you verbatim — you must discover them yourself before writing assertions/locators. Do this:

1. Use Playwright's codegen or trace viewer (`playwright codegen https://evo.dev.theysaid.io/`) against the authenticated session, or ask me to run it and paste back the generated locators if you don't have an authenticated browser session available in this environment.
2. Prefer this locator priority order, in this order, falling back down the list only if the preferred option isn't available in the DOM:
   1. `get_by_role(...)` with accessible name (e.g. `page.get_by_role("button", name="Add Project")`)
   2. `get_by_text(...)` for exact visible text from the spec below
   3. `data-testid` attributes if present in the DOM
   4. CSS selector as a last resort, with a comment explaining why role/text/testid weren't usable
3. Do not invent class names, IDs, or testids that you have not actually observed in the rendered DOM. If you cannot verify a selector, mark it with a `# TODO: verify selector` comment and use the most plausible role/text-based locator as a placeholder rather than a guessed CSS class.
4. Every button/link click in the steps below is described by its **visible label text** — use that as the accessible name for `get_by_role`/`get_by_text` lookups.

## Global waiting/assertion strategy (apply throughout, do not use fixed `sleep()`)

- Never use bare `page.wait_for_timeout()` as the primary wait strategy for app state changes — only as a last-resort fallback with a comment, capped at a few seconds.
- For "wait until X loads / wait until button Y appears" steps, use `page.get_by_role(...).wait_for(state="visible", timeout=...)` (default 30s timeout, override per-step where the app is known to be slow, e.g. AI generation steps — use 60–90s for those).
- For loading-state text (e.g. "Generating data"), assert it appears first (`expect(locator).to_be_visible()`), then assert it disappears (`expect(locator).to_be_hidden()` or `.not_to_be_visible()`) before asserting the next step's success state — don't just wait for the next button blindly.
- Wrap each multi-step flow in clearly commented sections matching the numbered steps in this spec, so failures are easy to localize to a specific step.
- Add a screenshot-on-failure hook (Playwright's built-in `page.screenshot()` on test failure, or rely on `pytest-playwright`'s automatic trace/video/screenshot-on-failure config) so failed runs are debuggable.

---

## Thread 1 — Create Project Flow

File: `tests/test_create_project.py`

Test name: `test_create_project_flow`

Steps (map each to a clearly commented block):

1. Click the **"Add Project"** button.
2. Fill the URL field with: `https://jsonplaceholder.typicode.com/`
3. Fill the **Additional Information** field with this exact text (load it from a constant at the top of the file, not inline, since it's long):

   ```
   Thank you for taking part in this survey. We're exploring how testers, developers, and students use free mock REST APIs — like `jsonplaceholder.typicode.com` — to learn and practice API testing skills before working with real production systems.
   Your responses will help us understand which features of these sandbox APIs are most valuable, where they fall short, and whether they're effective tools for onboarding and training. This should take about 5 minutes to complete. All responses are anonymous and will be used solely to improve our testing curriculum and tooling recommendations.
   ```

4. Attach a file: use `./fixtures/PDF.pdf` via the file input's `set_input_files()` (find the actual `<input type="file">` — it may be hidden behind a styled "Attach file" button; locate the underlying input rather than trying to click-and-pick a native OS file dialog, since Playwright can't interact with OS dialogs).
5. Click **"Create AI User Test"**.
6. Click **"Start with AI"**.
7. Click **"Apply Ai Suggestion"**.
8. Click **"Continue to Learning goals"**, then wait for the page to finish loading until the *next* button is visible before proceeding (don't assume a fixed transition time — wait on the next expected element's visibility, ~30–60s timeout).
9. Wait for the page to load until the **"Publish"** button appears (visibility wait, generous timeout — this may involve AI generation, allow up to 60–90s).
10. Click **"Create Project"**.
11. Click **"Copy link"**.
    - The link is copied to the clipboard, not necessarily rendered as text in the DOM. Read it via Playwright's clipboard access (`page.evaluate("navigator.clipboard.readText()")` — note this requires clipboard permissions; grant `clipboard-read`/`clipboard-write` permissions on the browser context in the fixture).
    - If the UI also displays the link as visible text near the "Copy link" button, prefer reading it directly from that DOM element instead of the clipboard — it's more reliable in headless CI. Try DOM-text extraction first, fall back to clipboard read if no visible link text exists.
    - Write the captured link to `./output/project-link.txt` (create `./output/` if missing), overwriting any previous content.
    - Assert the captured string looks like a URL (e.g. starts with `http`) before writing it, and fail the test with a clear message if it doesn't.

Add assertions after each major step confirming the expected next-state element is visible (e.g. after step 1, assert the URL field is visible; after step 5, assert the AI test UI loaded; etc.) so a failure clearly points to which step broke, rather than only asserting at the very end.

---

## Thread 2 — Teach AI Upload Document Flow

File: `tests/test_teach_ai_upload.py`

Test name: `test_teach_ai_upload_document`

This flow assumes a project already exists for the authenticated user to navigate into "Teach AI" from. If "Teach AI" is scoped per-project, add a fixture/helper that either (a) navigates to an existing known project first, or (b) reuses the project created in Thread 1 if one is required — but do **not** make this test depend on Thread 1 running first in the same session; instead, add a small setup helper in this file that ensures at least one project exists (reuse a "find or create" helper) so this test can run standalone in parallel.

Steps:

1. Locate and click the **"Teach AI"** link/nav item.
2. Click the **"Add file"** button.
3. Click the **"Upload file"** button.
4. Upload `./fixtures/PDF.pdf` via the underlying `<input type="file">` (same approach as Thread 1, step 4 — find the real file input, use `set_input_files()`, don't try to click through an OS dialog).
5. Click the **"Confirm"** button.
6. Assert the **"Generating data"** loading text becomes visible (`expect(...).to_be_visible()`).
7. Wait for the **"Generating data"** loading text to disappear (`to_be_hidden()`), with a generous timeout (60–90s, since this is AI processing) — do not proceed to the next assertion until this resolves.
8. After generating completes, assert the uploaded file (e.g. `PDF.pdf`) appears in whatever file list/UI element represents "Teach AI" documents — confirm by visible filename text and/or a success indicator, not just absence of the loading spinner.


---

## Thread 3 — Answer Survey Flow

File: `tests/test_answer_survey.py`

Test name: `test_answer_survey_flow`

This flow consumes the project link produced by Thread 1, opened in a **separate browser context/tab** (this is a respondent-facing survey link, not an authenticated dashboard view — it should be opened in its own fresh `BrowserContext`, not the authenticated context used elsewhere, since a real survey respondent would not be logged in).

Setup:

1. Read the link from `./output/project-link.txt` (written by Thread 1). If the file doesn't exist or is empty, fail the test early with a clear message instructing the user to run the create-project flow first — don't silently skip.
2. Open a **new, separate `BrowserContext`** (and a new `page` within it) — do not reuse the authenticated context/page from other threads. This simulates a respondent opening the link fresh, e.g. in a new tab.
3. Navigate to the link.

Survey-answering loop (the structure/number/types of questions is not known ahead of time — the test must handle this generically and dynamically, not assume a fixed question count or fixed question text):

4. Loop until a clear end-of-survey state is reached (e.g. a "Thank you" / completion screen, or no further "Continue"/"Next"/"Submit" button is found):
   - Detect the current question's input type by inspecting what's actually rendered, in this priority order:
     - **Multiple choice / option buttons / radio / checkbox** — if `get_by_role("radio")`, `get_by_role("checkbox")`, or clickable option elements (cards/buttons representing answer choices) are present, select one option. Prefer the first available option unless a more deterministic choice is obviously indicated (e.g. always picking index 0 is fine — note this in a comment as "arbitrary choice, AI-graded survey doesn't require a specific answer").
     - **Free-text field** — if a `textarea` or `get_by_role("textbox")` is present instead, fill it with a generic but plausible placeholder response (e.g. a constant string like `"This is a test response generated by automated QA."`) long enough to satisfy any visible minimum-length validation if present.
     - **Rating/scale (e.g. NPS-style 0–10 or star rating)** — if neither of the above matches but numbered buttons or a scale widget is present, click a value roughly in the middle of the range as a safe default.
   - After answering, locate and click whichever continuation control is present and visible — check in this order: **"Continue"**, **"Next"**, **"Submit"**, **"Finish"** (use `get_by_role("button", name=re.compile(...))` with a case-insensitive pattern matching any of these, since the exact label may vary question-to-question).
   - Wait for the next question (or the end screen) to become visible before the next loop iteration — don't assume a fixed transition time; wait on visibility of new question content or the completion state.
   - Cap the loop at a safety limit (e.g. 50 iterations) and fail with a clear message if exceeded, to avoid an infinite loop if the survey UI doesn't match any detection branch — log which step/iteration it got stuck on and a snippet of the unmatched DOM state for debugging.
5. Once the loop exits via a detected completion state, assert that some clear "thank you" / completion indicator is visible (e.g. text containing "thank you", "complete", "submitted" — case-insensitive partial match) to confirm the survey was actually finished rather than the loop simply running out of recognizable controls.

Notes:
- Because question content/order is AI-generated and not fixed, this test should assert on **structure and successful completion**, not on specific question text or specific answer content.
- Add a comment at the top of the file noting that answer selection is intentionally arbitrary/best-effort since there's no "correct" answer to grade against — the goal is verifying the respondent flow doesn't break, not validating survey logic.
- Take a screenshot at the final completion state (success or failure) for debugging, in addition to whatever screenshot-on-failure hook is already configured globally.


## Cross-cutting requirements

- **Independence**: Each test file should be runnable via `pytest tests/test_create_project.py` or `pytest tests/test_teach_ai_upload.py` alone, and also together via `pytest -n 2 tests/` without race conditions (e.g. don't have both threads create a project with the same hardcoded name if project name uniqueness matters — use a timestamp or `uuid4()` suffix in any project name/identifier you must supply, if the "Add Project" flow requires one we haven't been told about explicitly; check the actual UI for a name field and only add this if it exists).
- **Idempotency**: Re-running these tests shouldn't fail due to leftover state from a previous run (e.g. duplicate file names, duplicate projects) — use unique-enough identifiers where the app requires user-supplied names.
- **Config**: Add/update `pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` with `base_url`, default timeout, and `pytest-playwright` browser/headless settings as project-level config rather than per-test.
- **No fixed sleeps** except as a last-resort fallback (see waiting strategy above).
- **Comments**: Each numbered step in this spec should have a matching comment in the code (e.g. `# Step 5: Click "Create AI User Test"`) so the mapping from this spec to code is traceable.
- **Don't write or modify login code.** If existing login fixtures/helpers exist in the repo, search for and reuse them; ask me before creating new auth scaffolding if none is found.

## Deliverables

1. `tests/conftest.py` — shared fixtures (authenticated context/page, base URL, clipboard permissions, output dir setup)
2. `tests/test_create_project.py` — Thread 1
3. `tests/test_teach_ai_upload.py` — Thread 2
4. Updated `pytest.ini`/`pyproject.toml` config
5. A short `README.md` section (or inline docstring) per test file noting any selectors marked `# TODO: verify selector` so I know what to double check against the live app

If at any point a button/field named in this spec doesn't exist verbatim in the rendered DOM (e.g. slightly different label, or it's an icon-only button), stop and ask me rather than guessing silently — list the closest candidates you found via role/text search.
