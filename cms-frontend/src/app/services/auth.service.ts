import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_admin: boolean;
  is_active: boolean;
}

export interface AuthResponse {
  success: boolean;
  message?: string;
  user?: User;
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
   
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    const userJson = localStorage.getItem('current_user');
    if (userJson) {
      try {
        const user = JSON.parse(userJson);
        this.currentUserSubject.next(user);
      } catch (e) {
        console.error('Error parsing user from storage', e);
      }
    }
  }

  register(username: string, email: string, password: string, firstName?: string, lastName?: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/register`, {
      username,
      email,
      password,
      first_name: firstName,
      last_name: lastName
    }).pipe(
      tap(response => {
        if (response.success && response.access_token) {
          this.handleAuthSuccess(response);
        }
      })
    );
  }

  login(usernameOrEmail: string, password: string): Observable<AuthResponse> {
    const payload: any = { password };
    
    
    if (usernameOrEmail.includes('@')) {
      payload.email = usernameOrEmail;
    } else {
      payload.username = usernameOrEmail;
    }

    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/login`, payload).pipe(
      tap(response => {
        if (response.success && response.access_token) {
          this.handleAuthSuccess(response);
        }
      })
    );
  }

  logout(): Observable<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    return this.http.post(`${this.apiUrl}/api/auth/logout`, {
      refresh_token: refreshToken
    }, {
      headers: this.getAuthHeaders()
    }).pipe(
      tap(() => {
        this.clearAuthData();
      })
    );
  }

  refreshToken(): Observable<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/refresh`, {
      refresh_token: refreshToken
    }).pipe(
      tap(response => {
        if (response.success && response.access_token) {
          localStorage.setItem('access_token', response.access_token);
        }
      })
    );
  }

  getProfile(): Observable<{ success: boolean; user: User }> {
    return this.http.get<{ success: boolean; user: User }>(
      `${this.apiUrl}/api/auth/me`,
      { headers: this.getAuthHeaders() }
    ).pipe(
      tap(response => {
        if (response.success && response.user) {
          this.currentUserSubject.next(response.user);
          localStorage.setItem('current_user', JSON.stringify(response.user));
        }
      })
    );
  }

  updateProfile(data: Partial<User>): Observable<{ success: boolean; user: User; message: string }> {
    return this.http.put<{ success: boolean; user: User; message: string }>(
      `${this.apiUrl}/api/auth/me`,
      data,
      { headers: this.getAuthHeaders() }
    ).pipe(
      tap(response => {
        if (response.success && response.user) {
          this.currentUserSubject.next(response.user);
          localStorage.setItem('current_user', JSON.stringify(response.user));
        }
      })
    );
  }

  changePassword(currentPassword: string, newPassword: string, logoutAllDevices: boolean = false): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/api/auth/change-password`,
      {
        current_password: currentPassword,
        new_password: newPassword,
        logout_all_devices: logoutAllDevices
      },
      { headers: this.getAuthHeaders() }
    );
  }

  private handleAuthSuccess(response: AuthResponse): void {
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
    }
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    if (response.user) {
      this.currentUserSubject.next(response.user);
      localStorage.setItem('current_user', JSON.stringify(response.user));
    }
  }

  private clearAuthData(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
  }

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.is_admin || false;
  }
}