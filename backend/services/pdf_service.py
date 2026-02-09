import fitz  # PyMuPDF
from logger import get_logger

logger = get_logger("PDF")


def extract_pdf_ocr(pdf_path):
    logger.info(f"📄 Extracting text from PDF: {pdf_path}")

    doc = fitz.open(pdf_path)
    ocr = []

    for page_no in range(len(doc)):
        page = doc[page_no]
        logger.info(f"🔍 Reading page {page_no + 1}")

        blocks = page.get_text("blocks")
        page_width = int(page.rect.width)
        page_height = int(page.rect.height)

        tokens_on_page = 0

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block

            text = text.strip()
            if not text:
                continue

            tokens_on_page += 1

            ocr.append({
                "page": page_no + 1,
                "text": text,
                "confidence": 100,
                "bbox": {
                    "x": int(x0),
                    "y": int(y0),
                    "w": int(x1 - x0),
                    "h": int(y1 - y0)
                },
                "page_size": (page_width, page_height)
            })

        logger.info(f"🧾 Tokens on page {page_no + 1}: {tokens_on_page}")

    logger.info(f"🧠 Total tokens collected: {len(ocr)}")
    return ocr
