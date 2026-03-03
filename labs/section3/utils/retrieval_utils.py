import os
import chromadb
import boto3
from pydantic import BaseModel
from typing import List, Dict
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction


# Resolve the chroma data path relative to this file's location.
# This file lives at labs/section3/utils/retrieval_utils.py
# The chroma data is at labs/data/chroma (i.e., ../../data/chroma from the notebook dirs,
# which is ../data/chroma from the section3/ directory).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CHROMA_PATH = os.path.join(_THIS_DIR, "..", "..", "data", "chroma")

# Initialize Chroma client from our persisted store
chroma_client = chromadb.PersistentClient(path=_CHROMA_PATH)

# Initialize the Bedrock client
session = boto3.Session()


class RetrievalResult(BaseModel):
    id: str
    document: str
    embedding: List[float]
    distance: float
    metadata: Dict = {}


class ChromaDBRetrievalClient:

    def __init__(self, chroma_client, collection_name: str, embedding_function: AmazonBedrockEmbeddingFunction):
        self.client = chroma_client
        self.collection_name = collection_name
        self.embedding_function = embedding_function

        # Create the collection
        self.collection = self._create_collection()

    def _create_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    def retrieve(self, query_text: str, n_results: int = 5) -> List[RetrievalResult]:
        # Query the collection
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['embeddings', 'documents', 'metadatas', 'distances']
        )

        # Transform the results into RetrievalResult objects
        retrieval_results = []
        for i in range(len(results['ids'][0])):
            retrieval_results.append(RetrievalResult(
                id=results['ids'][0][i],
                document=results['documents'][0][i],
                embedding=results['embeddings'][0][i],
                distance=results['distances'][0][i],
                metadata=results['metadatas'][0][i] if results['metadatas'][0] else {}
            ))

        return retrieval_results


def get_chroma_os_docs_collection() -> ChromaDBRetrievalClient:
    """Create and return a ChromaDBRetrievalClient for the opensearch-docs-rag collection."""
    EMBEDDING_MODEL_ID: str = 'amazon.titan-embed-text-v2:0'
    COLLECTION_NAME: str = 'opensearch-docs-rag'

    embedding_function = AmazonBedrockEmbeddingFunction(
        session=session,
        model_name=EMBEDDING_MODEL_ID
    )

    chroma_os_docs_collection: ChromaDBRetrievalClient = ChromaDBRetrievalClient(
        chroma_client=chroma_client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function
    )

    return chroma_os_docs_collection
