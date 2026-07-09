# ============================================================
# METADATA FILTERING
# ============================================================
def matches_where(metadata, where=None):
    if not where:
        return True

    metadata = metadata or {}

    for key, expected_value in where.items():
        actual_value = metadata.get(key)

        if actual_value is None:
            return False

        if str(actual_value).strip().lower() != str(expected_value).strip().lower():
            return False

    return True


# ============================================================
# NORMALIZE DENSE RESULTS
# ============================================================
def normalize_dense_results(results, where=None):
    if not results:
        return []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if results.get("distances") else []

    normalized = []

    for index, (doc_id, document, metadata) in enumerate(
        zip(ids, documents, metadatas),
        start=1,
    ):
        metadata = metadata or {}

        if not matches_where(metadata, where):
            continue

        distance = None
        if distances and (index - 1) < len(distances):
            distance = distances[index - 1]

        normalized.append(
            {
                "id": doc_id,
                "document": document,
                "metadata": metadata,
                "score": distance,
                "rank": len(normalized) + 1,
                "retrievers": ["dense"],
            }
        )

    return normalized


# ============================================================
# RANK FUSION
# ============================================================
def reciprocal_rank_fusion(rank_lists, k=60):
    fused = {}

    for rank_list in rank_lists:
        for item in rank_list:
            doc_id = item["id"]

            if doc_id not in fused:
                fused[doc_id] = {
                    "id": item["id"],
                    "document": item["document"],
                    "metadata": item["metadata"],
                    "rrf_score": 0.0,
                    "retrievers": set(),
                }

            fused[doc_id]["rrf_score"] += 1.0 / (k + item["rank"])
            fused[doc_id]["retrievers"].update(item.get("retrievers", []))

    final_results = sorted(
        fused.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    for rank, item in enumerate(final_results, start=1):
        item["rank"] = rank
        item["retrievers"] = sorted(item["retrievers"])

    return final_results