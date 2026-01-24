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
import { ChangeDetectorRef } from '@angular/core';

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
  
  wordpressPosts: any[] = [];
  loading = true;
  error: string | null = null;

  constructor(private articleService: ArticleService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    console.log('HomeComponent initialized');
    this.loadWordPressPosts();
  }

  loadWordPressPosts(): void {
    this.loading = true;
    console.log('Loading WordPress posts...');
    this.articleService.getWordPressPosts(5).subscribe({
      next: (posts) => {
        console.log('Posts loaded:', posts);
        this.wordpressPosts = posts.filter(p => p !== null);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading WordPress posts:', err);
        this.error = 'Failed to load posts';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}