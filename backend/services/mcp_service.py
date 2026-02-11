# services/mcp_service.py
import os
import json
from logger import get_logger

logger = get_logger("MCP")

DATABASE = {}

def load_database(upload_dir):
    """
    Load all JSON files from uploads folder
    into in-memory database.
    """
    logger.info("📦 Loading JSON files into MCP memory")

    for file in os.listdir(upload_dir):
        if file.endswith(".json"):
            path = os.path.join(upload_dir, file)

            with open(path) as f:
                data = json.load(f)

            form_id = data.get("policy", {}).get("number")

            if form_id:
                form_id = form_id.strip().upper()
                DATABASE[form_id] = data
                logger.info(f"✅ Loaded JSON for form {form_id}")

def get_expected_json(form_id):
    """
    Fetch JSON by policy.number (used as form_id)
    """
    form_id = form_id.strip().upper()

    logger.info(f"🔎 MCP fetching JSON for form {form_id}")
    logger.info(f"📦 Available keys: {list(DATABASE.keys())}")

    return DATABASE.get(form_id)
