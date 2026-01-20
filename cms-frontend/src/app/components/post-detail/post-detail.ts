import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ArticleService, Article } from '../../services/article.service';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';

@Component({
  selector: 'app-post-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatProgressSpinnerModule,
    MatToolbarModule
  ],
  templateUrl: './post-detail.html',
  styleUrls: ['./post-detail.scss']
})
export class PostDetailComponent implements OnInit {
  article: Article | null = null;
  loading = true;
  error: string | null = null;
  isAdmin = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private articleService: ArticleService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.isAdmin = this.authService.isAdmin();
    
    this.route.params.subscribe(params => {
      const id = +params['id'];
      this.loadArticle(id);
    });
  }

  loadArticle(id: number): void {
    this.loading = true;
    this.articleService.getArticle(id).subscribe({
      next: (article) => {
        this.article = article;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load article';
        this.loading = false;
        console.error('Error:', err);
      }
    });
  }

  editArticle(): void {
    if (this.article) {
      this.router.navigate(['/admin'], { 
        queryParams: { editId: this.article.id } 
      });
    }
  }

  deleteArticle(): void {
    if (!this.article || !confirm('Are you sure you want to delete this article?')) {
      return;
    }

    this.articleService.deleteArticle(this.article.id!).subscribe({
      next: (response) => {
        if (response.success) {
          this.router.navigate(['/posts']);
        }
      },
      error: (err) => {
        alert('Failed to delete article');
        console.error('Error:', err);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/posts']);
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}