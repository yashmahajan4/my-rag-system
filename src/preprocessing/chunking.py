import hashlib
import re

import numpy as np
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from sklearn.metrics.pairwise import cosine_similarity

from src.config import Config
from src.embedding import DynamicEmbedding
from src.loaders.document_loader import load_document
from src.preprocessing.cleaning import clean_documents


# ============================================================
# SECTION EXTRACTION
# ============================================================
def extract_section(text):
    match = re.search(r"(\d+\.\d+|\bAnnex\s+[A-Z]\b)", text)
    return match.group(0) if match else "unknown"


# ============================================================
# HELPERS
# ============================================================
def clone_document(doc, page_content, extra_metadata=None):
    metadata = dict(doc.metadata or {})

    if extra_metadata:
        metadata.update(extra_metadata)

    return type(doc)(
        page_content=page_content,
        metadata=metadata,
    )


def build_chunk_signature(chunk):
    page = chunk.metadata.get("page", "0")
    strategy = chunk.metadata.get("chunking", "")
    text = (chunk.page_content or "").strip()

    raw = f"{page}::{strategy}::{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def deduplicate_chunks(chunks):
    unique_chunks = []
    seen = set()

    for chunk in chunks:
        text = (chunk.page_content or "").strip()

        if not text:
            continue

        signature = build_chunk_signature(chunk)

        if signature in seen:
            continue

        seen.add(signature)
        unique_chunks.append(chunk)

    return unique_chunks


def print_chunking_runtime_banner(strategy):
    print("\n------------------------------")
    print("🧩 CHUNKING RUNTIME")
    print("------------------------------")
    print(f"Strategy         : {strategy}")
    print(f"Provider         : {Config.PROVIDER}")
    print(f"Embedding Model  : {Config.get_embedding_model()}")
    print(f"Chat Model       : {Config.get_chat_model()}")

    if strategy == "semantic":
        print("Semantic Model   : uses embedding model")
        print(f"Window Size      : {Config.SEMANTIC_WINDOW_SIZE}")
        print(f"Similarity Thres.: {Config.SEMANTIC_SIM_THRESHOLD}")

    print("------------------------------")


def split_oversized_chunks(chunks):
    safe_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=min(Config.CHUNK_OVERLAP, max(0, Config.CHUNK_SIZE // 5)),
    )

    oversized_count = 0

    for chunk in chunks:
        text = (chunk.page_content or "").strip()

        if not text:
            continue

        if len(text) <= Config.CHUNK_SIZE:
            safe_chunks.append(
                clone_document(
                    doc=chunk,
                    page_content=text,
                )
            )
            continue

        oversized_count += 1

        temp_doc = clone_document(
            doc=chunk,
            page_content=text,
        )

        split_docs = splitter.split_documents([temp_doc])

        for split_doc in split_docs:
            split_text = (split_doc.page_content or "").strip()

            if not split_text:
                continue

            safe_chunks.append(
                clone_document(
                    doc=split_doc,
                    page_content=split_text,
                )
            )

    if oversized_count > 0:
        print(
            f"⚠️ Safety split applied to {oversized_count} oversized chunk(s) "
            f"using recursive fallback"
        )

    return safe_chunks


# ============================================================
# FIXED CHUNK
# ============================================================
def fixed_chunk(text, chunk_size):
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


# ============================================================
# FIXED OVERLAP
# ============================================================
def fixed_chunk_with_overlap(text, size, overlap):
    chunks = []

    if size <= 0:
        return chunks

    if overlap >= size:
        overlap = max(0, size - 1)

    start = 0

    while start < len(text):
        end = start + size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        next_start = start + size - overlap

        if next_start <= start:
            break

        start = next_start

    return chunks


# ============================================================
# RECURSIVE
# ============================================================
def recursive_chunk(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )

    return splitter.split_documents(docs)


# ============================================================
# CHARACTER
# ============================================================
def character_chunk(docs):
    splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )

    return splitter.split_documents(docs)


# ============================================================
# STRUCTURAL
# ============================================================
def structural_chunk(docs):
    chunks = []

    for doc in docs:
        sections = re.split(r"\n\s*\n+", doc.page_content or "")

        for section in sections:
            section = section.strip()

            if not section:
                continue

            chunks.append(
                clone_document(
                    doc=doc,
                    page_content=section,
                )
            )

    return chunks


