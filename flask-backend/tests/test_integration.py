import pytest
from app.models import User

def test_user_registration_to_db(app):
    
    with app.test_client() as client:
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123"
        }
        
        response = client.post('/api/auth/register', json=payload)
        assert response.status_code == 201
        
        
        from app import db
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        assert user.email == "test@example.com"