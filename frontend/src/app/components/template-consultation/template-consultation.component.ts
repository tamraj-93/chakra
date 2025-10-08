import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ConsultationService, TemplateConsultationResponse, TemplateStage, ConsultationTemplate } from '../../services/consultation.service';
import { TemplateService } from '../../services/template.service';
import { TemplateProgress } from '../chat-box/chat-box.component';
import { StructuredOutput, ConsultationSummary } from '../../models/consultation-summary';

interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
  stageId?: string;
}

interface StructuredInputField {
  id: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'radio' | 'checkbox';
  options?: Array<{value: string, label: string}>;
  value: string | string[];
  placeholder?: string;
  required?: boolean;
  helpText?: string;
}

interface ExtractedTemplateData {
  name: string;
  description: string;
  domain: string;
  stages: Array<{
    id?: string;
    name: string;
    description: string;
    prompt_template: string;
    stage_type: string;
    expected_outputs: Array<{
      name: string;
      description: string;
      data_type: string;
      required: boolean;
    }>;
  }>;
  initial_system_prompt: string;
  tags: string[];
}

@Component({
  selector: 'app-template-consultation',
  template: `
    <div class="template-consultation-container">
      <!-- Header with Template Info -->
      <div class="consultation-header">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h2>{{ templateName }}</h2>
            <p class="text-muted">{{ templateDescription }}</p>
          </div>
          <div class="col-md-4 text-md-end">
            <button class="btn btn-outline-secondary me-2" (click)="backToTemplates()">
              <i class="bi bi-arrow-left"></i> Back
            </button>
            <button class="btn btn-outline-primary" (click)="toggleSidebar()">
              <i class="bi bi-layout-sidebar"></i> {{ showSidebar ? 'Hide' : 'Show' }} Progress
            </button>
          </div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div *ngIf="loading" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading consultation template...</p>
      </div>
      
      <!-- Error State -->
      <div *ngIf="error" class="alert alert-danger">
        {{ error }}
      </div>
      
      <!-- Main Content with optional Sidebar -->
      <div *ngIf="!loading && !error" class="consultation-content">
        <div class="row">
          <!-- Sidebar with Stage Progress -->
          <div *ngIf="showSidebar" class="col-md-3 sidebar-col">
            <app-template-stage-progress
              [stages]="templateStages"
              [currentStage]="currentStageNumber"
              [allowNavigation]="false"
              [showDescription]="true">
            </app-template-stage-progress>
            
            <!-- Template Information -->
            <div class="template-info">
              <h5>About this Template</h5>
              <div class="template-detail">
                <span class="detail-label">Domain:</span>
                <span class="detail-value">{{ templateDomain }}</span>
              </div>
              <div class="template-detail">
                <span class="detail-label">Tags:</span>
                <div class="tags-container">
                  <span *ngFor="let tag of templateTags" class="template-tag">{{ tag }}</span>
                </div>
              </div>
              <div class="template-actions mt-3">
                <button class="btn btn-sm btn-outline-secondary w-100" (click)="exportConsultation()">
                  <i class="bi bi-download"></i> Export Results
                </button>
              </div>
            </div>
          </div>
          
          <!-- Main Chat Area -->
          <div [ngClass]="showSidebar ? 'col-md-9' : 'col-md-12'" class="chat-col">
            <!-- Show consultation summary when complete -->
            <div *ngIf="isConsultationComplete && consultationSummary" class="consultation-summary-container">
              <div class="summary-header">
                <h3>
                  <i class="bi bi-check-circle-fill text-success me-2"></i>
                  Consultation Complete
                </h3>
                <p class="text-muted">
                  All stages have been completed. Below is a summary of the collected information.
                </p>
              </div>
              
              <div class="summary-content">
                <!-- Summary Data -->
                <div class="card mb-4">
                  <div class="card-header bg-light">
                    <h5 class="mb-0">Consultation Summary</h5>
                  </div>
                  <div class="card-body">
                    <div *ngFor="let item of getSummaryItems()" class="summary-item mb-3">
                      <h6>{{ item.label }}</h6>
                      <div [ngSwitch]="item.type">
                        <div *ngSwitchCase="'array'" class="array-value">
                          <ul class="list-group list-group-flush">
                            <li *ngFor="let val of item.value" class="list-group-item">{{ val }}</li>
                          </ul>
                        </div>
                        <div *ngSwitchCase="'object'" class="object-value">
                          <div *ngFor="let key of getObjectKeys(item.value)" class="mb-2">
                            <strong>{{ key }}:</strong> {{ item.value[key] }}
                          </div>
                        </div>
                        <div *ngSwitchDefault class="simple-value">
                          {{ item.value }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Collected Data by Stage -->
                <div class="card">
                  <div class="card-header bg-light">
                    <h5 class="mb-0">Collected Data by Stage</h5>
                  </div>
                  <div class="card-body p-0">
                    <div class="accordion" id="stageDataAccordion">
                      <div *ngFor="let output of consultationSummary.outputs; let i = index" class="accordion-item">
                        <h2 class="accordion-header">
                          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" [attr.data-bs-target]="'#stageCollapse' + i">
                            {{ output.stageName }} (Stage {{ output.stageNumber }})
                          </button>
                        </h2>
                        <div [id]="'stageCollapse' + i" class="accordion-collapse collapse">
                          <div class="accordion-body">
                            <div *ngFor="let key of getObjectKeys(output.data)" class="mb-2">
                              <strong>{{ key }}:</strong> {{ output.data[key] | json }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Export Controls -->
                <div class="export-controls mt-4 text-end">
                  <button class="btn btn-primary me-2" (click)="createTemplateFromConsultation()">
                    <i class="bi bi-lightning me-2"></i>
                    Create Template from Consultation
                  </button>
                  <button class="btn btn-outline-primary me-2" (click)="exportConsultation()">
                    <i class="bi bi-file-earmark-pdf me-2"></i>
                    Export Results
                  </button>
                  <button class="btn btn-outline-secondary" (click)="startNewConsultation()">
                    <i class="bi bi-plus-circle me-2"></i>
                    Start New Consultation
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Chat Interface (hidden when consultation is complete) -->
            <div *ngIf="!isConsultationComplete" class="position-relative">
              <!-- Developer/Demo Tools (Hidden by default) -->
              <div *ngIf="showDevPanel" class="developer-tools-bar p-2 bg-light border-bottom">
                <div class="d-flex align-items-center justify-content-between">
                  <span class="badge bg-warning">Demo Mode</span>
                  <div>
                    <button class="btn btn-sm btn-primary me-2" (click)="forceNextStage()" [disabled]="messageLoading">
                      <i class="bi bi-skip-forward"></i> 
                      {{ messageLoading ? 'Processing...' : 'Force Next Stage' }}
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" (click)="showDevPanel = false">
                      <i class="bi bi-x"></i> Hide
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- User Guidance Panel -->
              <div *ngIf="currentStage && templateProgress" class="user-guidance-panel mb-3 p-3 border rounded bg-light">
                <div class="stage-header mb-2">
                  <h4 class="mb-1">{{currentStage.name}}</h4>
                  <p class="text-muted mb-2">{{currentStage.description}}</p>
                </div>
                
                <div class="stage-guidance">
                  <h5 class="mb-2">Information needed in this stage:</h5>
                  <ul class="expected-info-list">
                    <li *ngFor="let output of currentStage.expected_outputs" 
                        class="mb-2 d-flex align-items-start">
                      <span *ngIf="checkIfInfoProvided(output.name)" 
                            class="badge bg-success me-2 mt-1">
                        <i class="bi bi-check"></i>
                      </span>
                      <span *ngIf="!checkIfInfoProvided(output.name)" 
                            [class]="output.required ? 'badge bg-warning me-2 mt-1' : 'badge bg-secondary me-2 mt-1'">
                        <i class="bi bi-circle"></i>
                      </span>
                      <div>
                        <strong>{{output.name}}</strong>
                        <p class="text-muted mb-0 small">{{output.description}}</p>
                      </div>
                    </li>
                  </ul>
                </div>
                
                <div *ngIf="stageCompletionStatus" class="stage-completion-status mt-3">
                  <div class="progress mb-2">
                    <div class="progress-bar" 
                         [style.width.%]="stageCompletionStatus.confidence || 0"
                         [class.bg-success]="stageCompletionStatus.is_complete"
                         [class.bg-warning]="!stageCompletionStatus.is_complete">
                    </div>
                  </div>
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="small">
                      {{ stageCompletionStatus.is_complete ? 'Stage requirements met!' : 
                         'Gathering information...' }}
                    </span>
                    <span class="badge" 
                          [class.bg-success]="stageCompletionStatus.is_complete"
                          [class.bg-secondary]="!stageCompletionStatus.is_complete">
                      {{ stageCompletionStatus.confidence || 0 }}% confident
                    </span>
                  </div>
                  
                  <button *ngIf="stageCompletionStatus.is_complete" 
                          class="btn btn-success btn-sm mt-2"
                          (click)="forceNextStage()">
                    Continue to Next Stage <i class="bi bi-arrow-right"></i>
                  </button>
                </div>
              </div>
              
              <app-chat-box
                [messages]="messages"
                [loading]="messageLoading"
                [templateMode]="true"
                [templateProgress]="templateProgress"
                [structuredInputFields]="structuredInputFields"
                [structuredInputPrompt]="structuredInputPrompt"
                [showTextInput]="!structuredInputFields || structuredInputFields.length === 0"
                (messageSent)="sendMessage($event)"
                (structuredInputSubmitted)="submitStructuredInput($event)">
              </app-chat-box>
              
              <!-- Floating Developer Tools Toggle -->
              <button *ngIf="!showDevPanel" 
                      class="developer-tools-toggle btn btn-sm btn-light border shadow-sm"
                      (click)="showDevPanel = true">
                <i class="bi bi-gear-fill"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Template Preview Modal -->
      <div *ngIf="showTemplatePreviewModal" class="modal-backdrop fade show"></div>
      <div *ngIf="showTemplatePreviewModal" class="modal fade show d-block" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Create Template from Consultation</h5>
              <button type="button" class="btn-close" (click)="showTemplatePreviewModal = false"></button>
            </div>
            <div class="modal-body">
              <div *ngIf="!extractedTemplateData" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Analyzing consultation and extracting template structure...</p>
              </div>
              
              <div *ngIf="extractedTemplateData">
                <!-- Template Basic Info -->
                <div class="mb-4">
                  <h6>Template Information</h6>
                  <div class="form-group mb-3">
                    <label for="template-name">Name</label>
                    <input type="text" class="form-control" id="template-name" 
                           [(ngModel)]="extractedTemplateData.name">
                  </div>
                  <div class="form-group mb-3">
                    <label for="template-description">Description</label>
                    <textarea class="form-control" id="template-description" rows="2"
                              [(ngModel)]="extractedTemplateData.description"></textarea>
                  </div>
                  <div class="form-group mb-3">
                    <label for="template-domain">Domain</label>
                    <input type="text" class="form-control" id="template-domain"
                           [(ngModel)]="extractedTemplateData.domain">
                  </div>
                </div>
                
                <!-- Stages -->
                <div class="mb-4">
                  <h6>Consultation Stages</h6>
                  <div class="accordion" id="stagesAccordion">
                    <div *ngFor="let stage of extractedTemplateData.stages; let i = index" class="accordion-item mb-2">
                      <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" 
                                data-bs-toggle="collapse" [attr.data-bs-target]="'#stage' + i">
                          Stage {{i+1}}: {{stage.name}}
                        </button>
                      </h2>
                      <div [id]="'stage' + i" class="accordion-collapse collapse" data-bs-parent="#stagesAccordion">
                        <div class="accordion-body">
                          <div class="form-group mb-3">
                            <label>Stage Name</label>
                            <input type="text" class="form-control" [(ngModel)]="stage.name">
                          </div>
                          <div class="form-group mb-3">
                            <label>Description</label>
                            <textarea class="form-control" rows="2" [(ngModel)]="stage.description"></textarea>
                          </div>
                          <div class="form-group mb-3">
                            <label>Stage Type</label>
                            <select class="form-select" [(ngModel)]="stage.stage_type">
                              <option value="introduction">Introduction</option>
                              <option value="information_gathering">Information Gathering</option>
                              <option value="problem_analysis">Problem Analysis</option>
                              <option value="solution_design">Solution Design</option>
                              <option value="conclusion">Conclusion</option>
                            </select>
                          </div>
                          <div class="form-group mb-3">
                            <label>Prompt Template</label>
                            <textarea class="form-control" rows="3" [(ngModel)]="stage.prompt_template"></textarea>
                          </div>
                          
                          <!-- Expected Outputs -->
                          <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center">
                              <label>Expected Outputs</label>
                              <button class="btn btn-sm btn-outline-primary" 
                                      (click)="addExpectedOutput(stage)">Add Output</button>
                            </div>
                            <div *ngFor="let output of stage.expected_outputs; let j = index" 
                                class="card mb-2 p-3">
                              <div class="form-group mb-2">
                                <label>Name</label>
                                <input type="text" class="form-control" [(ngModel)]="output.name">
                              </div>
                              <div class="form-group mb-2">
                                <label>Description</label>
                                <input type="text" class="form-control" [(ngModel)]="output.description">
                              </div>
                              <div class="row">
                                <div class="col-md-8">
                                  <div class="form-group">
                                    <label>Data Type</label>
                                    <select class="form-select" [(ngModel)]="output.data_type">
                                      <option value="string">String</option>
                                      <option value="number">Number</option>
                                      <option value="boolean">Boolean</option>
                                      <option value="array">Array</option>
                                      <option value="object">Object</option>
                                    </select>
                                  </div>
                                </div>
                                <div class="col-md-4">
                                  <div class="form-group mt-4">
                                    <div class="form-check">
                                      <input class="form-check-input" type="checkbox" 
                                            [(ngModel)]="output.required" [id]="'required-' + i + '-' + j">
                                      <label class="form-check-label" [for]="'required-' + i + '-' + j">
                                        Required
                                      </label>
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <button class="btn btn-sm btn-outline-danger mt-2" 
                                     (click)="removeExpectedOutput(stage, j)">Remove</button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Tags -->
                <div class="mb-4">
                  <h6>Tags</h6>
                  <div class="d-flex flex-wrap gap-2">
                    <div *ngFor="let tag of extractedTemplateData.tags; let i = index" 
                         class="badge bg-light text-dark p-2 d-flex align-items-center">
                      <span>{{tag}}</span>
                      <button class="btn-close ms-2 small" 
                              (click)="extractedTemplateData.tags.splice(i, 1)"></button>
                    </div>
                    <div class="input-group" style="max-width: 200px;">
                      <input #tagInput type="text" class="form-control form-control-sm" 
                             placeholder="Add new tag">
                      <button class="btn btn-outline-secondary btn-sm" type="button"
                              (click)="addTag(tagInput.value); tagInput.value = ''">+</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" 
                     (click)="showTemplatePreviewModal = false">Cancel</button>
              <button type="button" class="btn btn-primary" 
                     [disabled]="!extractedTemplateData"
                     (click)="saveTemplate()">Save Template</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Developer Panel Trigger -->
      <div class="dev-panel-trigger" (click)="showDevPanel = !showDevPanel">DEV</div>
      
      <!-- Developer Panel -->
      <div *ngIf="showDevPanel" class="dev-panel">
        <div class="dev-panel-header">
          <h5>Developer Controls</h5>
          <button class="dev-panel-close" (click)="showDevPanel = false">&times;</button>
        </div>
        <div class="dev-panel-content">
          <p><strong>Current Stage:</strong> {{ currentStageNumber }} of {{ templateStages.length }}</p>
          <p><strong>Stage ID:</strong> {{ currentStageId }}</p>
          <p><strong>Progress:</strong> {{ templateProgress?.progressPercentage || 0 }}%</p>
          <p><strong>Completed Stages:</strong> {{ templateProgress?.completedStages?.length || 0 }}</p>
        </div>
        <div class="dev-panel-actions">
          <button class="btn btn-sm btn-primary" (click)="forceNextStage()">
            Force Next Stage
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .template-consultation-container {
      padding: 20px;
    }
    
    /* Modal styles */
    .modal-backdrop {
      opacity: 0.5;
    }
    
    .modal-dialog {
      max-width: 800px;
    }
    
    /* Notification styles */
    .error-notification,
    .success-notification,
    .stage-transition-notification {
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 20px;
      border-radius: 6px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
      z-index: 9999;
      transform: translateX(120%);
      transition: transform 0.4s ease;
      min-width: 300px;
      max-width: 400px;
    }
    
    .error-notification {
      background: #f44336;
      color: white;
    }
    
    .success-notification {
      background: #4caf50;
      color: white;
    }
    
    .stage-transition-notification {
      background: #2196f3;
      color: white;
    }
    
    .error-notification.show,
    .success-notification.show,
    .stage-transition-notification.show {
      transform: translateX(0);
    }
    
    .notification-title {
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    .notification-content {
      font-size: 0.9em;
    }
    
    .consultation-header {
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #dee2e6;
      animation: fadeIn 0.5s ease;
    }
    
    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 60px 0;
      animation: pulse 2s infinite;
    }
    
    .loading-container p {
      margin-top: 15px;
      color: #6c757d;
    }
    
    .consultation-content {
      display: flex;
      flex-direction: column;
    }
    
    .template-info {
      background-color: #f8f9fa;
      padding: 20px;
      border-radius: 8px;
      margin-top: 20px;
    }
    
    .template-info h5 {
      font-size: 1rem;
      margin-bottom: 15px;
      color: #495057;
    }
    
    .template-detail {
      margin-bottom: 10px;
      font-size: 0.9rem;
    }
    
    .detail-label {
      font-weight: 500;
      color: #6c757d;
      margin-right: 5px;
    }
    
    .detail-value {
      color: #495057;
    }
    
    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-top: 5px;
    }
    
    .template-tag {
      font-size: 0.75rem;
      background-color: #e9ecef;
      color: #495057;
      padding: 2px 8px;
      border-radius: 4px;
    }
    
    @media (min-width: 768px) {
      .consultation-content {
        flex-direction: row;
      }
      
      .sidebar-col {
        padding-right: 20px;
      }
    }
    
    .sidebar-col {
      margin-bottom: 20px;
      transition: all 0.3s ease;
    }
    
    .chat-col {
      margin-bottom: 20px;
      transition: all 0.3s ease;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    @keyframes slideIn {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes pulse {
      0% { opacity: 0.8; }
      50% { opacity: 1; }
      100% { opacity: 0.8; }
    }
    
    /* Stage transition notification */
    :host ::ng-deep .stage-transition-notification {
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: var(--primary);
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 1050;
      transform: translateX(120%);
      transition: transform 0.4s ease;
      max-width: 350px;
    }
    
    :host ::ng-deep .stage-transition-notification.show {
      transform: translateX(0);
    }
    
    /* Structured input animations */
    :host ::ng-deep .structured-input-container {
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.5s ease;
    }
    
    :host ::ng-deep .structured-input-container.visible {
      opacity: 1;
      transform: translateY(0);
    }
    
    /* Message transition animations */
    :host ::ng-deep .message.system {
      background-color: rgba(var(--info-rgb), 0.1);
      border-left: 3px solid var(--info);
      font-style: italic;
      padding: 12px 15px;
      margin: 10px 0;
      border-radius: 4px;
      animation: flashMessage 1.5s ease;
    }
    
    /* Consultation Summary Styles */
    .consultation-summary-container {
      animation: slideIn 0.5s ease;
    }
    
    .summary-header {
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #dee2e6;
    }
    
    .summary-content {
      margin-bottom: 2rem;
    }
    
    .summary-item {
      padding: 0.5rem 0;
    }
    
    .summary-item h6 {
      color: #495057;
      margin-bottom: 0.5rem;
    }
    
    .array-value, .object-value, .simple-value {
      background-color: #f8f9fa;
      padding: 0.75rem;
      border-radius: 4px;
      font-size: 0.95rem;
    }
    
    .export-controls {
      margin-top: 2rem;
    }
    
    /* Developer panel styles */
    .dev-panel-trigger {
      position: fixed;
      bottom: 10px;
      right: 10px;
      background-color: rgba(0, 0, 0, 0.1);
      color: #666;
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 10px;
      cursor: pointer;
      z-index: 1000;
    }
    
    .dev-panel {
      position: fixed;
      bottom: 30px;
      right: 10px;
      width: 300px;
      background-color: white;
      border: 1px solid #ddd;
      border-radius: 6px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
      padding: 10px;
      z-index: 999;
      font-size: 12px;
    }
    
    .dev-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding-bottom: 5px;
      border-bottom: 1px solid #eee;
    }
    
    .dev-panel-header h5 {
      margin: 0;
      font-size: 14px;
      font-weight: bold;
    }
    
    .dev-panel-close {
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
      color: #999;
    }
    
    .dev-panel-content {
      margin-bottom: 10px;
    }
    
    .dev-panel-content p {
      margin: 5px 0;
    }
    
    .dev-panel-actions {
      display: flex;
      justify-content: flex-end;
    }
    
    .dev-panel strong {
      color: #333;
    }
  `]
})
export class TemplateConsultationComponent implements OnInit, OnDestroy {
  // Template information
  templateId: string | null = null;
  templateName = 'Loading template...';
  templateDescription = '';
  templateDomain = '';
  templateTags: string[] = [];
  templateStages: TemplateStage[] = [];
  
