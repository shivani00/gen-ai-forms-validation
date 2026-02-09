from services.llm_service import semantic_check
from logger import get_logger

logger = get_logger("VALIDATION")

def get_value_from_json(obj, path):
    parts = path.split(".")
    val = obj
    for p in parts:
        if not isinstance(val, dict):
            return None
        val = val.get(p)
    return str(val) if val is not None else None


def validate(layout, expected_json, pdf_ocr):
    results = []
    img_w, img_h = layout["image_size"]

    for pos, json_path in layout["mapping"].items():
        logger.info(f"🔎 Validating field: {json_path}")

        marker = layout["markers"].get(pos)
        expected = get_value_from_json(expected_json, json_path)

        if not marker:
            logger.warning(f"⚠️ Marker missing for {json_path}")
            results.append({
                "tag": json_path,
                "status": "FAIL",
                "explanation": "Marker not found in Word image"
            })
            continue

        match_text = None

        for o in pdf_ocr:
            if o["page"] != 1:
                continue

            sx = o["page_size"][0] / img_w
            sy = o["page_size"][1] / img_h
            mx = int(marker["x"] * sx)
            my = int(marker["y"] * sy)

            if abs(o["bbox"]["x"] - mx) < 60 and abs(o["bbox"]["y"] - my) < 60:
                match_text = o["text"]
                break

        if not match_text:
            logger.warning(f"❌ No OCR match near marker for {json_path}")
            results.append({
                "tag": json_path,
                "status": "FAIL",
                "explanation": "No PDF text near expected position"
            })
            continue

        llm = semantic_check(json_path, expected, match_text)

        logger.info(
            f"🤖 LLM confidence={llm['confidence']} for {json_path}"
        )

        results.append({
            "tag": json_path,
            "expected": expected,
            "found": match_text,
            "confidence": llm["confidence"],
            "status": "PASS" if llm["confidence"] >= 0.7 else "FAIL",
            "explanation": llm["explanation"]
        })

    return results
