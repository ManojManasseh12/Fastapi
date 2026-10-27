import os

_model = None
_backend = None

def _get_model():
    global _model, _backend
    if _model is not None:
        return _model, _backend

    # Prioritize fastembed (pure ONNX, bypasses Windows Smart App Control / torch block)
    try:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        _backend = "fastembed"
        return _model, _backend
    except Exception:
        pass

    # Fallback to sentence_transformers
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _backend = "sentence_transformers"
        return _model, _backend
    except Exception as e:
        raise RuntimeError(f"Could not initialize embedding model: {e}")

def models(data):
    if not data:
        return []

    model, backend = _get_model()

    is_single = isinstance(data, str)
    texts = [data] if is_single else list(data)

    if backend == "fastembed":
        embeddings = [e.tolist() if hasattr(e, "tolist") else list(e) for e in model.embed(texts)]
    else:
        raw = model.encode(texts)
        if hasattr(raw, "tolist"):
            embeddings = raw.tolist()
        else:
            embeddings = [list(e) for e in raw]

    return embeddings[0] if is_single else embeddings

