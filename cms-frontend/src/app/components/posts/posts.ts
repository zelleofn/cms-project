import { Component, OnInit } from '@angular/core';
import { ArticleService, Article } from '../../services/article.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterModule } from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-posts',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTableModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './posts.html',
  styleUrls: ['./posts.scss']
})
export class PostsComponent implements OnInit {
  wordpressPosts: any[] = [];
  loading = true;
  error: string | null = null;
  
  displayedColumns: string[] = ['title', 'date', 'actions'];

  constructor(
    private articleService: ArticleService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadWordPressPosts();
  }

loadWordPressPosts(): void {
    this.loading = true;
    this.articleService.getWordPressPosts(5).subscribe({
      next: (posts) => {
        this.wordpressPosts = posts.filter(p => p !== null);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Error fetching posts';
        this.cdr.detectChanges();
      }
    });
  }

  viewArticle(id: string | number): void {
    this.router.navigate(['/posts', id]);
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  }
}