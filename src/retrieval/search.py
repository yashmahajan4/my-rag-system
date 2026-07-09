import re

from rank_bm25 import BM25Okapi

from src.config import Config
from src.retrieval.context import matches_where


# ============================================================
# TOKENIZE
# ============================================================
def tokenize(text: str):
    if not text:
        return []

    return re.findall(r"\b\w+\b", text.lower())


# ============================================================
# FILTERED COLLECTION DATA
# ============================================================
def get_filtered_collection_data(collection, where=None):
    data = collection.get(include=["documents", "metadatas"])

    ids = data.get("ids", [])
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    filtered_ids = []
    filtered_docs = []
    filtered_metas = []

    for doc_id, document, metadata in zip(ids, documents, metadatas):
        if matches_where(metadata, where):
            filtered_ids.append(doc_id)
            filtered_docs.append(document or "")
            filtered_metas.append(metadata or {})

    return {
        "ids": filtered_ids,
        "documents": filtered_docs,
        "metadatas": filtered_metas,
    }


# ============================================================
# BM25 SEARCH
# ============================================================
def bm25_search(collection, query, k=None, where=None):
    top_k = k or Config.BM25_TOP_K

    corpus = get_filtered_collection_data(
        collection=collection,
        where=where,
    )

    ids = corpus.get("ids", [])
    documents = corpus.get("documents", [])
    metadatas = corpus.get("metadatas", [])

    if not documents:
        return []

    tokenized_corpus = [tokenize(doc) for doc in documents]

    if not any(tokenized_corpus):
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(query_tokens)

    ranked = sorted(
        zip(ids, documents, metadatas, scores),
        key=lambda item: item[3],
        reverse=True,
    )

    results = []

    for doc_id, document, metadata, score in ranked:
        if score < Config.BM25_MIN_SCORE:
            continue

        results.append(
            {
                "id": doc_id,
                "document": document,
                "metadata": metadata or {},
                "score": float(score),
                "rank": len(results) + 1,
                "retrievers": ["bm25"],
            }
        )

        if len(results) >= top_k:
            break

    return results