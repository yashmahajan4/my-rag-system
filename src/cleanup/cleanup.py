import gc
import os
import shutil
import sqlite3
import time
import uuid
from pathlib import Path

from src.config import Config

# ============================================================
# PATHS
# ============================================================

FOLDER_PATH = Path(Config.CHROMA_PATH).resolve()
DB_PATH = FOLDER_PATH / "chroma.sqlite3"


# ============================================================
# HELPERS
# ============================================================


def is_uuid(name: str) -> bool:
    try:
        uuid.UUID(name)
        return True
    except ValueError:
        return False


def db_exists() -> bool:
    return DB_PATH.exists()


def table_exists(table_name: str) -> bool:

    if not db_exists():
        return False

    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name=?
                """,
                (table_name,),
            )

            return cursor.fetchone() is not None

    except Exception:
        return False


# ============================================================
# SEGMENTS
# ============================================================


def get_active_segments():

    if not db_exists():
        return set()

    if not table_exists("segments"):
        return set()

    try:
        with sqlite3.connect(str(DB_PATH)) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM segments
                """)

            segments = cursor.fetchall()

        return {str(row[0]) for row in segments}

    except Exception as e:

        print(f"❌ Failed to read segments: {e}")

        return set()


# ============================================================
# FOLDERS
# ============================================================


def get_all_folders():

    if not FOLDER_PATH.exists():
        return []

    folders = []

    for item in os.listdir(FOLDER_PATH):

        path = FOLDER_PATH / item

        if path.is_dir() and item != "__pycache__" and is_uuid(item):
            folders.append(item)

    return folders


def find_orphan_folders():

    active_segments = get_active_segments()

    folders = get_all_folders()

    return [folder for folder in folders if folder not in active_segments]


# ============================================================
# DELETE FOLDER
# ============================================================


def delete_folder_with_retry(
    path,
    folder_name,
    retries=10,
    delay=1,
):

    for attempt in range(1, retries + 1):

        try:

            shutil.rmtree(path)

            print(f"✅ Deleted: {folder_name}")

            return True

        except PermissionError as e:

            if attempt < retries:

                print(
                    f"⏳ Folder locked "
                    f"({attempt}/{retries}) "
                    f"→ retrying in {delay}s..."
                )

                gc.collect()

                time.sleep(delay)

            else:

                print(f"❌ Failed to delete " f"{folder_name}: {e}")

        except Exception as e:

            print(f"❌ Failed to delete " f"{folder_name}: {e}")

            return False

    return False


# ============================================================
# CLEAN ORPHANS
# ============================================================


def clean_orphans(dry_run=False):

    gc.collect()

    orphans = find_orphan_folders()

    if not orphans:

        print("✅ No orphan folders found")

        return

    print("\n🧹 Orphan UUID folders:")

    for orphan in orphans:
        print(f" - {orphan}")

    if dry_run:

        print("\n⚠️ Dry-run mode enabled")

        return

    print("\n🚨 Deleting orphan folders...")

    deleted_count = 0

    for orphan in orphans:

        path = FOLDER_PATH / orphan

        if not path.exists():
            continue

        if delete_folder_with_retry(path, orphan):
            deleted_count += 1

    print(f"\n📊 Cleanup complete " f"({deleted_count}/{len(orphans)} deleted)")


# ============================================================
# ORPHAN SEGMENTS
# ============================================================


def find_orphan_segments():

    if not db_exists():
        return []

    if not table_exists("segments"):
        return []

    try:

        active_folders = set(get_all_folders())

        with sqlite3.connect(str(DB_PATH)) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM segments
                """)

            segments = [str(row[0]) for row in cursor.fetchall()]

        return [seg for seg in segments if seg not in active_folders]

    except Exception as e:

        print(f"❌ Failed reading orphan segments: {e}")

        return []


def delete_orphan_segment_entries():

    orphan_segments = find_orphan_segments()

    if not orphan_segments:

        print("✅ No orphan DB entries found")

        return

    print("\n🧹 Removing orphan DB entries:")

    try:

        with sqlite3.connect(str(DB_PATH)) as conn:

            cursor = conn.cursor()

            for seg in orphan_segments:

                print(f" - {seg}")

                cursor.execute(
                    """
                    DELETE FROM segments
                    WHERE id = ?
                    """,
                    (seg,),
                )

            conn.commit()

        print(f"✅ Removed " f"{len(orphan_segments)} " f"orphan segment entries")

    except Exception as e:

        print(f"❌ Failed removing DB entries: {e}")


# ============================================================
# SIZE
# ============================================================


def get_folder_size(path):

    total = 0

    if not Path(path).exists():
        return 0

    for root, _, files in os.walk(path):

        for f in files:

            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass

    return total


# ============================================================
# REPORT
# ============================================================


def storage_report(db):

    active_segments = len(get_active_segments())

    folders = len(get_all_folders())

    orphans = len(find_orphan_folders())

    db_size = 0

    if db_exists():
        db_size = DB_PATH.stat().st_size

    storage_size = get_folder_size(FOLDER_PATH)

    print("\n==============================")
    print("📊 STORAGE REPORT")
    print("==============================")

    try:
        collections = len(db.list_collections())
    except Exception:
        collections = 0

    print(f"Collections     : {collections}")
    print(f"Active Segments : {active_segments}")
    print(f"UUID Folders    : {folders}")
    print(f"Orphans         : {orphans}")

    print(f"SQLite Size     : " f"{db_size / 1024 / 1024:.2f} MB")

    print(f"Storage Size    : " f"{storage_size / 1024 / 1024:.2f} MB")

    print(f"Total Size      : " f"{(db_size + storage_size) / 1024 / 1024:.2f} MB")


# ============================================================
# DEEP CLEANUP
# ============================================================


def deep_cleanup(db):

    print("\n🚀 Starting deep cleanup...")

    delete_orphan_segment_entries()

    clean_orphans(dry_run=False)

    storage_report(db)

    print("\n✅ Deep cleanup complete")
