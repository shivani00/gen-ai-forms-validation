import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data", "uploads")

UPLOAD_DIR = DATA_DIR
SPEC_DIR = DATA_DIR
MASTER_JSON_PATH = os.path.join(DATA_DIR, "forms_data.json")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")