import pytest
from app import create_app
from app.models import db

@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
       
        db.create_all()
        yield app
        
        db.session.remove()
        