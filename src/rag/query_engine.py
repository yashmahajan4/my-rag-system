from src.config import Config
from src.rag.generator import generate_answer
from src.retrieval.retrieval import retrieve_context


def ask_question(collection, query, db, where=None):
    results = retrieve_context(
        collection=collection,
        query=query,
        db=db,
        k=Config.FINAL_TOP_K,
        where=where,
    )

    if not results:
        print("❌ No results found")
        return

    docs = [item.get("document", "") for item in results if item.get("document")]
    metas = [item.get("metadata", {}) for item in results]

    if not docs:
        print("❌ No matching content found")
        return

    context_parts = []
    current_size = 0

    for doc in docs:
        if current_size + len(doc) > Config.MAX_CONTEXT_CHARS:
            break

        context_parts.append(doc)
        current_size += len(doc)

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a RAG assistant.

Use ONLY the provided context.

If the answer is not found in the context,
say:

I could not find that information in the provided document.

Context:

{context}

Question:

{query}

Answer:
"""

    answer = generate_answer(prompt)

    print("\n" + "=" * 60)
    print("💡 ANSWER")
    print("=" * 60)
    print(answer)

    print("\n" + "=" * 60)
    print("📚 CITATIONS")
    print("=" * 60)

    seen = set()

    for meta in metas:
        source = meta.get("source_name", "Unknown")
        page = meta.get("page", "N/A")
        key = (source, page)

        if key in seen:
            continue

        seen.add(key)
        print(f"• {source} (page {page})")