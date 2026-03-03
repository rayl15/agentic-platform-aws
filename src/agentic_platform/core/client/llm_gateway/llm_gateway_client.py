
from agentic_platform.core.models.llm_models import LLMRequest, LLMResponse
from agentic_platform.core.models.embedding_models import EmbedRequest, EmbedResponse
from agentic_platform.core.client.llm_gateway.bedrock_gateway_client import BedrockGatewayClient
from agentic_platform.core.client.llm_gateway.litellm_gateway_client import LiteLLMGatewayClient, LiteLLMClientInfo
# from openai import AsyncOpenAI
from typing import Any, Dict
from pydantic import BaseModel


# br_client = BedrockGatewayClient()
litellm_client = LiteLLMGatewayClient()



class LLMGatewayClient:
    '''Placeholder class for wherever you want to send your requests.'''
    @staticmethod
    def chat_invoke(request: LLMRequest) -> LLMResponse:
        return litellm_client.chat_invoke(request=request)
    
    @staticmethod
    def embed_invoke(request: EmbedRequest) -> EmbedResponse:
        return litellm_client.embed_invoke(request=request)

    @staticmethod
    def get_client_info() -> LiteLLMClientInfo:
        return litellm_client.get_client()
