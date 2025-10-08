import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { TemplateService } from './template.service';
import { ConsultationService, TemplateConsultationResponse } from './consultation.service';

@Injectable({
  providedIn: 'root'
})
export class HealthcareTemplateService {
  private apiUrl = `${environment.apiUrl}/api/v1/healthcare-templates`;
  private consultationUrl = `${environment.apiUrl}/api/consultation`;

  constructor(
    private http: HttpClient,
    private templateService: TemplateService
  ) {}

  /**
   * Get all healthcare templates
   */
  getHealthcareTemplates(): Observable<any[]> {
    return this.templateService.getHealthcareTemplates();
  }

  /**
   * Get a specific healthcare template by ID
   */
  getHealthcareTemplate(id: string): Observable<any> {
    return this.templateService.getHealthcareTemplate(id);
  }

  /**
   * Start a healthcare template-based consultation
   */
  startHealthcareConsultation(templateId: string): Observable<any> {
    console.log(`Starting healthcare consultation with template ID: ${templateId}`);
    const url = `${environment.apiUrl}/api/v1/healthcare-consultation/start?template_id=${templateId}`;
    console.log(`API URL: ${url}`);
    
    return this.http.post<any>(
      url, 
      {
        content: "Start healthcare template consultation",
        role: 'user'
      }
    );
  }
}