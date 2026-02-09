from services.llm_service import semantic_check
from logger import get_logger
import re

logger = get_logger("VALIDATION")

# --------------------------------------------------
# Utilities
# --------------------------------------------------
def normalize(text):
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def get_value_from_json(obj, path):
    parts = path.split(".")
    val = obj
    for p in parts:
        if not isinstance(val, dict):
            return None
        val = val.get(p)
    return str(val).strip() if val is not None else None


# --------------------------------------------------
# Exact labels as they appear in PDF
# --------------------------------------------------
FIELD_LABELS = {
    "customer.name": "name",
    "policy.name": "policy name",
    "policy.number": "policy number",
    "policy.effective_date": "policy effective date",
    "policy.premium.amount": "premium",
    "customer.address.home": "address"
}


# --------------------------------------------------
# Isolate tokens belonging to one form
# --------------------------------------------------
def isolate_form_tokens(pdf_ocr, form_id):
    form_tokens = []
    inside = False

    for t in pdf_ocr:
        text = normalize(t["text"])

        if text == f"form {form_id}".lower():
            inside = True
            continue

        if inside and text.startswith("form "):
            break

        if inside:
            form_tokens.append(t)

    return form_tokens


# --------------------------------------------------
# Extract value from SAME token if multiline,
# otherwise look ahead
# --------------------------------------------------
def extract_value(tokens, label):
    label_norm = normalize(label)

    for i, t in enumerate(tokens):
        raw_text = t["text"]
        text_norm = normalize(raw_text)

        if label_norm in text_norm:
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

            # Case 1: label + value in same token
            if len(lines) > 1:
                return lines[-1]

            # Case 2: value in next token
            for j in range(i + 1, len(tokens)):
                candidate = tokens[j]["text"].strip()
                if candidate:
                    return candidate

    return None


# --------------------------------------------------
# Main validation
# --------------------------------------------------
def validate(layout, expected_json, pdf_ocr):
    results = []

    form_id = get_value_from_json(expected_json, "policy.number")
    logger.info(f"📄 Validating form {form_id}")

    if not form_id:
        logger.error("❌ policy.number missing")
        return []

    form_tokens = isolate_form_tokens(pdf_ocr, form_id)

    if not form_tokens:
        logger.error(f"❌ Form {form_id} not found in PDF")
        for path in layout["mapping"].values():
            results.append({
                "tag": path,
                "expected": get_value_from_json(expected_json, path),
                "extracted": None,
                "status": "FAIL",
                "confidence": 0.0,
                "explanation": "Form not found in PDF"
            })
        return results

    for json_path in layout["mapping"].values():
        logger.info(f"🔎 Validating field: {json_path}")

        expected = get_value_from_json(expected_json, json_path)
        label = FIELD_LABELS.get(json_path)

        extracted = extract_value(form_tokens, label)

        logger.info(f"🧾 Expected : {expected}")
        logger.info(f"🧾 Extracted: {extracted}")

        if not extracted:
            results.append({
                "tag": json_path,
                "expected": expected,
                "extracted": None,
                "status": "FAIL",
                "confidence": 0.0,
                "explanation": "Value not found in PDF"
            })
            continue

        llm = semantic_check(
            field_name=json_path,
            expected=expected,
            extracted=extracted
        )

        confidence = float(llm.get("confidence", 0.0))
        explanation = llm.get("explanation", "")

        status = "PASS" if confidence >= 0.8 else "FAIL"

        results.append({
            "tag": json_path,
            "expected": expected,
            "extracted": extracted,
            "status": status,
            "confidence": confidence,
            "explanation": explanation
        })

    return results