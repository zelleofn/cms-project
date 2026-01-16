import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    
    
 
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
   
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
   
    WORDPRESS_GRAPHQL_URL = os.getenv('WORDPRESS_GRAPHQL_URL', 'http://localhost:8080/graphql')
    
   
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    CACHE_DEFAULT_TTL = 300  
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
  
    ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-token-change-in-production')


class DevelopmentConfig(Config):
    
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
   
    DEBUG = False
    TESTING = False
    
    
    @property
    def SECRET_KEY(self):
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY must be set in production!")
        return secret_key
    
    @property
    def JWT_SECRET_KEY(self):
        jwt_key = os.getenv('JWT_SECRET_KEY')
        if not jwt_key:
            raise ValueError("JWT_SECRET_KEY must be set in production!")
        return jwt_key


class TestingConfig(Config):
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
   
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
  
    REDIS_DB = 1



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}