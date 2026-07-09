from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    WebBaseLoader
)


SUPPORTED_TYPES = {
    ".pdf": "pdf",
    ".docx": "docx"
}


def load_pdf(path):

    loader = PyPDFLoader(path)

    docs = loader.load()

    for doc in docs:

        doc.metadata["source_type"] = "pdf"
        doc.metadata["source"] = path

    return docs


def load_docx(path):

    loader = Docx2txtLoader(path)

    docs = loader.load()

    for doc in docs:

        doc.metadata["source_type"] = "docx"
        doc.metadata["source"] = path

    return docs


def load_web(url):

    loader = WebBaseLoader(url)

    docs = loader.load()

    for doc in docs:

        doc.metadata["source_type"] = "web"
        doc.metadata["source"] = url

    return docs


def load_document(source):

    source = source.strip()

    if source.startswith("http://") or source.startswith("https://"):
        return load_web(source)

    source_lower = source.lower()

    if source_lower.endswith(".pdf"):
        return load_pdf(source)

    if source_lower.endswith(".docx"):
        return load_docx(source)

    raise ValueError(
        f"❌ Unsupported file type: {source}"
    )