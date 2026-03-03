#!/usr/bin/env python3
"""Setup ChromaDB with OpenSearch documentation for the workflow labs."""

import chromadb
import boto3
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from concurrent.futures import ThreadPoolExecutor, as_completed

print("🚀 Setting up ChromaDB with OpenSearch documentation...")
print()

# Setup clients
chroma_client = chromadb.PersistentClient(path="../../data/chroma")
session = boto3.Session()

EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name=EMBEDDING_MODEL_ID)

# Create collection
collection = chroma_client.get_or_create_collection(name="opensearch-docs-rag", embedding_function=embedding_function)

if collection.count() > 0:
    print(f"✅ Collection already exists with {collection.count()} chunks")
    exit(0)

# Load and chunk documents
print("📄 Loading OpenSearch documentation...")
docs = SimpleDirectoryReader(input_dir="../../data/opensearch-docs", recursive=True, required_exts=[".md"]).load_data()
print(f"   Loaded {len(docs)} documents")

# Chunk
print("✂️  Chunking documents...")
pipeline = IngestionPipeline(transformations=[SentenceSplitter(chunk_size=2048, chunk_overlap=128)])
nodes = pipeline.run(documents=docs)
print(f"   Created {len(nodes)} chunks")

# Add to ChromaDB in batches
print("📦 Indexing into ChromaDB (this takes ~2 minutes)...")

def add_batch(batch):
    collection.add(
        ids=[n.node_id for n in batch],
        documents=[n.text for n in batch],
        metadatas=[{"file": n.metadata.get("file_path", "")} for n in batch]
    )

batch_size = 20
batches = [nodes[i:i+batch_size] for i in range(0, len(nodes), batch_size)]

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(add_batch, b) for b in batches]
    for i, f in enumerate(as_completed(futures)):
        if (i+1) % 25 == 0:
            print(f"   Progress: {i+1}/{len(batches)} batches")
        f.result()

print()
print(f"✅ Done! Indexed {collection.count()} chunks into ChromaDB")
