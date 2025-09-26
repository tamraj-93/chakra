import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// Define interfaces locally
interface SLATemplate {
  id: number;
  name: string;
  description: string;
  industry: string;
  serviceType: string;
  metrics: SLAMetric[];
  template: string;
  createdBy?: number;
  createdAt: string;
}

interface SLAMetric {
  id: number;
  name: string;
  description: string;
  category: string;
  unit: string;
  thresholds: Record<string, number>;
}

@Injectable({
  providedIn: 'root'
})
export class TemplateService {
  private apiUrl = `${environment.apiUrl}/templates`;

  constructor(private http: HttpClient) { }

  /**
   * Get all templates with optional filtering
   */
  getTemplates(industry?: string, serviceType?: string): Observable<SLATemplate[]> {
    let url = this.apiUrl;
    const params: any = {};
    
    if (industry) params.industry = industry;
    if (serviceType) params.service_type = serviceType;
    
    return this.http.get<SLATemplate[]>(url, { params });
  }

  /**
   * Get a specific template
   */
  getTemplate(templateId: number): Observable<SLATemplate> {
    return this.http.get<SLATemplate>(`${this.apiUrl}/${templateId}`);
  }

  /**
   * Create a new SLA template
   */
  createTemplate(templateData: any): Observable<SLATemplate> {
    return this.http.post<SLATemplate>(this.apiUrl, templateData);
  }

  /**
   * Get SLA metrics with optional category filtering
   */
  getMetrics(category?: string): Observable<SLAMetric[]> {
    let url = `${this.apiUrl}/metrics`;
    const params: any = {};
    
    if (category) params.category = category;
    
    return this.http.get<SLAMetric[]>(url, { params });
  }

  /**
   * Generate a new SLA template document based on specified parameters
   */
  generateTemplate(data: {
    service_name: string;
    service_type: string;
    description: string;
    metrics: string[];
  }): Observable<{ template_url: string }> {
    return this.http.post<{ template_url: string }>(`${this.apiUrl}/generate`, data);
  }
}