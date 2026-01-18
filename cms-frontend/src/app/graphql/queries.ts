import { gql } from 'apollo-angular';


export const GET_ARTICLES = gql`
  query GetArticles($limit: Int, $offset: Int) {
    articles(limit: $limit, offset: $offset) {
      id
      title
      content
      author
      publishedDate
      createdAt
      updatedAt
    }
  }
`;

export const GET_ARTICLE = gql`
  query GetArticle($articleId: Int!) {
    article(articleId: $articleId) {
      id
      title
      content
      author
      publishedDate
      createdAt
      updatedAt
    }
  }
`;


export const GET_PRODUCTS = gql`
  query GetProducts($category: String) {
    products(category: $category) {
      id
      name
      description
      price
      sku
      createdAt
      updatedAt
    }
  }
`;


export const GET_TEAM_MEMBERS = gql`
  query GetTeamMembers {
    teamMembers {
      id
      name
      jobTitle
      bio
      createdAt
      updatedAt
    }
  }
`;


export const GET_WORDPRESS_POSTS = gql`
  query GetWordPressPosts($limit: Int) {
    wordpressPosts(limit: $limit) {
      id
      title
      content
      excerpt
      date
      authorName
    }
  }
`;

export const GET_WORDPRESS_POST = gql`
  query GetWordPressPost($postId: String!) {
    wordpressPost(postId: $postId) {
      id
      title
      content
      excerpt
      date
      authorName
    }
  }
`;


export const CREATE_ARTICLE = gql`
  mutation CreateArticle($title: String!, $content: String!, $author: String) {
    createArticle(title: $title, content: $content, author: $author) {
      success
      message
      article {
        id
        title
        content
        author
        publishedDate
      }
    }
  }
`;

export const UPDATE_ARTICLE = gql`
  mutation UpdateArticle($articleId: Int!, $title: String, $content: String, $author: String) {
    updateArticle(articleId: $articleId, title: $title, content: $content, author: $author) {
      success
      message
      article {
        id
        title
        content
        author
        updatedAt
      }
    }
  }
`;

export const DELETE_ARTICLE = gql`
  mutation DeleteArticle($articleId: Int!) {
    deleteArticle(articleId: $articleId) {
      success
      message
    }
  }
`;