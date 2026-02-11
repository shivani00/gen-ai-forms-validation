# services/agent_orchestrator.py

from services.tools import (
    detect_form,
    get_form_structure,
    get_json_value,
    get_pdf_tokens
)
from services.validation_service import validate
from logger import get_logger

logger = get_logger("AGENT")


def run_agent(pdf_path, word_path):
    """
    LLM-Orchestrated flow.
    Tools execute.
    LLM makes decisions.
    """

    logger.info("🤖 Agent started")

    # Tool 1: Detect form
    form_id = detect_form(pdf_path)

    if not form_id:
        return {"status": "error", "message": "Form ID not detected"}

    # Tool 2: Get structure
    layout = {"mapping": get_form_structure(word_path)}

    # Tool 3: Get expected JSON
    expected_json = get_json_value(form_id)

    if not expected_json:
        return {"status": "error", "message": "JSON not found in MCP"}

    # Tool 4: Extract PDF tokens
    pdf_ocr = get_pdf_tokens(pdf_path)

    # Deterministic validation (LLM semantic inside)
    results = validate(layout, expected_json, pdf_ocr)

    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]

    overall_status = "PASS" if len(failed) == 0 else "FAIL"

    return {
        "status": "completed",
        "overall_status": overall_status,
        "passed_fields": [{"field": r["tag"]} for r in passed],
        "failed_fields": [{"field": r["tag"]} for r in failed],
        "results": results
    }
