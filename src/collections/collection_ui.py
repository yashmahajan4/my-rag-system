def view_collections_with_files(db):

    collections = db.list_collections()

    if not collections:
        print("❌ No collections found")
        return

    print("\n📚 Collections:")

    for i, col in enumerate(collections, start=1):
        print(f"{i}. {col.name}")

    while True:

        user_input = input("\nSelect collection (number): ").strip()

        if not user_input.isdigit():
            print("❌ Please enter a valid number")
            continue

        choice = int(user_input) - 1

        if choice < 0 or choice >= len(collections):
            print("❌ Selection out of range")
            continue

        break

    collection = db.get_collection(collections[choice].name)

    files = db.list_files_in_collection(collection)

    if not files:
        print("\n⚠️ No files found " "in this collection")
        return

    print("\n📄 Files inside collection:")

    for f in files:
        print(f" - {f}")
