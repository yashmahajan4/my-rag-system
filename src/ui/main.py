import gc
import os
import subprocess
import sys
import time

from src.collections.collection_ui import view_collections_with_files
from src.config import Config
from src.db import ChromaManager
from src.ingestion.ingest import process_document
from src.pipeline.query import query_collection


# ============================================================
# HELPERS
# ============================================================
def print_divider(char="=", width=60):
    print(char * width)


def print_section(title, icon=None):
    print()
    print_divider("=")
    if icon:
        print(f"{icon} {title}")
    else:
        print(title)
    print_divider("=")


def print_key_value(label, value, width=18):
    print(f"{label:<{width}}: {value}")


def pause(seconds=1.0):
    time.sleep(seconds)


def get_resources_folder():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
        )
    )


def get_supported_resource_files(resources_dir):
    if not os.path.exists(resources_dir):
        return []

    return sorted(
        [
            filename
            for filename in os.listdir(resources_dir)
            if filename.lower().endswith((".pdf", ".docx"))
        ]
    )


def format_file_type(filename):
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "PDF"
    if lower.endswith(".docx"):
        return "DOCX"
    return "Unknown"


def choose_number(max_value, prompt="Enter choice: "):
    choice = input(prompt).strip()

    if not choice.isdigit():
        print("❌ Please enter a valid number.")
        return None

    index = int(choice)

    if index < 1 or index > max_value:
        print("❌ Selection out of range.")
        return None

    return index


def choose_collection(db, heading="📚 Select collection"):
    cols = db.list_collections()

    if not cols:
        print("❌ No collections available")
        return None

    print_section(heading)

    for i, col in enumerate(cols, start=1):
        try:
            collection = db.get_collection(col.name)
            files = db.list_files_in_collection(collection)
            file_count = len(files)
        except Exception:
            file_count = "?"

        print(f"{i}. {col.name}  |  files: {file_count}")

    print(f"{len(cols) + 1}. Back")

    while True:
        choice = choose_number(len(cols) + 1, "\nChoice: ")

        if choice is None:
            continue

        if choice == len(cols) + 1:
            return None

        selected = cols[choice - 1]
        return db.get_collection(selected.name)


def print_provider_status():
    try:
        summary = Config.get_active_provider_summary()

        print_section("ACTIVE MODEL CONFIG", "⚙️")
        print_key_value("Provider", summary["provider"])
        print_key_value("Embedding Model", summary["embedding_model"])
        print_key_value("Chat Model", summary["chat_model"])
        print_key_value("Base URL", summary["base_url"])
        print_key_value("Hybrid Search", "ON" if Config.USE_HYBRID else "OFF")
        print_key_value("Reranker", "ON" if Config.USE_RERANKER else "OFF")
        print_key_value("Reranker Type", Config.RERANKER_TYPE)
        print_key_value("Rerank Top-N", Config.RERANK_TOP_N)
        print_key_value("Chunk Size", Config.CHUNK_SIZE)
        print_key_value("Chunk Overlap", Config.CHUNK_OVERLAP)
        print_divider("=")

    except Exception as error:
        print(f"⚠️ Failed to load provider summary: {error}")


# ============================================================
# MENU
# ============================================================
def show_menu():
    print_section("SEMANTIC SEARCH SYSTEM", "📦")
    print("1. Ingest content")
    print("2. View collections & files")
    print("3. Storage & cleanup")
    print("4. Query existing collection")
    print("5. Query collection with AI")
    print("6. Show active model config")
    print("7. Exit")


# ============================================================
# INGEST
# ============================================================
def handle_ingest(db):
    resources_dir = get_resources_folder()
    supported_files = get_supported_resource_files(resources_dir)

    print_section("INGESTION SETTINGS", "📥")
    print_key_value("Provider", Config.PROVIDER)
    print_key_value("Embedding model", Config.get_embedding_model())
    print_key_value("Chunk size", Config.CHUNK_SIZE)
    print_key_value("Chunk overlap", Config.CHUNK_OVERLAP)
    print_key_value("Hybrid search", "ON" if Config.USE_HYBRID else "OFF")
    print("Semantic chunker uses the embedding model.")

    while True:
        print("""
1. Select file from resources
2. Enter file path
3. Enter website URL
4. Back
""")

        choice = input("Select option: ").strip()

        if choice == "1":
            if not supported_files:
                print("❌ No supported PDF/DOCX files found in resources.")
                continue

            print_section("AVAILABLE RESOURCE FILES", "📚")
            print(f"Folder: {resources_dir}\n")

            for i, filename in enumerate(supported_files, start=1):
                full_path = os.path.join(resources_dir, filename)
                file_type = format_file_type(filename)

                try:
                    size_kb = os.path.getsize(full_path) / 1024
                    size_label = f"{size_kb:.1f} KB"
                except Exception:
                    size_label = "Unknown size"

                print(f"{i}. {filename}")
                print(f"   Type: {file_type} | Size: {size_label}")

            print(f"{len(supported_files) + 1}. Back")

            while True:
                selected = choose_number(
                    len(supported_files) + 1,
                    "\nSelect file: ",
                )

                if selected is None:
                    continue

                if selected == len(supported_files) + 1:
                    break

                source = os.path.join(resources_dir, supported_files[selected - 1])

                print("\n✅ Selected source")
                print_key_value("File", supported_files[selected - 1])
                print_key_value("Path", source)

                process_document(source, db)
                return

        elif choice == "2":
            source = input("\n📄 Enter file path: ").strip().strip('"')

            if not os.path.exists(source):
                print("❌ Invalid path")
                continue

            if not source.lower().endswith((".pdf", ".docx")):
                print("❌ Only PDF and DOCX files are supported.")
                continue

            print("\n✅ Selected external file")
            print_key_value("Path", source)

            process_document(source, db)
            return

        elif choice == "3":
            url = input("\n🌐 Enter URL: ").strip()

            if not (url.startswith("http://") or url.startswith("https://")):
                print("❌ Invalid URL")
                continue

            print("\n✅ Selected website source")
            print_key_value("URL", url)

            process_document(url, db)
            return

        elif choice == "4":
            return

        else:
            print("❌ Invalid choice")


