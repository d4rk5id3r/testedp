from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from storage import extract_text, get_doc_path
from db import get_all_docs, query_docs, get_doc, delete_doc, add_doc

app = FastAPI()

@app.get("/")
async def read_root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.post("/api/docs")
async def upload_doc(file: UploadFile) -> Dict[str, str]:
    content = await file.read()
    doc = extract_text(file.filename, content)
    doc_uuid = doc.id
    get_doc_path(doc.filename).write_text(doc.content)
    add_doc(doc)
    return {"doc_id": doc_uuid, "message": "Document uploaded and indexed successfully"}

@app.get("/api/docs")
async def list_docs() -> Dict[str, Any]:
    documents = get_all_docs()
    return {"documents": documents, "count": len(documents)}

@app.delete("/api/docs/{doc_id}")
async def remove_doc(doc_id: str) -> Dict[str, str]:
    result = get_doc(doc_id)
    if not result or not result.get('ids') or len(result['ids']) == 0:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    metadata = result["metadatas"][0]
    filename = metadata["filename"]
    file_path = get_doc_path(filename)
    if file_path.exists():
        file_path.unlink()
    delete_doc(doc_id)
    return {"doc_id": doc_id, "message": "Document removed successfully"}

@app.get("/api/docs/{filename}")
async def get_doc_file(filename: str) -> Response:
    file_path = get_doc_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Document {filename} not found")
    content = file_path.read_bytes()
    return Response(content=content, media_type="text/plain")

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def query(req: QueryRequest) -> Dict[str, Any]:
    matches = query_docs(req.query)
    return {"matches": matches, "count": len(matches)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, workers=2)
