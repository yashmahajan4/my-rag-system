from src.ingestion.ingest import process_document

from src.pipeline.query import (
    query_collection
)

from src.collections.collection_ui import view_collections_with_files

from src.db import ChromaManager


def handle_ingest():
    db = ChromaManager()

    path = input("📄 Enter PDF path: ").strip().strip('"')

    process_document(path, db)


def handle_query():
    db = ChromaManager()

    collections = db.list_collections()

    for i, col in enumerate(collections):
        print(f"{i + 1}. {col.name}")

    idx = int(input("Select collection: ")) - 1

    collection = db.get_collection(collections[idx].name)

    query_collection(collection, db)


def handle_view():
    db = ChromaManager()

    view_collections_with_files(db)
