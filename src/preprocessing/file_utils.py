import os
import hashlib
from urllib.parse import urlparse


# ============================================================
# HASH HELPERS
# ============================================================
def sha256_text(text: str) -> str:

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def sha256_file(path: str) -> str:

    hash_obj = hashlib.sha256()

    with open(path, "rb") as f:

        while True:

            chunk = f.read(8192)

            if not chunk:
                break

            hash_obj.update(chunk)

    return hash_obj.hexdigest()


# ============================================================
# SOURCE DETECTION
# ============================================================
def is_url(source: str) -> bool:

    source = source.strip().lower()

    return (
        source.startswith("http://")
        or source.startswith("https://")
    )


def get_source_type(source: str) -> str:

    if is_url(source):
        return "web"

    ext = os.path.splitext(
        source
    )[1].lower()

    mapping = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".txt": "txt",
        ".md": "markdown"
    }

    return mapping.get(
        ext,
        "unknown"
    )


# ============================================================
# WEB SIGNATURE
# ============================================================
def get_web_signature(
    url: str,
    content_hash: str = None
):

    parsed = urlparse(url)

    source_name = parsed.netloc

    file_hash = (
        content_hash
        if content_hash
        else sha256_text(
            url.strip().lower()
        )
    )

    return (
        source_name,
        0,
        file_hash
    )


# ============================================================
# FILE SIGNATURE
# ============================================================
def get_file_signature(path: str):

    size = os.path.getsize(path)

    file_hash = sha256_file(path)

    file_name = os.path.splitext(
        os.path.basename(path)
    )[0]

    return (
        file_name,
        size,
        file_hash
    )


# ============================================================
# UNIVERSAL SIGNATURE
# ============================================================
def get_source_signature(
    source: str,
    content_hash: str = None
):

    if is_url(source):
        return get_web_signature(
            source,
            content_hash
        )

    return get_file_signature(source)


# ============================================================
# SOURCE METADATA
# ============================================================
def build_source_metadata(
    source: str,
    content_hash: str = None
):

    source_type = get_source_type(
        source
    )

    name, size, file_hash = (
        get_source_signature(
            source,
            content_hash
        )
    )

    metadata = {
        "source_name": name,
        "source_type": source_type,
        "source": source,
        "file_size": size,
        "file_hash": file_hash
    }

    if is_url(source):

        metadata["url_hash"] = sha256_text(
            source.strip().lower()
        )

    return metadata