import requests
from typing import Dict, List, Optional
import os


class WordPressGraphQLClient:
    def __init__(self, wordpress_url: str):
        self.graphql_endpoint = f"{wordpress_url}/graphql"
        self.graphql_fallback = f"{wordpress_url}/?graphql"
    
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        try:
            payload = {
                'query': query
            }
            
            if variables:
                payload['variables'] = variables
            
            response = requests.post(
                self.graphql_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 404:
                response = requests.post(
                    self.graphql_fallback,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            response.raise_for_status()
            result = response.json()
            
            if 'errors' in result:
                print(f"WordPress GraphQL errors: {result['errors']}")
                return {'data': None, 'errors': result['errors']}
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"WordPress GraphQL request error: {e}")
            return {'data': None, 'errors': [str(e)]}
    
    def get_posts(self, first: int = 10) -> List[Dict]:
        query = """
        query GetPosts($first: Int!) {
          posts(first: $first) {
            nodes {
              id
              databaseId
              title
              content
              excerpt
              date
              author {
                node {
                  name
                }
              }
              categories {
                nodes {
                  name
                }
              }
            }
          }
        }
        """
        
        result = self.execute_query(query, {'first': first})
        
        if result.get('data') and result['data'].get('posts'):
            return result['data']['posts']['nodes']
        return []
    
    def get_post_by_id(self, post_id: int) -> Optional[Dict]:
        query = """
        query GetPost($id: ID!) {
          post(id: $id, idType: DATABASE_ID) {
            id
            databaseId
            title
            content
            excerpt
            date
            author {
              node {
                name
              }
            }
            categories {
              nodes {
                name
              }
            }
          }
        }
        """
        
        result = self.execute_query(query, {'id': post_id})
        
        if result.get('data') and result['data'].get('post'):
            return result['data']['post']
        return None
    
    def get_pages(self, first: int = 10) -> List[Dict]:
        query = """
        query GetPages($first: Int!) {
          pages(first: $first) {
            nodes {
              id
              databaseId
              title
              content
              date
            }
          }
        }
        """
        
        result = self.execute_query(query, {'first': first})
        
        if result.get('data') and result['data'].get('pages'):
            return result['data']['pages']['nodes']
        return []