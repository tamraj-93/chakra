import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

interface TemplateGenerationRequest {
  session_id: number;
  template_name: string;
  template_description?: string;
  domain?: string;
  is_public?: boolean;
}

interface TemplateGenerationResponse {
  template_id: string;
  name: string;
  stages_count: number;
  tags: string[];
}

interface EligibleSession {
  id: number;
  created_at: string;
  name: string;
  message_count: number;
  sla_relevance: 'high' | 'medium' | 'low';
  preview: string;
}

interface SessionDetails {
  id: number;
  created_at: string;
  user_id: number;
  messages: Array<{
    id: number;
    content: string;
    role: string;
    timestamp: string;
  }>;
  context_data: Record<string, any>;
}

@Injectable({
  providedIn: 'root'
})
export class TemplateGeneratorService {
  private apiUrl = `${environment.apiUrl}/api/template_generator`;

  constructor(private http: HttpClient) { }

  /**
   * Convert an SLA consultation session into a reusable template
   */
  convertSlaToTemplate(request: TemplateGenerationRequest): Observable<TemplateGenerationResponse> {
    return this.http.post<TemplateGenerationResponse>(
      `${this.apiUrl}/convert-sla`,
      request
    );
  }

  /**
   * Get sessions eligible for conversion to templates
   */
  getEligibleSessions(): Observable<EligibleSession[]> {
    return this.http.get<EligibleSession[]>(`${this.apiUrl}/eligible-sessions`);
  }
  
  /**
   * Get detailed information about a specific session
   */
  getEligibleSessionDetails(sessionId: number): Observable<SessionDetails> {
    return this.http.get<SessionDetails>(`${this.apiUrl}/session-details/${sessionId}`);
  }
}