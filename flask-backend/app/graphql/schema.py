import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Article, Product, TeamMember
from app.graphql.resolvers import Query, Mutation


class ArticleType(SQLAlchemyObjectType):
    class Meta:
        model = Article
        exclude_fields = []


class ProductType(SQLAlchemyObjectType):
    class Meta:
        model = Product
        exclude_fields = []


class TeamMemberType(SQLAlchemyObjectType):
    class Meta:
        model = TeamMember
        exclude_fields = []


class WordPressPostType(graphene.ObjectType):
    id = graphene.String()
    title = graphene.String()
    content = graphene.String()
    excerpt = graphene.String()
    date = graphene.String()
    author_name = graphene.String()
    
    def resolve_author_name(self, info):
        author = self.get('author', {})
        node = author.get('node', {})
        return node.get('name', 'Unknown')


class CustomFieldType(graphene.ObjectType):
    field_group_name = graphene.String()
    custom_field_1 = graphene.String()
    custom_field_2 = graphene.String()


class ArticleResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    article = graphene.Field(ArticleType)


class ProductResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    product = graphene.Field(ProductType)


class QueryType(graphene.ObjectType):
    wordpress_posts = graphene.List(
        WordPressPostType,
        limit=graphene.Int(default_value=10),
        resolver=Query.resolve_wordpress_posts
    )
    wordpress_post = graphene.Field(
        WordPressPostType,
        post_id=graphene.String(required=True),
        resolver=Query.resolve_wordpress_post
    )
    
    articles = graphene.List(
        ArticleType,
        limit=graphene.Int(default_value=10),
        offset=graphene.Int(default_value=0),
        resolver=Query.resolve_articles
    )
    article = graphene.Field(
        ArticleType,
        article_id=graphene.Int(required=True),
        resolver=Query.resolve_article
    )
    
    products = graphene.List(
        ProductType,
        category=graphene.String(),
        resolver=Query.resolve_products
    )

    product = graphene.Field(
        ProductType,
        product_id=graphene.Int(required=True),
        resolver=Query.resolve_product 
    )
    
    team_members = graphene.List(
        TeamMemberType,
        resolver=Query.resolve_team_members
    )


class MutationType(graphene.ObjectType):
    create_article = graphene.Field(
        ArticleResponse,
        title=graphene.String(required=True),
        content=graphene.String(required=True),
        author=graphene.String(),
        resolver=Mutation.resolve_create_article
    )
    
    update_article = graphene.Field(
        ArticleResponse,
        article_id=graphene.Int(required=True),
        title=graphene.String(),
        content=graphene.String(),
        author=graphene.String(),
        resolver=Mutation.resolve_update_article
    )
    
    delete_article = graphene.Field(
        ArticleResponse,
        article_id=graphene.Int(required=True),
        resolver=Mutation.resolve_delete_article
    )


schema = graphene.Schema(
    query=QueryType,
    mutation=MutationType,
    auto_camelcase=True
)