import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Article, Product, TeamMember
from app import db


class ArticleType(SQLAlchemyObjectType):
    class Meta:
        model = Article
        interfaces = (graphene.relay.Node,)


class ProductType(SQLAlchemyObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)


class TeamMemberType(SQLAlchemyObjectType):
    class Meta:
        model = TeamMember
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    all_articles = graphene.List(ArticleType)
    article = graphene.Field(ArticleType, id=graphene.Int(required=True))
    
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    
    all_team_members = graphene.List(TeamMemberType)
    team_member = graphene.Field(TeamMemberType, id=graphene.Int(required=True))
    
    def resolve_all_articles(self, info):
        return Article.query.all()
    
    def resolve_article(self, info, id):
        return Article.query.get(id)
    
    def resolve_all_products(self, info):
        return Product.query.all()
    
    def resolve_product(self, info, id):
        return Product.query.get(id)
    
    def resolve_all_team_members(self, info):
        return TeamMember.query.all()
    
    def resolve_team_member(self, info, id):
        return TeamMember.query.get(id)


class CreateArticle(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String()
        author = graphene.String()
    
    article = graphene.Field(ArticleType)
    
    def mutate(self, info, title, content=None, author=None):
        article = Article(title=title, content=content, author=author)
        db.session.add(article)
        db.session.commit()
        return CreateArticle(article=article)


class UpdateArticle(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()
        author = graphene.String()
    
    article = graphene.Field(ArticleType)
    
    def mutate(self, info, id, title=None, content=None, author=None):
        article = Article.query.get(id)
        if not article:
            return None
        
        if title:
            article.title = title
        if content:
            article.content = content
        if author:
            article.author = author
        
        db.session.commit()
        return UpdateArticle(article=article)


class DeleteArticle(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    
    def mutate(self, info, id):
        article = Article.query.get(id)
        if article:
            db.session.delete(article)
            db.session.commit()
            return DeleteArticle(success=True)
        return DeleteArticle(success=False)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        price = graphene.Float()
        sku = graphene.String()
    
    product = graphene.Field(ProductType)
    
    def mutate(self, info, name, description=None, price=None, sku=None):
        product = Product(name=name, description=description, price=price, sku=sku)
        db.session.add(product)
        db.session.commit()
        return CreateProduct(product=product)


class CreateTeamMember(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        job_title = graphene.String()
        bio = graphene.String()
    
    team_member = graphene.Field(TeamMemberType)
    
    def mutate(self, info, name, job_title=None, bio=None):
        team_member = TeamMember(name=name, job_title=job_title, bio=bio)
        db.session.add(team_member)
        db.session.commit()
        return CreateTeamMember(team_member=team_member)


class Mutation(graphene.ObjectType):
    create_article = CreateArticle.Field()
    update_article = UpdateArticle.Field()
    delete_article = DeleteArticle.Field()
    create_product = CreateProduct.Field()
    create_team_member = CreateTeamMember.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)