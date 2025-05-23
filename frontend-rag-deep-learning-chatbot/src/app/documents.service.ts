import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class DocumentsService {
  private apiUrl = '/api/documents/';

  constructor(private http: HttpClient) { }

  getDocuments(): Observable<string[]> {
    return this.http.get<string[]>(this.apiUrl);
  }
}
