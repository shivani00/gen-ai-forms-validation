import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def semantic_check(tag, expected, found):
    prompt = f"""
Field: {tag}
Expected value: {expected}
Extracted value: {found}

Decide if they match semantically.
Respond ONLY in JSON:
{{"confidence":0-1,"explanation":"..."}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return eval(response.text)
