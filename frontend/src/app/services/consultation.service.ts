import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// Define interfaces locally
interface SourceCitation {
  title: string;
  source: string;
  relevance?: number;
  content_snippet?: string;
}

interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
  stageId?: string;
  sources?: SourceCitation[];  // Add sources field for RAG citations
}

interface ConsultationSession {
  id: number;
  userId: number;
  sessionType: 'discovery' | 'template_creation' | 'analysis' | 'template_guided';
  contextData: Record<string, any>;
  recommendations: Record<string, any>;
  createdAt: string;
  template_id?: string;
  session_state?: {
    current_stage?: string;
    completed_stages?: string[];
    stage_data?: Record<string, any>;
  };
}

export interface TemplateStage {
  id: string;
  name: string;
  description: string;
  stage_type: string;
  prompt_template: string;
  system_instructions?: string;
  expected_outputs: ExpectedOutput[];
  ui_components?: Record<string, any>;
  next_stage_conditions?: Record<string, any>;
}

export interface ExpectedOutput {
  name: string;
  description: string;
  data_type: string;
  required: boolean;
}

export interface ConsultationTemplate {
  id: string;
  name: string;
  description: string;
  domain: string;
  version: string;
  initial_system_prompt: string;
  stages: TemplateStage[];
  tags: string[];
  is_public: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TemplateConsultationResponse {
  message: Message;
  session_id: number;
  sources?: SourceCitation[];  // Add support for RAG citation sources
  template_progress: {
    // Support the new API response format
    completed_stage?: string;
    completed_stage_index?: number;
    next_stage?: {
      description?: string;
      name?: string;
      type?: string;
    };
    progress_percentage?: number;
    
    // Legacy/expected properties
    current_stage?: number;
    total_stages?: number;
    stage_name?: string;
    stage_description?: string;
    stage_id?: string;
    completed_stages?: string[];
    ui_components?: {
      structured_input?: {
        fields: Array<{
          id: string;
          label: string;
          type: string;
          options?: Array<{value: string, label: string}>;
          placeholder?: string;
          required?: boolean;
          help_text?: string;
        }>;
        prompt?: string;
      }
    };
  };
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
   * Start a template-based consultation
   */
  startTemplateConsultation(templateId: string): Observable<TemplateConsultationResponse> {
    return this.http.post<TemplateConsultationResponse>(
      `${this.apiUrl}/chat?template_id=${templateId}`, 
      {
        content: "Start template consultation",
        role: 'user'
      }
    );
  }

  /**
   * Start a healthcare template-based consultation
   */
  startHealthcareTemplateConsultation(templateId: string): Observable<TemplateConsultationResponse> {
    return this.http.post<TemplateConsultationResponse>(
      `${this.apiUrl}/chat?healthcare_template_id=${templateId}`, 
      {
        content: "Start healthcare template consultation",
        role: 'user'
      }
    );
  }

  /**
   * Send a message in a template-based consultation
   */
  sendTemplateMessage(message: string, sessionId: number): Observable<TemplateConsultationResponse> {
    const payload = {
      content: message,
      role: 'user'
    };
    
    return this.http.post<TemplateConsultationResponse>(
      `${this.apiUrl}/chat?session_id=${sessionId}`, 
      payload
    );
  }

  /**
   * Submit structured data in a template-based consultation
   */
  submitStructuredInput(data: Record<string, any>, sessionId: number): Observable<TemplateConsultationResponse> {
    const payload = {
      content: JSON.stringify(data),
      role: 'user',
      is_structured_input: true
    };
    
    return this.http.post<TemplateConsultationResponse>(
      `${this.apiUrl}/chat?session_id=${sessionId}`,
      payload
    );
  }

  /**
   * Get all consultation sessions for the current user
   */
  getUserSessions(): Observable<ConsultationSession[]> {
    return this.http.get<ConsultationSession[]>(`${this.apiUrl}/sessions`);
  }

  /**
   * Get template-based consultation sessions for the current user
   */
  getTemplateConsultations(): Observable<ConsultationSession[]> {
    return this.http.get<ConsultationSession[]>(
      `${this.apiUrl}/sessions?session_type=template_guided`
    );
  }

  /**
   * Get a specific consultation session
   */
  getSession(sessionId: number): Observable<ConsultationSession> {
    return this.http.get<ConsultationSession>(`${this.apiUrl}/sessions/${sessionId}`);
  }
  
  /**
   * Get all messages for a consultation session
   */
  getSessionMessages(sessionId: number): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/sessions/${sessionId}/messages`);
  }
  
  /**
   * Get current template progress for a session
   */
  getTemplateProgress(sessionId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/sessions/${sessionId}/progress`);
  }
  
  /**
   * Force progression to the next stage in a template consultation
   * This is useful when automatic stage detection fails
   */
  forceNextStage(sessionId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/sessions/${sessionId}/force-next-stage`, {});
  }
  
  /**
   * Check if the current stage in a template consultation is complete
   * Returns information about completion status and extracted data
   */
  checkStageCompletion(sessionId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/sessions/${sessionId}/check-stage-completion`);
  }

  /**
   * Extract a template from an existing consultation
   * This analyzes the conversation patterns to create a reusable template
   */
  extractTemplateFromConsultation(sessionId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/sessions/${sessionId}/extract-template`, {});
  }
}