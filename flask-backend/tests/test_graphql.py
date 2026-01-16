import pytest
from app import create_app

@pytest.fixture
def app():
    return create_app('testing')

def test_graphql_unauthorized(app):
   
    with app.test_client() as client:
        query = '{ articles { title } }'
        response = client.post('/graphql', json={'query': query})
        assert response.status_code == 401
        assert response.get_json()['error'] == 'Authentication required'

def test_query_articles_happy_path(app):
   
    with app.test_client() as client:
        query = '{ articles { title author } }'
        
        headers = {'Authorization': 'Bearer test-token'}
        response = client.post('/graphql', json={'query': query}, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'articles' in data['data']

def test_query_single_product_not_found(app):
    with app.test_client() as client:
     
        query = '{ product(productId: 999) { name } }' 
        headers = {'Authorization': 'Bearer test-token'}
        response = client.post('/graphql', json={'query': query}, headers=headers)
        
        data = response.get_json()
      
        assert 'errors' in data
        assert 'not found' in data['errors'][0]['message'].lower()