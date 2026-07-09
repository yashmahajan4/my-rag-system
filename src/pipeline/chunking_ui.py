def choose_chunking_strategies():

    print("""
🧩 Choose Chunking Strategies (comma separated):

1. Recursive ✅
2. Character
3. Structural
4. Semantic 🔥
5. Fixed
6. Overlap
""")

    mapping = {
        "1": "recursive",
        "2": "character",
        "3": "structural",
        "4": "semantic",
        "5": "fixed",
        "6": "overlap"
    }

    choice = input("Enter choices: ").strip()

    strategies = [
        mapping.get(c.strip())
        for c in choice.split(",")
        if mapping.get(c.strip())
    ]

    if not strategies:
        print("⚠️ Defaulting to recursive")
        strategies = ["recursive"]

    print(f"\n✅ Selected strategies: {strategies}")

    return strategies
