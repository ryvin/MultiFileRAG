#!/usr/bin/env python3
"""
Script to check the knowledge graph API and diagnose issues.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_graph_api(server_url="http://localhost:9621", label="*"):
    """Check the knowledge graph API endpoint."""
    try:
        # Get knowledge graph endpoint
        response = requests.get(f"{server_url}/graphs?label={label}")
        if response.status_code != 200:
            print(f"Error: Failed to get knowledge graph. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        # Parse the response
        data = response.json()
        return data
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def analyze_graph(graph_data):
    """Analyze the knowledge graph data."""
    if not graph_data:
        print("No graph data available.")
        return

    # Check if the graph has nodes and edges
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    print(f"Graph contains {len(nodes)} nodes and {len(edges)} edges.")

    if len(nodes) == 0:
        print("WARNING: The graph has no nodes. This indicates that entity extraction failed.")
        print("Possible causes:")
        print("1. The LLM model (deepseek-r1) failed to extract entities from the documents")
        print("2. The documents don't contain recognizable entities")
        print("3. The entity extraction process timed out")
        return

    if len(edges) == 0 and len(nodes) > 0:
        print("WARNING: The graph has nodes but no edges.")
        print("This indicates that entity extraction worked but relationship extraction failed.")
        print("Possible causes:")
        print("1. The LLM model failed to identify relationships between entities")
        print("2. The documents don't contain clear relationships between entities")
        print("3. The relationship extraction process timed out")
        return

    # If we have both nodes and edges, print some sample data
    print("\nSample nodes:")
    for i, node in enumerate(nodes[:5]):
        print(f"  Node {i+1}: ID={node.get('id')}, Labels={node.get('labels')}")

    if len(nodes) > 5:
        print(f"  ... and {len(nodes) - 5} more nodes")

    print("\nSample edges:")
    for i, edge in enumerate(edges[:5]):
        print(f"  Edge {i+1}: {edge.get('source')} --[{edge.get('type')}]--> {edge.get('target')}")

    if len(edges) > 5:
        print(f"  ... and {len(edges) - 5} more edges")

def main():
    """Main entry point."""
    # Always use localhost for testing
    server_url = "http://localhost:9621"

    print(f"Checking knowledge graph API on {server_url}...")

    # Try different labels to get the knowledge graph
    labels = ["*", "account", "statement", "transaction", "bank"]

    for label in labels:
        print(f"\nTrying label: '{label}'")
        graph_data = check_graph_api(server_url, label)

        if graph_data:
            analyze_graph(graph_data)

            # If we found a non-empty graph, break the loop
            if graph_data.get("nodes") and len(graph_data.get("nodes")) > 0:
                break

    # Check if the graph file exists
    graph_file = os.path.join("rag_storage", "graph_chunk_entity_relation.graphml")
    if os.path.exists(graph_file):
        file_size = os.path.getsize(graph_file)
        print(f"\nGraph file exists: {graph_file}")
        print(f"File size: {file_size} bytes")

        if file_size == 0:
            print("WARNING: Graph file is empty. No entities or relationships were extracted.")
        elif file_size < 1000:
            print("WARNING: Graph file is very small. Few entities or relationships were extracted.")
    else:
        print(f"\nWARNING: Graph file does not exist: {graph_file}")
        print("This indicates that no entities or relationships were extracted.")

if __name__ == "__main__":
    main()
