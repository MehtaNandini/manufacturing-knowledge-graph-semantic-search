import os
import fitz # PyMuPDF
import docx
from bs4 import BeautifulSoup
import re
from uuid import uuid4
from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/html"
]

def sanitize_filename(filename: str) -> str:
    # Prevent path traversal
    filename = os.path.basename(filename)
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

def extract_text_from_file(file_path: str, mime_type: str) -> list[dict]:
    pages = []
    
    if mime_type == "application/pdf":
        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            pages.append({
                "page_number": i + 1,
                "text": page.get_text()
            })
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file_path)
        # Word doesn't have true pages, simulate it
        pages.append({
            "page_number": 1,
            "text": "\n".join([p.text for p in doc.paragraphs])
        })
    elif mime_type == "text/plain":
        with open(file_path, "r", encoding="utf-8") as f:
            pages.append({
                "page_number": 1,
                "text": f.read()
            })
    elif mime_type == "text/html":
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            pages.append({
                "page_number": 1,
                "text": soup.get_text(separator='\n')
            })
    else:
        raise ValueError(f"Unsupported mime type: {mime_type}")
        
    return pages

def generate_chunks(pages: list[dict], chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]:
    chunks = []
    chunk_index = 0
    
    for page in pages:
        text = page["text"]
        page_num = page["page_number"]
        
        words = text.split()
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk_words = words[i:i + chunk_size]
            if not chunk_words:
                break
            
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "id": str(uuid4()),
                "text": chunk_text,
                "page_number": page_num,
                "chunk_index": chunk_index
            })
            chunk_index += 1
            
    return chunks
