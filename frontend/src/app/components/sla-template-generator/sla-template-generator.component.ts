import { Component, OnInit } from '@angular/core';
import { TemplateGeneratorService } from '../../services/template-generator.service';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TemplateStage } from '../../services/consultation.service';

interface EligibleSession {
  id: number;
  created_at: string;
  name: string;
  message_count: number;
  sla_relevance: 'high' | 'medium' | 'low';
  preview: string;
}

@Component({
  selector: 'app-sla-template-generator',
  template: `
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col">
          <h2>Convert SLA Consultations to Templates</h2>
          <p class="text-muted">
            Generate reusable templates from your successful SLA consultations
          </p>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <!-- Error Message -->
      <div *ngIf="error" class="alert alert-danger">
        {{ error }}
      </div>

      <!-- Success Message -->
      <div *ngIf="successMessage" class="alert alert-success">
        {{ successMessage }}
        <button *ngIf="generatedTemplateId" class="btn btn-sm btn-outline-success ms-3" (click)="viewTemplate()">
          View Template
        </button>
      </div>

      <!-- Session Selection -->
      <div *ngIf="!selectedSession && !loading" class="card mb-4">
        <div class="card-header bg-light">
          <h5 class="mb-0">Select an SLA Consultation</h5>
        </div>
        <div class="card-body">
          <p>Select a consultation session to convert into a reusable template:</p>
          
          <!-- No eligible sessions -->
          <div *ngIf="eligibleSessions.length === 0" class="alert alert-info">
            No eligible SLA consultation sessions found. Complete an SLA consultation first.
          </div>
          
          <!-- Session List -->
          <div *ngIf="eligibleSessions.length > 0" class="list-group mb-4">
            <button 
              *ngFor="let session of eligibleSessions"
              class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              (click)="selectSession(session)"
            >
              <div>
                <div><strong>{{ session.name || 'Session #' + session.id }}</strong> - {{ session.created_at | date:'medium' }}</div>
                <div class="text-muted small mt-1">{{ session.preview }}</div>
              </div>
              <div>
                <span class="badge rounded-pill" 
                      [ngClass]="{'bg-success': session.sla_relevance === 'high', 
                                 'bg-warning text-dark': session.sla_relevance === 'medium'}">
                  {{ session.sla_relevance }}
                </span>
                <span class="badge bg-secondary ms-2">
                  {{ session.message_count }} messages
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Template Creation Form -->
      <div *ngIf="selectedSession && !loading && !generatedTemplateId && !previewMode" class="card">
        <div class="card-header bg-light">
          <h5 class="mb-0">Create Template from {{ selectedSession.name || 'Session #' + selectedSession.id }}</h5>
        </div>
        <div class="card-body">
          <form [formGroup]="templateForm" (ngSubmit)="previewTemplate()">
            <div class="mb-3">
              <label for="templateName" class="form-label">Template Name*</label>
              <input 
                type="text" 
                class="form-control" 
                id="templateName" 
                formControlName="templateName"
                placeholder="E.g., Healthcare SLA Template"
              >
              <div *ngIf="templateForm.get('templateName')?.invalid && templateForm.get('templateName')?.touched" class="text-danger mt-1">
                Template name is required
              </div>
            </div>
            
            <div class="mb-3">
              <label for="templateDescription" class="form-label">Description</label>
              <textarea 
                class="form-control" 
                id="templateDescription" 
                rows="3" 
                formControlName="templateDescription"
                placeholder="Describe the purpose and use cases for this template"
              ></textarea>
            </div>
            
            <div class="mb-3">
              <label for="domain" class="form-label">Domain</label>
              <input 
                type="text" 
                class="form-control" 
                id="domain" 
                formControlName="domain"
                placeholder="E.g., SLA, Healthcare, Financial"
              >
            </div>
            
            <div class="mb-3 form-check">
              <input 
                type="checkbox" 
                class="form-check-input" 
                id="isPublic" 
                formControlName="isPublic"
              >
              <label class="form-check-label" for="isPublic">
                Make this template public (available to all users)
              </label>
            </div>
            
            <div class="d-flex justify-content-between">
              <button type="button" class="btn btn-outline-secondary" (click)="cancelSelection()">
                Back
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="templateForm.invalid || generating">
                <span *ngIf="generating" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                {{ generating ? 'Analyzing...' : 'Preview Template' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Template Preview Section -->
      <div *ngIf="previewMode && !generatedTemplateId" class="template-preview-section">
        <div class="card mb-4">
          <div class="card-header bg-light">
            <h5 class="mb-0">Template Preview</h5>
          </div>
          <div class="card-body">
            <!-- Preview Error -->
            <div *ngIf="previewError" class="alert alert-danger">
              {{ previewError }}
              <button class="btn btn-sm btn-outline-danger ms-2" (click)="cancelPreview()">
                Try Again
              </button>
            </div>
            
            <!-- Template Info -->
            <div class="mb-4">
              <h4>{{ templateForm.get('templateName')?.value }}</h4>
              <p class="text-muted">{{ templateForm.get('templateDescription')?.value || 'No description provided.' }}</p>
              
              <div class="mb-2">
                <strong>Domain:</strong> {{ templateForm.get('domain')?.value }}
              </div>
              
              <div class="mb-3">
                <strong>Visibility:</strong> 
                <span class="badge" [ngClass]="templateForm.get('isPublic')?.value ? 'bg-success' : 'bg-secondary'">
                  {{ templateForm.get('isPublic')?.value ? 'Public' : 'Private' }}
                </span>
              </div>
            </div>
            
            <!-- Stages Preview -->
            <div *ngIf="previewStages.length > 0" class="mt-4">
              <h5 class="mb-3">Conversation Stages</h5>
              
              <div class="stages-container">
                <div *ngFor="let stage of previewStages; let i = index" class="stage-card mb-3">
                  <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                      <span class="stage-number">Stage {{ i + 1 }}</span>
                      <h6 class="mb-0">{{ stage.name }}</h6>
                    </div>
                    <div class="card-body">
                      <p class="mb-3">{{ stage.description }}</p>
                      
                      <div class="mb-3">
                        <strong>Type:</strong> {{ stage.stage_type }}
                      </div>
                      
                      <div *ngIf="stage.expected_outputs && stage.expected_outputs.length > 0" class="mb-3">
                        <strong>Expected Outputs:</strong>
                        <ul class="list-group list-group-flush mt-2">
                          <li *ngFor="let output of stage.expected_outputs" class="list-group-item py-2">
                            <div><strong>{{ output.name }}</strong> <span class="text-muted">({{ output.data_type }})</span></div>
                            <small>{{ output.description }}</small>
                            <span *ngIf="output.required" class="badge bg-danger ms-2">Required</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-4 d-flex justify-content-between">
              <button type="button" class="btn btn-outline-secondary" (click)="cancelPreview()">
                Back to Form
              </button>
              <button type="button" class="btn btn-primary" (click)="confirmAndGenerateTemplate()">
                <span *ngIf="generating" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                {{ generating ? 'Generating...' : 'Confirm & Generate Template' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Template Generation Result -->
      <div *ngIf="generatedTemplateId" class="card">
        <div class="card-header bg-success text-white">
          <h5 class="mb-0">Template Generated Successfully!</h5>
        </div>
        <div class="card-body">
          <div class="mb-4">
            <h5>{{ templateForm.get('templateName')?.value }}</h5>
            <p class="text-muted">{{ templateForm.get('templateDescription')?.value }}</p>
          </div>
          
          <div class="row mb-3">
            <div class="col-md-6">
              <strong>Template ID:</strong> {{ generatedTemplateId }}
            </div>
            <div class="col-md-6">
              <strong>Stages:</strong> {{ generatedStagesCount }}
            </div>
          </div>
          
          <div class="mb-4">
            <strong>Tags:</strong>
            <span *ngFor="let tag of generatedTags" class="badge bg-secondary me-1">{{ tag }}</span>
          </div>
          
          <div class="d-flex justify-content-end">
            <button type="button" class="btn btn-outline-secondary me-2" (click)="reset()">
              Create Another
            </button>
            <button type="button" class="btn btn-primary" (click)="viewTemplate()">
              View Template
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .badge.bg-success {
      background-color: var(--bs-success) !important;
    }
    
    .badge.bg-warning {
      background-color: var(--bs-warning) !important;
    }
    
    .list-group-item:hover {
      background-color: var(--bs-light);
    }
    
    .stage-card {
      border-left: 4px solid var(--bs-primary);
    }
    
    .stage-number {
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--bs-secondary);
      margin-right: 10px;
    }
    
    .template-preview-section {
      animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class SlaTemplateGeneratorComponent implements OnInit {
  eligibleSessions: EligibleSession[] = [];
  selectedSession: EligibleSession | null = null;
  templateForm: FormGroup;
  loading = false;
  generating = false;
  error = '';
  successMessage = '';
  
  // Generated template info
  generatedTemplateId = '';
  generatedStagesCount = 0;
  generatedTags: string[] = [];
  
  // Template preview
  previewMode = false;
  previewStages: TemplateStage[] = [];
  previewError = '';

  constructor(
    private templateGeneratorService: TemplateGeneratorService,
    private formBuilder: FormBuilder,
    private router: Router
  ) {
    this.templateForm = this.formBuilder.group({
      templateName: ['', Validators.required],
      templateDescription: [''],
      domain: ['SLA'],
      isPublic: [false]
    });
  }

  ngOnInit(): void {
    this.loadEligibleSessions();
  }

  loadEligibleSessions(): void {
    this.loading = true;
    this.error = '';
    
    this.templateGeneratorService.getEligibleSessions().subscribe({
      next: (sessions) => {
        this.eligibleSessions = sessions;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading eligible sessions:', err);
        this.error = 'Failed to load eligible sessions. Please try again.';
        this.loading = false;
      }
    });
  }

  selectSession(session: EligibleSession): void {
    this.selectedSession = session;
    // Use the detected name or create a default one
    const templateName = session.name || `SLA Template #${session.id}`;
    this.templateForm.get('templateName')?.setValue(templateName);

    // Extract domain from name if possible
    if (session.name) {
      const domainKeywords = ['cloud', 'healthcare', 'financial', 'network', 'security'];
      const foundKeyword = domainKeywords.find(keyword => 
        session.name.toLowerCase().includes(keyword.toLowerCase())
      );
      if (foundKeyword) {
        this.templateForm.get('domain')?.setValue(foundKeyword.charAt(0).toUpperCase() + foundKeyword.slice(1));
      }
    }
  }

  cancelSelection(): void {
    this.selectedSession = null;
  }

  previewTemplate(): void {
    if (this.templateForm.invalid || !this.selectedSession) {
      return;
    }
    
    this.generating = true;
    this.error = '';
    this.previewError = '';
    
    // First, we'll fetch consultation data to analyze the stages
    this.templateGeneratorService.getEligibleSessionDetails(this.selectedSession.id).subscribe({
      next: (sessionDetails) => {
        // Now we can analyze the consultation to preview the stages
        this.analyzeConsultationStages(sessionDetails);
      },
      error: (err) => {
        console.error('Error fetching session details:', err);
        this.previewError = `Failed to fetch session details: ${err.error?.detail || 'Unknown error'}`;
        this.generating = false;
      }
    });
  }
  
  analyzeConsultationStages(sessionDetails: { id: number; messages: any[]; context_data: Record<string, any> }): void {
    // This would normally call the backend to analyze the stages
    // For now, we'll create a simplified simulation with static stages
    
    setTimeout(() => {
      // Simulate the analysis result
      this.previewStages = [
        {
          id: 'stage1',
          name: 'SLA Requirements Gathering',
          description: 'Collect basic requirements for the Service Level Agreement',
          stage_type: 'information_gathering',
          prompt_template: 'What are your key requirements for this SLA?',
          expected_outputs: [
            {
              name: 'service_name',
              description: 'Name of the service requiring an SLA',
              data_type: 'string',
              required: true
            },
            {
              name: 'industry',
              description: 'Industry or sector',
              data_type: 'string',
              required: true
            }
          ]
        },
        {
          id: 'stage2',
          name: 'Performance Metrics',
          description: 'Define key performance indicators and service metrics',
          stage_type: 'structured_input',
          prompt_template: 'Let\'s define the performance metrics for your SLA',
          expected_outputs: [
            {
              name: 'availability',
              description: 'Service availability requirement (e.g., 99.9%)',
              data_type: 'string',
              required: true
            },
            {
              name: 'response_time',
              description: 'Maximum response time',
              data_type: 'string',
              required: false
            }
          ]
        },
        {
          id: 'stage3',
          name: 'Support Terms',
          description: 'Define support levels and response times',
          stage_type: 'structured_input',
          prompt_template: 'Now, let\'s discuss support terms for the SLA',
          expected_outputs: [
            {
              name: 'support_hours',
              description: 'Hours when support is available',
              data_type: 'string',
              required: true
            },
            {
              name: 'response_times',
              description: 'Response time commitments for different severity levels',
              data_type: 'object',
              required: true
            }
          ]
        }
      ];
      
      // Switch to preview mode
      this.previewMode = true;
      this.generating = false;
    }, 1500); // Simulate analysis time
  }
  
  cancelPreview(): void {
    this.previewMode = false;
    this.previewStages = [];
    this.previewError = '';
  }
  
  confirmAndGenerateTemplate(): void {
    if (this.templateForm.invalid || !this.selectedSession) {
      return;
    }
    
    this.generating = true;
    this.error = '';
    
    const request = {
      session_id: this.selectedSession.id,
      template_name: this.templateForm.value.templateName,
      template_description: this.templateForm.value.templateDescription,
      domain: this.templateForm.value.domain,
      is_public: this.templateForm.value.isPublic
    };
    
    this.templateGeneratorService.convertSlaToTemplate(request).subscribe({
      next: (response) => {
        this.generating = false;
        this.previewMode = false;
        this.generatedTemplateId = response.template_id;
        this.generatedStagesCount = response.stages_count;
        this.generatedTags = response.tags;
        this.successMessage = `Template "${response.name}" created successfully with ${response.stages_count} stages!`;
      },
      error: (err) => {
        console.error('Error generating template:', err);
        this.error = `Failed to generate template: ${err.error?.detail || 'Unknown error'}`;
        this.generating = false;
      }
    });
  }

  reset(): void {
    this.selectedSession = null;
    this.generatedTemplateId = '';
    this.generatedStagesCount = 0;
    this.generatedTags = [];
    this.successMessage = '';
    this.templateForm.reset({
      templateName: '',
      templateDescription: '',
      domain: 'SLA',
      isPublic: false
    });
  }

  viewTemplate(): void {
    if (this.generatedTemplateId) {
      this.router.navigate(['/template-consultation', this.generatedTemplateId]);
    }
  }
}