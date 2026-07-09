def retrieve_context(
    collection,
    query,
    k=5,
):

    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    return results