import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) {}
  
  getApi() {
    return this.http.get(`${environment.apiUrl}/api/endpoint`);
  }

  getHealth() {
    return this.http.get(`${environment.apiUrl}/health`);
  }
  
  getGraphql(query: string) {
    return this.http.post(`${environment.graphqlUrl}`, { query });
  }
}