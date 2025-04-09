#!/usr/bin/env python3
"""
Hybrid Cache Implementation for MultiFileRAG.

This module implements a two-level cache system:
1. Redis as a fast first layer
2. PostgreSQL as a persistent second layer

The hybrid cache provides both speed and durability.
"""

import os
import json
import asyncio
import logging
import redis
import asyncpg
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import configparser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini", "utf-8")

class RedisCache:
    """Redis cache implementation for the first layer of the hybrid cache."""
    
    def __init__(self):
        """Initialize the Redis cache connection."""
        self.host = os.environ.get("REDIS_HOST", config.get("redis", "host", fallback="localhost"))
        self.port = int(os.environ.get("REDIS_PORT", config.get("redis", "port", fallback="6379")))
        self.db = int(os.environ.get("REDIS_DB", config.get("redis", "db", fallback="0")))
        self.password = os.environ.get("REDIS_PASSWORD", config.get("redis", "password", fallback=None))
        self.ttl = int(os.environ.get("REDIS_TTL", config.get("redis", "ttl", fallback="3600")))
        
        # Connect to Redis
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True
        )
        
        logger.info(f"Connected to Redis at {self.host}:{self.port}/{self.db}")
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from the Redis cache."""
        try:
            return self.redis.get(key)
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a value in the Redis cache with optional TTL."""
        try:
            return self.redis.set(key, value, ex=ttl or self.ttl)
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a key from the Redis cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in the Redis cache."""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking if key {key} exists in Redis: {e}")
            return False
    
    def flush(self) -> bool:
        """Flush all keys from the Redis cache."""
        try:
            return bool(self.redis.flushdb())
        except Exception as e:
            logger.error(f"Error flushing Redis cache: {e}")
            return False


class PostgreSQLCache:
    """PostgreSQL cache implementation for the second layer of the hybrid cache."""
    
    def __init__(self):
        """Initialize the PostgreSQL cache connection."""
        self.host = os.environ.get("POSTGRES_HOST", config.get("postgres", "host", fallback="localhost"))
        self.port = int(os.environ.get("POSTGRES_PORT", config.get("postgres", "port", fallback="5432")))
        self.user = os.environ.get("POSTGRES_USER", config.get("postgres", "user", fallback="postgres"))
        self.password = os.environ.get("POSTGRES_PASSWORD", config.get("postgres", "password", fallback="postgres"))
        self.database = os.environ.get("POSTGRES_DATABASE", config.get("postgres", "database", fallback="multifilerag"))
        self.pool = None
        
        logger.info(f"PostgreSQL cache configured for {self.host}:{self.port}/{self.database}")
    
    async def connect(self):
        """Connect to the PostgreSQL database."""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    host=self.host,
                    port=self.port
                )
                
                # Create cache table if it doesn't exist
                async with self.pool.acquire() as conn:
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS cache (
                            key TEXT PRIMARY KEY,
                            value TEXT NOT NULL,
                            expires_at TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Create index on expires_at for efficient cleanup
                    await conn.execute('''
                        CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON cache(expires_at)
                    ''')
                
                logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"Error connecting to PostgreSQL: {e}")
                raise
    
    async def disconnect(self):
        """Disconnect from the PostgreSQL database."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            logger.info("Disconnected from PostgreSQL")
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from the PostgreSQL cache."""
        if self.pool is None:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                # Get the value and check if it's expired
                row = await conn.fetchrow(
                    '''
                    SELECT value, expires_at FROM cache 
                    WHERE key = $1 AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ''', 
                    key
                )
                
                if row:
                    return row['value']
                return None
        except Exception as e:
            logger.error(f"Error getting key {key} from PostgreSQL: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a value in the PostgreSQL cache with optional TTL."""
        if self.pool is None:
            await self.connect()
        
        try:
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            async with self.pool.acquire() as conn:
                await conn.execute(
                    '''
                    INSERT INTO cache (key, value, expires_at, updated_at) 
                    VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) 
                    DO UPDATE SET 
                        value = $2, 
                        expires_at = $3,
                        updated_at = CURRENT_TIMESTAMP
                    ''',
                    key, value, expires_at
                )
                return True
        except Exception as e:
            logger.error(f"Error setting key {key} in PostgreSQL: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from the PostgreSQL cache."""
        if self.pool is None:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute('DELETE FROM cache WHERE key = $1', key)
                return 'DELETE' in result
        except Exception as e:
            logger.error(f"Error deleting key {key} from PostgreSQL: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the PostgreSQL cache."""
        if self.pool is None:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(
                    '''
                    SELECT COUNT(*) FROM cache 
                    WHERE key = $1 AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ''', 
                    key
                )
                return count > 0
        except Exception as e:
            logger.error(f"Error checking if key {key} exists in PostgreSQL: {e}")
            return False
    
    async def flush(self) -> bool:
        """Flush all keys from the PostgreSQL cache."""
        if self.pool is None:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('DELETE FROM cache')
                return True
        except Exception as e:
            logger.error(f"Error flushing PostgreSQL cache: {e}")
            return False
    
    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        if self.pool is None:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    'DELETE FROM cache WHERE expires_at < CURRENT_TIMESTAMP'
                )
                count = int(result.split(' ')[1]) if 'DELETE' in result else 0
                if count > 0:
                    logger.info(f"Cleaned up {count} expired cache entries")
                return count
        except Exception as e:
            logger.error(f"Error cleaning up expired cache entries: {e}")
            return 0


class HybridCache:
    """
    Hybrid cache implementation that uses Redis as the first layer and PostgreSQL as the second layer.
    
    The cache retrieval flow is:
    1. Try to get the value from Redis
    2. If not found in Redis, try to get it from PostgreSQL
    3. If found in PostgreSQL, store it in Redis for faster future access
    
    The cache storage flow is:
    1. Store the value in Redis
    2. Store the value in PostgreSQL for persistence
    """
    
    def __init__(self):
        """Initialize the hybrid cache."""
        self.redis_cache = RedisCache()
        self.pg_cache = PostgreSQLCache()
        logger.info("Initialized hybrid cache")
    
    async def connect(self):
        """Connect to both cache layers."""
        await self.pg_cache.connect()
    
    async def disconnect(self):
        """Disconnect from both cache layers."""
        await self.pg_cache.disconnect()
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from the hybrid cache."""
        # Try Redis first (fast)
        redis_value = self.redis_cache.get(key)
        if redis_value is not None:
            logger.debug(f"Cache hit in Redis for key: {key}")
            return redis_value
        
        # If not in Redis, try PostgreSQL (persistent)
        pg_value = await self.pg_cache.get(key)
        if pg_value is not None:
            logger.debug(f"Cache hit in PostgreSQL for key: {key}")
            # Store in Redis for faster future access
            self.redis_cache.set(key, pg_value)
            return pg_value
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a value in the hybrid cache."""
        # Store in Redis (fast)
        redis_success = self.redis_cache.set(key, value, ttl)
        
        # Store in PostgreSQL (persistent)
        pg_success = await self.pg_cache.set(key, value, ttl)
        
        return redis_success and pg_success
    
    async def delete(self, key: str) -> bool:
        """Delete a key from the hybrid cache."""
        # Delete from Redis
        redis_success = self.redis_cache.delete(key)
        
        # Delete from PostgreSQL
        pg_success = await self.pg_cache.delete(key)
        
        return redis_success and pg_success
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the hybrid cache."""
        # Check Redis first (fast)
        if self.redis_cache.exists(key):
            return True
        
        # If not in Redis, check PostgreSQL
        return await self.pg_cache.exists(key)
    
    async def flush(self) -> bool:
        """Flush all keys from the hybrid cache."""
        # Flush Redis
        redis_success = self.redis_cache.flush()
        
        # Flush PostgreSQL
        pg_success = await self.pg_cache.flush()
        
        return redis_success and pg_success
    
    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        # PostgreSQL handles expiration on read, but we can explicitly clean up
        return await self.pg_cache.cleanup_expired()


class HybridKVStorage:
    """
    Hybrid key-value storage implementation for MultiFileRAG.
    
    This class implements the BaseKVStorage interface using the hybrid cache.
    """
    
    def __init__(self, namespace, global_config, **kwargs):
        """Initialize the hybrid KV storage."""
        self.namespace = namespace
        self.global_config = global_config
        self.cache = HybridCache()
        self._max_batch_size = global_config.get("embedding_batch_num", 100)
    
    async def initialize(self):
        """Initialize the storage."""
        await self.cache.connect()
    
    async def finalize(self):
        """Finalize the storage."""
        await self.cache.disconnect()
    
    def _make_key(self, key: str) -> str:
        """Create a namespaced key."""
        return f"{self.namespace}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the storage."""
        namespaced_key = self._make_key(key)
        value_json = await self.cache.get(namespaced_key)
        if value_json is not None:
            return json.loads(value_json)
        return None
    
    async def set(self, key: str, value: Any) -> bool:
        """Set a value in the storage."""
        namespaced_key = self._make_key(key)
        value_json = json.dumps(value)
        return await self.cache.set(namespaced_key, value_json)
    
    async def delete(self, key: str) -> bool:
        """Delete a key from the storage."""
        namespaced_key = self._make_key(key)
        return await self.cache.delete(namespaced_key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the storage."""
        namespaced_key = self._make_key(key)
        return await self.cache.exists(namespaced_key)
    
    async def get_all(self) -> Dict[str, Any]:
        """Get all key-value pairs from the storage."""
        # This is a more complex operation that would require listing all keys
        # For now, we'll implement it using PostgreSQL directly
        result = {}
        try:
            if self.cache.pg_cache.pool is None:
                await self.cache.pg_cache.connect()
            
            async with self.cache.pg_cache.pool.acquire() as conn:
                rows = await conn.fetch(
                    '''
                    SELECT key, value FROM cache 
                    WHERE key LIKE $1 AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ''', 
                    f"{self.namespace}:%"
                )
                
                for row in rows:
                    key = row['key'].split(':', 1)[1]  # Remove namespace prefix
                    result[key] = json.loads(row['value'])
                
                return result
        except Exception as e:
            logger.error(f"Error getting all keys from PostgreSQL: {e}")
            return {}
    
    async def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from the storage."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_batch(self, items: Dict[str, Any]) -> bool:
        """Set multiple values in the storage."""
        success = True
        for key, value in items.items():
            if not await self.set(key, value):
                success = False
        return success
    
    async def delete_batch(self, keys: List[str]) -> bool:
        """Delete multiple keys from the storage."""
        success = True
        for key in keys:
            if not await self.delete(key):
                success = False
        return success


class HybridCacheStorage:
    """
    Hybrid cache storage implementation for MultiFileRAG.
    
    This class provides caching for query results and other frequently accessed data.
    """
    
    def __init__(self, namespace, global_config, **kwargs):
        """Initialize the hybrid cache storage."""
        self.namespace = namespace
        self.global_config = global_config
        self.cache = HybridCache()
    
    async def initialize(self):
        """Initialize the storage."""
        await self.cache.connect()
    
    async def finalize(self):
        """Finalize the storage."""
        await self.cache.disconnect()
    
    def _make_key(self, key: str) -> str:
        """Create a namespaced key."""
        return f"{self.namespace}:cache:{key}"
    
    async def get_query_result(self, query: str, mode: str) -> Optional[str]:
        """Get a cached query result."""
        # Create a key based on the query and mode
        key = self._make_key(f"query:{mode}:{hash(query)}")
        return await self.cache.get(key)
    
    async def set_query_result(self, query: str, mode: str, result: str, ttl: Optional[int] = None) -> bool:
        """Cache a query result."""
        key = self._make_key(f"query:{mode}:{hash(query)}")
        return await self.cache.set(key, result, ttl)
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get a cached embedding."""
        key = self._make_key(f"embedding:{hash(text)}")
        embedding_json = await self.cache.get(key)
        if embedding_json is not None:
            return json.loads(embedding_json)
        return None
    
    async def set_embedding(self, text: str, embedding: List[float], ttl: Optional[int] = None) -> bool:
        """Cache an embedding."""
        key = self._make_key(f"embedding:{hash(text)}")
        embedding_json = json.dumps(embedding)
        return await self.cache.set(key, embedding_json, ttl)
    
    async def get_entity_extraction(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached entity extraction results."""
        key = self._make_key(f"entity:{hash(text)}")
        entity_json = await self.cache.get(key)
        if entity_json is not None:
            return json.loads(entity_json)
        return None
    
    async def set_entity_extraction(self, text: str, entities: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache entity extraction results."""
        key = self._make_key(f"entity:{hash(text)}")
        entity_json = json.dumps(entities)
        return await self.cache.set(key, entity_json, ttl)
    
    async def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        # This would require a more complex implementation to list keys by pattern
        # For now, we'll implement a simple flush
        if pattern == "*":
            await self.cache.flush()
            return 1
        return 0


# Scheduled task to clean up expired cache entries
async def cleanup_task():
    """Periodically clean up expired cache entries."""
    cache = HybridCache()
    await cache.connect()
    
    try:
        while True:
            await cache.cleanup_expired()
            await asyncio.sleep(3600)  # Run every hour
    except asyncio.CancelledError:
        await cache.disconnect()


# Start the cleanup task when the module is imported
cleanup_task_handle = None

def start_cleanup_task():
    """Start the cleanup task."""
    global cleanup_task_handle
    if cleanup_task_handle is None:
        cleanup_task_handle = asyncio.create_task(cleanup_task())

def stop_cleanup_task():
    """Stop the cleanup task."""
    global cleanup_task_handle
    if cleanup_task_handle is not None:
        cleanup_task_handle.cancel()
        cleanup_task_handle = None


if __name__ == "__main__":
    """Run a simple test of the hybrid cache."""
    async def test_hybrid_cache():
        cache = HybridCache()
        await cache.connect()
        
        # Set a value
        await cache.set("test_key", "test_value")
        
        # Get the value
        value = await cache.get("test_key")
        print(f"Retrieved value: {value}")
        
        # Check if the key exists
        exists = await cache.exists("test_key")
        print(f"Key exists: {exists}")
        
        # Delete the key
        deleted = await cache.delete("test_key")
        print(f"Key deleted: {deleted}")
        
        # Check if the key exists after deletion
        exists = await cache.exists("test_key")
        print(f"Key exists after deletion: {exists}")
        
        # Clean up
        await cache.disconnect()
    
    asyncio.run(test_hybrid_cache())
