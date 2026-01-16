import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User, RefreshToken
from app import db


class JWTAuth:
 
    
    @staticmethod
    def generate_access_token(user_id, username, is_admin=False):
       
        secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-change-me')
        
        payload = {
            'user_id': user_id,
            'username': username,
            'is_admin': is_admin,
            'exp': datetime.utcnow() + timedelta(hours=1), 
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    
    @staticmethod
    def generate_refresh_token(user_id):
        
        
        token_string = RefreshToken.generate_token()
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token_string,
            expires_at=expires_at
        )
        
        db.session.add(refresh_token)
        db.session.commit()
        
        return token_string
    
    @staticmethod
    def decode_token(token):
        
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-change-me')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}
    
    @staticmethod
    def verify_refresh_token(token_string):
        
        refresh_token = RefreshToken.query.filter_by(token=token_string).first()
        
        if not refresh_token:
            return None
        
        if not refresh_token.is_valid():
            return None
        
        return refresh_token
    
    @staticmethod
    def revoke_refresh_token(token_string):
       
        refresh_token = RefreshToken.query.filter_by(token=token_string).first()
        
        if refresh_token:
            refresh_token.revoked = True
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def revoke_all_user_tokens(user_id):
       
        RefreshToken.query.filter_by(user_id=user_id, revoked=False).update({'revoked': True})
        db.session.commit()


def require_auth(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
      
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        
       
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
       
        payload = JWTAuth.decode_token(token)
        
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
       
        user = User.query.filter_by(id=payload['user_id']).first()
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
       
        request.current_user = user
        request.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
   
    @wraps(f)
    def decorated_function(*args, **kwargs):
       
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        payload = JWTAuth.decode_token(token)
        
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        
        user = User.query.filter_by(id=payload['user_id']).first()
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        if not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        request.current_user = user
        request.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
  
    return getattr(request, 'current_user', None)


def get_token_payload():
   
    return getattr(request, 'token_payload', None)