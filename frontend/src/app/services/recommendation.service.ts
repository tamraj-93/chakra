import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// Define interfaces for template recommendations
export interface TemplateRecommendation {
  id: number;
  name: string;
  description: string;
  industry: string;
  service_type: string;
  similarity_score: number;
  match_reason: string;
}

export interface TemplateRequirements {
  service_type: string;
  description: string;
  industry?: string;
  metrics?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class RecommendationService {
  private apiUrl = `${environment.apiUrl}/api/templates`;

  constructor(private http: HttpClient) { }

  /**
   * Get template recommendations based on user requirements
   */
  getTemplateRecommendations(
    requirements: TemplateRequirements, 
    limit: number = 3
  ): Observable<TemplateRecommendation[]> {
    return this.http.post<TemplateRecommendation[]>(
      `${this.apiUrl}/recommend`, 
      requirements,
      { params: { limit: limit.toString() } }
    );
  }
}