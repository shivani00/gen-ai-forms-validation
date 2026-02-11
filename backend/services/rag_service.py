# services/rag_service.py

from rag.index_builder import build_index
from rag.retriever import retrieve_full_context
from logger import get_logger

logger = get_logger("RAG_SERVICE")


def build_spec_context(word_path):
    """
    High-level RAG orchestrator.
    Builds index and retrieves structured context.
    """

    logger.info("🧠 Building RAG spec context")

    index = build_index(word_path)
    context = retrieve_full_context(index)

    logger.info("✅ RAG context ready")

    return context
