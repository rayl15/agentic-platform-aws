from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

# Import these from the memory_models module.
from agentic_platform.core.models.memory_models import Message, ToolCall, ToolResult
from agentic_platform.core.models.llm_models import LLMRequest
from agentic_platform.core.models.tool_models import ToolSpec
# It makes sense to use class methods here because we're not using any instance state.
class BaseLLMRequestConverter(ABC):
    """Abstract base class for message converters"""
    @classmethod
    @abstractmethod
    def convert_messages(cls, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert a list of messages to provider format"""
        pass

    @classmethod
    @abstractmethod
    def convert_system(cls, system_prompt: str) -> Dict[str, Any]:
        """Convert a system prompt to provider format"""
        pass

    @classmethod
    @abstractmethod
    def convert_tool_spec(cls, tools: List[ToolSpec], force_tool: Optional[str] = None) -> Dict[str, Any]:
        """Convert tools to Bedrock tool spec config"""
        pass

    @classmethod
    @abstractmethod
    def convert_llm_request(cls, request: LLMRequest) -> Dict[str, Any]:
        """Convert a LLMRequest to provider format"""
        pass

class ConverseRequestConverter(BaseLLMRequestConverter):

    @classmethod
    def convert_tool_call(cls, tool: ToolCall) -> Dict[str, Any]:
        return {
            "toolUse": {
                "toolUseId": tool.id,
                "name": tool.name,
                "input": tool.arguments
            }
        }
    
    @classmethod
    def convert_tool_result(cls, tool_result: ToolResult) -> Dict[str, Any]:
        bedrock_content = []
        
        for content in tool_result.content:
            if content.type == "text":
                bedrock_content.append({"text": content.text})
            elif content.type == "json":
                bedrock_content.append({"json": content.content})
            elif content.type == "image":
                bedrock_content.append({
                    "image": {
                        "format": content.mimeType.split("/")[1],
                        "source": {
                            "bytes": content.data  # Note: This may need base64 decoding
                        }
                    }
                })
            elif content.type == "audio":
                # Add audio conversion if needed
                pass
        
        return {
            "toolResult": {
                "toolUseId": tool_result.id,
                "content": bedrock_content,
                "status": "success" if not tool_result.isError else "error"
            }
        }

    @classmethod
    def convert_message(cls, message: Message) -> Dict[str, Any]:
        """Convert an individual message object into Bedrock's format."""
        content = []
        
        if message.text:
            content.append({"text": message.text})
        
        if message.tool_calls:
            tool_contents = [cls.convert_tool_call(tool) for tool in message.tool_calls]
            content.extend(tool_contents)

        if message.tool_results:
            tool_contents = [cls.convert_tool_result(tool) for tool in message.tool_results]
            content.extend(tool_contents)
        
        return {
            "role": message.role,
            "content": content
        }

    ##########################################################################
    # These are our base class implementations.
    ##########################################################################

    @classmethod
    def convert_messages(cls, messages: List[Message]) -> List[Dict[str, Any]]:
        return [cls.convert_message(msg) for msg in messages]
    
    @classmethod
    def convert_system(cls, system_prompt: str) -> Dict[str, Any]:
        return [{"text": system_prompt}]
    
    @classmethod
    def convert_tool_spec(cls, tools: List[ToolSpec], force_tool: Optional[str] = None) -> Dict[str, Any]:
        """
        Create tool configuration for Bedrock.

        force_tool forces the model to use a specific tool. This is useful for testing
        and or generating structured output.
        """

        # Iterate through tools and convert to Bedrock tool spec format.
        tools = [{
            "toolSpec": {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {"json": tool.model.model_json_schema()}
            }
        } for tool in tools]
        
        # Create tool config like we did in module 1 notebook 6.
        tool_config = {
            "tools": tools,
            "toolChoice": {"tool": {"name": force_tool}} if force_tool else {"auto": {}}
        }
            
        return tool_config

    
    @classmethod
    def convert_llm_request(cls, request: LLMRequest) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "modelId": request.model_id,
            "inferenceConfig": request.hyperparams,
            "system": cls.convert_system(request.system_prompt),
            "messages": cls.convert_messages(request.messages)
        }

        if request.tools:
            kwargs["toolConfig"] = cls.convert_tool_spec(
                tools=request.tools, 
                force_tool=request.force_tool
            )

        return kwargs