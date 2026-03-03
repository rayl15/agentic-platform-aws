from pydantic import BaseModel, field_validator
from typing import List

SUPPORTED_MODELS: List[str] = [
    "amazon.titan-embed-text-v2:0",
]

class EmbedRequest(BaseModel):
    text: str
    model_id: str

    # Check for supported models
    @field_validator("model_id")
    @classmethod
    def validate_model_id(cls, v, info):
        if v not in SUPPORTED_MODELS:
            raise ValueError(f"Model ID {v} is not supported")
        return v
    
class EmbedResponse(BaseModel):
    embedding: List[float]