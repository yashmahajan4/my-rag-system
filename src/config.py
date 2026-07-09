import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # ==========================================================
    # PROVIDER
    # ==========================================================
    PROVIDER = os.getenv("PROVIDER", "google").strip().lower()

    # ==========================================================
    # GOOGLE
    # ==========================================================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

    GOOGLE_EMBEDDING_MODEL = os.getenv(
        "GOOGLE_EMBEDDING_MODEL",
        "gemini-embedding-001",
    ).strip()

    GOOGLE_CHAT_MODEL = os.getenv(
        "GOOGLE_CHAT_MODEL",
        "gemini-3.1-flash-lite",
    ).strip()

    GOOGLE_BASE_URL = os.getenv(
        "GOOGLE_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    ).strip().rstrip("/")

    # ==========================================================
    # OLLAMA
    # ==========================================================
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    ).strip().rstrip("/")

    OLLAMA_API_KEY = os.getenv(
        "OLLAMA_API_KEY",
        "ollama",
    ).strip()

    OLLAMA_CHAT_MODEL = os.getenv(
        "OLLAMA_CHAT_MODEL",
        "deepseek-r1:1.5b",
    ).strip()

    OLLAMA_EMBEDDING_MODEL = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text",
    ).strip()

    OLLAMA_TIMEOUT = int(
        os.getenv("OLLAMA_TIMEOUT", "120")
    )

    # ==========================================================
    # STORAGE
    # ==========================================================
    CHROMA_PATH = os.getenv(
        "CHROMA_PATH",
        "storage/chroma_db",
    ).strip()

    # ==========================================================
    # CHUNKING
    # ==========================================================
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "30"))

    SEMANTIC_WINDOW_SIZE = int(
        os.getenv("SEMANTIC_WINDOW_SIZE", "3")
    )

    SEMANTIC_SIM_THRESHOLD = float(
        os.getenv("SEMANTIC_SIM_THRESHOLD", "0.75")
    )

    # ==========================================================
    # SEARCH / RAG
    # ==========================================================
    TOP_K = int(os.getenv("TOP_K", "5"))
    MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

    # ==========================================================
    # HYBRID SEARCH
    # ==========================================================
    USE_HYBRID = os.getenv("USE_HYBRID", "true").strip().lower() == "true"
    DENSE_TOP_K = int(os.getenv("DENSE_TOP_K", "10"))
    BM25_TOP_K = int(os.getenv("BM25_TOP_K", "10"))
    FINAL_TOP_K = int(os.getenv("FINAL_TOP_K", "5"))
    RRF_K = int(os.getenv("RRF_K", "60"))
    BM25_MIN_SCORE = float(os.getenv("BM25_MIN_SCORE", "0.0"))

    # ==========================================================
    # RERANKER
    # ==========================================================
    USE_RERANKER = os.getenv("USE_RERANKER", "true").strip().lower() == "true"

    RERANKER_TYPE = os.getenv(
        "RERANKER_TYPE",
        "cross_encoder",
    ).strip().lower()

    RERANK_TOP_N = int(
        os.getenv("RERANK_TOP_N", "12")
    )

    CROSS_ENCODER_MODEL = os.getenv(
        "CROSS_ENCODER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ).strip()

    CROSS_ENCODER_MAX_LENGTH = int(
        os.getenv("CROSS_ENCODER_MAX_LENGTH", "512")
    )

    # ==========================================================
    # WEB
    # ==========================================================
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "SemanticSearchSystem/1.0",
    ).strip()

    # ==========================================================
    # HELPERS
    # ==========================================================
    @classmethod
    def validate_provider(cls):
        if cls.PROVIDER not in {"google", "ollama"}:
            raise ValueError(f"Unsupported provider: {cls.PROVIDER}")

    @classmethod
    def get_embedding_model(cls):
        cls.validate_provider()

        if cls.PROVIDER == "google":
            return cls.GOOGLE_EMBEDDING_MODEL

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_EMBEDDING_MODEL

        raise ValueError(f"Unsupported provider: {cls.PROVIDER}")

    @classmethod
    def get_chat_model(cls):
        cls.validate_provider()

        if cls.PROVIDER == "google":
            return cls.GOOGLE_CHAT_MODEL

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_CHAT_MODEL

        raise ValueError(f"Unsupported provider: {cls.PROVIDER}")

    @classmethod
    def get_api_key(cls):
        cls.validate_provider()

        if cls.PROVIDER == "google":
            return cls.GOOGLE_API_KEY

        if cls.PROVIDER == "ollama":
            return cls.OLLAMA_API_KEY or "ollama"

        return None

    @classmethod
    def get_base_url(cls):
        cls.validate_provider()

        if cls.PROVIDER == "google":
            return f"{cls.GOOGLE_BASE_URL}/"

        if cls.PROVIDER == "ollama":
            return f"{cls.OLLAMA_BASE_URL}/v1"

        return None

    @classmethod
    def get_ollama_embed_url(cls):
        return f"{cls.OLLAMA_BASE_URL}/api/embeddings"

    @classmethod
    def get_active_provider_summary(cls):
        return {
            "provider": cls.PROVIDER,
            "embedding_model": cls.get_embedding_model(),
            "chat_model": cls.get_chat_model(),
            "base_url": cls.get_base_url(),
        }