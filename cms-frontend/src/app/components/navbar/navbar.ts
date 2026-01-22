import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatChipsModule,
    MatDividerModule
  ],
  templateUrl: './navbar.html',
  styleUrls: ['./navbar.scss']
})
export class NavbarComponent implements OnInit {
  currentUser$: Observable<User | null>;
  isAuthenticated = false;
  isAdmin = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.currentUser$ = this.authService.currentUser$;
  }

  ngOnInit(): void {
   
    this.currentUser$.subscribe(user => {
      this.isAuthenticated = !!user;
      this.isAdmin = user?.is_admin || false;
    });
  }

 logout(): void {
  this.authService.logout().subscribe({
    next: () => {
      this.finalizeLogout();
    },
    error: (err) => {
      console.error('Logout error from server:', err);
    
      this.finalizeLogout();
    }
  });
}

private finalizeLogout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  this.router.navigate(['/login']);
}

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}