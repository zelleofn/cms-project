import requests
from typing import List, Optional
from app.models import Article, Product, TeamMember
from app import db
from app.utils.cache import cache_graphql_query, cache


class Query:
  
    
    @staticmethod
    @cache_graphql_query(ttl=300, key_prefix="wp_posts")
    def resolve_wordpress_posts(root, info, limit: int = 10) -> List[dict]:
        wp_url = info.context.get('wp_graphql_url')
        
        query = """
        query GetPosts($limit: Int) {
          posts(first: $limit) {
            nodes {
              id
              title
              content
              excerpt
              date
              author {
                node {
                  name
                }
              }
            }
          }
        }
        """
        
        try:
            response = requests.post(
                wp_url,
                json={'query': query, 'variables': {'limit': limit}},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', {}).get('posts', {}).get('nodes', [])
        except Exception as e:
            print(f"Error fetching WordPress posts: {e}")
            return []
    
    @staticmethod
    @cache_graphql_query(ttl=300, key_prefix="wp_post")
    def resolve_wordpress_post(root, info, post_id: str) -> Optional[dict]:
        wp_url = info.context.get('wp_graphql_url')
        
        query = """
        query GetPost($id: ID!) {
          post(id: $id, idType: DATABASE_ID) {
            id
            title
            content
            excerpt
            date
            author {
              node {
                name
              }
            }
            customFields {
              fieldGroupName
              customField1
              customField2
            }
          }
        }
        """
        
        try:
            response = requests.post(
                wp_url,
                json={'query': query, 'variables': {'id': post_id}},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', {}).get('post')
        except Exception as e:
            print(f"Error fetching WordPress post: {e}")
            return None
    
    
    @staticmethod
    @cache_graphql_query(ttl=300, key_prefix="articles")
    def resolve_articles(root, info, limit: int = 10, offset: int = 0) -> List:
        try:
            articles = Article.query.limit(limit).offset(offset).all()
            return articles
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
    
    @staticmethod
    @cache_graphql_query(ttl=300, key_prefix="article")
    def resolve_article(root, info, article_id: int) -> Optional[Article]:
        try:
            article = Article.query.filter_by(id=article_id).first()
            return article
        except Exception as e:
            print(f"Error fetching article: {e}")
            return None
    
    @staticmethod
    @cache_graphql_query(ttl=300, key_prefix="products")
    def resolve_products(root, info, category: Optional[str] = None) -> List:
        try:
            query = Product.query
            
            if category:
                query = query.filter_by(category=category)
            
            products = query.all()
            return products
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []

    @staticmethod
    def resolve_product(root, info, product_id: int) -> Optional[Product]:
        try:
            
            product = Product.query.filter_by(id=product_id).first()
            if not product:
                
                raise Exception("Product not found")
            return product
        except Exception as e:
           
            if str(e) == "Product not found":
                raise e
            print(f"Error fetching product: {e}")
            return None        
    
    @staticmethod
    @cache_graphql_query(ttl=300, key_prefix="team")
    def resolve_team_members(root, info) -> List:
        try:
            members = TeamMember.query.all()
            return members
        except Exception as e:
            print(f"Error fetching team members: {e}")
            return []


class Mutation:
    
    @staticmethod
    def resolve_create_article(root, info, title: str, content: str, author: Optional[str] = None) -> dict:
        try:
            article = Article(title=title, content=content, author=author)
            db.session.add(article)
            db.session.commit()
            
            cache.delete_pattern("graphql:*articles*")
            
            return {
                'success': True,
                'message': 'Article created successfully',
                'article': article
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating article: {str(e)}',
                'article': None
            }
    
    @staticmethod
    def resolve_update_article(root, info, article_id: int, title: Optional[str] = None, 
                              content: Optional[str] = None, author: Optional[str] = None) -> dict:
        try:
            article = Article.query.filter_by(id=article_id).first()
            
            if not article:
                return {
                    'success': False,
                    'message': 'Article not found',
                    'article': None
                }
            
            if title:
                article.title = title
            if content:
                article.content = content
            if author:
                article.author = author
            
            db.session.commit()
            
            cache.delete_pattern(f"graphql:*article*{article_id}*")
            cache.delete_pattern("graphql:*articles*")
            
            return {
                'success': True,
                'message': 'Article updated successfully',
                'article': article
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating article: {str(e)}',
                'article': None
            }
    
    @staticmethod
    def resolve_delete_article(root, info, article_id: int) -> dict:
        try:
            article = Article.query.filter_by(id=article_id).first()
            
            if not article:
                return {
                    'success': False,
                    'message': 'Article not found'
                }
            
            db.session.delete(article)
            db.session.commit()
            
            cache.delete_pattern(f"graphql:*article*{article_id}*")
            cache.delete_pattern("graphql:*articles*")
            
            return {
                'success': True,
                'message': 'Article deleted successfully'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting article: {str(e)}'
            }