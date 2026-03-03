from functools import wraps
from typing import Type, Any, get_type_hints, Dict, Callable
from pydantic import BaseModel, create_model
import inspect

from agentic_platform.core.models.memory_models import ToolResult, BaseContent, TextContent, JsonContent
from agentic_platform.core.models.tool_models import ToolSpec

def tool_spec(name: str = None, description: str = None, model: Type[BaseModel] = None):
    """
    Simplified decorator for creating tool specifications.
    Usage: @tool_spec(name="tool_name", description="Tool description")
    
    Args:
        name: Optional name for the tool (defaults to function name)
        description: Optional description (defaults to function docstring)
        model: Optional Pydantic model for input validation (auto-created if None)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Handle different input types
            if len(args) == 1 and not kwargs:
                arg = args[0]
                # Case 1: Dictionary input (from tool invocation)
                if isinstance(arg, dict):
                    # Inspect function signature to see if it expects a model
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())
                    
                    if len(param_names) == 1:
                        param = sig.parameters[param_names[0]]
                        param_type = param.annotation
                        
                        # If parameter is annotated as a Pydantic model, convert dict to that model
                        if param_type != inspect.Parameter.empty and isinstance(param_type, type) and issubclass(param_type, BaseModel):
                            try:
                                model_instance = param_type(**arg)
                                return func(model_instance)
                            except Exception as e:
                                print(f"Failed to convert dict to model: {e}")
                                # Fall through to keyword args approach
                    
                    # If function doesn't expect a model or conversion failed, unpack dict as kwargs
                    return func(**arg)
                    
                # Case 2: Model instance input
                elif hasattr(arg, "__dict__") and hasattr(arg, "model_fields" if hasattr(arg, "model_fields") else "__fields__"):
                    # Get function signature
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())
                    
                    if len(param_names) == 1:
                        param = sig.parameters[param_names[0]]
                        param_type = param.annotation if param.annotation != inspect.Parameter.empty else None
                        
                        # Check if function expects a different model type
                        if param_type and isinstance(param_type, type) and issubclass(param_type, BaseModel) and not isinstance(arg, param_type):
                            # Convert between model types
                            try:
                                # Get dict representation of input model
                                model_dict = arg.model_dump() if hasattr(arg, "model_dump") else arg.dict()
                                # Create expected model type
                                expected_model = param_type(**model_dict)
                                return func(expected_model)
                            except Exception as e:
                                print(f"Failed to convert between model types: {e}")
                    
                    # If direct model conversion isn't needed or failed, try to call with model
                    try:
                        return func(arg)
                    except Exception as e:
                        print(f"Failed to call with model directly: {e}")
                        # Try unpacking as kwargs as last resort
                        model_dict = arg.model_dump() if hasattr(arg, "model_dump") else arg.dict()
                        return func(**model_dict)
            
            # Default case: pass arguments through as-is
            result = func(*args, **kwargs)
            
            # If result is already a ToolResult, return it
            if isinstance(result, ToolResult):
                return result
                
            # Otherwise, wrap the result in a ToolResult
            if isinstance(result, (str, int, float, bool)):
                # Simple scalar types get converted to TextContent
                content = [TextContent(type="text", text=str(result))]
            elif isinstance(result, dict):
                # Dictionaries get converted to JsonContent
                content = [JsonContent(type="json", content=result)]
            elif isinstance(result, list) and all(isinstance(x, BaseContent) for x in result):
                # Lists of BaseContent objects are used directly
                content = result
            elif result is None:
                content = []
            else:
                # Try to convert to JSON, fall back to string
                try:
                    content = [JsonContent(type="json", content=result)]
                except:
                    content = [TextContent(type="text", text=str(result))]
                    
            return ToolResult(content=content)
            
        # Set tool name (default to function name if not provided)
        tool_name = name or func.__name__
        
        # Set tool description (default to docstring if not provided)
        tool_description = description or func.__doc__ or f"Tool for {tool_name}"
        
        # Create input model if not provided
        input_model = model
        if input_model is None:
            # Inspect function signature to get parameter names and annotations
            sig = inspect.signature(func)
            field_types = {}
            
            for param_name, param in sig.parameters.items():
                # Skip 'self' parameter if it exists
                if param_name == 'self':
                    continue
                    
                # Get type annotation if available, default to Any
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
                field_types[param_name] = (param_type, ... if param.default == inspect.Parameter.empty else param.default)
            
            # Create the model dynamically
            input_model = create_model(f"{tool_name.title()}Input", **field_types)
        
        # Create and attach ToolSpec
        wrapper.tool_spec = ToolSpec(
            model=input_model,
            name=tool_name,
            description=tool_description,
            function=wrapper
        )
        
        return wrapper
    
    # Handle case when decorator is used without parentheses @tool_spec
    if callable(name):
        func = name
        name = None
        return decorator(func)
        
    return decorator