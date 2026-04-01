from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata
import uuid

DOCS_DIR = Path(__file__).parent.parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)

@dataclass
class Doc:
    id: str
    filename: str
    content: str

def extract_text(filename: str, content: bytes) -> Doc:
    text = content.decode("utf-8", errors="ignore")
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\x20-\x7E\t\n\r]+", " ", text)
    sanitized = unicodedata.normalize("NFKC", filename)
    return Doc(id=str(uuid.uuid4()), filename=sanitized, content=text)

def get_doc_path(filename: str) -> Path:
    sanitized = unicodedata.normalize("NFKC", filename)
    return DOCS_DIR / sanitized
