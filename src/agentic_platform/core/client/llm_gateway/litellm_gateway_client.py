import requests
import json
import os
import httpx
from typing import Dict, Any, Optional, List, Generator, AsyncGenerator
from pydantic import BaseModel

from agentic_platform.core.models.llm_models import LLMResponse, LLMRequest, Usage
from agentic_platform.core.models.embedding_models import EmbedRequest, EmbedResponse
from agentic_platform.core.models.memory_models import Message, ToolCall, TextContent
from agentic_platform.core.context.request_context import get_auth_token
from agentic_platform.core.converter.litellm_converters import LiteLLMRequestConverter, LiteLLMResponseConverter
from agentic_platform.core.models.llm_models import LiteLLMClientInfo


# Default to localhost:4000 if not specified
LITELLM_API_ENDPOINT = os.getenv('LITELLM_API_ENDPOINT', 'http://localhost:4000')
LITELLM_API_KEY = os.getenv('LITELLM_KEY')


class LiteLLMGatewayClient:
    """
    A client for interacting with the LiteLLM API gateway.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LiteLLM Gateway Client.
        """
        self.api_endpoint = LITELLM_API_ENDPOINT
        self.api_key = api_key or LITELLM_API_KEY
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        # Try to get auth token from context, fall back to configured API key
        auth_token = self.api_key
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    
    def chat_invoke(self, request: LLMRequest) -> LLMResponse:
        """
        Send a chat completion request to the LiteLLM API.
        """
        # Convert the request to LiteLLM format
        payload = LiteLLMRequestConverter.convert_llm_request(request)
        
        # Make the API request
        response = requests.post(
            f"{self.api_endpoint}/v1/chat/completions",
            headers=self._get_headers(),
            json=payload
        )
        
        # Check for errors
        if response.status_code != 200:
            error_message = f"LiteLLM API error: {response.status_code} - {response.text}"
            raise Exception(error_message)
        
        # Parse the response
        litellm_response = response.json()
        
        # Convert to internal format
        return LiteLLMResponseConverter.to_llm_response(litellm_response)
    
    def chat_invoke_stream(self, request: LLMRequest) -> Generator[LLMResponse, None, None]:
        """
        Send a streaming chat completion request to the LiteLLM API.
        """
        # Convert the request to LiteLLM format and enable streaming
        payload = LiteLLMRequestConverter.convert_llm_request(request)
        payload["stream"] = True
        
        # Make the streaming API request
        response = requests.post(
            f"{self.api_endpoint}/v1/chat/completions",
            headers=self._get_headers(),
            json=payload,
            stream=True
        )
        
        # Check for errors
        if response.status_code != 200:
            error_message = f"LiteLLM API error: {response.status_code} - {response.text}"
            raise Exception(error_message)
        
        # Process streaming response
        accumulated_state = {}
        
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            
            # Parse the streaming line
            chunk_data = LiteLLMResponseConverter.parse_streaming_line(line)
            
            if not chunk_data or chunk_data.get("done"):
                continue
            
            # Process the chunk and yield response
            llm_response = LiteLLMResponseConverter.process_streaming_chunk(chunk_data, accumulated_state)
            yield llm_response
    
    async def chat_invoke_stream_async(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:
        """
        Send an async streaming chat completion request to the LiteLLM API.
        """
        # Convert the request to LiteLLM format and enable streaming
        payload = LiteLLMRequestConverter.convert_llm_request(request)
        payload["stream"] = True
        
        # Make the async streaming API request
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.api_endpoint}/v1/chat/completions",
                headers=self._get_headers(),
                json=payload
            ) as response:
                
                # Check for errors
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_message = f"LiteLLM API error: {response.status_code} - {error_text.decode()}"
                    raise Exception(error_message)
                
                # Process streaming response
                accumulated_state = {}
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    # Parse the streaming line
                    chunk_data = LiteLLMResponseConverter.parse_streaming_line(line)
                    
                    if not chunk_data or chunk_data.get("done"):
                        continue
                    
                    # Process the chunk and yield response
                    llm_response = LiteLLMResponseConverter.process_streaming_chunk(chunk_data, accumulated_state)
                    yield llm_response
    
    def embed_invoke(self, request: EmbedRequest) -> EmbedResponse:
        """
        Send an embedding request to the LiteLLM API.
        """
        # Prepare the request payload
        payload = {
            "model": request.model_id,
            "input": request.text
        }
        
        # Make the API request
        response = requests.post(
            f"{self.api_endpoint}/v1/embeddings",
            headers=self._get_headers(),
            json=payload
        )
        
        # Check for errors
        if response.status_code != 200:
            error_message = f"LiteLLM API error: {response.status_code} - {response.text}"
            raise Exception(error_message)
        
        # Parse the response
        litellm_response = response.json()
        
        # Extract the embedding
        embedding = []
        if "data" in litellm_response and litellm_response["data"]:
            embedding = litellm_response["data"][0].get("embedding", [])
        
        # Return the embedding response
        return EmbedResponse(embedding=embedding)
    
    def get_client(self) -> LiteLLMClientInfo:
        """
        Return a simple client object that can be used with other libraries.
        This is a placeholder since LiteLLM doesn't have a direct client library like boto3.
        """
        # Return a simple object with the API endpoint and headers

        return LiteLLMClientInfo(
            api_key=self.api_key,
            api_endpoint=f"{self.api_endpoint}/v1"
        )
