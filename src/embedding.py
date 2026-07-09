import time
from dotenv import load_dotenv

from src.config import Config

load_dotenv()


class DynamicEmbedding:

    def __init__(self):

        self.provider = Config.PROVIDER

        if self.provider == "google":

            from google import genai

            self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

        elif self.provider == "ollama":

            import requests

            self.client = requests

        else:

            raise ValueError("❌ Unsupported provider")

    def name(self):

        return f"{self.provider}-embedding"

    # ==========================================================
    # DOCUMENT EMBEDDINGS
    # ==========================================================

    def embed_documents(
        self,
        texts,
    ):

        embeddings = []

        for text in texts:

            retries = 3

            while retries > 0:

                try:

                    # ======================================
                    # GOOGLE
                    # ======================================
                    if self.provider == "google":

                        res = self.client.models.embed_content(
                            model=Config.get_embedding_model(), contents=text
                        )

                        embeddings.append(list(res.embeddings[0].values))

                    # ======================================
                    # OLLAMA
                    # ======================================
                    elif self.provider == "ollama":

                        response = self.client.post(
                            f"{Config.get_base_url()}/embeddings",
                            json={
                                "model": Config.get_embedding_model(),
                                "prompt": text,
                            },
                        )

                        data = response.json()

                        embeddings.append(list(data["embedding"]))

                    time.sleep(0.2)

                    break

                except Exception as e:

                    print(f"⚠️ Retry: {e}")

                    retries -= 1

                    time.sleep(2)

            if retries == 0:

                print("❌ Fallback embedding")

                embeddings.append([0.0] * 768)

        return embeddings

    # ==========================================================
    # QUERY EMBEDDING
    # ==========================================================

    def embed_query(self, input=None, **kwargs):

        text = input

        if text is None:
            text = kwargs.get("text")

        if text is None:
            raise ValueError("No query text provided")

        return self.embed_documents([text])

    # ==========================================================
    # CHROMA ENTRYPOINT
    # ==========================================================

    def __call__(self, input):

        # print("\n==== DEBUG CALL ====")
        # print("type(input):", type(input))
        # print("====================\n")

        if isinstance(input, str):
            input = [input]

        return self.embed_documents(input)
