import { Component, OnInit } from '@angular/core';
import { ArticleService, Article } from '../../services/article.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatDividerModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatGridListModule,
    MatCardModule,
    MatButtonModule,
    MatListModule
  ],
  templateUrl: './home.html',
  styleUrls: ['./home.scss']
})
export class HomeComponent implements OnInit {
  articles: Article[] = [];
  wordpressPosts: any[] = [];
  loading = true;
  error: string | null = null;

  constructor(private articleService: ArticleService) {}

  ngOnInit(): void {
    this.loadArticles();
    this.loadWordPressPosts();
  }

  loadArticles(): void {
    this.articleService.getArticles(5).subscribe({
      next: (articles) => {
        this.articles = articles;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load articles';
        this.loading = false;
        console.error('Error loading articles:', err);
      }
    });
  }

  loadWordPressPosts(): void {
    this.articleService.getWordPressPosts(5).subscribe({
      next: (posts) => {
        this.wordpressPosts = posts;
      },
      error: (err) => {
        console.error('Error loading WordPress posts:', err);
      }
    });
  }
}





