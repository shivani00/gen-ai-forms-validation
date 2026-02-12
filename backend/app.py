import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from config import UPLOAD_DIR, SPEC_DIR
from core.pdf_renderer import render_pdf_page_base64
from core.word_parser import extract_word_spec
from core.json_loader import load_full_json
from core.vision_validator import validate_with_vision
from config import UPLOAD_DIR, SPEC_DIR

app = FastAPI()

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/validate")
async def validate_form(
    pdf: UploadFile = File(...),
    form_id: str = Form(...)
):

    print("Call coming to app.py with form_id:", form_id)
    # Save uploaded PDF
    pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    # Convert PDF page to image (page 0 assumed)
    pdf_image_b64 = render_pdf_page_base64(pdf_path, page_number=0)

    # Load Word spec
    word_path = os.path.join(SPEC_DIR, f"{form_id}_spec.docx")

    template_image_b64, mapping_table = extract_word_spec(word_path)

    # Load JSON
    full_json = load_full_json()

    # Vision validation
    result = validate_with_vision(
        form_id,
        template_image_b64,
        pdf_image_b64,
        mapping_table,
        full_json
    )

    return {
        "status": "completed",
        "form_id": form_id,
        "validation": result
    }