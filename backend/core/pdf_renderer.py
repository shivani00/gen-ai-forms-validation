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