import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

INPUT_PATH = Path(os.getenv("INPUT_PATH", "./data/input"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", "./data/output"))
WEB_FORM_URL = os.getenv("WEB_FORM_URL", "https://rpachallenge.com/")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

LOG_DIR = OUTPUT_PATH / "logs"
