#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get model settings
llm_model = os.getenv("LLM_MODEL", "llama3")
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
embedding_dim = os.getenv("EMBEDDING_DIM", "768")

print(f"LLM Model: {llm_model}")
print(f"Embedding Model: {embedding_model}")
print(f"Embedding Dimension: {embedding_dim}")
