from pydantic import BaseModel
from typing import List, Dict
from chromadb.api.types import EmbeddingFunction
from typing import List, Dict, Any
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

import chromadb
import boto3
from chromadb.config import Settings

# Initialize Chroma client from our persisted store
chroma_client = chromadb.PersistentClient(path="../../data/chroma")

# Initialize the Bedrock client
session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime')

print("✅ Client setup complete!")


class RetrievalResult(BaseModel):
    id: str
    document: str
    embedding: List[float]
    distance: float
    metadata: Dict = {}


# Example of a concrete implementation
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
    # Define some experiment variables
    EMBEDDING_MODEL_ID: str = 'amazon.titan-embed-text-v2:0'
    COLLECTION_NAME: str = 'opensearch-docs-rag'

    # This is a handy function Chroma implemented for calling bedrock. Lets use it!
    embedding_function = AmazonBedrockEmbeddingFunction(
        session=session,
        model_name=EMBEDDING_MODEL_ID
    )

    # Create our retrieval task. All retrieval tasks in this tutorial implement BaseRetrievalTask which has the method retrieve()
    # If you'd like to extend this to a different retrieval configuration, all you have to do is create a class that that implements
    # this abstract class and the rest is the same!
    chroma_os_docs_collection: ChromaDBRetrievalClient = ChromaDBRetrievalClient(
        chroma_client = chroma_client, 
        collection_name = COLLECTION_NAME,
        embedding_function = embedding_function
    )

    return chroma_os_docs_collection