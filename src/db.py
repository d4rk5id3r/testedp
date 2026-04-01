from pathlib import Path
import chromadb
from chromadb.config import Settings
from storage import Doc

client = chromadb.Client(
    Settings(
        chroma_api_impl="chromadb.api.segment.SegmentAPI",
        chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
        chroma_producer_impl="chromadb.db.impl.sqlite.SqliteDB",
        chroma_consumer_impl="chromadb.db.impl.sqlite.SqliteDB",
        chroma_segment_manager_impl="chromadb.segment.impl.manager.local.LocalSegmentManager",
        is_persistent=True,
        persist_directory=(Path(__file__).parent.parent / "chroma-data").as_posix(),
    )
)

docs = client.get_or_create_collection('documents')

def get_all_docs():
    result = docs.get()
    documents = []
    if result and result.get("ids"):
        for i, doc_id in enumerate(result["ids"]):
            metadata = result["metadatas"][i] if result.get("metadatas") else {}
            documents.append({
                "doc_id": doc_id,
                "filename": metadata["filename"],
            })
    return documents

def get_doc(doc_id: str):
    return docs.get(ids=[doc_id])

def add_doc(doc: Doc):
    docs.add(
        documents=[doc.content],
        metadatas=[{"uuid": doc.id, "filename": doc.filename}],
        ids=[doc.id],
    )

def delete_doc(doc_id: str):
    docs.delete(ids=[doc_id])

def query_docs(query: str):
    results = docs.query(query_texts=[query], n_results=10)
    matches = []
    if results and results.get('ids'):
        for i, doc_id in enumerate(results['ids'][0]):
            match = {
                "doc_id": doc_id,
                "distance": results['distances'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
            }
            matches.append(match)
    return matches
