import os
import json
import re
from logger import get_logger
import google.generativeai as genai
# import ollama

logger = get_logger("LLM")
# MODEL_NAME = "mistral";

# Load API key from environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def clean_json_response(text: str) -> str:
    """
    Removes markdown formatting like ```json ... ```
    """
    # Remove ```json or ``` blocks
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


def semantic_check(field: str = None, field_name: str = None, expected: str = None, extracted: str = None):
    """
    Compares expected and extracted values using LLM.
    Accepts either `field` or `field_name` for backward compatibility.
    Returns structured JSON with confidence and explanation.
    """

    # Support callers using either parameter name
    field_name = field_name or field

    prompt = f"""
You are a strict document validation system.

Compare the expected value and extracted value.

Return ONLY valid JSON in this format:
{{
  "confidence": number_between_0_and_1,
  "explanation": "short explanation"
}}

Field: {field_name}
Expected Value: {expected}
Extracted Value: {extracted}
"""

    try:
        response = model.generate_content(prompt)

        raw_text = response.text
        cleaned = clean_json_response(raw_text)

        result = json.loads(cleaned)

        # Safety fallback
        if "confidence" not in result or "explanation" not in result:
            raise ValueError("Invalid JSON structure from LLM")

        return result

    except Exception as e:
        logger.error(f"LLM parsing failed: {str(e)}")

        return {
            "confidence": 0.0,
            "explanation": "LLM parsing failed"
        }


# def semantic_check(field, expected, extracted):
#     """
#     Compare expected vs extracted using Ollama local model.
#     Returns: { confidence: float, explanation: str }
#     """

#     prompt = f"""
# You are a document validation AI.

# Compare the following values and determine if they match semantically.

# Field: {field}
# Expected Value: {expected}
# Extracted Value: {extracted}

# Respond ONLY in valid JSON format:
# {{
#   "confidence": number_between_0_and_1,
#   "explanation": "short explanation"
# }}
# """

#     try:
#         response = ollama.chat(
#             model=MODEL_NAME,
#             messages=[{"role": "user", "content": prompt}],
#         )

#         content = response["message"]["content"]

#         # Extract JSON safely
#         start = content.find("{")
#         end = content.rfind("}") + 1
#         json_str = content[start:end]

#         result = json.loads(json_str)

#         return {
#             "confidence": float(result.get("confidence", 0)),
#             "explanation": result.get("explanation", "No explanation")
#         }

#     except Exception as e:
#         logger.error(f"Ollama parsing failed: {str(e)}")

#         return {
#             "confidence": 0.0,
#             "explanation": "LLM parsing failed"
#         }