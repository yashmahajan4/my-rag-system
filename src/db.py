import gc
from pathlib import Path

import chromadb

from src.config import Config
from src.embedding import DynamicEmbedding


class ChromaManager:

    def __init__(self):

        self.chroma_path = Path(Config.CHROMA_PATH).resolve()
        self.chroma_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.chroma_path))

        self.embedding = DynamicEmbedding()

    # ============================================================
    # SHUTDOWN / CLEANUP
    # ============================================================

    def close(self):
        try:

            self.embedding = None
            self.client = None

            gc.collect()

            print("✅ Chroma resources released")

        except Exception as ex:

            print(
                f"⚠️ Error releasing Chroma resources: {ex}"
            )


    # ============================================================
    # COLLECTION MANAGEMENT
    # ============================================================

    def list_collections(self):

        try:
            return self.client.list_collections()
        except Exception as ex:
            print(f"❌ Failed listing collections: {ex}")
            return []

    def collection_exists(self, name):

        try:

            return any(
                collection.name == name for collection in self.client.list_collections()
            )

        except Exception as ex:

            print(f"❌ Error checking collection existence: {ex}")

            return False

    def get_collection(self, name):

        try:

            return self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding,
            )

        except Exception as ex:

            print(f"❌ Failed to access collection '{name}': {ex}")

            raise

    def delete_collection(self, name):

        if not self.collection_exists(name):

            print("❌ Collection not found")

            return False

        try:

            # force release any references
            gc.collect()

            self.client.delete_collection(name)

            gc.collect()

            print(f"🧹 Deleted collection: {name}")

            return True

        except Exception as ex:

            print(f"❌ Failed deleting collection: {ex}")

            return False
    # ============================================================
    # DUPLICATE DETECTION
    # ============================================================

    def find_file(self, file_hash):

        for col in self.client.list_collections():

            try:

                collection = self.get_collection(col.name)

                data = collection.get(where={"file_hash": file_hash})

                if len(data.get("ids", [])) > 0:
                    return col.name

            except Exception as ex:

                print(f"⚠️ Error checking collection " f"{col.name}: {ex}")

        return None

    def file_exists_in_collection(
        self,
        collection,
        file_hash,
    ):

        try:

            data = collection.get(where={"file_hash": file_hash})

            return len(data.get("ids", [])) > 0

        except Exception as ex:

            print(f"⚠️ Error checking file existence: {ex}")

            return False

    # ============================================================
    # INSERT
    # ============================================================

    def insert_batches(
        self,
        collection,
        docs,
        metas,
        ids,
        batch_size,
    ):

        total = len(docs)

        for i in range(0, total, batch_size):

            end = min(i + batch_size, total)

            print(f"📦 Batch {i} → {end}")

            try:

                collection.add(
                    documents=docs[i:end],
                    metadatas=metas[i:end],
                    ids=ids[i:end],
                )

            except Exception as ex:

                print(f"❌ Failed inserting " f"batch {i}-{end}: {ex}")

                raise

    # ============================================================
    # QUERY
    # ============================================================

    def query(
    self,
    collection,
    query_text,
    n_results=None,
    where=None,
):

        try:

            return collection.query(
                query_texts=[query_text],
                n_results=n_results or Config.TOP_K,
                where=where,
            )

        except Exception as ex:

            import traceback

            traceback.print_exc()

            print(
                f"❌ Query failed: {ex}"
            )

            return None

    # ============================================================
    # RESULT DISPLAY
    # ============================================================

    def print_results(self, results):

        if not results:

            print("❌ No results")

            return

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:

            print("❌ No matching content found")

            return

        print("\n🌍 SEARCH RESULTS:")

        for doc, meta in zip(documents, metadatas):

            meta = meta or {}

            print("\n" + "-" * 60)

            print(f"📄 Source   : " f"{meta.get('source_name', 'Unknown')}")

            print(f"📦 Type     : " f"{meta.get('source_type', 'Unknown')}")

            print(f"📑 Page     : " f"{meta.get('page', 'N/A')}")

            print(f"📚 Section  : " f"{meta.get('section', 'Unknown')}")

            print(f"🧩 Chunking : " f"{meta.get('chunking', 'Unknown')}")

            print("\n📖 Content:\n")

            print(doc[:500])

    # ============================================================
    # COLLECTION FILES
    # ============================================================

    def list_files_in_collection(self, collection):

        try:

            data = collection.get(include=["metadatas"])

            files = {
                meta["source_name"]
                for meta in data.get("metadatas", [])
                if meta and "source_name" in meta
            }

            return sorted(files)

        except Exception as ex:

            print(f"❌ Error fetching files: {ex}")

            return []

    # ============================================================
    # PATH UTILITIES
    # ============================================================

    def get_chroma_path(self):

        return str(self.chroma_path)

    def get_sqlite_path(self):

        return str(self.chroma_path / "chroma.sqlite3")
