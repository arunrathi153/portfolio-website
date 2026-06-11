# resume_reader.py
import os
from typing import Optional
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import docx  # python-docx
except Exception:
    docx = None

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    if PyPDF2 is None:
        print("PyPDF2 not installed; can't read PDFs.")
        return None
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for p in reader.pages:
                page_text = p.extract_text()
                if page_text:
                    text += "\n" + page_text
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None

def extract_text_from_txt(txt_path: str) -> Optional[str]:
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {txt_path}: {e}")
        return None

def extract_text_from_docx(docx_path: str) -> Optional[str]:
    if docx is None:
        print("python-docx not installed; can't read .docx files.")
        return None
    try:
        doc = docx.Document(docx_path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
        return None

def extract_text(file_path: str) -> Optional[str]:
    file_path = file_path.strip()
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".txt"):
        return extract_text_from_txt(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file type for {file_path}. Supported: .pdf, .txt, .docx")
        return None