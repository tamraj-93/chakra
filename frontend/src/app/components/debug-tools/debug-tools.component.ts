import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

interface Template {
  id: string;
  name: string;
  description: string;
  stages: any[];
}

@Component({
  selector: 'app-debug-tools',
  templateUrl: './debug-tools.component.html',
  styleUrls: []
})
export class DebugToolsComponent implements OnInit {
  templates: Template[] = [];
  loading = false;
  error = '';
  apiResponse: any = null;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.loading = true;
    this.error = '';
    
    this.http.get<Template[]>(`${environment.apiUrl}/api/consultation_templates/templates`)
      .subscribe({
        next: (templates) => {
          this.templates = templates;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading templates:', err);
          this.error = 'Failed to load templates. Check console for details.';
          this.loading = false;
        }
      });
  }

  startConsultation(templateId: string): void {
    this.router.navigate(['/template-consultation', templateId]);
  }

  testTemplatesAPI(): void {
    this.apiResponse = null;
    this.http.get(`${environment.apiUrl}/api/consultation_templates/templates`)
      .subscribe({
        next: (response) => {
          this.apiResponse = response;
        },
        error: (err) => {
          this.apiResponse = { error: err.message };
        }
      });
  }

  testConsultationAPI(): void {
    this.apiResponse = null;
    this.http.get(`${environment.apiUrl}/api/consultation`)
      .subscribe({
        next: (response) => {
          this.apiResponse = response;
        },
        error: (err) => {
          this.apiResponse = { error: err.message };
        }
      });
  }
}