from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def encode(text: str) -> np.ndarray:
    model = get_model()
    return model.encode([text])[0]


def compute_similarity(text_a: str, text_b: str) -> float:
    vec_a = encode(text_a).reshape(1, -1)
    vec_b = encode(text_b).reshape(1, -1)
    score = cosine_similarity(vec_a, vec_b)[0][0]
    return float(score)


def rank_resumes(resumes: list[dict], jd_text: str) -> list[dict]:
    """
    resumes: list of {"name": str, "text": str, "skills": dict}
    Returns sorted list with similarity scores added.
    """
    jd_vec = encode(jd_text).reshape(1, -1)
    results = []
    for r in resumes:
        r_vec = encode(r["text"]).reshape(1, -1)
        sim = float(cosine_similarity(r_vec, jd_vec)[0][0])
        results.append({**r, "similarity": round(sim * 100, 2)})
    return sorted(results, key=lambda x: x["similarity"], reverse=True)
