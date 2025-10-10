import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TemplateService } from '../../services/template.service';
import { ConsultationTemplate } from '../../services/consultation.service';
import { HealthcareTemplateService } from '../../services/healthcare-template.service';

// Define interface for categorized templates
interface CategorizedTemplates {
  [category: string]: ConsultationTemplate[];
}

@Component({
  selector: 'app-template-list',
  template: `
    <div class="container mt-4">
      <div class="row align-items-center mb-4">
        <div class="col">
          <h2>Industry-Specific SLA Templates</h2>
          <p class="text-muted">Choose a template to start a guided consultation for your industry</p>
        </div>
        <div class="col-auto">
          <div class="btn-group category-filter" role="group">
            <button *ngFor="let category of categories"
                    type="button"
                    class="btn"
                    [class.btn-primary]="activeCategory === category"
                    [class.btn-outline-primary]="activeCategory !== category"
                    (click)="filterByCategory(category)">
              {{ category }}
            </button>
          </div>
        </div>
      </div>
      
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

      <!-- Healthcare Templates -->
      <div *ngIf="healthcareTemplates.length > 0 && (activeCategory === 'All' || activeCategory === 'Healthcare')">
        <div class="category-header healthcare">
          <div class="category-icon">
            <i class="bi bi-heart-pulse"></i>
          </div>
          <h3>Healthcare Templates</h3>
        </div>
        <div class="row">
          <div *ngFor="let template of healthcareTemplates" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 template-card healthcare-template">
              <div class="card-header bg-info text-white">
                <i class="bi bi-heart-pulse me-2"></i>Healthcare Template
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
                  <i class="bi bi-play-circle me-1"></i> Start Healthcare SLA
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Infrastructure Templates -->
      <div *ngIf="infrastructureTemplates.length > 0 && (activeCategory === 'All' || activeCategory === 'Infrastructure')">
        <div class="category-header infrastructure">
          <div class="category-icon">
            <i class="bi bi-hdd-rack"></i>
          </div>
          <h3>Infrastructure Templates</h3>
        </div>
        <div class="row">
          <div *ngFor="let template of infrastructureTemplates" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 template-card infrastructure-template">
              <div class="card-header bg-success text-white">
                <i class="bi bi-hdd-rack me-2"></i>Infrastructure Template
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
                <button class="btn btn-success" (click)="startConsultation(template.id)">
                  <i class="bi bi-play-circle me-1"></i> Start Infrastructure SLA
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Finance Templates -->
      <div *ngIf="financeTemplates.length > 0 && (activeCategory === 'All' || activeCategory === 'Finance')">
        <div class="category-header finance">
          <div class="category-icon">
            <i class="bi bi-currency-exchange"></i>
          </div>
          <h3>Finance Templates</h3>
        </div>
        <div class="row">
          <div *ngFor="let template of financeTemplates" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 template-card finance-template">
              <div class="card-header bg-warning text-dark">
                <i class="bi bi-currency-exchange me-2"></i>Finance Template
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
                <button class="btn btn-warning text-dark" (click)="startConsultation(template.id)">
                  <i class="bi bi-play-circle me-1"></i> Start Finance SLA
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- General Templates -->
      <div *ngIf="templates.length > 0 && (activeCategory === 'All' || activeCategory === 'General')">
        <div class="category-header general">
          <div class="category-icon">
            <i class="bi bi-file-earmark-text"></i>
          </div>
          <h3>General Templates</h3>
        </div>
        <div class="row">
          <div *ngFor="let template of templates" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 template-card">
              <div class="card-header bg-primary text-white">
                <i class="bi bi-file-earmark-text me-2"></i>General Template
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
                <div class="template-info mb-3">
                  <small class="text-muted">
                    <i class="bi bi-layers"></i> {{ template.stages.length || 0 }} stages
                  </small>
                </div>
              </div>
              <div class="card-footer bg-transparent">
                <button class="btn btn-primary" (click)="startConsultation(template.id)">
                  <i class="bi bi-play-circle me-1"></i> Start Consultation
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty state -->
      <div *ngIf="!loading && categories.length <= 1" class="text-center my-5">
        <div class="display-6 text-muted mb-3">No templates available</div>
        <p>There are currently no consultation templates available.</p>
      </div>
    </div>
  `,
  styles: [`
    .template-card {
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      border: 1px solid #eaeaea;
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    
    .template-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .card-body {
      flex: 1;
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
    
    /* Category Filter */
    .category-filter {
      margin-bottom: 1.5rem;
    }
    
    /* Category Headers */
    .category-header {
      display: flex;
      align-items: center;
      margin: 2rem 0 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #eee;
    }
    
    .category-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      margin-right: 1rem;
      font-size: 1.25rem;
    }
    
    .category-header h3 {
      margin: 0;
    }
    
    /* Healthcare Templates */
    .healthcare-template {
      border: 1px solid #17a2b8;
    }
    
    .healthcare-template .card-header {
      background-color: #17a2b8 !important;
    }
    
    .healthcare-template:hover {
      box-shadow: 0 10px 20px rgba(23, 162, 184, 0.2);
    }
    
    .category-header.healthcare .category-icon {
      background-color: rgba(23, 162, 184, 0.2);
      color: #17a2b8;
    }
    
    /* Infrastructure Templates */
    .infrastructure-template {
      border: 1px solid #28a745;
    }
    
    .infrastructure-template .card-header {
      background-color: #28a745 !important;
    }
    
    .infrastructure-template:hover {
      box-shadow: 0 10px 20px rgba(40, 167, 69, 0.2);
    }
    
    .category-header.infrastructure .category-icon {
      background-color: rgba(40, 167, 69, 0.2);
      color: #28a745;
    }
    
    /* Finance Templates */
    .finance-template {
      border: 1px solid #ffc107;
    }
    
    .finance-template .card-header {
      background-color: #ffc107 !important;
    }
    
    .finance-template:hover {
      box-shadow: 0 10px 20px rgba(255, 193, 7, 0.2);
    }
    
    .category-header.finance .category-icon {
      background-color: rgba(255, 193, 7, 0.2);
      color: #ffc107;
    }
    
    /* General Templates */
    .category-header.general .category-icon {
      background-color: rgba(0, 123, 255, 0.2);
      color: #007bff;
    }
  `]
})
export class TemplateListComponent implements OnInit {
  templates: ConsultationTemplate[] = [];
  healthcareTemplates: any[] = [];
  infrastructureTemplates: any[] = [];
  financeTemplates: any[] = [];
  categorizedTemplates: CategorizedTemplates = {};
  categories: string[] = [];
  activeCategory: string = 'All';
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
    this.loadInfrastructureTemplates();
    this.loadFinanceTemplates();
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
          this.categorizeTemplates();
        },
        error: (err) => {
          console.error('Error loading healthcare templates:', err);
        }
      });
  }
  
  loadInfrastructureTemplates(): void {
    // For demo purposes, create infrastructure templates
    this.infrastructureTemplates = [
      {
        id: 'inf-cloud-sla-001',
        name: 'Enterprise Infrastructure SLA',
        description: 'Service Level Agreement for Enterprise Cloud Infrastructure Services covering compute, storage, and networking',
        domain: 'Infrastructure',
        tags: ['cloud', 'enterprise', 'compute', 'storage', 'networking']
      },
      {
        id: 'inf-datacenter-sla-001',
        name: 'Data Center Operations SLA',
        description: 'Service Level Agreement for Data Center Operations including power, cooling, and physical security',
        domain: 'Infrastructure',
        tags: ['datacenter', 'physical', 'operations', 'security']
      }
    ];
    this.categorizeTemplates();
  }
  
  loadFinanceTemplates(): void {
    // For demo purposes, create finance templates
    this.financeTemplates = [
      {
        id: 'fin-banking-sla-001',
        name: 'Financial Services Banking SLA',
        description: 'Service Level Agreement for Banking and Financial Services covering transaction processing, reporting, and compliance',
        domain: 'Finance',
        tags: ['banking', 'payments', 'compliance', 'transactions']
      },
      {
        id: 'fin-trading-sla-001',
        name: 'Trading Platform SLA',
        description: 'Service Level Agreement for Trading Platforms focusing on low-latency execution and high availability',
        domain: 'Finance',
        tags: ['trading', 'low-latency', 'markets', 'financial']
      }
    ];
    this.categorizeTemplates();
  }
  
  categorizeTemplates(): void {
    // Initialize the categories map
    this.categorizedTemplates = {
      'Healthcare': [...this.healthcareTemplates],
      'Infrastructure': [...this.infrastructureTemplates],
      'Finance': [...this.financeTemplates],
      'General': []
    };
    
    // Categorize standard templates
    if (this.templates.length > 0) {
      this.templates.forEach(template => {
        const domain = template.domain || 'General';
        if (!this.categorizedTemplates[domain]) {
          this.categorizedTemplates[domain] = [];
        }
        this.categorizedTemplates[domain].push(template);
      });
    }
    
    // Extract categories for the filter
    this.categories = ['All', ...Object.keys(this.categorizedTemplates).filter(cat => 
      this.categorizedTemplates[cat] && this.categorizedTemplates[cat].length > 0
    )];
  }
  
  filterByCategory(category: string): void {
    this.activeCategory = category;
  }
  
  shouldShowTemplate(template: any): boolean {
    if (this.activeCategory === 'All') return true;
    return template.domain === this.activeCategory;
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