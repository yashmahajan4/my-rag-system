from functools import lru_cache

from src.config import Config


@lru_cache(maxsize=1)
def get_cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(
        Config.CROSS_ENCODER_MODEL,
        max_length=Config.CROSS_ENCODER_MAX_LENGTH,
    )


def rerank_with_cross_encoder(query, candidates, top_n=None):
    if not candidates:
        return []

    limit = top_n or Config.RERANK_TOP_N
    working_set = candidates[:limit]

    model = get_cross_encoder()

    pairs = [
        (query, item.get("document", ""))
        for item in working_set
    ]

    scores = model.predict(pairs)

    reranked = []

    for item, score in zip(working_set, scores):
        updated = dict(item)
        updated["rerank_score"] = float(score)

        retrievers = set(updated.get("retrievers", []))
        retrievers.add("reranker")
        updated["retrievers"] = sorted(retrievers)

        reranked.append(updated)

    reranked.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    for rank, item in enumerate(reranked, start=1):
        item["rank"] = rank

    return reranked


def rerank_results(query, candidates, top_n=None):
    if not candidates:
        return []

    if not Config.USE_RERANKER:
        return candidates

    if Config.RERANKER_TYPE != "cross_encoder":
        return candidates

    try:
        return rerank_with_cross_encoder(
            query=query,
            candidates=candidates,
            top_n=top_n,
        )
    except Exception as error:
        print(f"⚠️ Reranker failed, falling back to retrieval order: {error}")
        return candidates