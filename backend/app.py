from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.word_service import extract_layout_from_word
from services.pdf_service import extract_pdf_ocr
from services.validation_service import validate
from logger import get_logger
import json
import os
import shutil

print("🔥🔥🔥 backend.app LOADED 🔥🔥🔥", flush=True)

logger = get_logger("APP")

app = FastAPI()

# -----------------------------
# ✅ FIX: ABSOLUTE UPLOAD PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# ✅ CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/validate")
async def validate_documents(
    pdf: UploadFile = File(...),
    word: UploadFile = File(...),
    data: UploadFile = File(...)
):
    print("🔥🔥🔥 /validate HIT 🔥🔥🔥", flush=True)
    logger.info("📥 Validation request received")

    pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)
    word_path = os.path.join(UPLOAD_DIR, word.filename)
    json_path = os.path.join(UPLOAD_DIR, data.filename)

    for file, path in [(pdf, pdf_path), (word, word_path), (data, json_path)]:
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    logger.info(f"📁 Files saved to {UPLOAD_DIR}")

    with open(json_path) as f:
        expected_json = json.load(f)

    layout = extract_layout_from_word(word_path)
    pdf_ocr = extract_pdf_ocr(pdf_path)
    results = validate(layout, expected_json, pdf_ocr)

    logger.info("✅ Validation completed")

    return {
        "status": "completed",
        "results": results
    }
