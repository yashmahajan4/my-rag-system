import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    # ==========================================================
    # PROVIDER
    # ==========================================================
    PROVIDER = os.getenv(
        "PROVIDER",
        "google"
    ).lower()

    # ==========================================================
    # GOOGLE
    # ==========================================================
    GOOGLE_API_KEY = os.getenv(
        "GOOGLE_API_KEY"
    )

    # Embeddings
    GOOGLE_EMBEDDING_MODEL = os.getenv(
        "GOOGLE_EMBEDDING_MODEL",
        "gemini-embedding-001"
    )

    # RAG / Generation
    GOOGLE_CHAT_MODEL = os.getenv(
        "GOOGLE_CHAT_MODEL",
        "gemini-2.5-flash-lite"
    )

    GOOGLE_BASE_URL = os.getenv(
        "GOOGLE_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # ==========================================================
    # OLLAMA
    # ==========================================================
    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "phi-3.5-mini"
    )

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434/v1"
    )

    OLLAMA_API_KEY = os.getenv(
        "OLLAMA_API_KEY",
        "ollama"
    )

    # ==========================================================
    # STORAGE
    # ==========================================================
    CHROMA_PATH = os.getenv(
        "CHROMA_PATH",
        "storage/chroma_db"
    )

    # ==========================================================
    # CHUNKING
    # ==========================================================
    CHUNK_SIZE = int(
        os.getenv("CHUNK_SIZE", 800)
    )

    CHUNK_OVERLAP = int(
        os.getenv("CHUNK_OVERLAP", 100)
    )

    BATCH_SIZE = int(
        os.getenv("BATCH_SIZE", 30)
    )

    # ==========================================================
    # SEARCH / RAG
    # ==========================================================
    TOP_K = int(
        os.getenv("TOP_K", 5)
    )

    MAX_CONTEXT_CHARS = int(
        os.getenv("MAX_CONTEXT_CHARS", 12000)
    )

    TEMPERATURE = float(
        os.getenv("TEMPERATURE", 0.1)
    )

    # ==========================================================
    # WEB
    # ==========================================================
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "SemanticSearchSystem/1.0"
    )

    # ==========================================================
    # HELPERS
    # ==========================================================
    @classmethod
    def get_embedding_model(cls):

        if cls.PROVIDER == "google":
            return cls.GOOGLE_EMBEDDING_MODEL

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_MODEL

        raise ValueError(
            f"Unsupported provider: {cls.PROVIDER}"
        )

    @classmethod
    def get_chat_model(cls):

        if cls.PROVIDER == "google":
            return cls.GOOGLE_CHAT_MODEL

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_MODEL

        raise ValueError(
            f"Unsupported provider: {cls.PROVIDER}"
        )

    @classmethod
    def get_api_key(cls):

        if cls.PROVIDER == "google":
            return cls.GOOGLE_API_KEY

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_API_KEY

        return None

    @classmethod
    def get_base_url(cls):

        if cls.PROVIDER == "google":
            return cls.GOOGLE_BASE_URL

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_BASE_URL

        return None