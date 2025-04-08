#!/usr/bin/env python3
"""
Script to check if entities from resume documents were extracted and added to the knowledge graph.
"""

import os
import sys
import json
import requests
from pathlib import Path

def check_graph_for_entities(entities, server_url="http://localhost:9621"):
    """Check if specific entities exist in the knowledge graph."""
    found_entities = []
    
    for entity in entities:
        try:
            # Try to get the knowledge graph for this entity
            response = requests.get(f"{server_url}/graphs?label={entity}", timeout=30)
            
            if response.status_code != 200:
                print(f"Error querying for entity '{entity}': Status code {response.status_code}")
                continue
            
            data = response.json()
            nodes = data.get("nodes", [])
            
            # Check if the entity exists as a node
            entity_nodes = [node for node in nodes if entity.lower() in node.get("id", "").lower()]
            
            if entity_nodes:
                print(f"✅ Entity '{entity}' found in the knowledge graph")
                found_entities.append(entity)
                
                # Print some details about the entity
                for node in entity_nodes:
                    node_id = node.get("id", "Unknown")
                    labels = node.get("labels", [])
                    properties = node.get("properties", {})
                    
                    print(f"   ID: {node_id}")
                    print(f"   Labels: {labels}")
                    print(f"   Properties: {properties}")
                    
                    # Check for connected edges
                    edges = data.get("edges", [])
                    connected_edges = [
                        edge for edge in edges 
                        if edge.get("source") == node_id or edge.get("target") == node_id
                    ]
                    
                    if connected_edges:
                        print(f"   Connected to {len(connected_edges)} other entities:")
                        for i, edge in enumerate(connected_edges[:5]):  # Show up to 5 connections
                            source = edge.get("source")
                            target = edge.get("target")
                            edge_type = edge.get("type")
                            
                            if source == node_id:
                                print(f"     {i+1}. {node_id} --[{edge_type}]--> {target}")
                            else:
                                print(f"     {i+1}. {source} --[{edge_type}]--> {node_id}")
                        
                        if len(connected_edges) > 5:
                            print(f"     ... and {len(connected_edges) - 5} more connections")
            else:
                print(f"❌ Entity '{entity}' not found in the knowledge graph")
        
        except Exception as e:
            print(f"Error checking entity '{entity}': {str(e)}")
    
    return found_entities

def query_for_resume_info(server_url="http://localhost:9621"):
    """Query the system for resume-related information."""
    try:
        # Create a query about Raul Pineda's resume
        query = "What information is available about Raul Pineda's resume, including his education, experience, and skills?"
        
        print(f"Querying: '{query}'")
        response = requests.post(
            f"{server_url}/query", 
            json={"query": query, "mode": "hybrid"},
            timeout=60  # Longer timeout for complex query
        )
        
        if response.status_code != 200:
            print(f"Error: Failed to query. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = response.json()
        response_text = result.get("response", "")
        
        # Print the response
        print("\nResponse:")
        print(response_text)
        
        # Analyze the response
        if "no information" in response_text.lower() or "i don't have" in response_text.lower():
            print("\nAnalysis: The system does not have information about Raul Pineda's resume")
        elif len(response_text) < 100:
            print("\nAnalysis: The response is very short, suggesting limited information")
        else:
            print("\nAnalysis: The system has some information about Raul Pineda's resume")
    
    except Exception as e:
        print(f"Error querying for resume information: {str(e)}")

def main():
    """Main entry point."""
    server_url = "http://localhost:9621"
    
    print("=== Resume Entity Check ===\n")
    
    # Define entities that should be in the knowledge graph if resumes were processed
    resume_entities = [
        "Raul Pineda",
        "Resume",
        "Education",
        "Experience",
        "Skills",
        "University",
        "Bachelor",
        "Master",
        "Software Engineer",
        "Developer"
    ]
    
    # Check if these entities exist in the knowledge graph
    print("Checking for resume-related entities in the knowledge graph...")
    found_entities = check_graph_for_entities(resume_entities, server_url)
    
    # Query for resume information
    print("\nQuerying for resume information...")
    query_for_resume_info(server_url)
    
    # Print recommendations
    print("\n=== Recommendations ===")
    if not found_entities:
        print("1. The knowledge graph does not contain resume-related entities")
        print("2. This suggests that entity extraction failed for the resume documents")
        print("3. Try the following:")
        print("   a. Reprocess the resume documents")
        print("   b. Use a different LLM model that might be better at entity extraction")
        print("   c. Check if the resume documents are in a format that can be properly processed")
    elif len(found_entities) < len(resume_entities) / 2:
        print("1. The knowledge graph contains some resume-related entities, but not many")
        print("2. Entity extraction might be partially working")
        print("3. Try reprocessing the documents with improved settings")
    else:
        print("1. The knowledge graph contains several resume-related entities")
        print("2. If information is still missing in queries, the issue might be with:")
        print("   a. The query processing")
        print("   b. The relationships between entities")
        print("   c. The way the LLM is using the knowledge graph for responses")

if __name__ == "__main__":
    main()
