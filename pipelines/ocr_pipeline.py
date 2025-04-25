import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
import os

tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def run_ocr_pipeline(pdf_path, book_id):
    output_dir = "data/cleaned_books"
    output_path = os.path.join(output_dir, f"{book_id}.txt")
    os.makedirs(output_dir, exist_ok=True)

    text = ""
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            img = Image.open(BytesIO(pix.tobytes()))
            page_text = pytesseract.image_to_string(img, lang="eng")
            text += page_text + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return output_path
