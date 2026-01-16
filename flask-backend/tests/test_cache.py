import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from app.utils.cache import RedisCache, cache_query


@pytest.fixture
def redis_cache():
    
    with patch('app.utils.cache.redis.Redis') as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        cache = RedisCache()
        cache.redis_client = mock_client
        yield cache


class TestRedisCache:
    
    def test_cache_initialization(self, redis_cache):
       
        assert redis_cache.default_ttl == 300
        assert redis_cache.redis_client is not None
    
    def test_generate_cache_key(self, redis_cache):
       
        key1 = redis_cache._generate_cache_key("posts", "arg1", kwarg1="value1")
        key2 = redis_cache._generate_cache_key("posts", "arg1", kwarg1="value1")
        key3 = redis_cache._generate_cache_key("posts", "arg2", kwarg1="value1")
        
      
        assert key1 == key2
        
        assert key1 != key3
       
        assert key1.startswith("graphql:")
    
    def test_set_and_get_value(self, redis_cache):
        
        test_data = {"title": "Test Post", "id": 1}
        redis_cache.redis_client.get.return_value = json.dumps(test_data)
        redis_cache.redis_client.setex.return_value = True
        
        
        result = redis_cache.set("test_key", test_data, ttl=300)
        assert result is True
        
       
        cached_value = redis_cache.get("test_key")
        assert cached_value == test_data
    
    def test_get_nonexistent_key(self, redis_cache):
       
        redis_cache.redis_client.get.return_value = None
        
        result = redis_cache.get("nonexistent_key")
        assert result is None
    
    def test_delete_key(self, redis_cache):
       
        redis_cache.redis_client.delete.return_value = 1
        
        result = redis_cache.delete("test_key")
        assert result is True
        redis_cache.redis_client.delete.assert_called_once_with("test_key")
    
    def test_delete_pattern(self, redis_cache):
        
        redis_cache.redis_client.keys.return_value = ["key1", "key2", "key3"]
        redis_cache.redis_client.delete.return_value = 3
        
        deleted_count = redis_cache.delete_pattern("graphql:*")
        
        assert deleted_count == 3
        redis_cache.redis_client.keys.assert_called_once_with("graphql:*")
    
    def test_clear_all(self, redis_cache):
     
        redis_cache.redis_client.flushdb.return_value = True
        
        result = redis_cache.clear_all()
        assert result is True
        redis_cache.redis_client.flushdb.assert_called_once()
    
    def test_is_connected_success(self, redis_cache):
        
        redis_cache.redis_client.ping.return_value = True
        
        assert redis_cache.is_connected() is True
    
    def test_is_connected_failure(self, redis_cache):
       
        redis_cache.redis_client.ping.side_effect = Exception("Connection failed")
        
        assert redis_cache.is_connected() is False
    
    def test_cache_handles_json_error(self, redis_cache):
       
        redis_cache.redis_client.get.return_value = "invalid json{"
        
        result = redis_cache.get("bad_key")
        assert result is None


class TestCacheQueryDecorator:
    
    def test_cache_hit(self):
        with patch('app.utils.cache.RedisCache') as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.is_connected.return_value = True
            mock_cache_instance.get.return_value = {"cached": "data"}
            MockCache.return_value = mock_cache_instance
            
            @cache_query(ttl=300, key_prefix="test")
            def test_function(root, info):
                return {"fresh": "data"}
            
            result = test_function(None, None)
            
            assert result == {"cached": "data"}
            mock_cache_instance.get.assert_called_once()
            mock_cache_instance.set.assert_not_called()
    
    def test_cache_miss(self):
        with patch('app.utils.cache.RedisCache') as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.is_connected.return_value = True
            mock_cache_instance.get.return_value = None
            mock_cache_instance.set.return_value = True
            MockCache.return_value = mock_cache_instance
            
            @cache_query(ttl=300, key_prefix="test")
            def test_function(root, info):
                return {"fresh": "data"}
            
            result = test_function(None, None)
            
            assert result == {"fresh": "data"}
            mock_cache_instance.get.assert_called_once()
            mock_cache_instance.set.assert_called_once()
    
    def test_cache_unavailable_executes_function(self):
        with patch('app.utils.cache.RedisCache') as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.is_connected.return_value = False
            MockCache.return_value = mock_cache_instance
            
            @cache_query(ttl=300, key_prefix="test")
            def test_function(root, info):
                return {"fresh": "data"}
            
            result = test_function(None, None)
            
            assert result == {"fresh": "data"}
            mock_cache_instance.get.assert_not_called()
            mock_cache_instance.set.assert_not_called()
    
    def test_decorator_with_arguments(self):
        with patch('app.utils.cache.RedisCache') as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.is_connected.return_value = True
            mock_cache_instance.get.return_value = None
            mock_cache_instance.set.return_value = True
            MockCache.return_value = mock_cache_instance
            
            @cache_query(ttl=300, key_prefix="test")
            def test_function(root, info, post_id, limit=10):
                return {"id": post_id, "limit": limit}
            
            result = test_function(None, None, post_id=123, limit=20)
            
            assert result == {"id": 123, "limit": 20}
            mock_cache_instance.set.assert_called_once()


@pytest.fixture
def app():
   
    from app import create_app
    from config import TestingConfig
    
    app = create_app('testing')
    
    with app.app_context():
        yield app


class TestCacheEndpoints:

    
    def test_cache_status_connected(self, app):
      
        with app.test_client() as client:
            with patch('app.routes.cache.cache.is_connected', return_value=True):
                with patch('app.routes.cache.cache.redis_client.info') as mock_info:
                    mock_info.return_value = {
                        'total_commands_processed': 1000,
                        'keyspace_hits': 800,
                        'keyspace_misses': 200
                    }
                    
                    response = client.get('/api/cache/status')
                    
                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['status'] == 'connected'
                    assert data['hit_rate'] == 80.0
    
    def test_cache_status_disconnected(self, app):
       
        with app.test_client() as client:
            with patch('app.routes.cache.cache.is_connected', return_value=False):
                response = client.get('/api/cache/status')
                
                assert response.status_code == 503
                data = response.get_json()
                assert data['status'] == 'disconnected'
    
    def test_clear_cache_unauthorized(self, app):
    
        with app.test_client() as client:
            response = client.post('/api/cache/clear')
            
            assert response.status_code == 401
    
    def test_clear_cache_authorized(self, app):
      
        app.config['ADMIN_TOKEN'] = 'test-token'
        
        with app.test_client() as client:
            with patch('app.routes.cache.cache.clear_all', return_value=True):
                response = client.post(
                    '/api/cache/clear',
                    headers={'Authorization': 'Bearer test-token'}
                )
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True


