import pytest
from app.ingestion.processor import sanitize_filename, extract_text_from_file

def test_sanitize_filename():
    # TC UNIT 003
    assert sanitize_filename("../../secret.txt") == "secret.txt"
    assert sanitize_filename("a/b/c/test.pdf") == "test.pdf"

def test_extract_text_plain(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("The CNC milling machine uses a carbide cutting tool.")
    
    pages = extract_text_from_file(str(p), "text/plain")
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "CNC milling machine" in pages[0]["text"]
