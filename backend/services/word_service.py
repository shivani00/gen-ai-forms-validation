from docx import Document
from PIL import Image
import pytesseract
import io
import os
from logger import get_logger

# ✅ REQUIRED ON WINDOWS — SET TESSERACT PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logger = get_logger("WORD")


def extract_layout_from_word(word_path):
    logger.info(f"📄 Reading Word file: {word_path}")

    doc = Document(word_path)

    # -------------------------
    # Extract embedded image
    # -------------------------
    image = None
    for rel in doc.part._rels.values():
        if "image" in rel.target_ref:
            image = Image.open(io.BytesIO(rel.target_part.blob))
            break

    if not image:
        raise Exception("No image found in Word file")

    logger.info(f"🖼 Image extracted | size={image.size}")

    # -------------------------
    # Read mapping table
    # -------------------------
    table = doc.tables[0]
    position_to_tag = {}

    for row in table.rows[1:]:
        pos = int(row.cells[0].text.strip())
        tag = row.cells[1].text.strip()
        position_to_tag[pos] = tag

    logger.info(f"📋 Mapping table parsed | fields={len(position_to_tag)}")

    # -------------------------
    # OCR image to detect numeric markers
    # -------------------------
    data = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
        config="--psm 6 -c tessedit_char_whitelist=0123456789"
    )

    markers = {}

    for i, txt in enumerate(data["text"]):
        if txt.strip().isdigit():
            pos = int(txt.strip())
            if pos in position_to_tag:
                markers[pos] = {
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "w": data["width"][i],
                    "h": data["height"][i],
                }

    logger.info(f"🔢 Markers detected | count={len(markers)}")

    return {
        "image_size": image.size,
        "markers": markers,
        "mapping": position_to_tag
    }
