import sys
print(f"Python executable: {sys.executable}")

try:
    import lightrag
    print(f"LightRAG is installed at {lightrag.__file__}")
except ImportError:
    print("LightRAG is not installed in this environment")
