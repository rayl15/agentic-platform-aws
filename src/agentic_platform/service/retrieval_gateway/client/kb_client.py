import os
import boto3
from typing import List, Dict, Any, Optional
from agentic_platform.core.models.vectordb_models import (
    VectorSearchRequest, 
    VectorSearchResponse, 
    VectorSearchResult,
    FilterCondition
)

knowledgebase_id = os.getenv("KNOWLEDGE_BASE_ID")

# Create boto3 client at module level
bedrock_client = boto3.client('bedrock-agent-runtime', region_name="us-west-2")

class BedrockKnowledgeBaseClient:
    """Client for Bedrock Knowledge Base search with built-in pagination."""
    
    @staticmethod
    def retrieve(request: VectorSearchRequest) -> VectorSearchResponse:
        """
        Perform a vector search with automatic pagination.
        Returns a single response with all results combined.
        """

        # Initial search
        kb_request = BedrockKnowledgeBaseClient._build_request(request)
        all_results = []
        next_token = None
        
        # Fetch results until we have enough or run out of pages
        while len(all_results) < request.limit:
            # Update token if we have one
            if next_token:
                kb_request["nextToken"] = next_token
            
            # Perform search
            response = bedrock_client.retrieve(**kb_request)
            
            # Extract and convert results
            results = response.get("retrievalResults", [])
            print(f"Results: {results}")
            for item in results:
                print(f"Item: {item}")
                all_results.append(BedrockKnowledgeBaseClient._convert_result(item))
                
                # Stop if we've reached the limit
                if len(all_results) >= request.limit:
                    break
            
            # Check for next page
            next_token = response.get("nextToken")
            if not next_token:
                break
        
        # Trim to requested limit
        all_results = all_results[:request.limit]

        print(f"All results: {all_results}")
        
        # Return final response
        return VectorSearchResponse(
            results=all_results,
            guardrail_action=response.get("guardrailAction")
        )
    
    @staticmethod
    def _build_request(request: VectorSearchRequest) -> Dict[str, Any]:
        """Build the Bedrock KB API request from our generic request."""
        kb_request = {
            "knowledgeBaseId": knowledgebase_id,
            "retrievalQuery": {
                "text": request.query
            }
        }
        
        # Add retrieval configuration
        retrieval_config = {}
        vector_search_config = {}
        
        # Set number of results (request a bit more to handle pagination)
        vector_search_config["numberOfResults"] = min(request.limit, 20)  # Bedrock page size limit
        
        # Convert filters if present
        if request.filters:
            filter_dict = BedrockKnowledgeBaseClient._convert_filters(request.filters)
            if filter_dict:
                vector_search_config["filter"] = filter_dict
        
        # Add search type if specified
        if request.search_type:
            vector_search_config["overrideSearchType"] = request.search_type
        
        # Add configurations to request
        if vector_search_config:
            retrieval_config["vectorSearchConfiguration"] = vector_search_config
        
        if retrieval_config:
            kb_request["retrievalConfiguration"] = retrieval_config
        
        # TODO: Implement guardrail configuration
        # if request.guardrail_id and request.guardrail_version:
        #     kb_request["guardrailConfiguration"] = {
        #         "guardrailId": request.guardrail_id,
        #         "guardrailVersion": request.guardrail_version
        #     }
        
        return kb_request
    
    @staticmethod
    def _convert_filters(filters: List[FilterCondition]) -> Dict[str, Any]:
        """Convert generic filters to Bedrock KB filter format."""
        if not filters:
            return {}
        
        # For multiple filters, use andAll
        if len(filters) > 1:
            filter_objects = []
            for f in filters:
                bedrock_op = BedrockKnowledgeBaseClient._map_operator(f.operator)
                filter_obj = {bedrock_op: {"key": f.field, "value": f.value}}
                filter_objects.append(filter_obj)
            return {"andAll": filter_objects}
        
        # For a single filter
        f = filters[0]
        bedrock_op = BedrockKnowledgeBaseClient._map_operator(f.operator)
        return {bedrock_op: {"key": f.field, "value": f.value}}
    
    @staticmethod
    def _map_operator(generic_op: str) -> str:
        """Map generic operators to Bedrock KB operators."""
        operator_map = {
            "eq": "equals",
            "neq": "notEquals",
            "gt": "greaterThan", 
            "gte": "greaterThanOrEquals",
            "lt": "lessThan",
            "lte": "lessThanOrEquals",
            "contains": "stringContains",
            "starts_with": "startsWith",
            "in": "in",
            "not_in": "notIn"
        }
        return operator_map.get(generic_op, generic_op)
    
    @staticmethod
    def _convert_result(item: Dict[str, Any]) -> VectorSearchResult:
        """Convert a single Bedrock KB result to generic result."""
        content = item.get("content", {})
        
        # Extract text content
        text = content.get("text", "")
        if not text and content.get("byteContent"):
            text = f"[Binary content]"
        elif not text and content.get("row"):
            text = " | ".join([f"{col.get('columnName')}: {col.get('columnValue')}" 
                              for col in content.get("row", [])])
        
        return VectorSearchResult(
            text=text,
            score=item.get("score", 0.0),
            metadata=item.get("metadata", {}),
            source_location=item.get("location", {}),
            content_type=content.get("type")
        )