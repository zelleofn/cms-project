import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';
import { Observable, map } from 'rxjs';
import { 
  GET_ARTICLES,
  GET_ARTICLE,
  CREATE_ARTICLE,
  UPDATE_ARTICLE,
  DELETE_ARTICLE,
  GET_WORDPRESS_POSTS,
  GET_WORDPRESS_POST
} from '../graphql/queries';


export interface Article {
  id?: number;
  title?: string;
  content?: string;
  author?: string;
  publishedDate?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface MutationResponse {
  success: boolean;
  message: string;
  article?: Article;
}

@Injectable({
    providedIn: 'root'
})
export class ArticleService {
    constructor(private apollo: Apollo) {}

    getArticles(limit: number = 10, offset: number = 0): Observable<Article[]> {
    return this.apollo
    .watchQuery<{ articles: Article[] }>({
        query: GET_ARTICLES,
        variables: { limit, offset }
    })
      .valueChanges.pipe(
        map(result => (result.data?.articles ?? []) as Article[])
      );
  }

  getArticle(articleId: number): Observable<Article | null> {
    return this.apollo
      .watchQuery<{ article: Article }>({
        query: GET_ARTICLE,
        variables: { articleId }
      })
      .valueChanges.pipe(
        map(result => result.data?.article ?? null)
      );
  }

getWordPressPost(postId: string): Observable<any | null> {
  return this.apollo
    .watchQuery<{ wordpressPost: any }>({
      query: GET_WORDPRESS_POST,
      variables: { 
        postId: postId 
      }
    })
    .valueChanges.pipe(
      map(result => result.data?.wordpressPost ?? null)
    );
}

  createArticle(title: string, content: string, author?: string): Observable<MutationResponse> {
    return this.apollo
      .mutate<{ createArticle: MutationResponse }>({
        mutation: CREATE_ARTICLE,
        variables: { title, content, author },
        refetchQueries: [{ query: GET_ARTICLES, variables: { limit: 10, offset: 0 } }]
      })
      .pipe(
        map(result => result.data!.createArticle)
      );
  }

  updateArticle(articleId: number, title?: string, content?: string, author?: string): Observable<MutationResponse> {
    return this.apollo
      .mutate<{ updateArticle: MutationResponse }>({
        mutation: UPDATE_ARTICLE,
        variables: { articleId, title, content, author },
        refetchQueries: [
          { query: GET_ARTICLES, variables: { limit: 10, offset: 0 } },
          { query: GET_ARTICLE, variables: { articleId } }
        ]
      })
      .pipe(
        map(result => result.data!.updateArticle)
      );
  }

  deleteArticle(articleId: number): Observable<MutationResponse> {
    return this.apollo
      .mutate<{ deleteArticle: MutationResponse }>({
        mutation: DELETE_ARTICLE,
        variables: { articleId },
        refetchQueries: [{ query: GET_ARTICLES, variables: { limit: 10, offset: 0 } }]
      })
      .pipe(
        map(result => result.data!.deleteArticle)
      );
  }

  getWordPressPosts(limit: number = 10): Observable<any[]> {
    return this.apollo
      .watchQuery<{ wordpressPosts: any[] }>({
        query: GET_WORDPRESS_POSTS,
        variables: { limit }
      })
      .valueChanges.pipe(
       map(result => result.data?.wordpressPosts ?? [])
      );
  }
}