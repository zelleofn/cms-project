import { TestBed } from '@angular/core/testing';
import { AuthGuard } from './auth-guard';
import { AuthService } from '../services/auth.service';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authService: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AuthGuard, AuthService] 
    });
    guard = TestBed.inject(AuthGuard); 
    authService = TestBed.inject(AuthService); 
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

 it('should allow activation', () => {
  jest.spyOn(authService, 'isAuthenticated').mockReturnValue(true);
  jest.spyOn(authService, 'isAdmin').mockReturnValue(true);

  const route = { data: { requireAdmin: true } } as any; 
  const state = {} as any;

  expect(guard.canActivate(route, state)).toBe(true);

});
});