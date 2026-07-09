import time

from src.config import Config
from src.pipeline.chunking_ui import choose_chunking_strategies
from src.preprocessing.chunking import (
    apply_multiple_chunking_strategies,
    chunk_document,
    extract_section,
    load_and_clean_document,
)
from src.preprocessing.file_utils import (
    build_source_metadata,
    get_source_signature,
    is_url,
    sha256_text,
)


def sanitize_metadata(metadata):
    cleaned = {}

    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            cleaned[key] = value
        elif value is None:
            cleaned[key] = ""
        else:
            cleaned[key] = str(value)

    return cleaned


def _print_box_title(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def _safe_collection_count(collection, file_hash):
    try:
        data = collection.get(where={"filehash": file_hash}, include=["metadatas"])
        return len(data.get("ids", []))
    except Exception:
        return 0


def _show_existing_source_details(collection_name, source_name, file_hash, db):
    collection = db.get_collection(collection_name)
    data = db.get_file_records(collection, file_hash)

    ids = data.get("ids", [])
    metadatas = data.get("metadatas", [])

    print("\n📌 Existing source detected")
    print("-" * 60)
    print(f"Collection : {collection_name}")
    print(f"Source     : {source_name}")
    print(f"Chunks     : {len(ids)}")

    if metadatas:
        sample = metadatas[0] or {}
        print(f"Type       : {sample.get('source_type', 'Unknown')}")
        print(f"Chunking   : {sample.get('chunking_combo', sample.get('chunking', 'Unknown'))}")
        print(f"Version    : {sample.get('version', 'Unknown')}")
    print("-" * 60)


def _handle_existing_source(collection, collection_name, source_name, file_hash, db):
    _print_box_title("🔁 SOURCE ALREADY EXISTS")

    _show_existing_source_details(
        collection_name=collection_name,
        source_name=source_name,
        file_hash=file_hash,
        db=db,
    )

    print("""
Choose what to do next:

1. Skip
   Keep existing data as-is and do not ingest this source again.

2. Re-embed
   Delete the old stored chunks for this same source from this collection,
   then ingest it again using your CURRENT models/settings/chunking choices.

3. Replace
   Same result as re-embed in the current system:
   remove old stored chunks for this source and insert fresh content again.

⚠️ Note:
In your current architecture, Re-embed and Replace behave almost the same.
They are both kept for clarity and backward compatibility.
""")

    while True:
        choice = input("Enter choice (1/2/3): ").strip()

        if choice == "1":
            print("\n⏭️ Skipped ingestion. Existing stored source was kept unchanged.")
            return collection, False

        if choice in {"2", "3"}:
            removed = db.delete_file_from_collection(collection, file_hash)

            print("\n🧹 Old source content removed")
            print(f"Collection : {collection_name}")
            print(f"Source     : {source_name}")
            print(f"Deleted    : {removed} chunk(s)")

            return collection, True

        print("❌ Invalid choice. Please enter 1, 2, or 3.")


def _choose_collection_for_new_source(source_name, collections, db):
    _print_box_title("🆕 NEW SOURCE DETECTED")

    print("Choose where to store this source:\n")
    print("1. Merge into existing collection")
    print("2. Create new collection")

    while True:
        choice = input("\nEnter choice (1/2): ").strip()

        if choice not in {"1", "2"}:
            print("❌ Invalid choice. Please enter 1 or 2.")
            continue

        if choice == "1":
            if not collections:
                print("\n⚠️ No existing collections found.")
                print("➡️ Switching to: Create new collection")
                choice = "2"
            else:
                print("\n📚 Existing Collections")
                print("-" * 60)

                for i, col in enumerate(collections, start=1):
                    try:
                        current_collection = db.get_collection(col.name)
                        files = db.list_files_in_collection(current_collection)
                        file_count = len(files)
                    except Exception:
                        file_count = "?"

                    print(f"{i}. {col.name}  |  files: {file_count}")

                print("-" * 60)

                while True:
                    selected = input("Select collection number: ").strip()

                    if not selected.isdigit():
                        print("❌ Please enter a valid number.")
                        continue

                    idx = int(selected) - 1

                    if idx < 0 or idx >= len(collections):
                        print("❌ Selection out of range.")
                        continue

                    collection_name = collections[idx].name
                    collection = db.get_collection(collection_name)

                    print("\n✅ Selected collection")
                    print(f"Collection : {collection_name}")
                    print(f"New Source : {source_name}")

                    return collection

        if choice == "2":
            while True:
                collection_name = input("Enter collection name: ").strip()

                if not collection_name:
                    collection_name = source_name

                if collection_name:
                    collection = db.get_collection(collection_name)
                    print("\n✅ Collection ready")
                    print(f"Collection : {collection_name}")
                    print(f"New Source : {source_name}")
                    return collection

                print("❌ Collection name cannot be empty.")


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
    # DUPLICATE CHECK ACROSS COLLECTIONS
    # ========================================================
    for col in collections:
        c = db.get_collection(col.name)

        if db.file_exists_in_collection(c, file_hash):
            collection, should_continue = _handle_existing_source(
                collection=c,
                collection_name=col.name,
                source_name=source_name,
                file_hash=file_hash,
                db=db,
            )

            if not should_continue:
                return collection, False

            break

    # ========================================================
    # COLLECTION SELECTION FOR NEW SOURCE
    # ========================================================
    if not collection:
        collection = _choose_collection_for_new_source(
            source_name=source_name,
            collections=collections,
            db=db,
        )

        if db.file_exists_in_collection(collection, file_hash):
            _print_box_title("ℹ️ SOURCE ALREADY EXISTS IN SELECTED COLLECTION")
            print(f"Collection : {getattr(collection, 'name', 'Unknown')}")
            print(f"Source     : {source_name}")
            print("\nNo new ingestion was performed because this source is already stored there.")
            return collection, False

    # ========================================================
    # CHUNKING
    # ========================================================
    strategies = choose_chunking_strategies()

    print(f"\n⚡ Processing using {len(strategies)} strategy(s)")

    if len(strategies) == 1:
        all_chunks = chunk_document(source, strategy=strategies[0])
    else:
        docs = load_and_clean_document(source)
        all_chunks = apply_multiple_chunking_strategies(docs, strategies)

    print(f"\n✅ Final chunk count to store: {len(all_chunks)}")

    # ========================================================
    # METADATA
    # ========================================================
    docs = []
    metas = []
    ids = []

    version = int(time.time())
    strategy_combo = ",".join(strategies)

    for i, chunk in enumerate(all_chunks):
        docs.append(chunk.page_content)

        page_value = chunk.metadata.get("page")

        if not isinstance(page_value, (str, int, float, bool)):
            page_value = 0

        metadata = {
            "source_name": str(source_metadata.get("source_name", "")),
            "source_type": str(source_metadata.get("source_type", "")),
            "source": str(source_metadata.get("source", "")),
            "filehash": str(source_metadata.get("file_hash", "")),
            "page": page_value,
            "section": str(extract_section(chunk.page_content)),
            "chunking": str(chunk.metadata.get("chunking", "")),
            "chunking_combo": strategy_combo,
            "version": int(version),
            "ingested_at": int(time.time()),
        }

        metadata = sanitize_metadata(metadata)
        metas.append(metadata)

        ids.append(
            f"{source_name}_{file_hash}_{metadata['chunking']}_{i}"
        )

    # ========================================================
    # STORE
    # ========================================================
    db.insert_batches(collection, docs, metas, ids, Config.BATCH_SIZE)

    print("\n✅ Content stored successfully")
    print(f"📄 Source       : {source_metadata['source_name']}")
    print(f"📦 Type         : {source_metadata['source_type']}")
    print(f"🗂️ Collection   : {getattr(collection, 'name', 'Unknown')}")
    print(f"🧩 Strategies   : {strategy_combo}")
    print(f"🧩 Chunks       : {len(all_chunks)}")

    return collection, True


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================
def process_pdf(pdf_path, db):
    return process_document(pdf_path, db)