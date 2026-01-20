import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home';
import { PostsComponent } from './components/posts/posts';
import { PostDetailComponent } from './components/post-detail/post-detail';
import { AdminComponent } from './components/admin/admin';
import { LoginComponent } from './components/login/login';
import { RegisterComponent } from './components/register/register';
import { AuthGuard } from './guards/auth-guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'posts', component: PostsComponent },
  { path: 'posts/:id', component: PostDetailComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [AuthGuard],
    data: { requireAdmin: true }
  },
  { path: '**', redirectTo: '' }
];



