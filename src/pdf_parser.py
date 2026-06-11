import pdfplumber
from docx import Document
import re


def extract_text_from_pdf(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return clean_text(text)


def extract_text_from_docx(file) -> str:
    doc = Document(file)
    text = "\n".join(para.text for para in doc.paragraphs)
    return clean_text(text)


def extract_text(file, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(file)
    elif ext == "txt":
        return clean_text(file.read().decode("utf-8", errors="ignore"))
    return ""


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()