# ============================================================
# VIEW COLLECTIONS
# ============================================================
def view_collections(db):
    view_collections_with_files(db)


# ============================================================
# DELETE COLLECTION
# ============================================================
def delete_collection(db):
    cols = db.list_collections()

    if not cols:
        print("❌ No collections found")
        return

    print_section("DELETE COLLECTION", "🧹")
    print("Select a collection to delete:\n")

    for i, col in enumerate(cols, start=1):
        try:
            collection = db.get_collection(col.name)
            files = db.list_files_in_collection(collection)
            file_count = len(files)
        except Exception:
            file_count = "?"

        print(f"{i}. {col.name}  |  files: {file_count}")

    print(f"{len(cols) + 1}. Back")

    while True:
        choice = choose_number(len(cols) + 1, "\nEnter number to delete: ")

        if choice is None:
            continue

        if choice == len(cols) + 1:
            return

        break

    collection_name = cols[choice - 1].name

    confirm = input(
        f"⚠️ Delete collection '{collection_name}'? (y/n): "
    ).strip().lower()

    if confirm != "y":
        print("ℹ️ Deletion cancelled.")
        return

    success = db.delete_collection(collection_name)

    if success:
        print("\n🧹 Running cleanup...")
        gc.collect()
        pause(2)

        subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cleanup.cleanup_runner",
            ]
        )
    else:
        print("❌ Collection deletion failed")

    del cols
    gc.collect()


# ============================================================
# QUERY
# ============================================================
def query_existing(db):
    collection = choose_collection(db, heading="🔎 Select collection for search")

    if collection is None:
        return

    try:
        print_section("RETRIEVAL CONFIG", "🔍")
        print_key_value("Provider", Config.PROVIDER)
        print_key_value("Embedding model", Config.get_embedding_model())
        print_key_value(
            "Retrieval mode",
            "Hybrid" if Config.USE_HYBRID else "Dense only",
        )
        print_key_value(
            "Reranker",
            "ON" if Config.USE_RERANKER else "OFF",
        )

        query_collection(collection, db)

    finally:
        del collection
        gc.collect()


def query_collection_with_ai(db):
    collection = choose_collection(db, heading="🤖 Select collection for AI Q&A")

    if collection is None:
        return

    try:
        from src.rag.query_engine import ask_question

        print_section("QUESTION ANSWERING", "🤖")
        query = input("Ask a question: ").strip()

        if not query:
            print("❌ Query cannot be empty")
            return

        print("\nAnswer generation config")
        print_key_value("Provider", Config.PROVIDER)
        print_key_value("Chat model", Config.get_chat_model())
        print_key_value(
            "Retriever",
            "Hybrid" if Config.USE_HYBRID else "Dense only",
        )
        print_key_value(
            "Reranker",
            "ON" if Config.USE_RERANKER else "OFF",
        )

        ask_question(collection=collection, query=query, db=db)

    finally:
        del collection
        gc.collect()


# ============================================================
# CLEANUP
# ============================================================
def cleanup_menu(db):
    from src.cleanup.cleanup import (
        deep_cleanup,
        find_orphan_folders,
        storage_report,
    )

    while True:
        print_section("STORAGE & CLEANUP", "🧹")
        print("1. Delete collection")
        print("2. View orphan UUID folders")
        print("3. Delete orphan UUID folders")
        print("4. Deep cleanup")
        print("5. Storage report")
        print("6. Back")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            delete_collection(db)

        elif choice == "2":
            orphans = find_orphan_folders()

            if not orphans:
                print("✅ No orphan UUID folders found")
            else:
                print("\n🧹 Orphan UUID folders:")
                for orphan in orphans:
                    print(f" - {orphan}")

        elif choice == "3":
            orphans = find_orphan_folders()

            if not orphans:
                print("✅ No orphan UUID folders found")
            else:
                print("""
⚠️ Orphan UUID folders exist.

Actual deletion is postponed until
application exit to avoid Chroma
file-lock issues (WinError 32).

Exit the application and cleanup
will run automatically.
""")
                for orphan in orphans:
                    print(f" - {orphan}")

        elif choice == "4":
            confirm = input("\n⚠️ Run deep cleanup? (y/n): ").lower().strip()

            if confirm == "y":
                deep_cleanup(db)

        elif choice == "5":
            storage_report(db)

        elif choice == "6":
            break

        else:
            print("❌ Invalid choice")


# ============================================================
# MAIN
# ============================================================
def main():
    print_provider_status()

    db = ChromaManager()

    try:
        while True:
            show_menu()
            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                handle_ingest(db)

            elif choice == "2":
                view_collections(db)

            elif choice == "3":
                cleanup_menu(db)

            elif choice == "4":
                query_existing(db)

            elif choice == "5":
                query_collection_with_ai(db)

            elif choice == "6":
                print_provider_status()

            elif choice == "7":
                print("\n👋 Exiting...")
                break

            else:
                print("❌ Invalid choice")

    finally:
        print("\n🔓 Releasing Chroma resources...")

        try:
            db.close()
        except Exception as error:
            print(f"⚠️ Close warning: {error}")

        gc.collect()
        pause(3)

        print("\n🧹 Final cleanup...")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cleanup.cleanup_runner",
            ]
        )


if __name__ == "__main__":
    main()