/**
 * SLA Metric definition
 */
export interface SLAMetric {
  id: number;
  name: string;
  category: 'availability' | 'performance' | 'security' | 'support';
  unitOfMeasure: string;
  calculationMethod: string;
  industryBenchmarks: Record<string, any>;
  complianceMappings: Record<string, any>;
}

/**
 * SLA Template definition
 */
export interface SLATemplate {
  id: number;
  userId: number;
  name: string;
  industry: string;
  serviceType: string;
  templateData: Record<string, any>;
  isPublic: boolean;
  createdAt: string;
}