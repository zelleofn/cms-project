import redis
import json
import hashlib
import os
from functools import wraps
from typing import Any, Optional, Callable
from datetime import datetime, date


class RedisCache:
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        self.default_ttl = 300  
        
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return f"graphql:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _serialize_value(self, value: Any) -> str:
        def default_serializer(obj):
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if hasattr(obj, '__dict__') and not isinstance(obj, type):
               
                return {
                    k: v for k, v in obj.__dict__.items() 
                    if not k.startswith('_')
                }
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        return json.dumps(value, default=default_serializer)
    
    def get(self, key: str) -> Optional[Any]:
       
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
    
        try:
            ttl = ttl or self.default_ttl
            serialized_value = self._serialize_value(value)
            return self.redis_client.setex(key, ttl, serialized_value)
        except (redis.RedisError, TypeError, json.JSONDecodeError) as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
      
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    def clear_all(self) -> bool:
      
        try:
            return self.redis_client.flushdb()
        except redis.RedisError as e:
            print(f"Cache clear error: {e}")
            return False
    
    def is_connected(self) -> bool:
       
        try:
            return self.redis_client.ping()
        except Exception:
            return False


def cache_graphql_query(ttl: int = 300, key_prefix: str = "query"):

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = RedisCache()
            
         
            if not cache.is_connected():
                print(f"Redis not available, executing {func.__name__} without cache")
                return func(*args, **kwargs)
            
            
            cache_key = cache._generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                *args[1:],  
                **kwargs
            )
            
         
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f" Cache HIT for {func.__name__}")
                return cached_result
            
            print(f" Cache MISS for {func.__name__}")
            result = func(*args, **kwargs)
            
           
            if result is not None:
                try:
                  
                    if isinstance(result, list) and len(result) > 0:
                        if hasattr(result[0], 'to_dict'):
                            cache_data = [item.to_dict() for item in result]
                            cache.set(cache_key, cache_data, ttl)
                  
                    elif hasattr(result, 'to_dict'):
                        cache_data = result.to_dict()
                        cache.set(cache_key, cache_data, ttl)
                   
                    else:
                        cache.set(cache_key, result, ttl)
                except Exception as e:
                    print(f"Cache serialization warning: {e}")
            
            
            return result
        
        return wrapper
    return decorator


cache_query = cache_graphql_query


cache = RedisCache()