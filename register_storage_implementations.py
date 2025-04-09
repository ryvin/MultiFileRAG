#!/usr/bin/env python3
"""
Register Custom Storage Implementations for LightRAG.

This script registers custom storage implementations with LightRAG.
Run this script before starting the MultiFileRAG server to ensure
custom storage implementations are available.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def register_storage_implementations():
    """Register custom storage implementations with LightRAG."""
    try:
        # Import LightRAG
        import lightrag
        from lightrag.storage import register_storage_implementation
        
        logger.info("Registering custom storage implementations...")
        
        # Check if our hybrid_cache.py exists
        hybrid_cache_path = Path("hybrid_cache.py")
        if hybrid_cache_path.exists():
            # Import the HybridKVStorage class
            sys.path.insert(0, str(Path.cwd()))
            try:
                from hybrid_cache import HybridKVStorage, HybridCacheStorage
                
                # Register the HybridKVStorage implementation
                register_storage_implementation("KV_STORAGE", "HybridKVStorage", HybridKVStorage)
                logger.info("✅ Registered HybridKVStorage implementation")
                
                # Register the HybridCacheStorage implementation
                register_storage_implementation("CACHE_STORAGE", "HybridCacheStorage", HybridCacheStorage)
                logger.info("✅ Registered HybridCacheStorage implementation")
                
            except ImportError as e:
                logger.error(f"❌ Failed to import hybrid cache implementations: {e}")
                return False
            except Exception as e:
                logger.error(f"❌ Failed to register hybrid cache implementations: {e}")
                return False
        else:
            logger.warning("⚠️ hybrid_cache.py not found. Skipping registration of hybrid cache implementations.")
        
        return True
    
    except ImportError as e:
        logger.error(f"❌ Failed to import LightRAG: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to register storage implementations: {e}")
        return False

if __name__ == "__main__":
    success = register_storage_implementations()
    sys.exit(0 if success else 1)
