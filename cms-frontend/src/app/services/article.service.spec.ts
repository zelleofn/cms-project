import { TestBed } from '@angular/core/testing';
import { ApolloTestingModule, ApolloTestingController } from 'apollo-angular/testing';
import { ArticleService } from './article.service';
import { GET_ARTICLES } from '../graphql/queries'; 
import { firstValueFrom } from 'rxjs';

const mockArticles = [
  { id: 1, title: 'Test Article', author: 'Admin' },
];

describe('ArticleService', () => {
  let service: ArticleService;
  let controller: ApolloTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ApolloTestingModule],
      providers: [ArticleService],
    });

    service = TestBed.inject(ArticleService);
    controller = TestBed.inject(ApolloTestingController);
  });

  afterEach(() => {
    controller.verify();
  });

  it('should return articles when the query is successful', async () => {
    const articlesPromise = firstValueFrom(service.getArticles());

    const op = controller.expectOne(GET_ARTICLES);
    op.flush({
      data: { articles: mockArticles },
    });

    const articles = await articlesPromise;
    expect(articles).toEqual(mockArticles);
  });
});
