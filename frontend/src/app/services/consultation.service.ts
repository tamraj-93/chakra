import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// Define interfaces locally
interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
}

interface ConsultationSession {
  id: number;
  userId: number;
  sessionType: 'discovery' | 'template_creation' | 'analysis';
  contextData: Record<string, any>;
  recommendations: Record<string, any>;
  createdAt: string;
}

@Injectable({
  providedIn: 'root'
})
export class ConsultationService {
  private apiUrl = `${environment.apiUrl}/api/consultation`;

  constructor(private http: HttpClient) { }

  /**
   * Send a message to the AI assistant
   */
  sendMessage(message: string, sessionId?: number): Observable<any> {
    const payload: any = {
      content: message,
      role: 'user'
    };
    
    if (sessionId) {
      return this.http.post(`${this.apiUrl}/chat?session_id=${sessionId}`, payload);
    } else {
      return this.http.post(`${this.apiUrl}/chat`, payload);
    }
  }

  /**
   * Get all consultation sessions for the current user
   */
  getUserSessions(): Observable<ConsultationSession[]> {
    return this.http.get<ConsultationSession[]>(`${this.apiUrl}/sessions`);
  }

  /**
   * Get a specific consultation session
   */
  getSession(sessionId: number): Observable<ConsultationSession> {
    return this.http.get<ConsultationSession>(`${this.apiUrl}/sessions/${sessionId}`);
  }
}