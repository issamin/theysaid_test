# TheySaid E2E Automation

Playwright (Python) end-to-end tests for [evo.dev.theysaid.io](https://evo.dev.theysaid.io/).

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill in credentials
python tests/test_login_flow.py   # optional: refresh auth state
```

Auth state is cached at `fixtures/auth_state.json` and reused by all tests.

## Run tests

From the project root:

```bash
pytest tests/test_create_project.py
pytest tests/test_teach_ai_upload.py
pytest tests/test_answer_survey.py

# All tests (parallel — run Thread 1 first if project-link.txt is missing)
pytest -n 3 tests/
```

Or `cd tests` and run pytest directly (config is picked up from the parent `pytest.ini`):

```bash
cd tests
pytest test_create_project.py
pytest   # all E2E tests
```

Login script (refreshes auth state — not a pytest test):

```bash
python tests/test_login_flow.py
```

Set `HEADLESS=false` in `.env` to run headed.

## Project layout

| Path | Purpose |
|------|---------|
| `tests/conftest.py` | Shared fixtures (auth, clipboard, screenshots on failure) |
| `tests/test_login_flow.py` | Standalone login script (refreshes auth state) |
| `tests/test_create_project.py` | Thread 1 — create project flow |
| `tests/test_teach_ai_upload.py` | Thread 2 — Teach AI document upload |
| `tests/test_answer_survey.py` | Thread 3 — answer survey as respondent (needs `output/project-link.txt`) |
| `locators/` | Page locators (role/text based) |
| `fixtures/PDF.pdf` | Sample upload file |
| `output/project-link.txt` | Project link written by Thread 1 |

## Selectors to verify

Some labels differ from the spec in the live DOM. Check `locators/project_locators.py`, `locators/teach_ai_locators.py`, and `locators/survey_locators.py` for `# TODO: verify selector` comments and observed label notes in each test file docstring.
