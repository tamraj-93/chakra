import { Component, Input, OnInit } from '@angular/core';
import { TemplateService } from '../../services/template.service';
import { ExportService } from '../../services/export.service';

@Component({
  selector: 'app-template-preview',
  template: `
    <div class="template-preview-container" [ngClass]="{'embedded': embedded}">
      <!-- Header with actions - Only show in modal mode -->
      <div class="preview-header" *ngIf="!embedded">
        <h3>{{ template?.name || 'Template Preview' }}</h3>
        <div class="preview-actions">
          <button class="btn btn-sm btn-outline-secondary" (click)="onClose()">
            <i class="bi bi-x"></i> Close
          </button>
          <button class="btn btn-sm btn-outline-primary ms-2" (click)="onDownloadPdf()">
            <i class="bi bi-download"></i> Download PDF
          </button>
        </div>
      </div>
      
      <!-- Header for embedded mode -->
      <div class="preview-header embedded-header" *ngIf="embedded">
        <h4>Template Preview</h4>
        <div class="preview-actions">
          <button class="btn btn-sm btn-outline-primary" (click)="onDownloadPdf()">
            <i class="bi bi-download"></i> Download PDF
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div *ngIf="isLoading" class="preview-loading">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading template content...</p>
      </div>

      <!-- Error state -->
      <div *ngIf="error" class="preview-error alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ error }}
      </div>

      <!-- Template content -->
      <div *ngIf="!isLoading && !error" class="preview-content">
        <!-- SLA Document styled to look like a paper document -->
        <div class="sla-document">
          <div class="sla-header">
            <h2 class="text-center">SERVICE LEVEL AGREEMENT</h2>
            <h3 class="text-center">{{ template?.name }}</h3>
            <p class="text-center text-muted">Generated on {{ currentDate | date:'longDate' }}</p>
          </div>

          <div class="sla-section">
            <h4>AGREEMENT OVERVIEW</h4>
            <p>{{ getOverview() }}</p>
          </div>

          <div class="sla-section">
            <h4>SERVICE DESCRIPTION</h4>
            <p>{{ template?.description || 'No description provided.' }}</p>
          </div>

          <div class="sla-section">
            <h4>SERVICE TYPE</h4>
            <p>{{ formatServiceType(template?.service_type) }}</p>
          </div>

          <div class="sla-section">
            <h4>INDUSTRY</h4>
            <p>{{ formatIndustry(template?.industry) }}</p>
          </div>

          <div *ngIf="metrics && metrics.length > 0" class="sla-section">
            <h4>PERFORMANCE METRICS</h4>
            <table class="table table-bordered">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Target</th>
                  <th>Measurement</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let metric of metrics">
                  <td>{{ metric.name }}</td>
                  <td>{{ metric.target || 'N/A' }}</td>
                  <td>{{ metric.measurement || 'N/A' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="sla-section">
            <h4>SUPPORT RESPONSE TIMES</h4>
            <table class="table table-bordered">
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Description</th>
                  <th>Response Time</th>
                  <th>Resolution Time</th>
                </tr>
              </thead>
              <tbody>
                <ng-container *ngIf="supportLevels && supportLevels.length > 0">
                  <tr *ngFor="let level of supportLevels">
                    <td>{{ level.severity }}</td>
                    <td>{{ level.description }}</td>
                    <td>{{ level.response_time }}</td>
                    <td>{{ level.resolution_time }}</td>
                  </tr>
                </ng-container>
                <ng-container *ngIf="!supportLevels || supportLevels.length === 0">
                  <tr>
                    <td>Critical</td>
                    <td>System outage affecting all users</td>
                    <td>15 minutes</td>
                    <td>2 hours</td>
                  </tr>
                  <tr>
                    <td>High</td>
                    <td>Major functionality impacted</td>
                    <td>30 minutes</td>
                    <td>4 hours</td>
                  </tr>
                  <tr>
                    <td>Medium</td>
                    <td>Minor functionality issues</td>
                    <td>2 hours</td>
                    <td>8 hours</td>
                  </tr>
                  <tr>
                    <td>Low</td>
                    <td>Cosmetic issues or enhancement requests</td>
                    <td>8 hours</td>
                    <td>24 hours</td>
                  </tr>
                </ng-container>
              </tbody>
            </table>
          </div>

          <div class="sla-section">
            <h4>TERMS AND CONDITIONS</h4>
            <p>{{ termsAndConditions }}</p>
          </div>

          <div class="sla-footer">
            <p class="text-center text-muted">Generated by Chakra SLM</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .template-preview-container {
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
      height: 100%;
      overflow-y: auto;
    }
    
    .template-preview-container.embedded {
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 15px;
      margin-top: 20px;
      border: 1px solid #e9ecef;
      border-radius: 6px;
      background-color: #fcfcfc;
    }
    
    .embedded-header {
      border-bottom: 1px solid #e9ecef;
      padding-bottom: 10px;
      margin-bottom: 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .embedded .sla-document {
      border: none;
      padding: 15px 0;
    }
    
    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #e0e0e0;
      padding-bottom: 15px;
      margin-bottom: 20px;
    }
    
    .preview-loading, .preview-error {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 0;
    }
    
    .sla-document {
      background-color: #fff;
      border: 1px solid #e0e0e0;
      padding: 30px;
      font-family: 'Times New Roman', Times, serif;
    }
    
    .sla-header {
      margin-bottom: 30px;
    }
    
    .sla-section {
      margin-bottom: 25px;
    }
    
    .sla-section h4 {
      border-bottom: 1px solid #e0e0e0;
      padding-bottom: 8px;
      margin-bottom: 15px;
      font-weight: bold;
    }
    
    .sla-footer {
      margin-top: 40px;
      border-top: 1px solid #e0e0e0;
      padding-top: 15px;
    }
    
    table {
      width: 100%;
      margin-bottom: 20px;
    }
    
    th {
      background-color: #f5f5f5;
    }
  `]
})
export class TemplatePreviewComponent implements OnInit {
  @Input() templateId: number | null = null;
  @Input() embedded: boolean = false; // Whether this preview is embedded in another component
  template: any = null;
  isLoading: boolean = true;
  error: string | null = null;
  currentDate = new Date();
  metrics: any[] = [];
  supportLevels: any[] = [];
  termsAndConditions: string = 'Standard terms and conditions apply. This document serves as a template and should be reviewed by legal counsel before formal implementation.';

