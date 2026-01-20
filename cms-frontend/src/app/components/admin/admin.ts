import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ArticleService, Article } from '../../services/article.service';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';


@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatToolbarModule
  ],
  templateUrl: './admin.html',
  styleUrls: ['./admin.scss']
})
export class AdminComponent implements OnInit {
  articleForm: FormGroup;
  editMode = false;
  editId: number | null = null;
  loading = false;
  error: string | null = null;
  success: string | null = null;

  constructor(
    private fb: FormBuilder,
    private articleService: ArticleService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.articleForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(5)]],
      content: ['', [Validators.required, Validators.minLength(20)]],
      author: ['', Validators.required]
    });
  }

  ngOnInit(): void {

    this.route.queryParams.subscribe(params => {
      if (params['editId']) {
        this.editId = +params['editId'];
        this.editMode = true;
        this.loadArticleForEdit(this.editId);
      }
    });
  }

  loadArticleForEdit(id: number): void {
    this.loading = true;
    this.articleService.getArticle(id).subscribe({
      next: (article) => {
        if (article) {
          this.articleForm.patchValue({
            title: article.title,
            content: article.content,
            author: article.author || ''
          });
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load article for editing';
        this.loading = false;
        console.error('Error:', err);
      }
    });
  }

  onSubmit(): void {
    if (this.articleForm.invalid) {
      this.error = 'Please fill in all required fields correctly';
      return;
    }

    this.loading = true;
    this.error = null;
    this.success = null;

    const formValue = this.articleForm.value;

    if (this.editMode && this.editId) {
   
      this.articleService.updateArticle(
        this.editId,
        formValue.title,
        formValue.content,
        formValue.author
      ).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success) {
            this.success = 'Article updated successfully!';
            setTimeout(() => {
              this.router.navigate(['/posts', this.editId]);
            }, 1500);
          } else {
            this.error = response.message || 'Failed to update article';
          }
        },
        error: (err) => {
          this.loading = false;
          this.error = 'Failed to update article';
          console.error('Error:', err);
        }
      });
    } else {
    
      this.articleService.createArticle(
        formValue.title,
        formValue.content,
        formValue.author
      ).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success) {
            this.success = 'Article created successfully!';
            this.articleForm.reset();
            if (response.article) {
              setTimeout(() => {
                this.router.navigate(['/posts', response.article!.id]);
              }, 1500);
            }
          } else {
            this.error = response.message || 'Failed to create article';
          }
        },
        error: (err) => {
          this.loading = false;
          this.error = 'Failed to create article';
          console.error('Error:', err);
        }
      });
    }
  }

  cancel(): void {
    if (this.editMode && this.editId) {
      this.router.navigate(['/posts', this.editId]);
    } else {
      this.router.navigate(['/posts']);
    }
  }

  getErrorMessage(fieldName: string): string {
    const field = this.articleForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
    }
    if (field?.hasError('minlength')) {
      const minLength = field.errors?.['minlength'].requiredLength;
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least ${minLength} characters`;
    }
    return '';
  }
}