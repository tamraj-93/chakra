export interface StructuredOutput {
  stageId: string;
  stageName: string;
  stageNumber: number;
  data: Record<string, any>;
  timestamp: Date;
}

export interface ConsultationSummary {
  consultationId?: number; // Same as sessionId
  templateId: string;
  templateName: string;
  outputs: StructuredOutput[];
  startTime?: Date;
  completedAt?: Date; // When the consultation was completed
  completed: boolean;
  sessionId?: number | undefined; // Can be undefined initially before session is created
  keyFindings?: string[];
  recommendations?: string[];
  summary?: Record<string, any>; // Generated summary data from outputs
}