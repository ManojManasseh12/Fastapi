<<<<<<< HEAD
from functools import lru_cache
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.ai.rag.data_loader import extract_text_from_file, chunk_text
from app.ai.rag.embed import models
from app.ai.rag.pipeline import store_chunks, query_chunks, get_or_create_collection, get_client

router = APIRouter()


# ── Request schema for /query ────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    n_results: int = 5


@lru_cache(maxsize=1)
def get_image_text():
    import easyocr
    return easyocr.Reader(["en"], gpu=False)


# ── Upload file → extract → chunk → embed → store in ChromaDB ───────────
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_bytes = await file.read()
    filename = file.filename or ""

    try:
        text = extract_text_from_file(file_bytes, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

    chunks = chunk_text(text, chunk_size=200, overlap=50)
    if not chunks:
        return {
            "message": f"File '{filename}' uploaded but no text content found to embed.",
            "Total": 0,
            "Chunks": [],
            "Embeddings": [],
            "ChromaDB": {"stored": 0},
        }

    embeddings = models(chunks)
    if hasattr(embeddings, "tolist"):
        embeddings = embeddings.tolist()

    # ⭐ Store in ChromaDB
    chroma_result = store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        filename=filename,
    )

    return {
        "message": f"File '{filename}' uploaded, embedded and stored in ChromaDB successfully.",
        "Total": len(chunks),
        "Chunks": chunks,
        "Embeddings": embeddings,
        "ChromaDB": chroma_result,
    }


# ── Query ChromaDB for similar chunks ───────────────────────────────────
@router.post("/query")
async def query(req: QueryRequest):
    # Embed the question using the same model
    query_embedding = models(req.question)

    results = query_chunks(
        query_embedding=query_embedding,
        n_results=req.n_results,
    )

    return {
        "question": req.question,
        "results": results,
    }


# ── Inspect ChromaDB – verify stored data ────────────────────────────────
def _fetch_collections_sync():
    """Synchronous helper — runs ChromaDB reads off the async event loop."""
    client = get_client()
    collections = client.list_collections()

    info = []
    for col in collections:
        count = col.count()

        # Get stored data (skip embeddings to keep response small)
        all_data = col.get(include=["documents", "metadatas"]) if count > 0 else {}

        documents_detail = []
        if all_data:
            ids = all_data.get("ids", [])
            docs = all_data.get("documents", [])
            metas = all_data.get("metadatas", [])

            for i in range(len(ids)):
                documents_detail.append({
                    "id": ids[i],
                    "document": docs[i] if docs else None,
                    "metadata": metas[i] if metas else None,
                })

        info.append({
            "collection_name": col.name,
            "total_documents": count,
            "documents": documents_detail,
        })

    return {"collections": info}


@router.get("/collections")
async def list_collections():
    """Check what's stored in ChromaDB — full details with IDs."""
    return await run_in_threadpool(_fetch_collections_sync)


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_text = await run_in_threadpool(get_image_text)
    text = await run_in_threadpool(image_text.readtext, image_bytes, detail=0)
    return {"text": " ".join(text), "lines": text}
=======
from fastapi import APIRouter,UploadFile

router = APIRouter()

@router.post("/upload")
# def upload_file(file:UploadFile):
#     return file.filename

async def upload_file(file:UploadFile):
    load_text = await file.read()

    content=[]

    for text in load_text.splitlines():
        content.append(text)

    return content
>>>>>>> 4a480110f464f2dfc4ad365bab9edf9efc27ff4e
