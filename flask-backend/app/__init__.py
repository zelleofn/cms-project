from flask import Flask, request, jsonify  
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from graphql_server.flask import GraphQLView
from config import config
from app.utils.cache import cache

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    
    if cache.is_connected():
        app.logger.info(" Redis connection successful")
    else:
        app.logger.warning("  Redis connection failed - caching disabled")
    
    
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.routes.cache import cache_bp
    app.register_blueprint(cache_bp)
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.graphql.schema import schema

    
    @app.before_request
    def check_graphql_auth():
    if request.path == '/graphql' and request.method == 'POST':
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if query.startswith('mutation'):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Authentication required'}), 401

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True, 
        get_context=lambda: {
            'WORDPRESS_GRAPHQL_URL': app.config.get('WORDPRESS_GRAPHQL_URL')
        }
    )
)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        health_status = {
            'status': 'healthy',
            'database': 'connected',
            'redis': 'connected' if cache.is_connected() else 'disconnected'
        }
        status_code = 200 if cache.is_connected() else 503
        return health_status, status_code

    @app.route('/', methods=['GET'])
    def index():
        return {
            'message': 'Headless CMS GraphQL API',
            'version': '1.0.0',
            'endpoints': {
                'graphql': '/graphql',
                'graphiql': '/graphql (browser)',
                'api': '/api',
                'health': '/health',
                'cache_status': '/api/cache/status'
            }
        }, 200

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.warning(f"Could not create database tables: {e}")
            app.logger.info("App will start without database - check DATABASE_URL")
    
    return app