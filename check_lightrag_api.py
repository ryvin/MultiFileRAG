import sys
print(f"Python executable: {sys.executable}")

try:
    import lightrag
    print(f"LightRAG is installed at {lightrag.__file__}")
    print(f"LightRAG version: {lightrag.__version__}")
    
    # Try to import API modules
    try:
        from lightrag.api import config
        print("lightrag.api.config module is available")
    except ImportError as e:
        print(f"Error importing lightrag.api.config: {e}")
    
    # List all available modules in lightrag
    import pkgutil
    print("\nAvailable modules in lightrag:")
    for loader, name, is_pkg in pkgutil.iter_modules(lightrag.__path__):
        print(f"  - {name} ({'package' if is_pkg else 'module'})")
        
except ImportError:
    print("LightRAG is not installed in this environment")
