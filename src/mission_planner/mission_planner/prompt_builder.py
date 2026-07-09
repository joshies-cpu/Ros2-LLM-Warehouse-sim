from pathlib import Path

from .config import (
    SUPPORTED_MISSION_TYPES,
    AVAILABLE_ROUTES,
    MAX_SPEED,
    DEFAULT_SPEED,
)


class PromptBuilder:
    """Build the prompt that will be sent to the LLM."""

    def __init__(self):
        self.prompt_template = Path(__file__).parent / "prompt_template.txt"
        self.prompt_text = self.prompt_template.read_text()

    def build_prompt(self, user_prompt: str) -> str:
        prompt = self.prompt_text
        prompt = prompt.replace(
            "{missions}", "\n".join(f"- {m}" for m in SUPPORTED_MISSION_TYPES)
        )
        prompt = prompt.replace(
            "{routes}", "\n".join(f"- {r}" for r in AVAILABLE_ROUTES)
        )
        prompt = prompt.replace("{max_speed}", str(MAX_SPEED))
        prompt = prompt.replace("{default_speed}", str(DEFAULT_SPEED))
        prompt = prompt.replace("{user_prompt}", user_prompt)
        return prompt
