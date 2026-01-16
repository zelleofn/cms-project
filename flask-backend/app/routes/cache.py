from flask import Blueprint, jsonify, request, current_app
from app.utils.cache import cache
from functools import wraps


cache_bp = Blueprint('cache', __name__, url_prefix='/api/cache')


def require_admin(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
       
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {current_app.config.get('ADMIN_TOKEN')}":
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@cache_bp.route('/status', methods=['GET'])
def cache_status():
    
    is_connected = cache.is_connected()
    
    if is_connected:
        try:
            info = cache.redis_client.info('stats')
            return jsonify({
                'status': 'connected',
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': round(
                    info.get('keyspace_hits', 0) / 
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100, 
                    2
                )
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'connected',
                'message': 'Connected but could not retrieve stats',
                'error': str(e)
            }), 200
    else:
        return jsonify({
            'status': 'disconnected',
            'message': 'Redis is not available'
        }), 503


@cache_bp.route('/clear', methods=['POST'])
@require_admin
def clear_cache():
    try:
        cache.clear_all()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cache_bp.route('/invalidate', methods=['POST'])
@require_admin
def invalidate_pattern():
    
    data = request.get_json()
    pattern = data.get('pattern')
    
    if not pattern:
        return jsonify({
            'success': False,
            'error': 'Pattern is required'
        }), 400
    
    try:
        deleted_count = cache.delete_pattern(pattern)
        return jsonify({
            'success': True,
            'message': f'Invalidated {deleted_count} keys matching pattern',
            'deleted_count': deleted_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cache_bp.route('/keys', methods=['GET'])
@require_admin
def list_keys():
   
    try:
        pattern = request.args.get('pattern', 'graphql:*')
        keys = cache.redis_client.keys(pattern)
        
      
        keys_with_ttl = []
        for key in keys[:100]: 
            ttl = cache.redis_client.ttl(key)
            keys_with_ttl.append({
                'key': key,
                'ttl': ttl,
                'expires_in': f"{ttl}s" if ttl > 0 else 'No expiration'
            })
        
        return jsonify({
            'total_keys': len(keys),
            'keys': keys_with_ttl,
            'showing': min(100, len(keys))
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cache_bp.route('/warmup', methods=['POST'])
@require_admin
def warmup_cache():
   
    try:
        from app.graphql.resolvers import Query
        
      
        class MockInfo:
            context = {'wp_graphql_url': request.app.config.get('WORDPRESS_GRAPHQL_URL')}
        
        info = MockInfo()
        
   
        Query.resolve_wordpress_posts(None, info, limit=10)
        Query.resolve_articles(None, info, limit=10)
        Query.resolve_products(None, info)
        Query.resolve_team_members(None, info)
        
        return jsonify({
            'success': True,
            'message': 'Cache warmed up successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500