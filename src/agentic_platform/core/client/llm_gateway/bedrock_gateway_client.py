import boto3
from botocore.auth import UNSIGNED_PAYLOAD
from botocore.config import Config
import botocore
import json
from typing import Dict, Any, Optional
import os
from functools import partial
from agentic_platform.core.models.llm_models import LLMResponse, LLMRequest
from agentic_platform.core.models.embedding_models import EmbedRequest, EmbedResponse
from agentic_platform.core.converter.llm_request_converters import ConverseRequestConverter
from agentic_platform.core.converter.llm_response_converters import ConverseResponseConverter
from agentic_platform.core.context.request_context import get_auth_token

# This is our internal DNS name for the LLM Gateway.
BEDROCK_GATEWAY_ENDPOINT = os.getenv('LLM_GATEWAY_ENDPOINT')

class BedrockGatewayClient:
    '''
    A client for interacting with Bedrock via the LLM Gateway.
    In non-local environments, we need to register a custom event with boto3 that will add the auth token to the request.
    In local environments, we use IAM credentials directly.
    '''
    def __init__(self, api_key: Optional[str] = None):
        '''
        Initialize the Bedrock Gateway Client.
        '''
        self.environment = os.getenv('ENVIRONMENT')
        
        # In local environment, use IAM credentials directly
        if self.environment == 'local':
            # Use default credentials and sign requests
            config = Config(retries={'max_attempts': 1})
            
            # For local development, we can use Bedrock directly
            self.client = boto3.client(
                'bedrock-runtime',
                config=config
            )
        else:
            # For non-local environments, use the gateway with auth tokens
            config = Config(
                retries={'max_attempts': 1},
                signature_version=botocore.UNSIGNED
            )
                
            self.client = boto3.client(
                'bedrock-runtime',
                endpoint_url=BEDROCK_GATEWAY_ENDPOINT,
                config=config
            )
            
            # Add API key header to requests using partial
            self.client.meta.events.register_first(
                'before-send.bedrock-runtime.Converse',
                partial(self._add_headers)
            )
            
            # Register for embedding API as well
            self.client.meta.events.register_first(
                'before-send.bedrock-runtime.InvokeModel',
                partial(self._add_headers)
            )

    def _add_headers(self, request, **kwargs):
        # Function to pass into our event register. We can pull the auth token from the context variable.
        # Only needed for non-local environments
        if self.environment != 'local':
            auth_token: str = get_auth_token()
            if auth_token:
                request.headers['Authorization'] = f"Bearer {auth_token}"

    def get_client(self):
        '''
        Useful for plumbing into open source frameworks. You can generally always set a client in their constructors.
        Since this is just a boto3 client, instantiate the bedrock gateway client and then you're good to go.
        '''
        return self.client

    def chat_invoke(self, request: LLMRequest) -> LLMResponse:
        '''
        This is the main single LLM call endpoint. It takes in our owned type and returns our owned type.
        We can alternatively treat it as passthrough to boto3 but it's generally a safer bet to own your own types.
        It's much easier to refactor this interface than it is to refactor your entire code base if APIs change, etc..
        '''
        kwargs: Dict[str, Any] = ConverseRequestConverter.convert_llm_request(request)
        converse_response: Dict[str, Any] = self.client.converse(**kwargs)
        return ConverseResponseConverter.to_llm_response(converse_response)
    
    def embed_invoke(self, request: EmbedRequest) -> EmbedResponse:
        '''
        Endpoint for generating embeddings using Bedrock embedding models.
        Takes an EmbedRequest and returns an EmbedResponse with the embedding vector.
        '''
        # Prepare the request body for the embedding model
        request_body = {
            "inputText": request.text
        }
        
        # Convert to JSON string for the InvokeModel API
        body = json.dumps(request_body)
        
        # Call the InvokeModel API with the embedding model
        response = self.client.invoke_model(
            modelId=request.model_id,
            body=body
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        embedding = response_body.get('embedding', [])
        
        # Return the embedding response
        return EmbedResponse(embedding=embedding)
