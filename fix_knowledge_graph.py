#!/usr/bin/env python3
"""
Script to fix knowledge graph issues in MultiFileRAG.
This script will:
1. Check if the knowledge graph file exists and has content
2. Verify that the graph API is working
3. Provide recommendations for fixing visualization issues
"""

import os
import sys
import json
import requests
import time
import subprocess
from pathlib import Path

def check_graph_file():
    """Check if the knowledge graph file exists and has content."""
    graph_file = os.path.join("rag_storage", "graph_chunk_entity_relation.graphml")
    if os.path.exists(graph_file):
        file_size = os.path.getsize(graph_file)
        print(f"Graph file exists: {graph_file}")
        print(f"File size: {file_size} bytes")
        
        if file_size == 0:
            print("WARNING: Graph file is empty. No entities or relationships were extracted.")
            return False
        elif file_size < 1000:
            print("WARNING: Graph file is very small. Few entities or relationships were extracted.")
            return True
        else:
            print("Graph file has sufficient content.")
            return True
    else:
        print(f"WARNING: Graph file does not exist: {graph_file}")
        print("This indicates that no entities or relationships were extracted.")
        return False

def check_graph_api(server_url="http://localhost:9621", label="*"):
    """Check the knowledge graph API endpoint."""
    try:
        # Get knowledge graph endpoint
        response = requests.get(f"{server_url}/graphs?label={label}", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to get knowledge graph. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # Parse the response
        data = response.json()
        return data
    except Exception as e:
        print(f"Error accessing graph API: {str(e)}")
        return None

def analyze_graph(graph_data):
    """Analyze the knowledge graph data."""
    if not graph_data:
        print("No graph data available from API.")
        return False
    
    # Check if the graph has nodes and edges
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    print(f"Graph API returns {len(nodes)} nodes and {len(edges)} edges.")
    
    if len(nodes) == 0:
        print("WARNING: The graph has no nodes. This indicates that entity extraction failed.")
        return False
    
    if len(edges) == 0 and len(nodes) > 0:
        print("WARNING: The graph has nodes but no edges.")
        print("This indicates that entity extraction worked but relationship extraction failed.")
        return True
    
    # If we have both nodes and edges, the graph is valid
    return True

def restart_server():
    """Restart the MultiFileRAG server."""
    print("Restarting the MultiFileRAG server...")
    
    # Check if there's a restart script
    if os.path.exists("restart_server.bat"):
        subprocess.run(["restart_server.bat"], shell=True)
    else:
        # Try to find the server process and kill it
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq MultiFileRAG Server"], shell=True)
            else:  # Linux/Mac
                subprocess.run(["pkill", "-f", "multifilerag_server.py"], shell=True)
            
            # Wait for the process to terminate
            time.sleep(5)
            
            # Start the server again
            if os.path.exists("multifilerag_server.py"):
                subprocess.Popen(["python", "multifilerag_server.py"], shell=True)
                print("Server restarted.")
            else:
                print("Could not find multifilerag_server.py. Please restart the server manually.")
        except Exception as e:
            print(f"Error restarting server: {str(e)}")
            print("Please restart the server manually.")

def clear_browser_cache():
    """Provide instructions for clearing browser cache."""
    print("\nTo clear your browser cache:")
    print("1. Chrome: Press Ctrl+Shift+Delete, select 'Cached images and files', and click 'Clear data'")
    print("2. Firefox: Press Ctrl+Shift+Delete, select 'Cache', and click 'Clear Now'")
    print("3. Edge: Press Ctrl+Shift+Delete, select 'Cached images and files', and click 'Clear'")
    print("4. Safari: Press Option+Command+E")
    print("\nAfter clearing cache, refresh the page (F5 or Ctrl+R)")

def fix_knowledge_graph():
    """Fix knowledge graph issues."""
    print("=== Knowledge Graph Diagnostic Tool ===\n")
    
    # Step 1: Check if the graph file exists and has content
    graph_file_ok = check_graph_file()
    
    if not graph_file_ok:
        print("\nRecommendation: Reprocess your documents to generate the knowledge graph.")
        print("Run: python reprocess_docs.py")
        return
    
    # Step 2: Check if the graph API is working
    print("\nChecking graph API...")
    graph_data = check_graph_api()
    graph_api_ok = analyze_graph(graph_data)
    
    if not graph_api_ok:
        print("\nRecommendation: There may be an issue with the graph API.")
        restart = input("Would you like to restart the server? (y/n): ")
        if restart.lower() == 'y':
            restart_server()
        return
    
    # Step 3: If both checks pass but the graph is not visible in the UI
    print("\nThe knowledge graph file exists and the API is working correctly.")
    print("If you're not seeing the graph in the web UI, try the following:")
    
    print("\n1. Make sure you're on the Graph tab in the web UI")
    print("2. Try different search terms in the graph search box (e.g., '*', 'account', 'bank')")
    print("3. Clear your browser cache and refresh the page")
    
    clear_cache = input("\nWould you like instructions for clearing your browser cache? (y/n): ")
    if clear_cache.lower() == 'y':
        clear_browser_cache()
    
    restart = input("\nWould you like to restart the server? (y/n): ")
    if restart.lower() == 'y':
        restart_server()

if __name__ == "__main__":
    fix_knowledge_graph()
