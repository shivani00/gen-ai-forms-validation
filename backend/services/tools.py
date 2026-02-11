# services/tools.py

from services.pdf_service import extract_pdf_ocr
from services.word_service import extract_layout_from_word
from services.validation_service import normalize
from services.mcp_service import get_expected_json
from logger import get_logger

logger = get_logger("TOOLS")


def detect_form(pdf_path):
    pdf_ocr = extract_pdf_ocr(pdf_path)

    for token in pdf_ocr:
        text = normalize(token["text"])
        if text.startswith("form "):
            return text.replace("form ", "").strip()

    return None


def get_form_structure(word_path):
    layout = extract_layout_from_word(word_path)
    return layout.get("mapping", {})


def get_json_value(form_id):
    return get_expected_json(form_id)


def get_pdf_tokens(pdf_path):
    return extract_pdf_ocr(pdf_path)
