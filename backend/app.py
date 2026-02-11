from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from services.word_service import extract_layout_from_word
from services.pdf_service import extract_pdf_ocr
from services.validation_service import validate
from services.rag_service import build_spec_context
from services.mcp_service import get_expected_json
from services.mcp_service import load_database
from logger import get_logger
import os
import shutil

print("🔥🔥🔥 backend.app LOADED 🔥🔥🔥", flush=True)

logger = get_logger("APP")

app = FastAPI()

# -----------------------------
# 📁 ABSOLUTE UPLOAD PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

load_database(UPLOAD_DIR)

# -----------------------------
# 🌍 CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# 🚀 VALIDATION ENDPOINT (PDF ONLY)
# ==========================================================
@app.post("/validate")
async def validate_documents(
    pdf: UploadFile = File(...),
    form_id: str = Form(...)
):
    print("🔥🔥🔥 /validate HIT 🔥🔥🔥", flush=True)
    logger.info("📥 Validation request received")

    #------------------------------
    #Normalize form ID (ignore case)
    #------------------------------
    form_id = form_id.strip().upper()

    # -----------------------------
    # Save PDF
    # -----------------------------
    pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    logger.info(f"📁 PDF saved to {pdf_path}")

    # -----------------------------
    # Extract PDF OCR FIRST
    # -----------------------------
    pdf_ocr = extract_pdf_ocr(pdf_path)

    # -----------------------------
    # Load Expected JSON from in-memory DB
    # -----------------------------
    expected_json = get_expected_json(form_id)

    if not expected_json:
        logger.error(f"❌ No JSON found for form {form_id}")
        return {"error": f"No expected JSON found for form {form_id}"}

    # -----------------------------
    # Load Word Spec from uploads
    # -----------------------------
    word_filename = f"{form_id}_spec.docx"
    word_path = os.path.join(UPLOAD_DIR, word_filename)

    if not os.path.exists(word_path):
        logger.error(f"❌ Spec not found: {word_filename}")
        return {"error": f"Spec not found for form {form_id}"}

    # -----------------------------
    # Build RAG Context (SAFE)
    # -----------------------------
    spec_context = build_spec_context(word_path)

    # -----------------------------
    # Deterministic Layout Extraction
    # -----------------------------
    layout = extract_layout_from_word(word_path)

    # -----------------------------
    # Run Validation (UNCHANGED LOGIC)
    # -----------------------------
    results = validate(layout, expected_json, pdf_ocr)

    logger.info("✅ Validation completed")

    # -----------------------------
    # Structured Summary
    # -----------------------------
    passed_fields = [r for r in results if r["status"] == "PASS"]
    failed_fields = [r for r in results if r["status"] == "FAIL"]

    return {
        "status": "completed",
        "summary": {
            "total_fields": len(results),
            "passed": len(passed_fields),
            "failed": len(failed_fields)
        },
        "passed_fields": passed_fields,
        "failed_fields": failed_fields
    }