  // Session state
  sessionId: number | null = null;
  messages: Message[] = [];
  loading = true;
  error = '';
  messageLoading = false;
  showSidebar = true;
  showDevPanel = false;
  showDeveloperTools = false;
  stageTransitionInProgress = false;
  
  // Template progress
  currentStageId = '';
  currentStageNumber = 0;
  templateProgress: TemplateProgress | null = null;
  currentStage: any = null;
  stageCompletionStatus: any = null;
  stageCompletionCheckInterval: any = null;
  providedInformation: {[key: string]: boolean} = {};
  
  // Structured input
  structuredInputFields: StructuredInputField[] = [];
  structuredInputPrompt = '';
  
  // Consultation data
  structuredOutputs: StructuredOutput[] = [];
  consultationSummary: ConsultationSummary | null = null;
  isConsultationComplete = false;
  
  // Template creation
  isCreatingTemplate = false;
  extractedTemplateData: ExtractedTemplateData | null = null;
  showTemplatePreviewModal = false;
  
  // Subscriptions
  private subscriptions: Subscription = new Subscription();
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private consultationService: ConsultationService,
    private templateService: TemplateService
  ) {}
  
  ngOnInit(): void {
    const templateId = this.route.snapshot.paramMap.get('id');
    this.templateId = templateId;
    
    if (!templateId) {
      this.error = 'Template ID is required';
      this.loading = false;
      return;
    }
    
    this.loadTemplate(templateId);
  }
  
  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    
    // Clear any ongoing stage completion checks
    if (this.stageCompletionCheckInterval) {
      clearInterval(this.stageCompletionCheckInterval);
    }
  }
  
  /**
   * Start periodic checking of stage completion status
   */
  startStageCompletionChecking(): void {
    // Clear any existing interval
    if (this.stageCompletionCheckInterval) {
      clearInterval(this.stageCompletionCheckInterval);
    }
    
    // Check stage completion every 10 seconds
    this.stageCompletionCheckInterval = setInterval(() => {
      this.checkStageCompletion();
    }, 10000);
    
    // Do an immediate check
    this.checkStageCompletion();
  }
  
  /**
   * Check if the current stage is complete by calling the API
   */
  checkStageCompletion(): void {
    if (!this.sessionId || !this.templateProgress) {
      return;
    }
    
    this.consultationService.checkStageCompletion(this.sessionId).subscribe({
      next: (response) => {
        this.stageCompletionStatus = response;
        
        // Update tracked information based on extracted data
        if (response.extracted_data) {
          Object.keys(response.extracted_data).forEach(key => {
            this.providedInformation[key] = true;
          });
        }
        
        // If stage is complete, notify the user
        if (response.is_complete && !this.templateProgress?.stageCompleted) {
          this.showSuccessNotification('Stage requirements met! You can proceed to the next stage.');
        }
      },
      error: (err) => {
        console.error('Error checking stage completion:', err);
      }
    });
  }
  
  /**
   * Check if a specific piece of information has been provided
   */
  checkIfInfoProvided(outputName: string): boolean {
    return this.providedInformation[outputName] === true;
  }
  
  loadTemplate(templateId: string): void {
    this.loading = true;
    
    this.templateService.getConsultationTemplate(templateId).subscribe({
      next: (template) => {
        this.initializeTemplate(template);
        this.startConsultation(templateId);
      },
      error: (err) => {
        console.error('Error loading template:', err);
        this.error = 'Failed to load template';
        this.loading = false;
      }
    });
  }
  
  initializeTemplate(template: ConsultationTemplate): void {
    this.templateName = template.name;
    this.templateDescription = template.description;
    this.templateDomain = template.domain;
    this.templateTags = template.tags;
    this.templateStages = template.stages;
    
    // Initialize consultation summary
    this.consultationSummary = {
      templateId: template.id,
      templateName: template.name,
      outputs: [],
      startTime: new Date(),
      completed: false
      // sessionId will be assigned after we get a response from the server
    };
  }
  
  startConsultation(templateId: string): void {
    console.log('Starting consultation with template ID:', templateId);
    
    this.consultationService.startTemplateConsultation(templateId).subscribe({
      next: (response) => {
        console.log('Consultation started. Response:', response);
        this.sessionId = response.session_id;
        
        if (this.consultationSummary) {
          this.consultationSummary.sessionId = response.session_id;
        }
        
        // Add initial message - handle message being either string or object
        if (response.message) {
          console.log('Adding initial message:', response.message);
          
          let initialMessage: Message;
          
          if (typeof response.message === 'string') {
            initialMessage = {
              content: response.message,
              role: 'assistant',
              stageId: this.currentStageId || ''
            };
          } else if (typeof response.message === 'object' && response.message.content) {
            initialMessage = {
              content: response.message.content,
              role: 'assistant',
              stageId: this.currentStageId || ''
            };
          } else {
            initialMessage = {
              content: JSON.stringify(response.message),
              role: 'assistant',
              stageId: this.currentStageId || ''
            };
          }
          
          this.messages = [initialMessage];
        }
        
        // Set initial template progress
        const progress = response.template_progress;
        console.log('Template progress from response:', progress);
        
        if (progress) {
          this.updateTemplateProgress(progress);
        } else {
          console.warn('No template progress in response, using default values');
          // Create default progress if none provided
          const defaultProgress = {
            stage_id: this.templateStages[0]?.id || '',
            current_stage: 1,
            completed_stages: []
          };
          this.updateTemplateProgress(defaultProgress);
        }
        
        // Check for structured inputs in the current stage
        this.updateStructuredInputs(response);
        
        this.loading = false;
      },
      error: (err) => {
        console.error('Error starting consultation:', err);
        this.error = 'Failed to start consultation';
        this.loading = false;
      }
    });
  }
  
  updateTemplateProgress(progress: any): void {
    if (!progress) {
      console.warn('Received null or undefined progress object');
      return;
    }
    
    console.log('Updating template progress with:', progress);
    
    // Handle both legacy and new API response formats
    let stageId = '';
    let currentStageNumber = 1;
    let stageName = '';
    let stageDescription = '';
    let completedStages: string[] = [];
    const stageCompleted = progress.stage_completed === true;
    let progressPercentage = 0;
    
    // Process new API format
    if (progress.next_stage && progress.completed_stage_index !== undefined) {
      // New format: Uses completed_stage_index and next_stage properties
      const nextStageIndex = progress.completed_stage_index + 1;
      currentStageNumber = nextStageIndex + 1; // API is 0-indexed, UI is 1-indexed
      
      // Try to get stage name and ID from next_stage
      if (progress.next_stage) {
        stageName = progress.next_stage.name || `Stage ${currentStageNumber}`;
        stageDescription = progress.next_stage.description || '';
        
        // Generate a unique ID if not available
        stageId = progress.next_stage.id || `stage_${nextStageIndex}`;
      }
      
      // Use provided progress percentage or calculate
      progressPercentage = progress.progress_percentage !== undefined ? 
        progress.progress_percentage : 
        Math.min(100, Math.max(0, (currentStageNumber / this.templateStages.length) * 100));
      
      // Track completed stages
      if (progress.completed_stage) {
        // Add the completed stage to our tracking
        completedStages = [progress.completed_stage];
      }
    } 
    // Process legacy format
    else {
      // Legacy format: Uses stage_id and current_stage properties
      stageId = progress.stage_id || '';
      
      // Ensure current_stage is a valid number
      currentStageNumber = typeof progress.current_stage === 'number' && !isNaN(progress.current_stage) 
        ? progress.current_stage 
        : 1;  // Default to 1 if undefined or not a valid number
      
      // Get stage details
      stageName = this.getStageNameById(stageId);
      stageDescription = this.getStageDescriptionById(stageId);
      
      // Get completed stages
      completedStages = Array.isArray(progress.completed_stages) ? progress.completed_stages : [];
      
      // Calculate progress percentage
      progressPercentage = progress.progress_percentage !== undefined ? 
        progress.progress_percentage : 
        Math.min(100, Math.max(0, (currentStageNumber / this.templateStages.length) * 100));
    }
    
    // Check if we're transitioning to a new stage
    const isStageChange = this.currentStageId !== stageId;
    
    // Store previous stage for animation
    const previousStage = this.currentStageNumber;
    
    // Update current state
    this.currentStageId = stageId;
    this.currentStageNumber = currentStageNumber;
    
    // Calculate total stages safely
    const totalStages = this.templateStages.length || 1;  // Default to 1 if no stages
    
    // Set template progress for the chat box component
    this.templateProgress = {
      currentStage: this.currentStageNumber,
      totalStages: totalStages,
      stageName: stageName,
      stageDescription: stageDescription,
      progressPercentage: progressPercentage,
      stageId: stageId,
      completedStages: completedStages,
      stageCompleted: stageCompleted
    };
    
    console.log('Updated template progress:', this.templateProgress);
    
    // Find and set the current stage object for user guidance
    this.currentStage = this.templateStages.find(s => s.id === stageId) || null;
    
    // Reset the provided information tracking when changing stages
    if (isStageChange) {
      this.providedInformation = {};
      this.stageCompletionStatus = null;
    }
    
    // Start checking stage completion periodically
    this.startStageCompletionChecking();
    
    // If we're changing stages, add a notification and transition message
    if (isStageChange && previousStage > 0) {
      this.handleStageTransition(previousStage, this.currentStageNumber);
    }
  }
  
  getStageDescriptionById(stageId: string): string {
    if (!stageId) return '';
    const stage = this.templateStages.find(s => s.id === stageId);
    return stage?.description || '';
  }
  
  getStageNameById(stageId: string): string {
    if (!stageId || !this.templateStages || this.templateStages.length === 0) {
      return `Stage ${this.currentStageNumber}`;
    }
    
    const stage = this.templateStages.find(s => s.id === stageId);
    return stage?.name || `Stage ${this.currentStageNumber}`;
  }
  
  handleStageTransition(fromStage: number, toStage: number): void {
    // Add a system message about stage transition
    const fromStageName = this.templateStages[fromStage - 1]?.name || `Stage ${fromStage}`;
    const toStageName = this.templateStages[toStage - 1]?.name || `Stage ${toStage}`;
    
    // Add a transition message
    this.messages.push({
      content: `✅ Completed: "${fromStageName}"\n\n▶️ Starting: "${toStageName}"`,
      role: 'system',
      stageId: this.currentStageId
    });
    
    // Show a visual notification
    this.showNotification(`Moving to stage ${toStage}: ${toStageName}`);
  }
  
  showNotification(message: string): void {
    // Create a notification element
    const notification = document.createElement('div');
    notification.className = 'stage-transition-notification';
    notification.innerHTML = `<div class="notification-content">${message}</div>`;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);
    
    // Hide and remove after delay
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 400);
    }, 3000);
  }
  
  updateStructuredInputs(response: TemplateConsultationResponse): void {
    console.log('Checking for structured inputs in response:', response);
    
    if (response.template_progress?.ui_components?.structured_input) {
      console.log('Found structured input in response:', response.template_progress.ui_components.structured_input);
      
      const structuredInput = response.template_progress.ui_components.structured_input;
      
      // Validate that fields is an array
      if (!Array.isArray(structuredInput.fields)) {
        console.error('Structured input fields is not an array:', structuredInput.fields);
        this.structuredInputFields = [];
        return;
      }
      
      try {
        this.structuredInputFields = structuredInput.fields.map(input => {
          // Validate required fields
          if (!input.id || !input.label) {
            console.warn('Structured input field missing required properties:', input);
          }
          
          // Handle null values
          const fieldType = (input.type || 'text') as 'text' | 'textarea' | 'select' | 'radio' | 'checkbox';
          
          return {
            id: input.id || `field_${Math.random().toString(36).substring(2, 9)}`,
            label: input.label || 'Unnamed Field',
            type: fieldType,
            options: Array.isArray(input.options) ? input.options : [],
            value: '',
            placeholder: input.placeholder || '',
            required: !!input.required,
            helpText: input.help_text || ''
          };
        });
        
        this.structuredInputPrompt = structuredInput.prompt || 'Please provide the following information:';
        console.log('Structured input fields processed:', this.structuredInputFields);
      } catch (err) {
        console.error('Error processing structured input fields:', err);
        this.structuredInputFields = [];
        this.structuredInputPrompt = '';
      }
    } else {
      console.log('No structured inputs in this response');
      this.structuredInputFields = [];
      this.structuredInputPrompt = '';
    }
  }
  
  sendMessage(message: string): void {
    if (!this.sessionId) {
      console.error('Cannot send message - no active session ID');
      this.error = 'No active session. Please refresh and try again.';
      return;
    }
    
    if (!message || message.trim() === '') {
      console.warn('Attempted to send empty message');
      return;
    }
    
    console.log('Sending message to session:', this.sessionId, 'Message:', message);
    
    this.messageLoading = true;
    
    // Add user message immediately for better UI feedback
    const userMessage = {
      content: message,
      role: 'user' as 'user',
      stageId: this.currentStageId
    };
    this.messages.push(userMessage);
    
    this.consultationService.sendTemplateMessage(message, this.sessionId).subscribe({
      next: (response) => {
        console.log('Message response received:', response);
        
        // Check if we have a valid response message - handle string or object
        if (response.message) {
          // Handle response.message being either an object or a string
          let messageContent = '';
          
          if (typeof response.message === 'string') {
            messageContent = response.message;
          } else if (typeof response.message === 'object') {
            messageContent = response.message.content || 'No response content';
          } else {
            messageContent = JSON.stringify(response.message);
          }
          
          // Create assistant message
          const assistantMessage = {
            content: messageContent,
            role: 'assistant' as 'assistant',
            stageId: this.currentStageId
          };
          
          // Add assistant response
          this.messages.push(assistantMessage);
        } else {
          console.warn('Received response without message object');
          // Add fallback message
          this.messages.push({
            content: 'The system responded but did not provide a message.',
            role: 'system' as 'system',
            stageId: this.currentStageId
          });
        }
        
        // Update template progress
        if (response.template_progress) {
          this.updateTemplateProgress(response.template_progress);
        } else {
          console.warn('Response missing template_progress data');
        }
        
        // Check for structured inputs
        this.updateStructuredInputs(response);
        
        this.messageLoading = false;
      },
      error: (err) => {
        console.error('Error sending message:', err);
        this.error = 'Failed to send message';
        this.messageLoading = false;
        
        // Add error message to chat
        this.messages.push({
          content: 'There was an error communicating with the server. Please try again.',
          role: 'system' as 'system',
          stageId: this.currentStageId
        });
      }
    });
  }
  
  submitStructuredInput(data: Record<string, any>): void {
    if (!this.sessionId) {
      console.error('Cannot submit structured input - no active session ID');
      this.error = 'No active session. Please refresh and try again.';
      return;
    }
    
    console.log('Submitting structured input to session:', this.sessionId, 'Data:', data);
    
    this.messageLoading = true;
    
    // First add user message with structured data
    const structuredDataMessage = this.formatStructuredDataForDisplay(data);
    this.messages.push({
      content: structuredDataMessage,
      role: 'user',
      stageId: this.currentStageId
    });
    
    // Store structured output data
    if (this.currentStageId) {
      const currentStage = this.templateStages.find(stage => stage.id === this.currentStageId);
      if (currentStage) {
        const structuredOutput: StructuredOutput = {
          stageId: this.currentStageId,
          stageName: currentStage.name,
          stageNumber: this.currentStageNumber,
          data: { ...data }, // Clone data to avoid reference issues
          timestamp: new Date()
        };
        
        console.log('Adding structured output for stage:', currentStage.name, structuredOutput);
        
        // Save to our structured outputs array
        this.structuredOutputs.push(structuredOutput);
        
        // Add to consultation summary if it exists
        if (this.consultationSummary) {
          this.consultationSummary.outputs.push(structuredOutput);
        }
      } else {
        console.warn('Could not find stage with ID:', this.currentStageId);
      }
    }
    
    this.consultationService.submitStructuredInput(data, this.sessionId).subscribe({
      next: (response) => {
        console.log('Structured input response received:', response);
        
        // Check if we have a valid response message
        if (response.message) {
          // Add assistant response
          this.messages.push({
            content: response.message.content || 'No response content',
            role: 'assistant',
            stageId: this.currentStageId
          });
        } else {
          console.warn('Received response without message object');
          // Add fallback message
          this.messages.push({
            content: 'The system processed your input but did not provide a response message.',
            role: 'system',
            stageId: this.currentStageId
          });
        }
        
        // Update template progress
        if (response.template_progress) {
          this.updateTemplateProgress(response.template_progress);
          
          // Check if consultation is complete
          if ((response.template_progress?.current_stage !== undefined && 
               response.template_progress.current_stage > this.templateStages.length) || 
              (this.currentStageNumber >= this.templateStages.length && 
               response.template_progress?.completed_stages && 
               response.template_progress.completed_stages.length >= this.templateStages.length) ||
              (response.template_progress?.progress_percentage === 100)) {
            this.finalizeConsultation();
          }
          
          // Check for structured inputs for the next stage
          this.updateStructuredInputs(response);
        } else {
          console.warn('Response missing template_progress data');
        }
        
        this.messageLoading = false;
      },
      error: (err) => {
        console.error('Error submitting structured data:', err);
        this.error = 'Failed to submit data';
        this.messageLoading = false;
        
        // Add error message to chat
        this.messages.push({
          content: 'There was an error submitting your data. Please try again.',
          role: 'system',
          stageId: this.currentStageId
        });
      }
    });
  }
  
  formatStructuredDataForDisplay(data: Record<string, any>): string {
    let result = '### Structured Input:\n';
    
    for (const [key, value] of Object.entries(data)) {
      const formattedKey = key.replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
        
      result += `**${formattedKey}**: ${value}\n`;
    }
    
    return result;
  }
  
  toggleSidebar(): void {
    this.showSidebar = !this.showSidebar;
  }
  
  backToTemplates(): void {
    this.router.navigate(['/templates']);
  }
  
  /**
   * Finalizes the consultation when all stages are complete
   * Generates summary and prepares for export
   */
  finalizeConsultation(): void {
    console.log('Finalizing consultation');
    
    // Make sure we have a consultation summary
    if (!this.consultationSummary) {
      this.consultationSummary = {
        consultationId: this.sessionId || undefined,
        sessionId: this.sessionId || undefined,
        templateId: this.templateId!,
        templateName: this.templateName,
        completedAt: new Date(),
        completed: true,
        outputs: [...this.structuredOutputs], // Copy all collected outputs
        summary: {} // This will be filled with summary data
      };
    } else {
      // Update completion time
      this.consultationSummary.completedAt = new Date();
      this.consultationSummary.completed = true;
      // Ensure all outputs are included
      this.consultationSummary.outputs = [...this.structuredOutputs];
    }
    
    // Generate summary data based on collected outputs
    this.generateConsultationSummary();
    
    // Show completion notification
    this.showConsultationCompleteNotification();
    
    // Mark consultation as completed
    this.isConsultationComplete = true;
  }
  
  /**
   * Generate a summary of all collected outputs from the consultation
   * This organizes the structured data into a cohesive summary
   */
  generateConsultationSummary(): void {
    if (!this.consultationSummary) return;
    
    // Initialize summary object
    const summary: Record<string, any> = {};
    
    // Process all structured outputs and organize by categories
    this.structuredOutputs.forEach(output => {
      // Extract key information based on stage type or data structure
      // This logic will depend on your specific template structure
      Object.entries(output.data).forEach(([key, value]) => {
        // Group similar data across stages
        if (!summary[key]) {
          summary[key] = value;
        } else if (Array.isArray(summary[key])) {
          // If it's already an array, append
          if (Array.isArray(value)) {
            summary[key] = [...summary[key], ...value];
          } else {
            summary[key].push(value);
          }
        } else {
          // Convert to array if we have multiple values
          summary[key] = [summary[key], value];
        }
      });
    });
    
    // Save the generated summary
    this.consultationSummary.summary = summary;
    console.log('Generated consultation summary:', summary);
  }
  
  /**
   * Show a notification that the consultation is complete
   */
  showConsultationCompleteNotification(): void {
    // Create a notification element
    const notification = document.createElement('div');
    notification.className = 'stage-transition-notification consultation-complete';
    notification.innerHTML = `
      <div class="notification-title">
        <i class="bi bi-check-circle-fill me-2"></i>
        Consultation Complete
      </div>
      <div class="notification-content">
        All stages have been completed. You can now export your results.
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);
    
    // Hide and remove after delay
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 400);
    }, 5000);
  }
  
  /**
   * Gets the summary items in a format suitable for display
   */
  getSummaryItems(): Array<{label: string, value: any, type: string}> {
    if (!this.consultationSummary?.summary) return [];
    
    return Object.entries(this.consultationSummary.summary).map(([key, value]) => {
      // Format the key for display (capitalize, replace underscores)
      const label = key.replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      
      // Determine the type of value
      let type = 'string';
      if (Array.isArray(value)) {
        type = 'array';
      } else if (typeof value === 'object' && value !== null) {
        type = 'object';
      }
      
      return { label, value, type };
    });
  }
  
  /**
   * Gets keys from an object for template iteration
   */
  getObjectKeys(obj: any): string[] {
    return obj ? Object.keys(obj) : [];
  }
  
  /**
   * Start a new consultation using the same template
   */
  startNewConsultation(): void {
    // Navigate to the same template but reset everything
    if (this.templateId) {
      this.router.navigate(['/templates', this.templateId]);
    }
  }
  
  exportConsultation(): void {
    if (!this.sessionId) return;
    
    // TODO: Implement export functionality
    console.log('Exporting consultation results for session:', this.sessionId);
    
    // This would typically call a service method to generate and download
    // a PDF or other document format with the consultation results
  }
  
  /**
   * Create a new template from the current consultation
   * This extracts patterns from the conversation and generates a reusable template
   */
  createTemplateFromConsultation(): void {
    if (!this.sessionId || !this.consultationSummary) {
      console.error('Cannot create template: missing session ID or consultation data');
      return;
    }
    
    // Show loading state
    this.isCreatingTemplate = true;
    
    // Call service to extract template from consultation
    this.consultationService.extractTemplateFromConsultation(this.sessionId)
      .subscribe({
        next: (templateData: ExtractedTemplateData) => {
          console.log('Template extraction successful:', templateData);
          this.isCreatingTemplate = false;
          
          // Store the extracted template data for the preview
          this.extractedTemplateData = templateData;
          
          // Show the template preview modal
          this.showTemplatePreviewModal = true;
        },
        error: (error: any) => {
          console.error('Error extracting template:', error);
          this.isCreatingTemplate = false;
          
          // Show error message
          const errorMessage = error.error?.detail || 'Failed to extract template from consultation';
          this.error = errorMessage;
          
          // Create a notification element for the error
          this.showErrorNotification(errorMessage);
        }
      });
  }
  
  /**
   * Show error notification
   */
  showErrorNotification(message: string): void {
    // Create a notification element
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.innerHTML = `
      <div class="notification-title">
        <i class="bi bi-exclamation-circle-fill me-2"></i>
        Error
      </div>
      <div class="notification-content">
        ${message}
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);
    
    // Hide and remove after delay
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 400);
    }, 5000);
  }
  
  /**
   * Add a new expected output to a stage
   */
  addExpectedOutput(stage: any): void {
    if (!stage.expected_outputs) {
      stage.expected_outputs = [];
    }
    
    stage.expected_outputs.push({
      name: '',
      description: '',
      data_type: 'string',
      required: false
    });
  }
  
  /**
   * Remove an expected output from a stage
   */
  removeExpectedOutput(stage: any, index: number): void {
    stage.expected_outputs.splice(index, 1);
  }
  
  /**
   * Add a new tag to the template
   */
  addTag(tag: string): void {
    if (!tag || !this.extractedTemplateData) return;
    
    const trimmedTag = tag.trim();
    if (trimmedTag && !this.extractedTemplateData.tags.includes(trimmedTag)) {
      this.extractedTemplateData.tags.push(trimmedTag);
    }
  }
  
  /**
   * Save the template to the database
   */
  saveTemplate(): void {
    if (!this.extractedTemplateData) return;
    
    // Validate template data
    if (!this.extractedTemplateData.name || this.extractedTemplateData.name.trim() === '') {
      this.showErrorNotification('Template name is required');
      return;
    }
    
    if (!this.extractedTemplateData.stages || this.extractedTemplateData.stages.length === 0) {
      this.showErrorNotification('Template must have at least one stage');
      return;
    }
    
    // Show loading state
    this.isCreatingTemplate = true;
    
    // Prepare the template data for saving
    // Convert ExtractedTemplateData to ConsultationTemplate format
    const templateToSave: Partial<ConsultationTemplate> = {
      name: this.extractedTemplateData.name,
      description: this.extractedTemplateData.description,
      domain: this.extractedTemplateData.domain,
      initial_system_prompt: this.extractedTemplateData.initial_system_prompt,
      tags: this.extractedTemplateData.tags,
      is_public: false,
      stages: this.extractedTemplateData.stages.map((stage, index) => {
        return {
          id: `stage_${Date.now()}_${index}`, // Generate unique IDs for each stage
          name: stage.name,
          description: stage.description,
          stage_type: stage.stage_type,
          prompt_template: stage.prompt_template,
          expected_outputs: stage.expected_outputs
        };
      })
    };
    
    // Call service to save the template
    this.templateService.createConsultationTemplate(templateToSave)
      .subscribe({
        next: (savedTemplate) => {
          console.log('Template saved successfully:', savedTemplate);
          this.isCreatingTemplate = false;
          this.showTemplatePreviewModal = false;
          
          // Show success notification
          this.showSuccessNotification('Template created successfully!');
          
          // Redirect to the template details page
          setTimeout(() => {
            this.router.navigate(['/templates', savedTemplate.id]);
          }, 2000);
        },
        error: (error: any) => {
          console.error('Error saving template:', error);
          this.isCreatingTemplate = false;
          
          // Show error message
          const errorMessage = error.error?.detail || 'Failed to save template';
          this.showErrorNotification(errorMessage);
        }
      });
  }
  
  /**
   * Force progression to the next stage
   * This is helpful when automatic stage detection fails
   */
  forceNextStage(): void {
    if (!this.sessionId) {
      this.showErrorNotification('No active session found');
      return;
    }
    
    this.messageLoading = true;
    this.stageTransitionInProgress = true;
    
    this.consultationService.forceNextStage(this.sessionId)
      .subscribe({
        next: (response) => {
          // Find the new stage information from our template stages
          const nextStage = this.templateStages.find(stage => stage.id === response.current_stage) || 
                          { name: 'Next Stage', description: '' };
          
          // Create template progress wrapper to match expected format
          const templateProgress = {
            currentStage: response.current_stage_index,
            totalStages: this.templateStages.length,
            stageName: nextStage.name,
            stageDescription: nextStage.description,
            progressPercentage: response.progress_percentage,
            stageId: response.current_stage,
            completedStages: response.completed_stages
          };
          
          // Update template progress
          this.templateProgress = templateProgress;
          this.currentStageId = templateProgress.stageId || '';
          this.currentStageNumber = templateProgress.currentStage || 0;
          
          // Show success notification
          this.showSuccessNotification('Successfully advanced to the next stage');
          
          // Hide the developer panel
          this.showDevPanel = false;
          
          this.messageLoading = false;
          this.stageTransitionInProgress = false;
        },
        error: (error) => {
          console.error('Error forcing next stage:', error);
          this.showErrorNotification('Failed to advance to the next stage: ' + (error.error?.detail || 'Unknown error'));
          this.messageLoading = false;
          this.stageTransitionInProgress = false;
        }
      });
  }
  
  /**
   * Toggle developer tools panel
   */
  toggleDeveloperTools(): void {
    this.showDeveloperTools = !this.showDeveloperTools;
  }

  /**
   * Show success notification
   */
  showSuccessNotification(message: string): void {
    // Create a notification element
    const notification = document.createElement('div');
    notification.className = 'success-notification';
    notification.innerHTML = `
      <div class="notification-title">
        <i class="bi bi-check-circle-fill me-2"></i>
        Success
      </div>
      <div class="notification-content">
        ${message}
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);
    
    // Hide and remove after delay
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 400);
    }, 5000);
  }
}