# backend/rag/index_builder.py

from services.word_service import extract_layout_from_word
from logger import get_logger

logger = get_logger("RAG_INDEX")


def build_index(word_path):
    """
    Build lightweight in-memory index from Word spec.
    No embeddings. Just structured memory.
    """

    logger.info("📄 Building spec index")

    layout = extract_layout_from_word(word_path)

    mapping = layout.get("mapping", {})
    image_size = layout.get("image_size")

    index = {
        "total_fields": len(mapping),
        "mapping": mapping,
        "image_size": image_size
    }

    logger.info("✅ Spec index created")

    return index
