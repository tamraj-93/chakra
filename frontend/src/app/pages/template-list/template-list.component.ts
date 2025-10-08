import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TemplateService } from '../../services/template.service';
import { ConsultationTemplate } from '../../services/consultation.service';
import { HealthcareTemplateService } from '../../services/healthcare-template.service';

@Component({
  selector: 'app-template-list',
  template: `
    <div class="container mt-4">
      <h2>Consultation Templates</h2>
      <p class="text-muted">Choose a template to start a guided consultation</p>
      
      <!-- Loading state -->
      <div *ngIf="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <!-- Error state -->
      <div *ngIf="error" class="alert alert-danger">
        {{ error }}
      </div>

      <!-- Healthcare Template section -->
      <div *ngIf="healthcareTemplates.length > 0">
        <h3 class="mt-4">Healthcare Templates</h3>
        <div class="row">
          <div *ngFor="let template of healthcareTemplates" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 template-card healthcare-template">
              <div class="card-header bg-info text-white">
                Healthcare Template
              </div>
              <div class="card-body">
                <h5 class="card-title">{{ template.name }}</h5>
                <div class="template-domain mb-2">{{ template.domain }}</div>
                <p class="card-text">{{ template.description }}</p>
                <div class="template-tags mb-3">
                  <span *ngFor="let tag of template.tags" class="badge bg-light text-dark me-1">
                    {{ tag }}
                  </span>
                </div>
              </div>
              <div class="card-footer bg-transparent">
                <button class="btn btn-info" (click)="startHealthcareConsultation(template)">
                  Start Healthcare Consultation
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Standard Template list -->
      <div *ngIf="!loading && templates.length > 0" class="row">
        <h3 class="mt-4">Standard Templates</h3>
        <div *ngFor="let template of templates" class="col-md-6 col-lg-4 mb-4">
          <div class="card h-100 template-card">
            <div class="card-body">
              <h5 class="card-title">{{ template.name }}</h5>
              <div class="template-domain mb-2">{{ template.domain }}</div>
              <p class="card-text">{{ template.description }}</p>
              <div class="template-tags mb-3">
                <span *ngFor="let tag of template.tags" class="badge bg-light text-dark me-1">
                  {{ tag }}
                </span>
              </div>
              <div class="template-info mb-3">
                <small class="text-muted">
                  <i class="bi bi-layers"></i> {{ template.stages.length || 0 }} stages
                </small>
              </div>
            </div>
            <div class="card-footer bg-transparent">
              <button class="btn btn-primary" (click)="startConsultation(template.id)">
                Start Consultation
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty state -->
      <div *ngIf="!loading && templates.length === 0" class="text-center my-5">
        <div class="display-6 text-muted mb-3">No templates available</div>
        <p>There are currently no consultation templates available.</p>
      </div>
    </div>
  `,
  styles: [`
    .template-card {
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      border: 1px solid #eaeaea;
    }
    
    .template-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .template-domain {
      font-size: 0.9rem;
      color: #6c757d;
    }
    
    .template-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
    
    .template-tags .badge {
      font-weight: normal;
      font-size: 0.8rem;
    }

    .healthcare-template {
      border: 1px solid #17a2b8;
    }

    .healthcare-template .card-header {
      background-color: #17a2b8 !important;
    }

    .healthcare-template:hover {
      box-shadow: 0 10px 20px rgba(23, 162, 184, 0.2);
    }
  `]
})
export class TemplateListComponent implements OnInit {
  templates: ConsultationTemplate[] = [];
  healthcareTemplates: any[] = [];
  loading = false;
  error = '';
  
  constructor(
    private templateService: TemplateService,
    private healthcareTemplateService: HealthcareTemplateService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.loadTemplates();
    this.loadHealthcareTemplates();
  }
  
  loadTemplates(): void {
    this.loading = true;
    this.error = '';
    
    this.templateService.getConsultationTemplates()
      .subscribe({
        next: (templates) => {
          this.templates = templates;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading templates:', err);
          this.error = 'Failed to load templates. Please try again later.';
          this.loading = false;
        }
      });
  }
  
  loadHealthcareTemplates(): void {
    this.healthcareTemplateService.getHealthcareTemplates()
      .subscribe({
        next: (templates) => {
          this.healthcareTemplates = templates;
          console.log('Healthcare templates loaded:', this.healthcareTemplates);
        },
        error: (err) => {
          console.error('Error loading healthcare templates:', err);
        }
      });
  }
  
  startConsultation(templateId: string): void {
    this.router.navigate(['/template-consultation', templateId]);
  }
  
  startHealthcareConsultation(template: any): void {
    console.log('Starting healthcare consultation with template:', template);
    
    // Remove alerts for production use
    // alert('Starting healthcare consultation for template: ' + template.name);
    
    // Use the healthcare template service to start the consultation
    this.healthcareTemplateService.startHealthcareConsultation(template.id)
      .subscribe({
        next: (response) => {
          console.log('Healthcare consultation started:', response);
          // alert('Response received: ' + JSON.stringify(response));
          
          // The response format changed for our new endpoint
          // New endpoint returns { message, session_id, template }
          if (response && response.session_id) {
            // Navigate to the consultation page with the session ID
            this.router.navigate(['/consultation'], { queryParams: { session_id: response.session_id } });
          } else {
            console.error('No session ID received from healthcare consultation');
            // Fallback to standard template consultation
            this.router.navigate(['/template-consultation', template.id]);
          }
        },
        error: (err) => {
          console.error('Error starting healthcare consultation:', err);
          // Fallback to standard template consultation
          this.router.navigate(['/template-consultation', template.id]);
        }
      });
  }
}