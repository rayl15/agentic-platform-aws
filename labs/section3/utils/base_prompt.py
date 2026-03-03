from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

HAIKU_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

class BasePrompt(BaseModel):
    """
    A streamlined base class for creating prompts with system and user components.
    Extracted from the 3.1-prompt-chaining bonus notebook for reuse across section 3 labs.
    """
    system_prompt: str
    user_prompt: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    model_id: str = HAIKU_MODEL_ID
    hyperparams: Dict[str, Any] = Field(default_factory=lambda: {
        "temperature": 0.5,
        "maxTokens": 1000
    })

    # Just format the prompt if inputs were provided during initialization
    def __init__(self, **data):
        super().__init__(**data)
        # Format prompts if inputs were provided during initialization
        if self.inputs:
            self.format()

    def format(self, inputs: Dict[str, Any] = None) -> None:
        """Format system_prompt and user_prompt with inputs."""

        # Override the inputs if provided.
        inputs_to_use = inputs if inputs else self.inputs

        try:
            self.system_prompt = self.system_prompt.format(**inputs_to_use)
            self.user_prompt = self.user_prompt.format(**inputs_to_use)
        except KeyError as e:
            raise KeyError(f'Missing input value: {e}')
        except Exception as e:
            raise Exception(f'Error formatting prompt: {e}')

    def to_bedrock_messages(self, conversation: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Convert to Bedrock messages format."""
        messages = conversation.copy() if conversation else []
        messages.append({"role": "user", "content": [{"text": self.user_prompt}]})
        return messages

    def to_bedrock_system(self, guard_content: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Convert to Bedrock system format."""
        system = [{"text": self.system_prompt}]
        if guard_content:
            system.append({"guard": guard_content})
        return system
