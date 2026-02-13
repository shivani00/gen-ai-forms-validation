import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from config import UPLOAD_DIR, SPEC_DIR
from core.pdf_renderer import find_form_page, render_pdf_page_base64
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
    pdf: UploadFile = File(...)
):
    # Save uploaded PDF
    pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    # Load JSON to extract form codes
    full_json = load_full_json()
    
    # Extract form codes from policy.forms[]
    forms = full_json.get("policy", {}).get("forms", [])
    
    if not forms:
        return {
            "status": "failed",
            "error": "No forms found in policy data."
        }
    
    validation_results = []
    
    # Validate each form in the policy
    for form in forms:
        form_id = form.get("formCode")
        
        if not form_id:
            continue
        
        print(f"Processing form with form_id: {form_id}")
        
        # Convert PDF page to image
        page_number = find_form_page(pdf_path, form_id)

        if page_number == -1:
            validation_results.append({
                "form_id": form_id,
                "status": "failed",
                "error": f"Form {form_id} not found in uploaded PDF."
            })
            continue

        print(f"Detected {form_id} on page {page_number}")

        # Convert correct page to image
        pdf_image_b64 = render_pdf_page_base64(pdf_path, page_number=page_number)

        # Load Word spec
        word_path = os.path.join(SPEC_DIR, f"{form_id}_spec.docx")

        template_image_b64, mapping_table = extract_word_spec(word_path)

        # Vision validation
        result = validate_with_vision(
            form_id,
            template_image_b64,
            pdf_image_b64,
            mapping_table,
            full_json
        )

        validation_results.append({
            "form_id": form_id,
            "status": "completed",
            "validation": result
        })
    print(f"validation_results: {validation_results}")
    return {
        "status": "completed",
        "total_forms": len(forms),
        "results": validation_results
    }