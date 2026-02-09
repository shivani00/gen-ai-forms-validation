from pdf2image import convert_from_path
import pytesseract
from logger import get_logger

# ✅ REQUIRED ON WINDOWS — SET TESSERACT PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ REQUIRED ON WINDOWS — SET POPPLER PATH
POPPLER_PATH = r"C:\poppler-25.11.0\Library\bin"

logger = get_logger("PDF")

def extract_pdf_ocr(pdf_path):
    logger.info(f"📄 Converting PDF to images: {pdf_path}")

    pages = convert_from_path(
        pdf_path,
        dpi=200,
        poppler_path=POPPLER_PATH
    )

    logger.info(f"📄 Pages detected: {len(pages)}")

    ocr = []

    for page_no, page in enumerate(pages):
        logger.info(f"🔍 OCR page {page_no + 1}")

        data = pytesseract.image_to_data(
            page,
            output_type=pytesseract.Output.DICT
        )

        for i, txt in enumerate(data["text"]):
            if txt.strip():
                ocr.append({
                    "page": page_no + 1,
                    "text": txt,
                    "bbox": {
                        "x": data["left"][i],
                        "y": data["top"][i],
                        "w": data["width"][i],
                        "h": data["height"][i]
                    },
                    "page_size": page.size
                })

    logger.info(f"🧠 OCR tokens collected: {len(ocr)}")
    return ocr
