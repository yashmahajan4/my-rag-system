from src.config import Config
from src.retrieval.retrieval import retrieve_context


def query_collection(collection, db):
    query = input("\n🔎 Enter query: ").strip()

    print(
        """
🔍 Filter options:

1. Global
2. Source Name
3. Chunking Strategy
4. Source Type
"""
    )

    choice = input("Choice: ").strip()

    where = None

    if choice == "2":
        where = {"source_name": input("Source name: ").strip()}

    elif choice == "3":
        where = {"chunking": input("Strategy: ").strip()}

    elif choice == "4":
        where = {"source_type": input("Type (pdf/docx/web): ").strip().lower()}

    results = retrieve_context(
        collection=collection,
        query=query,
        db=db,
        k=Config.FINAL_TOP_K,
        where=where,
    )

    if not results:
        print("❌ No matching content found")
        return

    print("\n🌍 SEARCH RESULTS:")

    for item in results:
        meta = item.get("metadata", {})
        retrievers = item.get("retrievers", [])
        match_type = " + ".join(retrievers) if retrievers else "unknown"

        print("\n" + "-" * 60)
        print(f"📄 Source   : {meta.get('source_name', 'Unknown')}")
        print(f"📦 Type     : {meta.get('source_type', 'Unknown')}")
        print(f"📑 Page     : {meta.get('page', 'N/A')}")
        print(f"📚 Section  : {meta.get('section', 'Unknown')}")
        print(f"🧩 Chunking : {meta.get('chunking', 'Unknown')}")
        print(f"🔀 Match    : {match_type}")
        print(f"🏆 Rank     : {item.get('rank', 'N/A')}")

        if "rrf_score" in item:
            print(f"🧠 RRF Score: {item['rrf_score']:.6f}")

        if "rerank_score" in item:
            print(f"🎯 Rerank   : {item['rerank_score']:.6f}")

        print("\n📖 Content:\n")
        print(item.get("document", "")[:500])