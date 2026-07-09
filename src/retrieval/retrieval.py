from src.config import Config
from src.retrieval.context import normalize_dense_results, reciprocal_rank_fusion
from src.retrieval.reranker import rerank_results
from src.retrieval.search import bm25_search


# ============================================================
# DENSE SEARCH
# ============================================================
def dense_search(collection, query, db, k=None, where=None):
    dense_results = db.query(
        collection=collection,
        query_text=query,
        n_results=k or Config.DENSE_TOP_K,
        where=where,
    )

    return normalize_dense_results(
        results=dense_results,
        where=where,
    )


# ============================================================
# RETRIEVE CONTEXT
# ============================================================
def retrieve_context(collection, query, db, k=None, where=None):
    final_k = k or Config.FINAL_TOP_K

    dense_results = dense_search(
        collection=collection,
        query=query,
        db=db,
        k=Config.DENSE_TOP_K,
        where=where,
    )

    if not Config.USE_HYBRID:
        base_results = dense_results
    else:
        sparse_results = bm25_search(
            collection=collection,
            query=query,
            k=Config.BM25_TOP_K,
            where=where,
        )

        if not dense_results and not sparse_results:
            return []

        if dense_results and not sparse_results:
            base_results = dense_results

        elif sparse_results and not dense_results:
            base_results = sparse_results

        else:
            base_results = reciprocal_rank_fusion(
                rank_lists=[dense_results, sparse_results],
                k=Config.RRF_K,
            )

    if not base_results:
        return []

    if Config.USE_RERANKER:
        rerank_pool = base_results[: Config.RERANK_TOP_N]
        reranked_pool = rerank_results(
            query=query,
            candidates=rerank_pool,
            top_n=Config.RERANK_TOP_N,
        )
        remaining = base_results[Config.RERANK_TOP_N :]
        final_results = reranked_pool + remaining
    else:
        final_results = base_results

    for rank, item in enumerate(final_results, start=1):
        item["rank"] = rank

    return final_results[:final_k]