# ============================================================
# SEMANTIC
# ============================================================
def semantic_chunk(
    docs,
    window_size=None,
    sim_threshold=None,
):
    window_size = (
        Config.SEMANTIC_WINDOW_SIZE
        if window_size is None
        else window_size
    )

    sim_threshold = (
        Config.SEMANTIC_SIM_THRESHOLD
        if sim_threshold is None
        else sim_threshold
    )

    print("\n🧠 Semantic chunking is using the embedding model")
    print(f"Provider         : {Config.PROVIDER}")
    print(f"Embedding Model  : {Config.get_embedding_model()}")
    print(f"Window Size      : {window_size}")
    print(f"Similarity Thres.: {sim_threshold}")

    embedder = DynamicEmbedding()
    final_chunks = []

    for doc_index, doc in enumerate(docs, start=1):
        text = (doc.page_content or "").strip()

        if not text:
            continue

        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if len(sentences) < 2:
            final_chunks.append(doc)
            continue

        try:
            embeddings = np.array(embedder.embed_documents(sentences))
        except Exception as error:
            print(f"⚠️ Semantic chunk fallback on doc {doc_index}: {error}")
            final_chunks.append(doc)
            continue

        current_chunk = [sentences[0]]

        for i in range(1, len(sentences)):
            start_idx = max(0, i - window_size)
            context_embedding = np.mean(embeddings[start_idx:i], axis=0)

            similarity = cosine_similarity(
                [context_embedding],
                [embeddings[i]],
            )[0][0]

            if similarity < sim_threshold:
                final_chunks.append(
                    clone_document(
                        doc=doc,
                        page_content=" ".join(current_chunk),
                    )
                )
                current_chunk = [sentences[i]]
            else:
                current_chunk.append(sentences[i])

        if current_chunk:
            final_chunks.append(
                clone_document(
                    doc=doc,
                    page_content=" ".join(current_chunk),
                )
            )

    return final_chunks


# ============================================================
# APPLY STRATEGY
# ============================================================
def apply_chunking_strategy(docs, strategy):
    print_chunking_runtime_banner(strategy)

    if strategy == "recursive":
        chunks = recursive_chunk(docs)

    elif strategy == "character":
        chunks = character_chunk(docs)

    elif strategy == "structural":
        chunks = structural_chunk(docs)

    elif strategy == "semantic":
        chunks = semantic_chunk(docs)

    elif strategy == "fixed":
        chunks = []

        for doc in docs:
            parts = fixed_chunk(
                doc.page_content or "",
                Config.CHUNK_SIZE,
            )

            for part in parts:
                part = part.strip()

                if not part:
                    continue

                chunks.append(
                    clone_document(
                        doc=doc,
                        page_content=part,
                    )
                )

    elif strategy == "overlap":
        chunks = []

        for doc in docs:
            parts = fixed_chunk_with_overlap(
                doc.page_content or "",
                Config.CHUNK_SIZE,
                Config.CHUNK_OVERLAP,
            )

            for part in parts:
                part = part.strip()

                if not part:
                    continue

                chunks.append(
                    clone_document(
                        doc=doc,
                        page_content=part,
                    )
                )

    else:
        raise ValueError(f"❌ Unsupported chunking strategy: {strategy}")

    final_chunks = []

    for chunk in chunks:
        text = (chunk.page_content or "").strip()

        if not text:
            continue

        final_chunks.append(
            clone_document(
                doc=chunk,
                page_content=text,
            )
        )

    final_chunks = split_oversized_chunks(final_chunks)

    return final_chunks


# ============================================================
# APPLY MULTIPLE STRATEGIES
# ============================================================
def apply_multiple_chunking_strategies(docs, strategies):
    all_chunks = []

    print("\n🧩 Multi-strategy chunking selected")
    print(f"Strategies        : {strategies}")
    print(f"Provider          : {Config.PROVIDER}")
    print(f"Embedding Model   : {Config.get_embedding_model()}")
    print(f"Chat Model        : {Config.get_chat_model()}")

    for strategy in strategies:
        print(f"\n⚙️ Applying {strategy}")

        strategy_chunks = apply_chunking_strategy(docs, strategy)

        for chunk in strategy_chunks:
            chunk.metadata["chunking"] = strategy

        strategy_chunks = deduplicate_chunks(strategy_chunks)

        print(f"✅ {strategy} produced {len(strategy_chunks)} unique chunks")

        all_chunks.extend(strategy_chunks)

    all_chunks = deduplicate_chunks(all_chunks)

    print(f"\n✅ Total unique chunks after merge: {len(all_chunks)}")

    return all_chunks


# ============================================================
# LOAD AND CLEAN DOCUMENTS
# ============================================================
def load_and_clean_document(source):
    docs = load_document(source)
    docs = clean_documents(docs)

    print(f"\n📥 Loaded {len(docs)} document(s)")

    return docs


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def chunk_document(source, strategy="recursive"):
    docs = load_and_clean_document(source)

    print(f"🧩 Chunking strategy: {strategy}")

    chunks = apply_chunking_strategy(docs, strategy)

    for chunk in chunks:
        chunk.metadata["chunking"] = strategy

    chunks = deduplicate_chunks(chunks)

    print(f"✅ Generated {len(chunks)} unique chunks")

    return chunks