  constructor(
    private templateService: TemplateService,
    private exportService: ExportService
  ) {}

  ngOnInit(): void {
    this.loadTemplate();
  }

  loadTemplate(): void {
    if (!this.templateId) {
      this.error = "No template ID provided";
      this.isLoading = false;
      return;
    }

    this.isLoading = true;
    this.error = null;

    this.templateService.getTemplate(this.templateId).subscribe({
      next: (template) => {
        this.template = template;
        
        // Try to extract all template data
        if (template.template && typeof template.template === 'string') {
          // Try to parse template field if it's a JSON string
          try {
            const templateData = JSON.parse(template.template);
            
            // Extract metrics
            if (templateData.metrics && Array.isArray(templateData.metrics)) {
              this.metrics = templateData.metrics;
            } else {
              this.metrics = [];
            }
            
            // Extract support levels
            if (templateData.support && Array.isArray(templateData.support)) {
              this.supportLevels = templateData.support;
            } else {
              this.supportLevels = [];
            }
            
            // Extract terms
            if (templateData.terms) {
              this.termsAndConditions = templateData.terms;
            }
            
          } catch (e) {
            console.error('Error parsing template JSON:', e);
            this.metrics = [];
            this.supportLevels = [];
          }
        } else {
          // Fall back to direct properties if available
          if (template.metrics && Array.isArray(template.metrics)) {
            this.metrics = template.metrics;
          } else {
            this.metrics = [];
          }
          
          // Use type assertion to access potentially undefined properties
          const anyTemplate = template as any;
          
          if (anyTemplate.supportLevels && Array.isArray(anyTemplate.supportLevels)) {
            this.supportLevels = anyTemplate.supportLevels;
          }
          
          if (anyTemplate.terms) {
            this.termsAndConditions = anyTemplate.terms;
          }
        }
        
        this.isLoading = false;
      },
      error: (err) => {
        this.error = "Failed to load template. Please try again.";
        this.isLoading = false;
        console.error("Template loading error:", err);
      }
    });
  }

  onClose(): void {
    // This will be implemented by the parent component
  }

  onDownloadPdf(): void {
    if (!this.templateId) return;
    
    this.exportService.exportTemplatePdf(this.templateId).subscribe({
      next: (response) => {
        if (response && response.content) {
          this.exportService.downloadPdf(response.content, response.filename || 'template.pdf');
        } else {
          console.error("Invalid PDF response", response);
          alert("Error generating PDF. Please try again.");
        }
      },
      error: (err) => {
        console.error("PDF download error:", err);
        alert("Error downloading PDF. Please try again.");
      }
    });
  }

  getOverview(): string {
    // Try to get overview from template data if it exists
    if (this.template?.template && typeof this.template.template === 'string') {
      try {
        const templateData = JSON.parse(this.template.template);
        if (templateData.overview) {
          return templateData.overview;
        }
      } catch (e) {
        console.error('Error parsing template JSON for overview:', e);
      }
    }
    
    return `This Service Level Agreement (SLA) outlines the terms and conditions for ${this.template?.name || 'the service'} 
            as provided to customers. It defines the scope, quality parameters, and responsibilities of all parties involved.`;
  }

  formatServiceType(serviceType: string): string {
    if (!serviceType) return 'Not specified';
    
    // Convert snake_case to Title Case
    return serviceType
      .replace(/_/g, ' ')
      .replace(/\b\w/g, char => char.toUpperCase());
  }

  formatIndustry(industry: string): string {
    if (!industry) return 'Not specified';
    return industry.charAt(0).toUpperCase() + industry.slice(1);
  }
}