# backend/rag/retriever.py

from logger import get_logger

logger = get_logger("RAG_RETRIEVER")


def retrieve_full_context(index):
    """
    For Option A, retrieval simply returns full spec context.
    """

    logger.info("📚 Retrieving full spec context")

    return {
        "total_fields": index.get("total_fields"),
        "fields": list(index.get("mapping", {}).values()),
        "image_size": index.get("image_size")
    }
