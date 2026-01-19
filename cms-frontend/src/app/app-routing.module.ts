import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Posts } from './components/posts/posts';
import { PostDetail } from './components/post-detail/post-detail';
import { Admin } from './components/admin/admin';
import { Login } from './components/login/login';
import { Register } from './components/register/register';
import { AuthGuard } from './guards/auth-guard';

const routes: Routes = [
  { path: '', component: Home },
  { path: 'posts', component: Posts },
  { path: 'posts/:id', component: PostDetail },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  {
    path: 'admin',
    component: Admin,
    canActivate: [AuthGuard],
    data: { requireAdmin: true }
  },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}