import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Document {
  id: string;
  filename: string;
  title: string;
  industry?: string;
  service_type?: string;
  upload_date: string;
  file_size: number;
  status: 'processed' | 'pending' | 'error';
}

@Injectable({
  providedIn: 'root'
})
export class KnowledgeBaseService {
  private apiUrl = environment.apiUrl + '/api/v1/documents';

  constructor(private http: HttpClient) { }

  getDocuments(): Observable<Document[]> {
    return this.http.get<Document[]>(this.apiUrl);
  }

  getDocument(id: string): Observable<Document> {
    return this.http.get<Document>(`${this.apiUrl}/${id}`);
  }

  uploadDocuments(files: File[]): Observable<HttpEvent<any>> {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });

    const request = new HttpRequest('POST', `${this.apiUrl}/upload`, formData, {
      reportProgress: true,
    });

    return this.http.request(request);
  }

  deleteDocument(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  updateDocumentMetadata(id: string, metadata: Partial<Document>): Observable<Document> {
    return this.http.patch<Document>(`${this.apiUrl}/${id}`, metadata);
  }

  searchDocuments(query: string, filters?: Record<string, any>): Observable<Document[]> {
    let url = `${this.apiUrl}/search?query=${encodeURIComponent(query)}`;
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          url += `&${key}=${encodeURIComponent(String(value))}`;
        }
      });
    }
    
    return this.http.get<Document[]>(url);
  }
}