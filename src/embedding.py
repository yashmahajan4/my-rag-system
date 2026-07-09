import re
import time

from dotenv import load_dotenv

from src.config import Config


load_dotenv()


class DynamicEmbedding:
    def __init__(self):
        self.provider = Config.PROVIDER
        self.embedding_model = Config.get_embedding_model()

        if self.provider == "google":
            from google import genai

            if not Config.GOOGLE_API_KEY:
                raise ValueError("❌ GOOGLE_API_KEY is missing")

            self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

        elif self.provider == "ollama":
            import requests

            self.client = requests.Session()
            self.client.headers.update({"Content-Type": "application/json"})

        else:
            raise ValueError(f"❌ Unsupported provider: {self.provider}")

    def name(self):
        return f"{self.provider}-{self.embedding_model}-embedding"

    def _sanitize_text(self, text):
        text = "" if text is None else str(text)

        text = text.replace("\x00", " ")
        text = re.sub(r"[\r\t]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        max_len = max(200, Config.CHUNK_SIZE)
        if len(text) > max_len:
            text = text[:max_len]

        return text

    def _preview_text(self, text, limit=180):
        text = "" if text is None else str(text)
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text[:limit]

    def _google_embed_one(self, text):
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text,
        )

        if not getattr(response, "embeddings", None):
            raise ValueError("Google embedding response missing embeddings")

        vector = response.embeddings[0].values

        if not vector or not isinstance(vector, (list, tuple)):
            raise ValueError("Google embedding vector is empty or invalid")

        return list(vector)

    def _ollama_embed_one(self, text):
        response = self.client.post(
            Config.get_ollama_embed_url(),
            json={
                "model": self.embedding_model,
                "prompt": text,
            },
            timeout=Config.OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()
        vector = data.get("embedding")

        if not vector or not isinstance(vector, list):
            raise ValueError(f"Ollama embedding response invalid: {data}")

        return vector

    def _embed_one(self, text):
        text = self._sanitize_text(text)

        if not text:
            raise ValueError("Cannot embed empty text")

        if self.provider == "google":
            return self._google_embed_one(text)

        if self.provider == "ollama":
            return self._ollama_embed_one(text)

        raise ValueError(f"❌ Unsupported provider: {self.provider}")

    def embed_documents(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        if not isinstance(texts, list):
            raise ValueError("embed_documents expects a list of texts")

        embeddings = []

        for index, text in enumerate(texts, start=1):
            retries = 3
            last_error = None
            safe_text = self._sanitize_text(text)

            while retries > 0:
                try:
                    vector = self._embed_one(safe_text)

                    if not isinstance(vector, list):
                        raise ValueError(
                            f"Embedding at item {index} is not a list"
                        )

                    embeddings.append(vector)
                    time.sleep(0.05)
                    last_error = None
                    break

                except Exception as error:
                    last_error = error
                    retries -= 1

                    if retries > 0:
                        print(f"⚠️ Embedding retry for item {index}: {error}")
                        print(
                            f"   Length : {len(safe_text)} chars"
                        )
                        print(
                            f"   Preview: {self._preview_text(safe_text)}"
                        )
                        time.sleep(1.2)

            if last_error is not None:
                raise RuntimeError(
                    f"❌ Failed to embed text at item {index}: {last_error}\n"
                    f"Length : {len(safe_text)} chars\n"
                    f"Preview: {self._preview_text(safe_text, limit=300)}"
                ) from last_error

        return embeddings

    def embed_query(self, query):
        vectors = self.embed_documents([query])

        if not vectors or not isinstance(vectors[0], list):
            raise ValueError("No valid query embedding generated")

        return vectors[0]

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]

        if not isinstance(input, list):
            raise ValueError("Embedding input must be a string or list")

        return self.embed_documents(input)