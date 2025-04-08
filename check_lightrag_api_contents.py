import sys
import os

try:
    import lightrag
    print(f"LightRAG version: {lightrag.__version__}")
    
    # Check the API directory
    api_dir = os.path.join(os.path.dirname(lightrag.__file__), 'api')
    print(f"API directory: {api_dir}")
    
    if os.path.exists(api_dir):
        print("\nFiles in the API directory:")
        for file in os.listdir(api_dir):
            print(f"  - {file}")
    else:
        print("API directory does not exist")
        
except ImportError:
    print("LightRAG is not installed in this environment")
