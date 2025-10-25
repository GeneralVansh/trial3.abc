import pdfplumber
from PIL import Image
import pytesseract
import docx
import os

# Optional: set path to tesseract executable if needed (uncomment and edit)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
                else:
                    try:
                        img = page.to_image(resolution=300).original
                        text += pytesseract.image_to_string(img) + " "
                    except Exception:
                        pass
    except Exception:
        try:
            text = pytesseract.image_to_string(Image.open(pdf_path))
        except Exception:
            text = ""
    return text.strip()

def extract_text_docx(docx_path: str) -> str:
    try:
        doc = docx.Document(docx_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return " ".join(paragraphs).strip()
    except Exception:
        return ""

def extract_text_image(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img).strip()
    except Exception:
        return ""

def extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_pdf(path)
    elif ext in [".docx"]:
        return extract_text_docx(path)
    elif ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
        return extract_text_image(path)
    else:
        try:
            return pytesseract.image_to_string(Image.open(path)).strip()
        except Exception:
            return ""
