import time

from src.preprocessing.chunking import chunk_document, extract_section

from src.config import Config

from src.preprocessing.file_utils import (
    get_source_signature,
    build_source_metadata,
    sha256_text,
    is_url,
)

from src.pipeline.chunking_ui import choose_chunking_strategies


def sanitize_metadata(metadata):

    cleaned = {}

    for key, value in metadata.items():

        # Chroma-supported types
        if isinstance(value, (str, int, float, bool)):
            cleaned[key] = value

        # Convert None
        elif value is None:
            cleaned[key] = ""

        # Convert everything else safely
        else:
            cleaned[key] = str(value)

    return cleaned


# ============================================================
# MAIN INGESTION PIPELINE
# ============================================================
def process_document(source, db):

    content_hash = None

    if is_url(source):

        from src.loaders.document_loader import load_document

        docs = load_document(source)

        full_text = "\n".join(doc.page_content for doc in docs)

        content_hash = sha256_text(full_text)

    source_name, _, file_hash = get_source_signature(source, content_hash)

    source_metadata = build_source_metadata(source, content_hash)

    collections = db.list_collections()

    collection = None

    # ========================================================
    # DUPLICATE CHECK
    # ========================================================
    for col in collections:

        c = db.get_collection(col.name)

        if db.file_exists_in_collection(c, file_hash):

            print(f"\n✅ Source already exists " f"in collection: {col.name}")

            while True:

                choice = input("""
1. Skip
2. Re-embed
3. Replace

Choice:
""").strip()

                if choice == "1":
                    return c, False

                elif choice == "2":
                    collection = c
                    break

                elif choice == "3":

                    print("🧹 Removing old content...")

                    c.delete(where={"file_hash": file_hash})

                    collection = c
                    break

                else:
                    print("❌ Invalid choice")

            break

    # ========================================================
    # COLLECTION SELECTION
    # ========================================================
    if not collection:

        print("\n🆕 New source detected")

        print("""
Choose storage option:

1. Merge into existing collection
2. Create new collection
""")

        while True:

            choice = input("Enter choice: ").strip()

            if choice not in ["1", "2"]:

                print("❌ Invalid choice")

                continue

            break

        # ----------------------------------------------------
        # MERGE
        # ----------------------------------------------------
        if choice == "1":

            if not collections:

                print("❌ No collections exist")

                choice = "2"

            else:

                print("\n📚 Existing Collections:")

                for i, col in enumerate(collections, start=1):
                    print(f"{i}. {col.name}")

                while True:

                    selected = input("\nSelect collection: ").strip()

                    if not selected.isdigit():

                        print("❌ Enter a number")

                        continue

                    idx = int(selected) - 1

                    if idx < 0 or idx >= len(collections):

                        print("❌ Out of range")

                        continue

                    collection_name = collections[idx].name

                    break

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------
        if choice == "2":

            collection_name = input("Enter collection name: ").strip()

            if not collection_name:

                collection_name = source_name

        collection = db.get_collection(collection_name)

        # additional safety
        if db.file_exists_in_collection(collection, file_hash):

            print("✅ Source already exists " "inside selected collection")

            return (collection, False)

    # ========================================================
    # CHUNKING
    # ========================================================
    strategies = choose_chunking_strategies()

    print("\n⚡ Processing using " f"{len(strategies)} strategy(s)")

    all_chunks = []

    for strategy in strategies:

        print(f"\n⚙️ Applying " f"{strategy}")

        chunks = chunk_document(source, strategy=strategy)

        for chunk in chunks:

            chunk.metadata["chunking"] = strategy

        all_chunks.extend(chunks)

    print(f"\n✅ Total chunks: " f"{len(all_chunks)}")

    # ========================================================
    # METADATA
    # ========================================================
    docs = []
    metas = []
    ids = []

    version = int(time.time())

    for i, chunk in enumerate(all_chunks):

        docs.append(chunk.page_content)

        page_value = chunk.metadata.get("page")

        if not isinstance(page_value, (str, int, float, bool)):
            page_value = 0

        metadata = {
            "source_name": str(source_metadata.get("source_name", "")),
            "source_type": str(source_metadata.get("source_type", "")),
            "source": str(source_metadata.get("source", "")),
            "file_hash": str(source_metadata.get("file_hash", "")),
            "page": page_value,
            "section": str(extract_section(chunk.page_content)),
            "chunking": str(chunk.metadata.get("chunking", "")),
            "version": int(version),
            "ingested_at": int(time.time()),
        }

        metadata = sanitize_metadata(metadata)

        # #   Tempory Debugging
        #     if i == 0:
        #         print("\n🔍 Metadata Debug:")
        #         for k, v in metadata.items():
        #             print(
        #                 f"{k} -> {type(v)} -> {repr(v)}"
        #             )

        metas.append(metadata)

        ids.append(f"{source_name}_" f"{file_hash}_" f"{i}")

    # ========================================================
    # STORE
    # ========================================================
    db.insert_batches(collection, docs, metas, ids, Config.BATCH_SIZE)

    print("\n✅ Content stored successfully")

    print(f"📄 Source       : " f"{source_metadata['source_name']}")

    print(f"📦 Type         : " f"{source_metadata['source_type']}")

    print(f"🧩 Chunks       : " f"{len(all_chunks)}")

    return (collection, True)


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================
def process_pdf(pdf_path, db):
    return process_document(pdf_path, db)
