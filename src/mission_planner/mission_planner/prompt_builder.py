from pathlib import Path

from .config import (
    AVAILABLE_MISSIONS,
    AVAILABLE_ROUTES,
    MAX_SPEED,
    DEFAULT_SPEED,
)


class PromptBuilder:
    """
    Builds the prompt that will be sent to the LLM.
    """

    def __init__(self):
        self.prompt_template = Path(__file__).parent / "prompt_template.txt"
        self.prompt_text = self.prompt_template.read_text()

    def build_prompt(self, user_prompt: str) -> str:
        return self.prompt_text.format(
            missions="\n".join(f"- {m}" for m in AVAILABLE_MISSIONS),
            routes="\n".join(f"- {r}" for r in AVAILABLE_ROUTES),
            max_speed=MAX_SPEED,
            default_speed=DEFAULT_SPEED,
            user_prompt=user_prompt,
        )
    
