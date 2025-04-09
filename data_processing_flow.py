#!/usr/bin/env python3
"""
Data Processing Flow for MultiFileRAG.

This module implements the data processing flow:

Document Ingestion:
1. Documents are chunked into manageable pieces
2. LLM extracts entities and relationships
3. Embedding model converts chunks to vectors
4. Data is stored in respective databases

Query Processing:
1. User query is analyzed to identify entities and keywords
2. Query is converted to vector representation
3. Vector similarity search finds relevant chunks
4. Graph traversal identifies related entities and relationships
5. Results from both approaches are combined and ranked

Answer Generation:
1. Retrieved context is formatted and sent to LLM
2. LLM generates response based on retrieved information
3. Results can be cached for similar future queries
"""

import os
import sys
import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
import configparser
from pathlib import Path
import time
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import hybrid cache
from hybrid_cache import HybridCache, HybridCacheStorage

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini", "utf-8")

class DocumentProcessor:
    """
    Document processor for MultiFileRAG.
    
    This class handles the document ingestion flow:
    1. Documents are chunked into manageable pieces
    2. LLM extracts entities and relationships
    3. Embedding model converts chunks to vectors
    4. Data is stored in respective databases
    """
    
    def __init__(self, rag_instance):
        """Initialize the document processor."""
        self.rag = rag_instance
        self.cache = HybridCache()
        self.processing_stages = [
            "chunking",
            "entity_extraction",
            "embedding_generation",
            "vector_storage",
            "graph_storage",
            "indexing"
        ]
    
    async def connect(self):
        """Connect to the cache."""
        await self.cache.connect()
    
    async def disconnect(self):
        """Disconnect from the cache."""
        await self.cache.disconnect()
    
    async def process_document(self, file_path: str) -> bool:
        """
        Process a document through the entire pipeline.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Generate a unique document ID
            doc_id = self._generate_document_id(file_path)
            
            # Record the start of processing
            await self._record_processing_stage(doc_id, "start", "in_progress")
            
            # Step 1: Chunking
            await self._record_processing_stage(doc_id, "chunking", "in_progress")
            chunks = await self.rag.chunk_document(file_path)
            if not chunks:
                await self._record_processing_stage(doc_id, "chunking", "failed", "No chunks generated")
                await self._record_processing_stage(doc_id, "overall", "failed", "Chunking failed")
                return False
            await self._record_processing_stage(doc_id, "chunking", "completed", metadata={"chunk_count": len(chunks)})
            
            # Step 2: Entity Extraction
            await self._record_processing_stage(doc_id, "entity_extraction", "in_progress")
            entities_by_chunk = {}
            relationships = []
            
            for i, chunk in enumerate(chunks):
                # Check cache first
                cached_entities = await self._get_cached_entity_extraction(chunk.text)
                
                if cached_entities:
                    entities_by_chunk[i] = cached_entities
                else:
                    # Extract entities using LLM
                    chunk_entities = await self.rag.extract_entities(chunk.text)
                    entities_by_chunk[i] = chunk_entities
                    
                    # Cache the results
                    await self._cache_entity_extraction(chunk.text, chunk_entities)
                
                # Extract relationships between entities
                if i > 0 and entities_by_chunk[i-1] and entities_by_chunk[i]:
                    chunk_relationships = await self.rag.extract_relationships(
                        entities_by_chunk[i-1], 
                        entities_by_chunk[i]
                    )
                    relationships.extend(chunk_relationships)
            
            await self._record_processing_stage(
                doc_id, 
                "entity_extraction", 
                "completed", 
                metadata={
                    "entity_count": sum(len(entities) for entities in entities_by_chunk.values()),
                    "relationship_count": len(relationships)
                }
            )
            
            # Step 3: Embedding Generation
            await self._record_processing_stage(doc_id, "embedding_generation", "in_progress")
            embeddings_by_chunk = {}
            
            for i, chunk in enumerate(chunks):
                # Check cache first
                cached_embedding = await self._get_cached_embedding(chunk.text)
                
                if cached_embedding is not None:
                    embeddings_by_chunk[i] = cached_embedding
                else:
                    # Generate embedding
                    embedding = await self.rag.generate_embedding(chunk.text)
                    embeddings_by_chunk[i] = embedding
                    
                    # Cache the embedding
                    await self._cache_embedding(chunk.text, embedding)
            
            await self._record_processing_stage(
                doc_id, 
                "embedding_generation", 
                "completed", 
                metadata={"embedding_count": len(embeddings_by_chunk)}
            )
            
            # Step 4: Vector Storage
            await self._record_processing_stage(doc_id, "vector_storage", "in_progress")
            vector_keys = []
            
            for i, chunk in enumerate(chunks):
                # Store in vector database
                key = f"{doc_id}:chunk:{i}"
                metadata = {
                    "document_id": doc_id,
                    "chunk_id": i,
                    "text": chunk.text,
                    "entities": entities_by_chunk.get(i, [])
                }
                
                success = await self.rag.store_vector(
                    key, 
                    embeddings_by_chunk[i], 
                    metadata
                )
                
                if success:
                    vector_keys.append(key)
            
            await self._record_processing_stage(
                doc_id, 
                "vector_storage", 
                "completed", 
                metadata={"vector_count": len(vector_keys)}
            )
            
            # Step 5: Graph Storage
            await self._record_processing_stage(doc_id, "graph_storage", "in_progress")
            
            # Create document node
            doc_node = {
                "id": doc_id,
                "label": "Document",
                "properties": {
                    "file_path": file_path,
                    "file_name": Path(file_path).name,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            await self.rag.store_graph_node(doc_node)
            
            # Create chunk nodes and connect to document
            chunk_nodes = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}:chunk:{i}"
                chunk_node = {
                    "id": chunk_id,
                    "label": "Chunk",
                    "properties": {
                        "document_id": doc_id,
                        "chunk_index": i,
                        "text": chunk.text[:1000],  # Store a preview of the text
                        "embedding_key": f"{doc_id}:chunk:{i}"
                    }
                }
                chunk_nodes.append(chunk_node)
                
                # Connect chunk to document
                await self.rag.store_graph_edge({
                    "source_id": doc_id,
                    "target_id": chunk_id,
                    "relation_type": "CONTAINS",
                    "properties": {
                        "chunk_index": i
                    }
                })
            
            # Store all chunk nodes
            for chunk_node in chunk_nodes:
                await self.rag.store_graph_node(chunk_node)
            
            # Store entity nodes and connect to chunks
            entity_nodes = {}
            for chunk_idx, entities in entities_by_chunk.items():
                chunk_id = f"{doc_id}:chunk:{chunk_idx}"
                
                for entity in entities:
                    entity_id = f"entity:{hashlib.md5(entity['name'].encode()).hexdigest()}"
                    
                    # Create entity node if it doesn't exist
                    if entity_id not in entity_nodes:
                        entity_node = {
                            "id": entity_id,
                            "label": entity.get("type", "Entity"),
                            "properties": {
                                "name": entity["name"],
                                "description": entity.get("description", ""),
                                "type": entity.get("type", "Entity")
                            }
                        }
                        entity_nodes[entity_id] = entity_node
                        await self.rag.store_graph_node(entity_node)
                    
                    # Connect entity to chunk
                    await self.rag.store_graph_edge({
                        "source_id": chunk_id,
                        "target_id": entity_id,
                        "relation_type": "MENTIONS",
                        "properties": {
                            "confidence": entity.get("confidence", 1.0)
                        }
                    })
            
            # Store relationships between entities
            for relationship in relationships:
                source_id = f"entity:{hashlib.md5(relationship['source'].encode()).hexdigest()}"
                target_id = f"entity:{hashlib.md5(relationship['target'].encode()).hexdigest()}"
                
                if source_id in entity_nodes and target_id in entity_nodes:
                    await self.rag.store_graph_edge({
                        "source_id": source_id,
                        "target_id": target_id,
                        "relation_type": relationship.get("type", "RELATED_TO"),
                        "properties": {
                            "description": relationship.get("description", ""),
                            "confidence": relationship.get("confidence", 1.0)
                        }
                    })
            
            await self._record_processing_stage(
                doc_id, 
                "graph_storage", 
                "completed", 
                metadata={
                    "entity_count": len(entity_nodes),
                    "relationship_count": len(relationships)
                }
            )
            
            # Step 6: Indexing
            await self._record_processing_stage(doc_id, "indexing", "in_progress")
            
            # Update document status
            await self.rag.update_document_status(
                doc_id,
                "processed",
                metadata={
                    "file_path": file_path,
                    "chunk_count": len(chunks),
                    "entity_count": len(entity_nodes),
                    "relationship_count": len(relationships),
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            await self._record_processing_stage(doc_id, "indexing", "completed")
            
            # Record overall completion
            await self._record_processing_stage(doc_id, "overall", "completed")
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            await self._record_processing_stage(doc_id, "overall", "failed", str(e))
            return False
    
    async def _record_processing_stage(self, doc_id: str, stage: str, status: str, error: str = None, metadata: Dict[str, Any] = None):
        """Record the status of a processing stage in PostgreSQL."""
        try:
            # This would typically use a direct database connection
            # For now, we'll use the cache to store the status
            key = f"processing:{doc_id}:{stage}"
            value = {
                "doc_id": doc_id,
                "stage": stage,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            if error:
                value["error"] = error
            
            if metadata:
                value["metadata"] = metadata
            
            await self.cache.set(key, json.dumps(value))
            
            logger.info(f"Document {doc_id}, stage {stage}: {status}")
            if error:
                logger.error(f"Document {doc_id}, stage {stage} error: {error}")
        
        except Exception as e:
            logger.error(f"Error recording processing stage: {e}")
    
    async def _get_cached_entity_extraction(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached entity extraction results."""
        key = f"entity:{hashlib.md5(text.encode()).hexdigest()}"
        value = await self.cache.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def _cache_entity_extraction(self, text: str, entities: List[Dict[str, Any]]) -> bool:
        """Cache entity extraction results."""
        key = f"entity:{hashlib.md5(text.encode()).hexdigest()}"
        return await self.cache.set(key, json.dumps(entities))
    
    async def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get a cached embedding."""
        key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
        value = await self.cache.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def _cache_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache an embedding."""
        key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
        return await self.cache.set(key, json.dumps(embedding))
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate a unique document ID based on the file path and modification time."""
        file_stat = os.stat(file_path)
        unique_string = f"{file_path}:{file_stat.st_mtime}"
        return f"doc:{hashlib.md5(unique_string.encode()).hexdigest()}"


class QueryProcessor:
    """
    Query processor for MultiFileRAG.
    
    This class handles the query processing flow:
    1. User query is analyzed to identify entities and keywords
    2. Query is converted to vector representation
    3. Vector similarity search finds relevant chunks
    4. Graph traversal identifies related entities and relationships
    5. Results from both approaches are combined and ranked
    """
    
    def __init__(self, rag_instance):
        """Initialize the query processor."""
        self.rag = rag_instance
        self.cache = HybridCache()
        self.cache_storage = HybridCacheStorage("query", {})
    
    async def connect(self):
        """Connect to the cache."""
        await self.cache.connect()
        await self.cache_storage.initialize()
    
    async def disconnect(self):
        """Disconnect from the cache."""
        await self.cache.disconnect()
        await self.cache_storage.finalize()
    
    async def process_query(self, query: str, mode: str = "hybrid") -> Dict[str, Any]:
        """
        Process a query through the entire pipeline.
        
        Args:
            query: The user's query
            mode: The query mode (hybrid, vector, graph, or direct)
            
        Returns:
            Dict: The query results
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cached_result = await self.cache_storage.get_query_result(query, mode)
            if cached_result:
                logger.info(f"Cache hit for query: {query}")
                result = json.loads(cached_result)
                result["cache_hit"] = True
                return result
            
            # Step 1: Analyze query to identify entities and keywords
            query_analysis = await self._analyze_query(query)
            
            # Step 2: Generate query embedding
            query_embedding = await self._get_query_embedding(query)
            
            # Step 3: Process query based on mode
            if mode == "vector" or mode == "hybrid":
                # Vector similarity search
                vector_results = await self._vector_search(query, query_embedding)
            else:
                vector_results = []
            
            if mode == "graph" or mode == "hybrid":
                # Graph traversal
                graph_results = await self._graph_search(query, query_analysis)
            else:
                graph_results = []
            
            if mode == "direct":
                # Direct LLM query without retrieval
                answer = await self.rag.generate_direct_answer(query)
                result = {
                    "query": query,
                    "mode": mode,
                    "answer": answer,
                    "sources": [],
                    "processing_time": time.time() - start_time
                }
            else:
                # Step 4: Combine and rank results
                combined_results = self._combine_results(vector_results, graph_results)
                
                # Step 5: Generate answer
                context = self._format_context(combined_results)
                answer = await self.rag.generate_answer(query, context)
                
                # Format the final result
                result = {
                    "query": query,
                    "mode": mode,
                    "answer": answer,
                    "sources": self._format_sources(combined_results),
                    "processing_time": time.time() - start_time,
                    "vector_results_count": len(vector_results),
                    "graph_results_count": len(graph_results)
                }
            
            # Cache the result
            await self.cache_storage.set_query_result(
                query, 
                mode, 
                json.dumps(result)
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "query": query,
                "mode": mode,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query to identify entities and keywords.
        
        Args:
            query: The user's query
            
        Returns:
            Dict: Analysis results including entities and keywords
        """
        # Check cache first
        cache_key = f"query_analysis:{hashlib.md5(query.encode()).hexdigest()}"
        cached_analysis = await self.cache.get(cache_key)
        
        if cached_analysis:
            return json.loads(cached_analysis)
        
        # Extract entities using LLM
        entities = await self.rag.extract_entities(query)
        
        # Extract keywords
        keywords = await self.rag.extract_keywords(query)
        
        analysis = {
            "entities": entities,
            "keywords": keywords
        }
        
        # Cache the analysis
        await self.cache.set(cache_key, json.dumps(analysis))
        
        return analysis
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """
        Generate an embedding for the query.
        
        Args:
            query: The user's query
            
        Returns:
            List[float]: The query embedding
        """
        # Check cache first
        cached_embedding = await self.cache_storage.get_embedding(query)
        
        if cached_embedding is not None:
            return cached_embedding
        
        # Generate embedding
        embedding = await self.rag.generate_embedding(query)
        
        # Cache the embedding
        await self.cache_storage.set_embedding(query, embedding)
        
        return embedding
    
    async def _vector_search(self, query: str, query_embedding: List[float]) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query: The user's query
            query_embedding: The query embedding
            
        Returns:
            List[Dict]: Vector search results
        """
        # Search vector database
        vector_results = await self.rag.search_vectors(query_embedding)
        
        return vector_results
    
    async def _graph_search(self, query: str, query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform graph traversal search.
        
        Args:
            query: The user's query
            query_analysis: The query analysis
            
        Returns:
            List[Dict]: Graph search results
        """
        graph_results = []
        
        # Search for entities in the graph
        for entity in query_analysis.get("entities", []):
            entity_results = await self.rag.search_graph_entities(entity["name"])
            graph_results.extend(entity_results)
        
        # Search for keywords in the graph
        for keyword in query_analysis.get("keywords", []):
            keyword_results = await self.rag.search_graph_keywords(keyword)
            graph_results.extend(keyword_results)
        
        return graph_results
    
    def _combine_results(self, vector_results: List[Dict[str, Any]], graph_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine and rank results from vector and graph searches.
        
        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            
        Returns:
            List[Dict]: Combined and ranked results
        """
        # Combine results
        combined = {}
        
        # Add vector results
        for result in vector_results:
            key = result.get("key", "")
            if key not in combined:
                combined[key] = {
                    "key": key,
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "vector_score": result.get("score", 0),
                    "graph_score": 0,
                    "combined_score": result.get("score", 0)
                }
        
        # Add graph results
        for result in graph_results:
            key = result.get("key", "")
            if key in combined:
                # Update existing result
                combined[key]["graph_score"] = result.get("score", 0)
                combined[key]["combined_score"] = (
                    combined[key]["vector_score"] + result.get("score", 0)
                ) / 2
            else:
                # Add new result
                combined[key] = {
                    "key": key,
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "vector_score": 0,
                    "graph_score": result.get("score", 0),
                    "combined_score": result.get("score", 0) / 2
                }
        
        # Convert to list and sort by combined score
        results = list(combined.values())
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return results[:10]  # Return top 10 results
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format the context for the LLM.
        
        Args:
            results: The combined search results
            
        Returns:
            str: Formatted context
        """
        context_parts = []
        
        for i, result in enumerate(results):
            context_parts.append(f"[{i+1}] {result['text']}")
        
        return "\n\n".join(context_parts)
    
    def _format_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format the sources for the response.
        
        Args:
            results: The combined search results
            
        Returns:
            List[Dict]: Formatted sources
        """
        sources = []
        
        for result in results:
            metadata = result.get("metadata", {})
            source = {
                "document_id": metadata.get("document_id", ""),
                "chunk_id": metadata.get("chunk_id", ""),
                "text_preview": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "score": result["combined_score"]
            }
            sources.append(source)
        
        return sources


class AnswerGenerator:
    """
    Answer generator for MultiFileRAG.
    
    This class handles the answer generation flow:
    1. Retrieved context is formatted and sent to LLM
    2. LLM generates response based on retrieved information
    3. Results can be cached for similar future queries
    """
    
    def __init__(self, rag_instance):
        """Initialize the answer generator."""
        self.rag = rag_instance
        self.cache_storage = HybridCacheStorage("answer", {})
    
    async def initialize(self):
        """Initialize the answer generator."""
        await self.cache_storage.initialize()
    
    async def finalize(self):
        """Finalize the answer generator."""
        await self.cache_storage.finalize()
    
    async def generate_answer(self, query: str, context: str, mode: str = "default") -> str:
        """
        Generate an answer based on the query and context.
        
        Args:
            query: The user's query
            context: The retrieved context
            mode: The generation mode
            
        Returns:
            str: The generated answer
        """
        # Create a cache key based on the query and context
        cache_key = f"answer:{hashlib.md5((query + context).encode()).hexdigest()}"
        
        # Check cache first
        cached_answer = await self.cache_storage.get_query_result(query, mode)
        if cached_answer:
            return cached_answer
        
        # Generate answer using LLM
        answer = await self.rag.generate_answer(query, context)
        
        # Cache the answer
        await self.cache_storage.set_query_result(query, mode, answer)
        
        return answer


# Main function to test the data processing flow
async def main():
    """Test the data processing flow."""
    # This would typically use the actual RAG instance
    # For now, we'll use a mock implementation
    from unittest.mock import MagicMock
    
    # Create a mock RAG instance
    rag = MagicMock()
    
    # Initialize the document processor
    doc_processor = DocumentProcessor(rag)
    await doc_processor.connect()
    
    # Process a document
    success = await doc_processor.process_document("test_document.pdf")
    print(f"Document processing {'succeeded' if success else 'failed'}")
    
    # Clean up
    await doc_processor.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
