from flask import Blueprint, request, jsonify
from app.models import User, RefreshToken
from app.utils.auth import JWTAuth, require_auth, get_current_user
from app import db
from datetime import datetime
import re


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def validate_email(email):
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


@auth_bp.route('/register', methods=['POST'])
def register():
    
    data = request.get_json()
    
   
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
   
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
   
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    
    try:
        user = User(
            username=username,
            email=email,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_admin=False  
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        access_token = JWTAuth.generate_access_token(user.id, user.username, user.is_admin)
        refresh_token = JWTAuth.generate_refresh_token(user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
   
    data = request.get_json()
    
    
    if not data.get('username') and not data.get('email'):
        return jsonify({'error': 'Username or email is required'}), 400
    
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    
    
    user = None
    if data.get('email'):
        user = User.query.filter_by(email=data['email'].lower()).first()
    else:
        user = User.query.filter_by(username=data['username']).first()
    
   
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
   
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    
   
    access_token = JWTAuth.generate_access_token(user.id, user.username, user.is_admin)
    refresh_token = JWTAuth.generate_refresh_token(user.id)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    
    data = request.get_json()
    
    if not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token is required'}), 400
    
    
    refresh_token_obj = JWTAuth.verify_refresh_token(data['refresh_token'])
    
    if not refresh_token_obj:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401
    
    
    user = User.query.filter_by(id=refresh_token_obj.user_id).first()
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
   
    access_token = JWTAuth.generate_access_token(user.id, user.username, user.is_admin)
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'token_type': 'Bearer'
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    data = request.get_json()
    
    if not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token is required'}), 400
    
  
    revoked = JWTAuth.revoke_refresh_token(data['refresh_token'])
    
    if revoked:
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Token not found'
        }), 404


@auth_bp.route('/logout-all', methods=['POST'])
@require_auth
def logout_all():
   
    user = get_current_user()
    
    JWTAuth.revoke_all_user_tokens(user.id)
    
    return jsonify({
        'success': True,
        'message': 'Logged out from all devices'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_profile():
    
    user = get_current_user()
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['PUT'])
@require_auth
def update_profile():
    
    user = get_current_user()
    data = request.get_json()
    
    allowed_fields = ['first_name', 'last_name', 'email']
    
    try:
        for field in allowed_fields:
            if field in data:
                if field == 'email':
                    email = data['email'].strip().lower()
                    if not validate_email(email):
                        return jsonify({'error': 'Invalid email format'}), 400
                  
                    existing = User.query.filter_by(email=email).first()
                    if existing and existing.id != user.id:
                        return jsonify({'error': 'Email already in use'}), 409
                    setattr(user, field, email)
                else:
                    setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    
    user = get_current_user()
    data = request.get_json()
    
   
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
   
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
   
    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
  
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        
        
        if data.get('logout_all_devices', False):
            JWTAuth.revoke_all_user_tokens(user.id)
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500