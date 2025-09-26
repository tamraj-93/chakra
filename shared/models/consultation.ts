/**
 * Message in a consultation session
 */
export interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
}

/**
 * Consultation session information
 */
export interface ConsultationSession {
  id: number;
  userId: number;
  sessionType: 'discovery' | 'template_creation' | 'analysis';
  contextData: Record<string, any>;
  recommendations: Record<string, any>;
  createdAt: string;
}