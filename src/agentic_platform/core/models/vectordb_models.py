from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

class FilterCondition(BaseModel):
    """Represents a filter condition for vector search queries."""
    field: str = Field(..., description="Field name to filter on")
    operator: str = Field(..., description="Operator (eq, gt, lt, etc.)")
    value: Any = Field(..., description="Value to compare against")

class VectorSearchRequest(BaseModel):
    """Generic vector search request for vector databases."""
    model_config = ConfigDict(extra="allow")
    
    query: str = Field(..., description="Search query text")
    filters: Optional[List[FilterCondition]] = Field(None, description="Filters to apply")
    limit: int = Field(10, description="Maximum number of results to return")
    search_type: Optional[str] = Field(None, description="Search type: HYBRID or SEMANTIC (Bedrock specific)")

class VectorSearchResult(BaseModel):
    """Represents a single result from vector search."""
    text: str = Field(..., description="Result text content")
    score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    source_location: Optional[Dict[str, Any]] = Field(None, description="Source information")
    content_type: Optional[str] = Field(None, description="Content type")

class VectorSearchResponse(BaseModel):
    """Response from vector search."""
    results: List[VectorSearchResult] = Field(..., description="Search results")
    guardrail_action: Optional[str] = Field(None, description="Guardrail action if any")