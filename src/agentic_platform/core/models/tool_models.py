from typing import Dict, Any, Type, Callable, Optional
from pydantic import BaseModel

class ToolSpec(BaseModel):
    """
    A Pydantic model wrapper for a function definition.
    Both name and description must be explicitly provided.
    """
    model: Type[BaseModel]
    name: str 
    description: str

    # This is not part of the spec, but is useful for binding the tool function to the tool spec.
    function: Optional[Callable] = None
    
    model_config = { "arbitrary_types_allowed": True }