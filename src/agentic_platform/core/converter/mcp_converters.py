from typing import Dict, Any, Optional, List
from uuid import uuid4
from pydantic import BaseModel

# Import the models we need for conversions
from agentic_platform.core.models.memory_models import Message, TextContent, JsonContent


##############################################################################
# MCP Compatibility Types (for protocol conversion)
##############################################################################

class MCPRequest(BaseModel):
    """MCP JSON-RPC request format"""
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Dict[str, Any]

class MCPResponse(BaseModel):
    """MCP JSON-RPC response format"""
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


##############################################################################
# Conversion Utilities
##############################################################################

def agent_request_to_mcp(request) -> MCPRequest:
    """Convert AgenticRequest to MCP format
    
    Args:
        request: AgenticRequest instance
        
    Returns:
        MCPRequest in JSON-RPC format
    """
    return MCPRequest(
        id=str(uuid4()),
        method="tools/call",
        params={
            "name": "invoke_agent",
            "arguments": {
                "messages": [msg.dict() for msg in request.messages],
                "session_id": request.session_id,
                "context": request.context,
                "stream": request.stream,
                "include_thinking": request.include_thinking,
                "max_tokens": request.max_tokens
            }
        }
    )

def mcp_response_to_agent_response(mcp_response: MCPResponse, session_id: str):
    """Convert MCP response to AgenticResponse
    
    Args:
        mcp_response: MCPResponse instance
        session_id: Session ID for the response
        
    Returns:
        AgenticResponse instance
    """
    # Import here to avoid circular imports
    from agentic_platform.core.models.api_models import AgenticResponse
    
    if mcp_response.error:
        # Create error message
        error_message = Message(
            role="assistant",
            content=[TextContent(type="text", text=f"Error: {mcp_response.error.get('message', 'Unknown error')}")]
        )
        return AgenticResponse(
            message=error_message,
            session_id=session_id,
            metadata={"error": mcp_response.error}
        )
    
    result = mcp_response.result or {}
    
    # Convert MCP content to our Message format
    content_items = []
    for content_block in result.get("content", []):
        if content_block["type"] == "text":
            content_items.append(TextContent(type="text", text=content_block["text"]))
        elif content_block["type"] == "json":
            content_items.append(JsonContent(type="json", content=content_block["data"]))
        # Add more conversions as needed for other content types
    
    response_message = Message(
        role="assistant",
        content=content_items
    )
    
    return AgenticResponse(
        message=response_message,
        session_id=session_id,
        metadata=result.get("metadata", {})
    )


##############################################################################
# MCP Protocol Helpers
##############################################################################

def create_mcp_error_response(request_id: str, error_code: int, error_message: str) -> MCPResponse:
    """Create a standardized MCP error response"""
    return MCPResponse(
        id=request_id,
        error={
            "code": error_code,
            "message": error_message
        }
    )

def create_mcp_success_response(request_id: str, result: Dict[str, Any]) -> MCPResponse:
    """Create a standardized MCP success response"""
    return MCPResponse(
        id=request_id,
        result=result
    )

def validate_mcp_request(data: Dict[str, Any]) -> bool:
    """Validate that a dictionary conforms to MCP request format"""
    required_fields = ["jsonrpc", "id", "method"]
    return all(field in data for field in required_fields) and data.get("jsonrpc") == "2.0"

def validate_mcp_response(data: Dict[str, Any]) -> bool:
    """Validate that a dictionary conforms to MCP response format"""
    required_fields = ["jsonrpc", "id"]
    has_result_or_error = "result" in data or "error" in data
    return (all(field in data for field in required_fields) and 
            data.get("jsonrpc") == "2.0" and 
            has_result_or_error) 