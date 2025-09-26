import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TemplateService } from '../../services/template.service';

@Component({
  selector: 'app-template-generator',
  template: `
    <div class="container mt-4">
      <div class="row">
        <div class="col-md-8 mx-auto">
          <div class="card">
            <div class="card-header bg-primary text-white">
              <h4>SLA Template Generator</h4>
            </div>
            <div class="card-body">
              <p class="card-text">
                Generate customized SLA templates based on your service requirements.
              </p>

              <form [formGroup]="templateForm" (ngSubmit)="onSubmit()">
                <div class="mb-3">
                  <label for="serviceName" class="form-label">Service Name</label>
                  <input type="text" class="form-control" id="serviceName" formControlName="serviceName">
                  <div *ngIf="templateForm.get('serviceName')?.touched && templateForm.get('serviceName')?.invalid" class="text-danger">
                    <small>Service name is required</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="serviceType" class="form-label">Service Type</label>
                  <select class="form-select" id="serviceType" formControlName="serviceType">
                    <option value="">Select a service type</option>
                    <option value="web_application">Web Application</option>
                    <option value="api">API Service</option>
                    <option value="database">Database Service</option>
                    <option value="infrastructure">Infrastructure</option>
                    <option value="other">Other</option>
                  </select>
                  <div *ngIf="templateForm.get('serviceType')?.touched && templateForm.get('serviceType')?.invalid" class="text-danger">
                    <small>Service type is required</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="description" class="form-label">Service Description</label>
                  <textarea 
                    class="form-control" 
                    id="description" 
                    rows="3" 
                    formControlName="description"
                    placeholder="Describe your service and its key functions..."></textarea>
                  <div *ngIf="templateForm.get('description')?.touched && templateForm.get('description')?.invalid" class="text-danger">
                    <small>Service description is required</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Required Metrics</label>
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="availabilityCheck" formControlName="availability">
                    <label class="form-check-label" for="availabilityCheck">
                      Availability
                    </label>
                  </div>
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="responseTimeCheck" formControlName="responseTime">
                    <label class="form-check-label" for="responseTimeCheck">
                      Response Time
                    </label>
                  </div>
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="throughputCheck" formControlName="throughput">
                    <label class="form-check-label" for="throughputCheck">
                      Throughput
                    </label>
                  </div>
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="errorRateCheck" formControlName="errorRate">
                    <label class="form-check-label" for="errorRateCheck">
                      Error Rate
                    </label>
                  </div>
                </div>

                <div class="d-grid gap-2">
                  <button 
                    type="submit" 
                    class="btn btn-primary" 
                    [disabled]="templateForm.invalid || isLoading">
                    <span *ngIf="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Generate Template
                  </button>
                </div>
              </form>

              <div *ngIf="templateUrl" class="mt-4">
                <div class="alert alert-success">
                  <h5>Template Generated Successfully!</h5>
                  <p>Your SLA template is ready to download.</p>
                  <a [href]="templateUrl" class="btn btn-outline-success" download="sla-template.docx">
                    <i class="bi bi-download"></i> Download Template
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class TemplateGeneratorComponent implements OnInit {
  templateForm: FormGroup;
  isLoading = false;
  templateUrl: string | null = null;
  
  constructor(
    private formBuilder: FormBuilder,
    private templateService: TemplateService
  ) {
    this.templateForm = this.formBuilder.group({
      serviceName: ['', Validators.required],
      serviceType: ['', Validators.required],
      description: ['', Validators.required],
      availability: [false],
      responseTime: [false],
      throughput: [false],
      errorRate: [false]
    });
  }
  
  ngOnInit(): void {
  }
  
  onSubmit(): void {
    if (this.templateForm.invalid) {
      return;
    }
    
    this.isLoading = true;
    this.templateUrl = null;
    
    const formValue = this.templateForm.value;
    const metrics = [];
    
    if (formValue.availability) metrics.push('availability');
    if (formValue.responseTime) metrics.push('response_time');
    if (formValue.throughput) metrics.push('throughput');
    if (formValue.errorRate) metrics.push('error_rate');
    
    const request = {
      service_name: formValue.serviceName,
      service_type: formValue.serviceType,
      description: formValue.description,
      metrics: metrics
    };
    
    this.templateService.createTemplate(request).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response && response.template_url) {
          this.templateUrl = response.template_url;
        }
      },
      error: (error: any) => {
        this.isLoading = false;
        console.error('Error generating template:', error);
      }
    });
  }
}