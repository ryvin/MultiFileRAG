#!/usr/bin/env python3
"""
Script to optimize MultiFileRAG settings for CPU-only usage.
This script updates the .env file with more appropriate settings for CPU-only operation.
"""

import os
import sys
import subprocess
import platform
from dotenv import load_dotenv

# Load current environment variables
load_dotenv()

def update_env_file(updates):
    """Update the .env file with new settings."""
    try:
        # Read the current .env file
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Create a dictionary of current settings
        current_settings = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                current_settings[key] = value
        
        # Update with new settings
        for key, value in updates.items():
            current_settings[key] = value
        
        # Create a backup of the original .env file
        with open(".env.backup", "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        # Write the updated .env file
        with open(".env", "w", encoding="utf-8") as f:
            # First write all the lines that don't match our keys
            for line in lines:
                line_strip = line.strip()
                if not line_strip or line_strip.startswith("#") or "=" not in line_strip:
                    f.write(line)
                    continue
                
                key = line_strip.split("=", 1)[0]
                if key not in updates:
                    f.write(line)
            
            # Then write our updated settings
            f.write("\n# Updated settings for CPU-only operation\n")
            for key, value in updates.items():
                f.write(f"{key}={value}\n")
        
        return True, "Settings updated successfully."
    except Exception as e:
        return False, str(e)

def pull_ollama_model(model_name):
    """Pull a model from Ollama."""
    try:
        print(f"Pulling model {model_name} from Ollama...")
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, f"Failed to pull model: {result.stderr}"
        
        return True, "Model pulled successfully."
    except Exception as e:
        return False, str(e)

def main():
    """Main entry point."""
    print("=== Optimizing MultiFileRAG for CPU-only Operation ===\n")
    
    # Get current settings
    current_llm = os.getenv("LLM_MODEL", "deepseek-r1:32b")
    current_timeout = os.getenv("TIMEOUT", "200")
    current_parallel = os.getenv("MAX_PARALLEL_INSERT", "2")
    
    print(f"Current settings:")
    print(f"LLM_MODEL={current_llm}")
    print(f"TIMEOUT={current_timeout}")
    print(f"MAX_PARALLEL_INSERT={current_parallel}")
    
    # Ask for confirmation
    print("\nRecommended changes for CPU-only operation:")
    print("1. Change LLM_MODEL from deepseek-r1:32b to llama3:8b (much faster on CPU)")
    print("2. Increase TIMEOUT from 200 to 600 seconds")
    print("3. Set MAX_PARALLEL_INSERT to 1 to avoid resource contention")
    
    confirm = input("\nDo you want to apply these changes? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Pull the llama3:8b model
    model_success, model_message = pull_ollama_model("llama3:8b")
    if not model_success:
        print(f"Warning: {model_message}")
        print("Continuing with configuration changes anyway...")
    else:
        print(f"✅ {model_message}")
    
    # Update the .env file
    updates = {
        "LLM_MODEL": "llama3:8b",
        "TIMEOUT": "600",
        "MAX_PARALLEL_INSERT": "1"
    }
    
    success, message = update_env_file(updates)
    
    if success:
        print(f"✅ {message}")
        print("The .env file has been updated with CPU-optimized settings.")
        print("A backup of the original settings has been saved to .env.backup.")
        print("\nTo apply these changes, restart the MultiFileRAG server:")
        print("1. Stop the current server")
        print("2. Run: python multifilerag_server.py")
    else:
        print(f"❌ Failed to update settings: {message}")

if __name__ == "__main__":
    main()
