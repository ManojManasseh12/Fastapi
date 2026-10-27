from sentence_transformers import SentenceTransformer

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def models(data):
    model = _get_model()
    embeddings = model.encode(data)
    if hasattr(embeddings, "tolist"):
        return embeddings.tolist()
    return embeddings
