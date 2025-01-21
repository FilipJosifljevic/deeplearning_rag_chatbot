import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000/query/';

  constructor(private http: HttpClient) {}

  sendQuery(query: string): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { query }; 

    return this.http.post<any>(this.apiUrl, body, { headers });
  }
}
