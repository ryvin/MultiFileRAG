#!/usr/bin/env python3
"""
Script to check if the deepseek-r1:32b model is properly installed and configured.
"""

import os
import sys
import json
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_ollama_status(ollama_host="http://localhost:11434"):
    """Check if Ollama is running and get its version."""
    try:
        response = requests.get(f"{ollama_host}/api/version")
        if response.status_code == 200:
            data = response.json()
            return True, data.get("version", "Unknown")
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_model_status(model_name, ollama_host="http://localhost:11434"):
    """Check if a model is available in Ollama."""
    try:
        response = requests.get(f"{ollama_host}/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            # Check if the model exists
            for model in models:
                if model.get("name") == model_name:
                    return True, model
            
            return False, "Model not found"
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_model_generation(model_name, ollama_host="http://localhost:11434"):
    """Test model generation with a simple prompt."""
    try:
        # Prepare the request
        data = {
            "model": model_name,
            "prompt": "Hello, can you tell me about yourself in one sentence?",
            "stream": False
        }
        
        # Send the request
        print(f"Testing {model_name} with a simple prompt...")
        start_time = time.time()
        
        response = requests.post(f"{ollama_host}/api/generate", json=data)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            return True, {
                "response": result.get("response", ""),
                "elapsed_time": elapsed_time
            }
        else:
            return False, f"Status code: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    """Main entry point."""
    # Get Ollama host from environment or use default
    ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")
    llm_model = os.getenv("LLM_MODEL", "deepseek-r1:32b")
    embedding_model = os.getenv("EMBEDDING_MODEL", "bge-m3")
    
    print(f"Checking Ollama status on {ollama_host}...")
    
    # Check Ollama status
    ollama_running, ollama_version = check_ollama_status(ollama_host)
    
    if ollama_running:
        print(f"✅ Ollama is running. Version: {ollama_version}")
    else:
        print(f"❌ Ollama is not running. Error: {ollama_version}")
        print("Please start Ollama with 'ollama serve' and try again.")
        return
    
    # Check LLM model status
    print(f"\nChecking LLM model: {llm_model}")
    llm_available, llm_info = check_model_status(llm_model, ollama_host)
    
    if llm_available:
        print(f"✅ LLM model {llm_model} is available.")
        print(f"   Model size: {llm_info.get('size', 'Unknown')}")
        print(f"   Modified: {llm_info.get('modified_at', 'Unknown')}")
        
        # Test model generation
        generation_success, generation_info = test_model_generation(llm_model, ollama_host)
        
        if generation_success:
            print(f"✅ Model generation test successful.")
            print(f"   Response time: {generation_info['elapsed_time']:.2f} seconds")
            print(f"   Response: {generation_info['response']}")
        else:
            print(f"❌ Model generation test failed. Error: {generation_info}")
    else:
        print(f"❌ LLM model {llm_model} is not available. Error: {llm_info}")
        print(f"   Try pulling the model with: ollama pull {llm_model}")
    
    # Check embedding model status
    print(f"\nChecking embedding model: {embedding_model}")
    embedding_available, embedding_info = check_model_status(embedding_model, ollama_host)
    
    if embedding_available:
        print(f"✅ Embedding model {embedding_model} is available.")
        print(f"   Model size: {embedding_info.get('size', 'Unknown')}")
        print(f"   Modified: {embedding_info.get('modified_at', 'Unknown')}")
    else:
        print(f"❌ Embedding model {embedding_model} is not available. Error: {embedding_info}")
        print(f"   Try pulling the model with: ollama pull {embedding_model}")
    
    # Print recommendations
    print("\n=== Recommendations ===")
    
    if llm_model == "deepseek-r1:32b":
        print("You are using deepseek-r1:32b, which is a large model that requires significant resources.")
        print("Recommendations for deepseek-r1:32b:")
        print("1. Increase the TIMEOUT setting in .env to at least 600 seconds")
        print("2. Set MAX_PARALLEL_INSERT=1 in .env to avoid resource contention")
        print("3. Process documents one at a time to avoid memory issues")
        print("4. Consider using a smaller model if you experience persistent timeouts")
    
    # Check current settings
    timeout = os.getenv("TIMEOUT", "200")
    max_parallel = os.getenv("MAX_PARALLEL_INSERT", "2")
    
    print(f"\nCurrent settings:")
    print(f"TIMEOUT={timeout}")
    print(f"MAX_PARALLEL_INSERT={max_parallel}")
    
    if int(timeout) < 600 and llm_model == "deepseek-r1:32b":
        print("⚠️ TIMEOUT is set too low for deepseek-r1:32b. Recommend increasing to at least 600.")
    
    if int(max_parallel) > 1 and llm_model == "deepseek-r1:32b":
        print("⚠️ MAX_PARALLEL_INSERT is set too high for deepseek-r1:32b. Recommend setting to 1.")

if __name__ == "__main__":
    main()
