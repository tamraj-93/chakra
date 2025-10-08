import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TemplateService } from '../../services/template.service';
import { ConsultationService, ConsultationTemplate } from '../../services/consultation.service';

@Component({
  selector: 'app-template-selection',
  template: `
    <div class="template-selection-container">
      <div class="section-header">
        <h2>Consultation Templates</h2>
        <p class="text-muted">Select a template to start a guided consultation</p>
      </div>
      
      <!-- Filters -->
      <div class="filters-container">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-search"></i></span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search templates..." 
                [(ngModel)]="searchQuery"
                (input)="applyFilters()">
            </div>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" [(ngModel)]="selectedDomain" (change)="applyFilters()">
              <option value="">All Domains</option>
              <option *ngFor="let domain of domains" [value]="domain">{{ domain }}</option>
            </select>
          </div>
          
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" (click)="resetFilters()">
              <i class="bi bi-x-circle"></i> Reset
            </button>
          </div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div *ngIf="loading" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading templates...</p>
      </div>
      
      <!-- Error State -->
      <div *ngIf="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill"></i> {{ error }}
      </div>
      
      <!-- Empty State -->
      <div *ngIf="!loading && !error && filteredTemplates.length === 0" class="empty-state">
        <i class="bi bi-folder-x display-1 text-muted"></i>
        <p class="lead">No templates found</p>
        <p class="text-muted">Try changing your search criteria or create a new template</p>
      </div>
      
      <!-- Templates Grid -->
      <div *ngIf="!loading && !error && filteredTemplates.length > 0" class="templates-grid">
        <div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
          <div *ngFor="let template of filteredTemplates" class="col">
            <div class="template-card">
              <div class="template-header">
                <h3 class="template-name">{{ template.name }}</h3>
                <div class="template-domain" *ngIf="template.domain">{{ template.domain }}</div>
              </div>
              
              <div class="template-body">
                <p class="template-description">{{ template.description }}</p>
                
                <div class="template-meta">
                  <div class="template-stages">
                    <i class="bi bi-list-check"></i> {{ template.stages.length }} stages
                  </div>
                  
                  <div class="template-tags">
                    <span *ngFor="let tag of template.tags.slice(0, 3)" class="template-tag">
                      {{ tag }}
                    </span>
                    <span *ngIf="template.tags.length > 3" class="template-tag more-tag">
                      +{{ template.tags.length - 3 }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="template-footer">
                <button class="btn btn-sm btn-outline-secondary" 
                        (click)="previewTemplate(template)">
                  <i class="bi bi-eye"></i> Preview
                </button>
                <button class="btn btn-sm btn-primary" 
                        (click)="startConsultation(template)">
                  <i class="bi bi-play-fill"></i> Start Consultation
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .template-selection-container {
      padding: 20px;
    }
    
    .section-header {
      margin-bottom: 30px;
    }
    
    .filters-container {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 30px;
    }
    
    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px;
    }
    
    .loading-container p {
      margin-top: 15px;
      color: #6c757d;
    }
    
    .empty-state {
      text-align: center;
      padding: 60px 0;
      color: #6c757d;
    }
    
    .template-card {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      overflow: hidden;
    }
    
    .template-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .template-header {
      padding: 15px;
      border-bottom: 1px solid #e9ecef;
      background-color: #f8f9fa;
    }
    
    .template-name {
      font-size: 1.2rem;
      margin-bottom: 5px;
      color: #212529;
    }
    
    .template-domain {
      font-size: 0.85rem;
      color: #6c757d;
      font-weight: 500;
    }
    
    .template-body {
      padding: 15px;
      flex-grow: 1;
    }
    
    .template-description {
      margin-bottom: 15px;
      color: #495057;
      font-size: 0.9rem;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .template-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: auto;
    }
    
    .template-stages {
      font-size: 0.85rem;
      color: #6c757d;
    }
    
    .template-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
    
    .template-tag {
      font-size: 0.75rem;
      background-color: #e9ecef;
      color: #495057;
      padding: 2px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }
    
    .more-tag {
      background-color: #6c757d;
      color: white;
    }
    
    .template-footer {
      padding: 15px;
      border-top: 1px solid #e9ecef;
      display: flex;
      justify-content: space-between;
    }
  `]
})
export class TemplateSelectionComponent implements OnInit {
  templates: ConsultationTemplate[] = [];
  filteredTemplates: ConsultationTemplate[] = [];
  domains: string[] = [];
  loading = false;
  error = '';
  
  // Filters
  searchQuery = '';
  selectedDomain = '';
  
  constructor(
    private templateService: TemplateService,
    private consultationService: ConsultationService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.loadTemplates();
  }
  
  loadTemplates(): void {
    this.loading = true;
    this.error = '';
    
    this.templateService.getConsultationTemplates().subscribe({
      next: (templates) => {
        this.templates = templates;
        this.filteredTemplates = [...templates];
        this.extractDomains();
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading templates:', err);
        this.error = 'Failed to load templates. Please try again later.';
        this.loading = false;
      }
    });
  }
  
  extractDomains(): void {
    // Extract unique domains from templates
    const domainsSet = new Set(this.templates.map(t => t.domain));
    this.domains = Array.from(domainsSet).sort();
  }
  
  applyFilters(): void {
    this.filteredTemplates = this.templates.filter(template => {
      // Filter by search query
      const matchesSearch = this.searchQuery ? 
        (template.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
         template.description.toLowerCase().includes(this.searchQuery.toLowerCase())) : 
        true;
      
      // Filter by domain
      const matchesDomain = this.selectedDomain ? 
        template.domain === this.selectedDomain : 
        true;
      
      return matchesSearch && matchesDomain;
    });
  }
  
  resetFilters(): void {
    this.searchQuery = '';
    this.selectedDomain = '';
    this.filteredTemplates = [...this.templates];
  }
  
  previewTemplate(template: ConsultationTemplate): void {
    // Navigate to template detail/preview page
    this.router.navigate(['/templates', template.id]);
  }
  
  startConsultation(template: ConsultationTemplate): void {
    this.loading = true;
    
    this.consultationService.startTemplateConsultation(template.id).subscribe({
      next: (response) => {
        this.loading = false;
        // Navigate to the consultation page with the session ID
        this.router.navigate(['/consultation', response.session_id]);
      },
      error: (err) => {
        console.error('Error starting consultation:', err);
        this.error = 'Failed to start consultation. Please try again later.';
        this.loading = false;
      }
    });
  }
}