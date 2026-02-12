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
You are a STRICT, DETERMINISTIC insurance form visual validation engine.

You must behave like a validation algorithm — NOT a conversational AI.

==================================================
INPUTS
==================================================

1) TEMPLATE IMAGE:
   - Contains numeric position markers (e.g., 1, 2, 3, etc.)
   - Each marker defines a fixed region where a field is expected.

2) FILLED PDF PAGE IMAGE:
   - The actual generated insurance form.
   - Contains printed field labels and values.

3) FIELD MAPPING TABLE:
{json.dumps(mapping_table, indent=2)}

Each entry contains:
- position (numeric marker in template)
- json_path (location in FULL JSON DATA)

4) FULL JSON DATA:
{json.dumps(full_json, indent=2)}

Form ID:
{form_id}

==================================================
VALIDATION PROCESS (MANDATORY STEPS)
==================================================

For EACH mapping entry:

STEP 1 — EXPECTED VALUE
- Extract expected_value strictly using json_path from FULL JSON DATA.
- If json_path does not exist → expected_value = "".
- Convert expected_value to string.

STEP 2 — POSITION VALIDATION
- Locate numeric marker in TEMPLATE IMAGE.
- Identify exact corresponding region in FILLED PDF IMAGE.
- Extract only text that appears visually inside that region.
- Do NOT extract text outside the region.

If region cannot be located:
    position_match = false
Else:
    position_match = true

STEP 3 — ACTUAL VALUE EXTRACTION
- Extract visible printed value in the region.
- Do NOT infer.
- Do NOT guess.
- If nothing visible → actual_value = "".

Convert actual_value to string.

==================================================
VALUE COMPARISON RULES
==================================================

Always trim leading/trailing spaces before comparison.

CASE 1 — Numeric Values
If BOTH expected_value AND actual_value:
    - contain only digits, commas, spaces, or periods
Then:
    - Remove commas
    - Remove spaces
    - Remove currency symbols
    - Compare cleaned values
Example:
    18750 == 18,750
    1250000 == 12,50,000

CASE 2 — Comma/Semicolon Separated Lists
If values contain comma (,) OR semicolon (;):
    - Replace ";" with ","
    - Split by ","
    - Trim spaces
    - Convert to lowercase
    - Sort alphabetically
    - Compare lists
Order does NOT matter.

CASE 3 — All Other Text
- Compare EXACT string match
- Case-sensitive
- Do NOT auto-correct spelling
- Do NOT reformat text

==================================================
FAIL CONDITIONS
==================================================

status = FAIL if ANY of the following:

- position_match = false
- expected_value != actual_value after normalization
- expected_value is non-empty but actual_value is empty

Otherwise:
    status = PASS

==================================================
OVERALL STATUS
==================================================

If ANY field status = FAIL:
    overall_status = "FAIL"
Else:
    overall_status = "PASS"

==================================================
STRICT RULES
==================================================

- Do NOT hallucinate values.
- Do NOT infer hidden text.
- Do NOT assume formatting.
- Only use visible printed text.
- Only use provided JSON.
- Return VALID JSON ONLY.
- No markdown.
- No explanations outside JSON.

==================================================
RESPONSE FORMAT (EXACT)
==================================================

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