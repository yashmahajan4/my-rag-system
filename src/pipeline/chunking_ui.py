from src.config import Config


def choose_chunking_strategies():
    strategy_info = {
        "1": {
            "key": "recursive",
            "label": "Recursive",
            "badge": "✅ Recommended",
            "desc": "Best default. Safest for most PDFs, DOCX, and websites.",
        },
        "2": {
            "key": "character",
            "label": "Character",
            "badge": "⚠️ Simple split",
            "desc": "Fast, but may produce uneven chunks depending on separators.",
        },
        "3": {
            "key": "structural",
            "label": "Structural",
            "badge": "📚 Section-aware",
            "desc": "Splits by document structure like paragraphs/sections.",
        },
        "4": {
            "key": "semantic",
            "label": "Semantic",
            "badge": "🔥 Expensive",
            "desc": "Uses embeddings while chunking; slower but meaning-aware.",
        },
        "5": {
            "key": "fixed",
            "label": "Fixed",
            "badge": "📏 Exact window",
            "desc": "Cuts text into fixed-size pieces.",
        },
        "6": {
            "key": "overlap",
            "label": "Overlap",
            "badge": "🔁 Context-preserving",
            "desc": "Fixed-size chunks with overlap between neighbors.",
        },
    }

    print("\n" + "=" * 50)
    print("🧩 CHUNKING STRATEGY SELECTION")
    print("=" * 50)
    print(f"Provider        : {Config.PROVIDER}")
    print(f"Embedding Model : {Config.get_embedding_model()}")
    print(f"Chunk Size      : {Config.CHUNK_SIZE}")
    print(f"Chunk Overlap   : {Config.CHUNK_OVERLAP}")
    print("=" * 50)

    print("\nChoose one or more chunking strategies.")
    print("Enter comma-separated numbers, for example: 1,3,6\n")

    for option, info in strategy_info.items():
        print(f"{option}. {info['label']:<10} {info['badge']}")
        print(f"   → {info['desc']}")

    print("\nQuick guidance:")
    print("- Use 1 (Recursive) for the most reliable ingestion.")
    print("- Use 3 (Structural) when the document has clear sections/headings.")
    print("- Use 4 (Semantic) only if you want meaning-aware chunking and can afford slower processing.")
    print("- Use 2, 5, or 6 carefully for messy PDFs because chunk boundaries can be rough.")

    choice = input("\nEnter choices: ").strip()
    raw_choices = [item.strip() for item in choice.split(",") if item.strip()]

    strategies = []
    seen = set()

    for item in raw_choices:
        info = strategy_info.get(item)

        if not info:
            print(f"⚠️ Ignoring invalid option: {item}")
            continue

        strategy = info["key"]

        if strategy in seen:
            print(f"⚠️ Duplicate strategy ignored: {strategy}")
            continue

        seen.add(strategy)
        strategies.append(strategy)

    if not strategies:
        print("\n⚠️ No valid strategy selected.")
        print("✅ Defaulting to: recursive")
        strategies = ["recursive"]

    print("\n" + "-" * 50)
    print("✅ SELECTED STRATEGIES")
    print("-" * 50)

    for index, strategy in enumerate(strategies, start=1):
        for info in strategy_info.values():
            if info["key"] == strategy:
                print(f"{index}. {info['label']} ({strategy})")
                print(f"   → {info['desc']}")
                break

    if "recursive" in strategies:
        print("\n💡 Reliability note: Recursive is the safest baseline for most documents.")

    if any(strategy in {"character", "structural", "fixed", "overlap"} for strategy in strategies):
        print("💡 Safety note: Non-recursive strategies may create rough boundaries on messy extracted text.")

    if "semantic" in strategies:
        print("💡 Performance note: Semantic chunking is slower because it uses embeddings during chunking.")

    print("-" * 50)

    return strategies