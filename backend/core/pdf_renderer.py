import fitz
import base64
from io import BytesIO
from PIL import Image


def render_pdf_page_base64(pdf_path: str, page_number: int = 0):

    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=300)

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode()

    return base64_img

import fitz


def find_form_page(pdf_path: str, form_id: str) -> int:
    """
    Scan all pages and return page index that contains form_id text.
    Returns -1 if not found.
    """
    doc = fitz.open(pdf_path)

    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text()

        if form_id.lower() in text.lower():
            return i

    return -1