#!/usr/bin/env python3
"""
Script to check if Ollama is using GPU acceleration and provide recommendations.
"""

import os
import sys
import json
import requests
import subprocess
import platform
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

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available and get its information."""
    try:
        # Check if nvidia-smi is available
        if platform.system() == "Windows":
            result = subprocess.run(["where", "nvidia-smi"], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "NVIDIA System Management Interface (nvidia-smi) not found."
        else:
            result = subprocess.run(["which", "nvidia-smi"], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "NVIDIA System Management Interface (nvidia-smi) not found."
        
        # Run nvidia-smi to get GPU information
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version,cuda_version", "--format=csv,noheader"], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, f"Failed to run nvidia-smi: {result.stderr}"
        
        # Parse the output
        gpu_info = result.stdout.strip().split(',')
        if len(gpu_info) >= 3:
            return True, {
                "name": gpu_info[0].strip(),
                "memory": gpu_info[1].strip(),
                "driver_version": gpu_info[2].strip(),
                "cuda_version": gpu_info[3].strip() if len(gpu_info) > 3 else "Unknown"
            }
        else:
            return False, f"Unexpected output from nvidia-smi: {result.stdout}"
    except Exception as e:
        return False, str(e)

def check_ollama_gpu_usage(ollama_host="http://localhost:11434"):
    """Check if Ollama is using GPU acceleration."""
    try:
        # Get Ollama version
        response = requests.get(f"{ollama_host}/api/version")
        if response.status_code != 200:
            return False, f"Failed to get Ollama version. Status code: {response.status_code}"
        
        # Check if GPU is mentioned in the response
        data = response.json()
        if "cuda" in data.get("version", "").lower() or "gpu" in data.get("version", "").lower():
            return True, "GPU support detected in Ollama version string."
        
        # Try to get model list to check for GPU usage
        response = requests.get(f"{ollama_host}/api/tags")
        if response.status_code != 200:
            return False, f"Failed to get model list. Status code: {response.status_code}"
        
        # Check if any model is using GPU
        data = response.json()
        models = data.get("models", [])
        
        for model in models:
            if "gpu" in model.get("details", {}).get("runtime", "").lower() or "cuda" in model.get("details", {}).get("runtime", "").lower():
                return True, f"GPU usage detected for model: {model.get('name')}"
        
        # If we couldn't determine from the API, assume it's not using GPU
        return False, "No explicit GPU usage detected in Ollama API responses."
    except Exception as e:
        return False, str(e)

def main():
    """Main entry point."""
    # Get Ollama host from environment or use default
    ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")
    llm_model = os.getenv("LLM_MODEL", "deepseek-r1:32b")
    
    print("=== GPU Usage Check for Ollama ===\n")
    
    # Check Ollama status
    ollama_running, ollama_version = check_ollama_status(ollama_host)
    
    if not ollama_running:
        print(f"❌ Ollama is not running. Error: {ollama_version}")
        print("Please start Ollama with 'ollama serve' and try again.")
        return
    
    print(f"✅ Ollama is running. Version: {ollama_version}")
    
    # Check NVIDIA GPU
    print("\n=== NVIDIA GPU Check ===")
    gpu_available, gpu_info = check_nvidia_gpu()
    
    if gpu_available:
        print(f"✅ NVIDIA GPU detected:")
        print(f"   GPU: {gpu_info['name']}")
        print(f"   Memory: {gpu_info['memory']}")
        print(f"   Driver Version: {gpu_info['driver_version']}")
        print(f"   CUDA Version: {gpu_info['cuda_version']}")
    else:
        print(f"❌ No NVIDIA GPU detected or nvidia-smi not available.")
        print(f"   Details: {gpu_info}")
    
    # Check if Ollama is using GPU
    print("\n=== Ollama GPU Usage Check ===")
    ollama_gpu, ollama_gpu_info = check_ollama_gpu_usage(ollama_host)
    
    if ollama_gpu:
        print(f"✅ Ollama appears to be using GPU acceleration.")
        print(f"   Details: {ollama_gpu_info}")
    else:
        print(f"❌ Ollama does not appear to be using GPU acceleration.")
        print(f"   Details: {ollama_gpu_info}")
    
    # Print recommendations
    print("\n=== Recommendations ===")
    
    if gpu_available and not ollama_gpu:
        print("You have an NVIDIA GPU, but Ollama doesn't appear to be using it.")
        print("To enable GPU acceleration for Ollama:")
        
        if platform.system() == "Windows":
            print("1. Make sure you have the NVIDIA CUDA Toolkit installed")
            print("2. Ensure you have the latest NVIDIA drivers")
            print("3. Install Ollama with GPU support")
            print("4. Set the OLLAMA_USE_GPU=1 environment variable before starting Ollama")
            print("\nExample commands:")
            print("   set OLLAMA_USE_GPU=1")
            print("   ollama serve")
        else:
            print("1. Make sure you have the NVIDIA CUDA Toolkit installed")
            print("2. Ensure you have the latest NVIDIA drivers")
            print("3. Install Ollama with GPU support")
            print("4. Set the OLLAMA_USE_GPU=1 environment variable before starting Ollama")
            print("\nExample commands:")
            print("   export OLLAMA_USE_GPU=1")
            print("   ollama serve")
    
    if not gpu_available:
        print("No NVIDIA GPU detected. Recommendations for CPU-only usage:")
        print("1. Consider using smaller models like llama3:8b or phi3 instead of deepseek-r1:32b")
        print("2. Increase the TIMEOUT setting in .env to at least 600 seconds")
        print("3. Set MAX_PARALLEL_INSERT=1 in .env to avoid resource contention")
        print("4. Process documents one at a time to avoid memory issues")
    
    if llm_model == "deepseek-r1:32b" and not (gpu_available and ollama_gpu):
        print("\nSpecific recommendations for deepseek-r1:32b without GPU acceleration:")
        print("1. This model is very large (32B parameters) and will be extremely slow without GPU")
        print("2. Consider switching to a smaller model like llama3:8b or phi3")
        print("3. If you must use deepseek-r1:32b, set very long timeouts (1000+ seconds)")
        print("4. Process only one document at a time and be prepared for long wait times")

if __name__ == "__main__":
    main()
