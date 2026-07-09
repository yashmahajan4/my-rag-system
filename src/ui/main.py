import os
import gc
import time
import subprocess
import sys

from src.db import ChromaManager
from src.ingestion.ingest import process_document
from src.collections.collection_ui import view_collections_with_files
from src.pipeline.query import (
    query_collection,
)

# ============================================================
# MAIN MENU
# ============================================================


def show_menu():

    print("\n==============================")
    print("📦 SEMANTIC SEARCH SYSTEM")
    print("==============================")
    print("1. Ingest Content")
    print("2. View collections & files ✅")
    print("3. Storage & Cleanup 🧹")
    print("4. Query existing collection")
    print("5. Query collection with AI 🤖")
    print("6. Exit")


def query_collection_with_ai(db):

    cols = db.list_collections()

    if not cols:
        print("❌ No collections available")
        return

    print("\n📚 Select collection:")

    for i, col in enumerate(cols, start=1):
        print(f"{i}. {col.name}")

    choice = input("\nChoice: ").strip()

    if not choice.isdigit():
        print("❌ Invalid selection")
        return

    idx = int(choice) - 1

    if idx < 0 or idx >= len(cols):
        print("❌ Invalid selection")
        return

    collection = db.get_collection(cols[idx].name)

    try:

        from src.rag.query_engine import ask_question

        query = input("\n🤖 Ask a question: ").strip()

        ask_question(collection=collection, query=query, db=db)

    finally:

        del collection
        gc.collect()


# ============================================================
# HELPER
# ============================================================


def get_resources_folder():

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
        )
    )


# ============================================================
# INGEST
# ============================================================


def handle_ingest(db):

    resources_dir = get_resources_folder()

    supported_files = []

    if os.path.exists(resources_dir):

        supported_files = sorted(
            [
                f
                for f in os.listdir(resources_dir)
                if f.lower().endswith((".pdf", ".docx"))
            ]
        )

    while True:

        print("""
==============================
📥 INGEST CONTENT
==============================
1. Select File From Resources
2. Enter File Path
3. Enter Website URL
4. Back
""")

        choice = input("Select option: ").strip()

        if choice == "1":

            if not supported_files:

                print("❌ No supported files found")
                continue

            print("\n📚 Available Files")

            for i, file in enumerate(supported_files, start=1):
                print(f"{i}. {file}")

            while True:

                selected = input("\nSelect file: ").strip()

                if not selected.isdigit():

                    print("❌ Enter a number")
                    continue

                index = int(selected) - 1

                if index < 0 or index >= len(supported_files):

                    print("❌ Out of range")
                    continue

                source = os.path.join(resources_dir, supported_files[index])

                break

            process_document(source, db)
            return

        elif choice == "2":

            source = input("\n📄 Enter file path: ").strip().strip('"')

            if not os.path.exists(source):

                print("❌ Invalid path")
                continue

            if not source.lower().endswith((".pdf", ".docx")):

                print("❌ Only PDF and DOCX supported")
                continue

            process_document(source, db)
            return

        elif choice == "3":

            url = input("\n🌐 Enter URL: ").strip()

            if not (url.startswith("http://") or url.startswith("https://")):

                print("❌ Invalid URL")
                continue

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

    print("\n📚 Collections:")

    for i, col in enumerate(cols, start=1):
        print(f"{i}. {col.name}")

    while True:

        choice = input("\nEnter number to delete: ").strip()

        if not choice.isdigit():

            print("❌ Enter a valid number")
            continue

        index = int(choice) - 1

        if index < 0 or index >= len(cols):

            print("❌ Choice out of range")
            continue

        break

    collection_name = cols[index].name

    success = db.delete_collection(collection_name)

    if success:

        print("\n🧹 Running cleanup...")

        gc.collect()
        time.sleep(2)

        cleanup_runner = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "cleanup", "cleanup_runner.py"
            )
        )

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
# QUERY EXISTING
# ============================================================


def query_existing(db):

    cols = db.list_collections()

    if not cols:

        print("❌ No collections available")
        return

    print("\n📚 Select collection:")

    for i, col in enumerate(cols, start=1):
        print(f"{i}. {col.name}")

    choice = input("\nChoice: ").strip()

    if not choice.isdigit():

        print("❌ Invalid selection")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(cols):

        print("❌ Invalid selection")
        return

    collection = db.get_collection(cols[index].name)

    try:

        query_collection(collection, db)

    finally:

        del collection
        del cols
        gc.collect()


# ============================================================
# CLEANUP MENU
# ============================================================


def cleanup_menu(db):

    from src.cleanup.cleanup import (
        find_orphan_folders,
        deep_cleanup,
        storage_report,
    )

    while True:

        print("""
==============================
🧹 STORAGE & CLEANUP
==============================
1. Delete Collection
2. View Orphan UUID Folders
3. Delete Orphan UUID Folders
4. Deep Cleanup
5. Storage Report
6. Back
""")

        choice = input("Enter choice: ").strip()

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

                print("\n👋 Exiting...")
                break

            else:

                print("❌ Invalid choice")

    finally:

        print("\n🔓 Releasing Chroma resources...")

        try:

            db.close()

        except Exception as e:

            print(f"⚠️ Close warning: {e}")

        gc.collect()
        time.sleep(3)

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
