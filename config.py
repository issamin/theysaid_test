from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = ROOT_DIR / "fixtures"
OUTPUT_DIR = ROOT_DIR / "output"
AUTH_STATE_PATH = FIXTURES_DIR / "auth_state.json"
PDF_PATH = FIXTURES_DIR / "PDF.pdf"
PROJECT_LINK_PATH = OUTPUT_DIR / "project-link.txt"
BASE_URL = "https://evo.dev.theysaid.io"

DEFAULT_TIMEOUT = 30_000
AI_GENERATION_TIMEOUT = 90_000
TEACH_AI_UPLOAD_TIMEOUT = 180_000  # 3 min — AI document processing after upload
