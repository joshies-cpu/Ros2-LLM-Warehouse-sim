from ollama import Client

from .config import OLLAMA_HOST, OLLAMA_MODEL


class LLMClient:
    """Handles communication with the Ollama LLM."""

    def __init__(self):
        self.client = Client(host=OLLAMA_HOST)

    def generate(self, prompt: str) -> str:
        """Send a prompt to the LLM and return its response."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            print("Sending prompt to Ollama...")

            response = self.client.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
            )

            print("Response received.")

            return response.get("response", "").strip()

        except Exception as e:
            raise RuntimeError(
                f"Failed to communicate with Ollama: {e}"
            )
