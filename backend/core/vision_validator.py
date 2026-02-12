import json
import google.generativeai as genai
from config import GEMINI_API_KEY
from logger import get_logger

logger = get_logger("VISION_VALIDATOR")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def validate_with_vision(
    form_id: str,
    template_image_b64: str,
    pdf_image_b64: str,
    mapping_table: list,
    full_json: dict
):

    prompt = f"""
You are a STRICT insurance form visual validation AI.

Inputs:
1) TEMPLATE IMAGE contains numeric markers indicating field regions.
2) FILLED PDF PAGE IMAGE is the actual generated form.
3) FIELD MAPPING TABLE:
{json.dumps(mapping_table, indent=2)}

4) FULL JSON DATA:
{json.dumps(full_json, indent=2)}

For form_id = {form_id}:

For each entry in FIELD MAPPING TABLE:
- Extract expected value using json_path.
- Locate region marked by position in TEMPLATE IMAGE.
- Identify same relative region in FILLED PDF IMAGE.
- Extract actual value from that region.
- Compare values exactly (no normalization).
- Check if value appears in correct region.

Rules:
- Do NOT hallucinate.
- If region missing → FAIL.
- If value mismatch → FAIL.
- Only return JSON.
- No markdown.

Return EXACT JSON:

{{
  "overall_status": "PASS" | "FAIL",
  "results": [
    {{
      "position": 0,
      "json_path": "",
      "expected_value": "",
      "actual_value": "",
      "value_match": true,
      "position_match": true,
      "status": "PASS" | "FAIL",
      "reason": ""
    }}
  ]
}}
"""

    response = model.generate_content(
        [
            {"text": prompt},
            {
                "inline_data": {
                    "mime_type": "image/png",
                    "data": template_image_b64
                }
            },
            {
                "inline_data": {
                    "mime_type": "image/png",
                    "data": pdf_image_b64
                }
            }
        ]
    )

    text = response.text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        logger.error("Invalid JSON from Vision model")
        return {"error": "Invalid JSON from Vision model"}