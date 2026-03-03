from pydantic import BaseModel, Field
from typing import Dict, Any

from pydantic import BaseModel, Field

HAIKU_MODEL_ID = "us.anthropic.claude-3-haiku-20240307-v1:0"
class BasePrompt(BaseModel):
    """
    A streamlined base class for creating prompts with system and user components.
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
    