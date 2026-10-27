import os
import uuid
import hashlib
import chromadb

# ---------------------------------------------------------------------------
# ChromaDB persistent client  –  data is saved under  ./chroma_db/
# ---------------------------------------------------------------------------

_CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "chroma_db")
_client = None


def get_client() -> chromadb.ClientAPI:
    """Return (and lazily create) a persistent ChromaDB client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=os.path.abspath(_CHROMA_DIR))
    return _client


def get_or_create_collection(name: str = "documents") -> chromadb.Collection:
    """Get or create a ChromaDB collection."""
    return get_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},   # cosine similarity
    )


def _make_chunk_id(filename: str, chunk_index: int) -> str:
    """
    Deterministic ID based on filename + chunk_index.
    Re-uploading the same file OVERWRITES old chunks instead of duplicating.
    """
    raw = f"{filename}::chunk::{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str = "unknown",
    collection_name: str = "documents",
) -> dict:
    """
    Upsert text chunks and their embeddings into ChromaDB.

    Each chunk gets:
      • a deterministic id  (based on filename + chunk_index → no duplicates)
      • the embedding vector
      • the raw text         (stored as the 'document')
      • metadata             (file_id, source filename, chunk index)
    """
    collection = get_or_create_collection(collection_name)

    # One file_id per upload batch
    file_id = str(uuid.uuid4())

    # Deterministic IDs: same file → same IDs → upsert overwrites
    ids = [_make_chunk_id(filename, i) for i in range(len(chunks))]

    metadatas = [
        {
            "file_id": file_id,
            "source": filename,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return {
        "stored": len(chunks),
        "collection_name": collection_name,
        "collection_id": collection.id,
        "file_id": file_id,
        "chunk_ids": ids,
    }


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def query_chunks(
    query_embedding: list[float],
    n_results: int = 5,
    collection_name: str = "documents",
) -> dict:
    """
    Find the most similar chunks for a given query embedding.

    Returns documents, distances, and metadata.
    """
    collection = get_or_create_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    return {
        "collection_name": collection_name,
        "collection_id": collection.id,
        "documents": results["documents"][0] if results["documents"] else [],
        "metadatas": results["metadatas"][0] if results["metadatas"] else [],
        "distances": results["distances"][0] if results["distances"] else [],
    }

