#!/usr/bin/env python3
"""
Script to monitor document processing performance in the MultiFileRAG system.
This script continuously checks the pipeline status and document counts.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_pipeline_status(server_url="http://localhost:9621"):
    """Get the current pipeline status from the server."""
    try:
        response = requests.get(f"{server_url}/documents/pipeline_status")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

def get_document_counts(server_url="http://localhost:9621"):
    """Get document counts by status."""
    try:
        response = requests.get(f"{server_url}/documents")
        if response.status_code == 200:
            data = response.json()
            counts = {
                "PENDING": len(data.get("statuses", {}).get("PENDING", [])),
                "PROCESSING": len(data.get("statuses", {}).get("PROCESSING", [])),
                "PROCESSED": len(data.get("statuses", {}).get("PROCESSED", [])),
                "FAILED": len(data.get("statuses", {}).get("FAILED", []))
            }
            counts["TOTAL"] = sum(counts.values())
            return counts
        else:
            return {"error": f"Status code: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

def monitor_processing(interval=10, server_url="http://localhost:9621"):
    """Monitor document processing with periodic updates."""
    try:
        print(f"Monitoring document processing on {server_url}")
        print(f"Press Ctrl+C to stop monitoring")
        print("-" * 80)
        
        while True:
            # Get current time
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get pipeline status
            status = get_pipeline_status(server_url)
            
            # Get document counts
            counts = get_document_counts(server_url)
            
            # Print status
            print(f"\n[{now}] Pipeline Status:")
            
            if "error" in status:
                print(f"  Error: {status['error']}")
            else:
                busy = status.get("busy", False)
                job_name = status.get("job_name", "N/A")
                latest_message = status.get("latest_message", "N/A")
                
                print(f"  Busy: {busy}")
                print(f"  Job: {job_name}")
                print(f"  Latest Message: {latest_message}")
            
            # Print document counts
            print(f"\n[{now}] Document Counts:")
            
            if "error" in counts:
                print(f"  Error: {counts['error']}")
            else:
                print(f"  PENDING:    {counts.get('PENDING', 0)}")
                print(f"  PROCESSING: {counts.get('PROCESSING', 0)}")
                print(f"  PROCESSED:  {counts.get('PROCESSED', 0)}")
                print(f"  FAILED:     {counts.get('FAILED', 0)}")
                print(f"  TOTAL:      {counts.get('TOTAL', 0)}")
            
            print("-" * 80)
            
            # Wait for the next update
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Get interval from command line argument or use default
    interval = 10
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}. Using default: 10 seconds.")
    
    # Get server URL from environment or use default
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "9621")
    server_url = f"http://{host}:{port}"
    
    # Start monitoring
    monitor_processing(interval, server_url)
