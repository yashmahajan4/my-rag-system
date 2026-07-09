import re
import numpy as np

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
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
# FIXED CHUNK
# ============================================================
def fixed_chunk(text, chunk_size):

    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


# ============================================================
# FIXED OVERLAP
# ============================================================
def fixed_chunk_with_overlap(text, size, overlap):

    chunks = []

    start = 0

    while start < len(text):

        end = start + size

        chunks.append(text[start:end])

        start += size - overlap

    return chunks


# ============================================================
# RECURSIVE
# ============================================================
def recursive_chunk(docs):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP
    )

    return splitter.split_documents(docs)


# ============================================================
# CHARACTER
# ============================================================
def character_chunk(docs):

    splitter = CharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP
    )

    return splitter.split_documents(docs)


# ============================================================
# STRUCTURAL
# ============================================================
def structural_chunk(docs):

    chunks = []

    for d in docs:

        sections = d.page_content.split("\n\n")

        for section in sections:

            section = section.strip()

            if not section:
                continue

            chunks.append(type(d)(page_content=section, metadata=dict(d.metadata)))

    return chunks


# ============================================================
# SEMANTIC
# ============================================================
def semantic_chunk(docs, window_size=2, sim_threshold=0.78):

    embedder = DynamicEmbedding()

    final_chunks = []

    for d in docs:

        text = d.page_content.strip()

        if not text:
            continue

        sentences = re.split(r"(?<=[.!?])\s+", text)

        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:

            final_chunks.append(d)
            continue

        try:

            embeddings = np.array(embedder.embed_documents(sentences))

        except Exception:

            final_chunks.append(d)
            continue

        current_chunk = [sentences[0]]

        for i in range(1, len(sentences)):

            start_idx = max(0, i - window_size)

            context_embedding = np.mean(embeddings[start_idx:i], axis=0)

            similarity = cosine_similarity([context_embedding], [embeddings[i]])[0][0]

            if similarity < sim_threshold:

                final_chunks.append(
                    type(d)(
                        page_content=" ".join(current_chunk), metadata=dict(d.metadata)
                    )
                )

                current_chunk = [sentences[i]]

            else:

                current_chunk.append(sentences[i])

        final_chunks.append(
            type(d)(page_content=" ".join(current_chunk), metadata=dict(d.metadata))
        )

    return final_chunks


# ============================================================
# APPLY STRATEGY
# ============================================================
def apply_chunking_strategy(docs, strategy):

    if strategy == "recursive":
        return recursive_chunk(docs)

    elif strategy == "character":
        return character_chunk(docs)

    elif strategy == "structural":
        return structural_chunk(docs)

    elif strategy == "semantic":
        return semantic_chunk(docs)

    elif strategy == "fixed":

        chunks = []

        for d in docs:

            parts = fixed_chunk(d.page_content, Config.CHUNK_SIZE)

            for part in parts:

                chunks.append(type(d)(page_content=part, metadata=dict(d.metadata)))

        return chunks

    elif strategy == "overlap":

        chunks = []

        for d in docs:

            parts = fixed_chunk_with_overlap(
                d.page_content, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP
            )

            for part in parts:

                chunks.append(type(d)(page_content=part, metadata=dict(d.metadata)))

        return chunks

    raise ValueError(f"❌ Unsupported chunking strategy: {strategy}")


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def chunk_document(source, strategy="recursive"):

    docs = load_document(source)

    docs = clean_documents(docs)

    print(f"\n📥 Loaded {len(docs)} document(s)")

    print(f"🧩 Chunking strategy: " f"{strategy}")

    chunks = apply_chunking_strategy(docs, strategy)

    print(f"✅ Generated " f"{len(chunks)} chunks")

    return chunks
