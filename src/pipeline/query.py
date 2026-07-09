def query_collection(collection, db):

    query = input("\n🔎 Enter query: ").strip()

    print("""
🔍 Filter options:

1. Global
2. Source Name
3. Chunking Strategy
4. Source Type
""")

    choice = input("Choice: ").strip()

    where = None

    # =====================================================
    # SOURCE NAME
    # =====================================================
    if choice == "2":

        where = {"source_name": input("Source name: ").strip()}

    # =====================================================
    # CHUNKING
    # =====================================================
    elif choice == "3":

        where = {"chunking": input("Strategy: ").strip()}

    # =====================================================
    # TYPE
    # =====================================================
    elif choice == "4":

        where = {"source_type": input("Type (pdf/docx/web): ").strip().lower()}

    results = db.query(collection, query, where=where)

    db.print_results(results)
