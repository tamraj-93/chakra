import { Component, Input, Output, EventEmitter, OnInit, ElementRef, ViewChild, AfterViewChecked, SecurityContext } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { chatMessageAnimation, typingAnimation } from '../../shared/animations';

// Define the Message interface locally
interface SourceCitation {
  title: string;
  source: string;
  relevance?: number;
  content_snippet?: string;
}

interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
  stageId?: string; // Added to track which stage a message belongs to
  sources?: SourceCitation[]; // Added to display RAG citation sources
}

// Define the template progress interface
export interface TemplateProgress {
  currentStage: number;
  totalStages: number;
  stageName: string;
  stageDescription?: string;
  progressPercentage: number;
  stageId?: string;
  completedStages?: string[];
  stageCompleted?: boolean;
}

@Component({
  selector: 'app-chat-box',
  animations: [chatMessageAnimation, typingAnimation],
  styleUrls: ['./healthcare-styles.css'],
  template: `
    <div class="chat-container">
      <!-- Healthcare RAG Indicator - Only show if using healthcare RAG -->
      <div *ngIf="isHealthcareConsultation" class="healthcare-rag-container">
        <div class="healthcare-rag-badge">
          <i class="bi bi-bookmark-check-fill"></i> Healthcare Knowledge Enhanced
        </div>
        <div class="healthcare-rag-info">
          <p>This consultation is using specialized healthcare knowledge to provide accurate and compliant recommendations.</p>
          <p class="small text-muted">Healthcare SLA recommendations include references to industry standards and regulations.</p>
        </div>
      </div>

      <!-- Template Progress Bar - Only show if in template mode -->
      <div *ngIf="templateMode && templateProgress" class="template-progress-container">
        <div class="stage-info">
          <span class="stage-number">Stage {{ templateProgress.currentStage || 1 }} of {{ templateProgress.totalStages || 1 }}</span>
          <span class="stage-name">{{ templateProgress.stageName || 'Consultation' }}</span>
        </div>
        <div class="progress">
          <div class="progress-bar" 
              [style.width.%]="templateProgress.progressPercentage !== undefined ? templateProgress.progressPercentage : 0"
              [ngClass]="{'progress-bar-animated': loading}">
          </div>
        </div>
        <div *ngIf="templateProgress.stageDescription" class="stage-description">
          {{ templateProgress.stageDescription }}
        </div>
      </div>

      <div class="messages-container" #messagesContainer>
        <!-- Debug: Display messages count -->
        <div *ngIf="messages.length === 0" class="text-center text-muted my-4">
          No messages yet
        </div>

        <div *ngFor="let message of messages; let i = index" 
             [@chatMessageAnimation]
             [ngClass]="{'message-user': message.role === 'user', 'message-assistant': message.role === 'assistant', 'message-stage-transition': message.stageId && i > 0 && message.stageId !== messages[i-1].stageId}"
             class="message">
          <!-- Stage Transition Marker -->
          <div *ngIf="message.stageId && i > 0 && message.stageId !== messages[i-1].stageId" class="stage-transition">
            <div class="stage-marker"></div>
            <div class="stage-label">Stage {{ getStageNumberById(message.stageId) }}</div>
            <div class="stage-marker"></div>
          </div>
          <div class="message-avatar">
            <div class="avatar-icon" 
                 [ngClass]="{
                   'user-avatar': message.role === 'user',
                   'assistant-avatar': message.role === 'assistant',
                   'healthcare-avatar': message.role === 'assistant' && isHealthcareConsultation
                 }">
              <ng-container *ngIf="message.role === 'user'">U</ng-container>
              <ng-container *ngIf="message.role === 'assistant' && !isHealthcareConsultation">A</ng-container>
              <ng-container *ngIf="message.role === 'assistant' && isHealthcareConsultation">
                <i class="bi bi-heart-pulse"></i>
              </ng-container>
            </div>
          </div>
          <div class="message-content">
            <div class="message-sender">
              {{ message.role === 'user' ? 'You' : (isHealthcareConsultation ? 'Healthcare SLA Assistant' : 'SLA Assistant') }}
              <span *ngIf="message.role === 'assistant' && isHealthcareConsultation" class="healthcare-badge-small">HIPAA</span>
            </div>
            <div class="message-text" [innerHTML]="formatMessageContent(message.content)">
            </div>
            <!-- Citation Sources Display - Enhanced for healthcare -->
            <div *ngIf="message.sources && message.sources.length > 0" 
                 class="message-sources" 
                 [ngClass]="{'healthcare-sources': isHealthcareConsultation}">
              <div class="sources-header">
                <div class="d-flex justify-content-between align-items-center">
                  <div class="sources-title" (click)="toggleSourcesVisibility(i)">
                    <i class="bi" [ngClass]="isSourcesVisible(i) ? 'bi-chevron-down' : 'bi-chevron-right'"></i>
                    <span *ngIf="!isHealthcareConsultation">Sources ({{ message.sources.length }})</span>
                    <span *ngIf="isHealthcareConsultation" class="healthcare-sources-header">
                      <i class="bi bi-journal-medical me-1"></i> Healthcare References ({{ message.sources.length }})
                    </span>
                  </div>
                  <div *ngIf="isHealthcareConsultation" class="sources-help" (click)="toggleSourcesHelp()">
                    <i class="bi bi-question-circle"></i>
                  </div>
                </div>
                
                <!-- Healthcare sources help popup -->
                <div *ngIf="showSourcesHelp && isHealthcareConsultation" class="sources-help-popup">
                  <h6><i class="bi bi-info-circle me-2"></i>About Healthcare References</h6>
                  <p>These references are from healthcare industry documentation, SLA templates, and compliance guidelines.</p>
                  <p>They provide verifiable information about:</p>
                  <ul>
                    <li>HIPAA compliance requirements</li>
                    <li>Healthcare data security standards</li>
                    <li>Patient privacy protection measures</li>
                    <li>Healthcare IT best practices</li>
                  </ul>
                  <button class="btn btn-sm btn-outline-primary" (click)="toggleSourcesHelp()">Close</button>
                </div>
              </div>
              <div class="sources-list" *ngIf="isSourcesVisible(i)">
                <div *ngFor="let source of message.sources; let s = index" 
                     class="source-item"
                     [ngClass]="{'healthcare-source-item': isHealthcareConsultation}">
                  <div class="source-title">
                    <i *ngIf="isHealthcareConsultation" class="bi bi-file-earmark-medical me-2"></i>
                    {{ source.title || (isHealthcareConsultation ? 'Healthcare Document ' : 'Document ') + (s + 1) }}
                  </div>
                  <div class="source-path">{{ source.source }}</div>
                  <div *ngIf="source.content_snippet" class="source-snippet">
                    <i class="bi bi-quote me-1"></i>
                    "{{ source.content_snippet }}"
                  </div>
                </div>
              </div>
            </div>
            <div class="message-time" *ngIf="message.timestamp">
              {{ formatTimestamp(message.timestamp) }}
            </div>
          </div>
        </div>
        <div *ngIf="loading" [@typingAnimation]="'active'" class="message message-assistant">
          <div class="message-avatar">
            <div class="avatar-icon" [ngClass]="{'assistant-avatar': !isHealthcareConsultation, 'healthcare-avatar': isHealthcareConsultation}">
              <ng-container *ngIf="!isHealthcareConsultation">A</ng-container>
              <ng-container *ngIf="isHealthcareConsultation"><i class="bi bi-heart-pulse"></i></ng-container>
            </div>
          </div>
          <div class="message-content">
            <div class="message-sender">
              {{ isHealthcareConsultation ? 'Healthcare SLA Assistant' : 'SLA Assistant' }}
              <span *ngIf="isHealthcareConsultation" class="healthcare-badge-small">HIPAA</span>
            </div>
            <div class="typing-indicator" [ngClass]="{'healthcare-typing': isHealthcareConsultation}">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="input-container">
        <!-- Structured Input Fields - Only show if specified in current stage -->
        <div *ngIf="structuredInputFields && structuredInputFields.length > 0" class="structured-input-fields">
          <h4>{{ structuredInputPrompt || 'Please provide the following information:' }}</h4>
          <div *ngFor="let field of structuredInputFields" class="form-group mb-3">
            <label [for]="field.id">{{ field.label }}{{ field.required ? ' *' : '' }}</label>
            
            <ng-container [ngSwitch]="field.type">
              <!-- Text input -->
              <input *ngSwitchCase="'text'" 
                     type="text" 
                     class="form-control" 
                     [id]="field.id" 
                     [placeholder]="field.placeholder || ''" 
                     [(ngModel)]="field.value"
                     [required]="!!field.required">
              
              <!-- Textarea -->
              <textarea *ngSwitchCase="'textarea'" 
                       class="form-control" 
                       [id]="field.id" 
                       [placeholder]="field.placeholder || ''" 
                       [(ngModel)]="field.value"
                       [required]="!!field.required"
                       rows="3"></textarea>
              
              <!-- Select dropdown -->
              <select *ngSwitchCase="'select'" 
                     class="form-select" 
                     [id]="field.id" 
                     [(ngModel)]="field.value"
                     [required]="!!field.required">
                <option value="" disabled selected>Select an option</option>
                <option *ngFor="let option of field.options" [value]="option.value">
                  {{ option.label }}
                </option>
              </select>
              
              <!-- Radio buttons -->
              <div *ngSwitchCase="'radio'" class="radio-group">
                <div *ngFor="let option of field.options" class="form-check">
                  <input type="radio" 
                         class="form-check-input" 
                         [id]="field.id + '-' + option.value" 
                         [name]="field.id" 
                         [value]="option.value" 
                         [(ngModel)]="field.value"
                         [required]="!!field.required">
                  <label class="form-check-label" [for]="field.id + '-' + option.value">
                    {{ option.label }}
                  </label>
                </div>
              </div>
              
              <!-- Default: text input -->
              <input *ngSwitchDefault 
                     type="text" 
                     class="form-control" 
                     [id]="field.id" 
                     [placeholder]="field.placeholder || ''" 
                     [(ngModel)]="field.value"
                     [required]="!!field.required">
            </ng-container>
            
            <small *ngIf="field.helpText" class="form-text text-muted">
              {{ field.helpText }}
            </small>
          </div>
          
          <div class="d-flex justify-content-end mt-3">
            <button class="btn btn-primary" 
                    (click)="submitStructuredInput()"
                    [disabled]="!areRequiredFieldsValid() || loading">
              Submit
            </button>
          </div>
        </div>
        
        <!-- Standard Text Input - Only show if no structured fields or showTextInput is true -->
        <form *ngIf="!structuredInputFields || structuredInputFields.length === 0 || showTextInput" 
              (ngSubmit)="sendMessage()">
          <div class="input-group">
            <input type="text" class="form-control" 
                   placeholder="Type your message..." 
                   [(ngModel)]="newMessage"
                   name="newMessage"
                   [disabled]="loading">
            <button class="btn btn-primary" 
                    type="submit"
                    [disabled]="!newMessage || loading">
              <i class="bi bi-send"></i> Send
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 600px;
      border: 1px solid var(--border);
      
    /* Healthcare RAG UI elements */
    .healthcare-rag-container {
      background-color: #EFF6FF;
      border-left: 4px solid #2563EB;
      margin-bottom: 12px;
      padding: 12px;
      border-radius: 4px;
      display: flex;
      flex-direction: column;
    }
    
    .healthcare-rag-badge {
      display: inline-flex;
      align-items: center;
      background-color: #2563EB;
      color: white;
      padding: 5px 12px;
      border-radius: 50px;
      font-weight: 600;
      font-size: 0.9rem;
      margin-bottom: 8px;
      align-self: flex-start;
    }
    
    .healthcare-rag-badge i {
      margin-right: 6px;
    }
    
    .healthcare-rag-info {
      font-size: 0.9rem;
    }
    
    .healthcare-rag-info p {
      margin-bottom: 4px;
    }
    
    .healthcare-sources {
      background-color: #F0FDF4;
      border-left: 3px solid #16A34A;
    }
    
    .healthcare-sources-header {
      color: #16A34A;
      font-weight: 600;
    }
    
    .healthcare-source-item {
      background-color: #F0FDF4;
      border-left: 2px solid #16A34A;
    }
    
    /* Source help elements */
    .sources-title {
      cursor: pointer;
      flex-grow: 1;
    }
    
    .sources-help {
      cursor: pointer;
      color: #64748b;
      padding: 0 8px;
      transition: color 0.2s;
    }
    
    .sources-help:hover {
      color: #2563EB;
    }
    
    .sources-help-popup {
      background-color: white;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 16px;
      margin-top: 8px;
      position: relative;
      z-index: 100;
    }
    
    .sources-help-popup h6 {
      color: #2563EB;
      margin-bottom: 12px;
    }
    
    .sources-help-popup p {
      font-size: 0.9rem;
      margin-bottom: 8px;
    }
    
    .sources-help-popup ul {
      padding-left: 20px;
      margin-bottom: 16px;
    }
    
    .sources-help-popup ul li {
      font-size: 0.85rem;
      margin-bottom: 4px;
    }
    
    /* Healthcare-specific UI elements */
    .healthcare-avatar {
      background-color: #16A34A !important;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .healthcare-avatar i {
      font-size: 0.9rem;
    }
    
    .healthcare-badge-small {
      background-color: #16A34A;
      color: white;
      font-size: 0.65rem;
      padding: 2px 4px;
      border-radius: 4px;
      margin-left: 6px;
      font-weight: 600;
      vertical-align: middle;
    }
      border-radius: 8px;
      background-color: var(--surface);
      box-shadow: 0 4px 6px var(--shadow);
      overflow: hidden; /* Ensure contents don't overflow */
    }
    
    .template-progress-container {
      padding: 15px;
      border-bottom: 1px solid var(--border);
      background-color: #f8f9fa;
    }
    
    .stage-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    
    .stage-number {
      font-weight: bold;
      color: var(--primary);
    }
    
    .stage-name {
      font-weight: 600;
    }
    
    .stage-description {
      font-size: 0.875rem;
      color: #6c757d;
      margin-top: 8px;
    }
    
    .progress {
      height: 8px;
      background-color: #e9ecef;
      border-radius: 4px;
      overflow: hidden;
    }
    
    .progress-bar {
      background-color: var(--primary);
      transition: width 0.6s ease;
    }
    
    .progress-bar-animated {
      animation: progress-bar-stripes 1s linear infinite;
      background-image: linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent);
      background-size: 1rem 1rem;
    }
    
    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      scroll-behavior: smooth;
      background-color: var(--background);
    }
    
    .message {
      display: flex;
      margin-bottom: 1.5rem;
      max-width: 85%;
      position: relative;
      width: 100%; /* Ensure message takes up space */
    }
    
    .message-avatar {
      margin-right: 12px;
      align-self: flex-start;
    }
    
    .avatar-icon {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: white;
      font-size: 16px;
    }
    
    .user-avatar {
      background-color: var(--primary);
    }
    
    .assistant-avatar {
      background-color: var(--secondary);
    }
    
    .message-content {
      padding: 12px 16px;
      border-radius: 12px;
      box-shadow: 0 1px 2px var(--shadow);
      background-color: white; /* Ensure there's a background color */
      color: black; /* Force text color to black */
      max-width: 100%; /* Ensure content doesn't overflow */
      width: 100%; /* Take up full width of parent */
    }
    
    .message-sender {
      font-weight: 600;
      margin-bottom: 4px;
      font-size: 0.9rem;
    }
    
    .message-text {
      white-space: pre-wrap;
      line-height: 1.5;
      color: #000 !important; /* Force black color with !important */
      font-size: 1rem; /* Ensure readable font size */
      word-break: break-word; /* Handle long words */
      width: 100%; /* Take full width of parent */
      max-width: 100%; /* Prevent overflow */
      overflow-wrap: break-word; /* Ensure words wrap */
    }
    
    .structured-input-header {
      background-color: #f0f0f5;
      padding: 8px;
      margin-bottom: 10px;
      border-left: 3px solid var(--primary);
      border-radius: 4px;
    }
    
    .message-time {
      font-size: 0.75rem;
      color: var(--text-secondary);
      margin-top: 6px;
      text-align: right;
    }
    
    /* Source citation styles */
    .message-sources {
      margin-top: 10px;
      border-top: 1px solid #eaeaea;
      padding-top: 8px;
    }
    
    .sources-header {
      font-size: 0.8rem;
      color: var(--primary);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      font-weight: 500;
    }
    
    .sources-list {
      margin-top: 8px;
      font-size: 0.85rem;
      background-color: rgba(0,0,0,0.03);
      padding: 10px;
      border-radius: 4px;
    }
    
    .source-item {
      margin-bottom: 8px;
      padding-bottom: 8px;
      border-bottom: 1px dashed #eaeaea;
    }
    
    .source-item:last-child {
      border-bottom: none;
      margin-bottom: 0;
      padding-bottom: 0;
    }
    
    .source-title {
      font-weight: 600;
      color: var(--primary);
    }
    
    .source-path {
      font-size: 0.8rem;
      color: #666;
      margin: 2px 0;
    }
    
    .source-snippet {
      font-style: italic;
      color: #333;
      margin-top: 5px;
      font-size: 0.8rem;
      background-color: rgba(0,0,0,0.02);
      padding: 5px;
      border-left: 3px solid var(--primary);
    }
    
    /* Stage transition styling */
    .stage-transition {
      width: 100%;
      display: flex;
      align-items: center;
      margin: 15px 0;
    }
    
    .stage-marker {
      flex: 1;
      height: 1px;
      background-color: #dee2e6;
    }
    
    .stage-label {
      padding: 0 10px;
      color: #6c757d;
      font-size: 0.85rem;
      font-weight: 500;
    }
    
    /* Structured input fields */
    .structured-input-fields {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 15px;
    }
    
    .structured-input-fields h4 {
      font-size: 1rem;
      margin-bottom: 15px;
      color: var(--primary);
    }
    
    .radio-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .message-user {
      align-self: flex-end;
      
      .message-content {
        background-color: #e6f7ff;
        color: #000;
        border-bottom-right-radius: 4px;
        border: 1px solid #b3e0ff;
      }
      
      .message-sender {
        color: #000;
        font-weight: bold;
      }
      
      .message-time {
        color: #666;
      }
      
      .message-text {
        color: #000;
      }
      
      code.inline-code {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9em;
      }
    }
    
    .message-assistant {
      align-self: flex-start;
      
      .message-content {
        background-color: #f5f5f5;
        color: var(--text-primary);
        border-bottom-left-radius: 4px;
        border: 1px solid #e0e0e0;
      }
      
      .message-sender {
        color: #000;
        font-weight: bold;
      }
      
      .message-text {
        color: #000;
      }
      
      code.inline-code {
        background-color: #f0f2f5;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9em;
        color: var(--primary-dark);
      }
    }
    
    .input-container {
      padding: 1rem;
      border-top: 1px solid var(--border);
      background-color: var(--surface);
    }
    
    .input-group {
      border-radius: 24px;
      overflow: hidden;
      box-shadow: 0 2px 4px var(--shadow);
    }
    
    .form-control {
      border: 1px solid var(--border);
      padding: 12px 16px;
      font-size: 1rem;
      transition: all 0.3s ease;
    }
    
    .form-control:focus {
      box-shadow: none;
      border-color: var(--primary);
    }
    
    .btn-primary {
      border-radius: 0;
      padding-left: 1.5rem;
      padding-right: 1.5rem;
    }
    
    /* Structured Data Styling */
    .structured-data-container {
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      margin: 10px 0;
      overflow: hidden;
    }
    
    .structured-data-header {
      background-color: #f1f5f9;
      padding: 8px 12px;
      display: flex;
      align-items: center;
      font-weight: 600;
      color: #334155;
      border-bottom: 1px solid #e2e8f0;
    }
    
    .structured-data-content {
      padding: 12px;
    }
    
    .data-object {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .data-property {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding-left: 8px;
      border-left: 2px solid #e2e8f0;
    }
    
    .data-property-name {
      font-weight: 600;
      color: #0369a1;
      font-size: 0.9rem;
    }
    
    .data-property-value {
      padding-left: 12px;
    }
    
    .data-array {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .data-array-item {
      display: flex;
      gap: 8px;
      align-items: flex-start;
    }
    
    .data-array-index {
      color: #64748b;
      font-weight: 500;
      min-width: 24px;
      text-align: right;
    }
    
    .data-string {
      color: #059669;
    }
    
    .data-number {
      color: #0284c7;
      font-weight: 500;
    }
    
    .data-boolean {
      color: #9333ea;
      font-weight: 500;
    }
    
    .data-null {
      color: #94a3b8;
      font-style: italic;
    }
    
    .data-url {
      color: #2563eb;
      text-decoration: underline;
    }
    
    .data-empty-object, .data-empty-array {
      color: #94a3b8;
      font-style: italic;
    }
    
    /* Code block formatting */
    pre.code-block {
      background-color: #f1f5f9;
      padding: 12px;
      border-radius: 6px;
      border-left: 4px solid var(--primary);
      overflow-x: auto;
      margin: 10px 0;
    }
    
    pre.code-block code {
      font-family: 'Consolas', 'Monaco', monospace;
      color: #334155;
    }
    
    .typing-indicator {
      display: inline-flex;
      align-items: center;
      padding: 6px 12px;
      background-color: #f1f3f5;
      border-radius: 16px;
    }
    
    .typing-indicator.healthcare-typing {
      background-color: #ECFDF5;
      border: 1px solid #D1FAE5;
    }
    
    .typing-indicator span {
      height: 8px;
      width: 8px;
      background-color: var(--primary);
      border-radius: 50%;
      margin: 0 2px;
      animation: typing 1.4s infinite;
      opacity: 0.7;
    }
    
    .healthcare-typing span {
      background-color: #16A34A;
    }
    
    .typing-indicator span:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
      animation-delay: 0.4s;
    }
    
    @keyframes typing {
      0% { opacity: 0.4; transform: translateY(0); }
      50% { opacity: 1; transform: translateY(-5px); }
      100% { opacity: 0.4; transform: translateY(0); }
    }
  `]
})
export class ChatBoxComponent implements OnInit, AfterViewChecked {
  @Input() messages: Message[] = [];
  @Input() loading = false;
  @Output() messageSent = new EventEmitter<string>();
  @Output() structuredInputSubmitted = new EventEmitter<any>();
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  
  // Input to indicate if this is a healthcare consultation using RAG
  @Input() isHealthcareConsultation = false;
  
  // New inputs for template support
  @Input() templateMode = false;
  @Input() templateProgress: TemplateProgress | null = null;

  // Track when healthcare mode changes
  ngOnChanges() {
    console.log("Chat box healthcare mode:", this.isHealthcareConsultation);
    // Force change detection when healthcare mode changes
    if (this.isHealthcareConsultation) {
      console.log("Healthcare mode active in chat box");
    }
  }
  @Input() structuredInputFields: Array<{
    id: string;
    label: string;
    type: 'text' | 'textarea' | 'select' | 'radio' | 'checkbox';
    options?: Array<{value: string, label: string}>;
    value: string | string[];
    placeholder?: string;
    required?: boolean;
    helpText?: string;
  }> | null = null;
  @Input() structuredInputPrompt?: string;
  @Input() showTextInput = true; // Whether to show text input alongside structured inputs
  
  newMessage = '';
  visibleSourcesMap: { [messageIndex: number]: boolean } = {};
  showSourcesHelp = false;
  
  constructor(private sanitizer: DomSanitizer) {}
  
  ngOnInit(): void {
    console.log('Chat box initialized with messages:', this.messages);
    if (this.templateMode) {
      console.log('Template mode enabled with progress:', this.templateProgress);
    }
  }
  
  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }
  
  scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) {}
  }
  
  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  
  formatMessageContent(content: string): SafeHtml {
    if (!content) {
      console.warn('Received empty message content');
      return this.sanitizer.bypassSecurityTrustHtml('<em>Empty message</em>') as string;
    }
    
    console.log('Formatting message content:', content.substring(0, 100) + (content.length > 100 ? '...' : ''));
    
    // Detect if content is structured data (JSON)
    try {
      // Check if the content is a JSON string
      if ((content.trim().startsWith('{') && content.trim().endsWith('}')) || 
          (content.trim().startsWith('[') && content.trim().endsWith(']'))) {
        const parsedContent = JSON.parse(content);
        return this.formatStructuredData(parsedContent);
      }
    } catch (e) {
      // Not valid JSON, continue with regular formatting
      console.log('Not valid JSON, using regular formatting');
    }

    // Regular text formatting
    
    // Replace URLs with clickable links
    let formattedContent = content.replace(
      /(https?:\/\/[^\s]+)/g, 
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Format structured input headers
    if (formattedContent.includes('### Structured Input:')) {
      formattedContent = formattedContent.replace(
        '### Structured Input:',
        '<div class="structured-input-header"><strong>Structured Input</strong></div>'
      );
    }
    
    // Add basic formatting for code blocks
    formattedContent = formattedContent.replace(
      /`([^`]+)`/g, 
      '<code class="inline-code">$1</code>'
    );

    // Format multi-line code blocks
    formattedContent = formattedContent.replace(
      /```([^```]+)```/g,
      '<pre class="code-block"><code>$1</code></pre>'
    );

    // Format headers (markdown-style)
    formattedContent = formattedContent.replace(/^### (.*$)/gm, '<h5>$1</h5>');
    formattedContent = formattedContent.replace(/^## (.*$)/gm, '<h4>$1</h4>');
    formattedContent = formattedContent.replace(/^# (.*$)/gm, '<h3>$1</h3>');

    // Format bold text
    formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Format italic text
    formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Ensure newlines are preserved in HTML
    formattedContent = formattedContent.replace(/\n/g, '<br>');
    
    return this.sanitizer.bypassSecurityTrustHtml(formattedContent) as string;
  }
  
  private formatStructuredData(data: any): string {
    // Create enhanced visual representation of structured data
    const formattedHtml = `
      <div class="structured-data-container">
        <div class="structured-data-header">
          <i class="bi bi-braces me-2"></i>
          <span>Structured Data</span>
        </div>
        <div class="structured-data-content">
          ${this.renderStructuredData(data)}
        </div>
      </div>
    `;
    
    return this.sanitizer.bypassSecurityTrustHtml(formattedHtml) as string;
  }
  
  private renderStructuredData(data: any, level = 0): string {
    if (data === null) return '<span class="data-null">null</span>';
    
    if (typeof data === 'boolean') {
      return `<span class="data-boolean">${data}</span>`;
    }
    
    if (typeof data === 'number') {
      return `<span class="data-number">${data}</span>`;
    }
    
    if (typeof data === 'string') {
      // Check if it's a URL
      if (data.match(/^(https?:\/\/[^\s]+)$/)) {
        return `<a href="${data}" target="_blank" class="data-url">${data}</a>`;
      }
      return `<span class="data-string">${data}</span>`;
    }
    
    if (Array.isArray(data)) {
      if (data.length === 0) return '<span class="data-empty-array">[ ]</span>';
      
      let result = '<div class="data-array">';
      data.forEach((item, index) => {
        result += `
          <div class="data-array-item">
            <span class="data-array-index">${index + 1}.</span>
            ${this.renderStructuredData(item, level + 1)}
          </div>
        `;
      });
      result += '</div>';
      return result;
    }
    
    if (typeof data === 'object') {
      const keys = Object.keys(data);
      if (keys.length === 0) return '<span class="data-empty-object">{ }</span>';
      
      let result = '<div class="data-object">';
      
      keys.forEach((key) => {
        result += `
          <div class="data-property">
            <div class="data-property-name">${key}</div>
            <div class="data-property-value">${this.renderStructuredData(data[key], level + 1)}</div>
          </div>
        `;
      });
      
      result += '</div>';
      return result;
    }
    
    return String(data);
  }
  
  // Methods for handling source citations
  toggleSourcesVisibility(messageIndex: number): void {
    this.visibleSourcesMap[messageIndex] = !this.isSourcesVisible(messageIndex);
  }
  
  isSourcesVisible(messageIndex: number): boolean {
    return !!this.visibleSourcesMap[messageIndex];
  }
  
  toggleSourcesHelp(): void {
    this.showSourcesHelp = !this.showSourcesHelp;
  }
  
  sendMessage(): void {
    if (this.newMessage.trim() && !this.loading) {
      this.messageSent.emit(this.newMessage);
      this.newMessage = '';
    }
  }
  
  submitStructuredInput(): void {
    if (!this.areRequiredFieldsValid() || this.loading) {
      return;
    }
    
    const structuredData = this.structuredInputFields?.reduce((acc: any, field) => {
      acc[field.id] = field.value;
      return acc;
    }, {});
    
    this.structuredInputSubmitted.emit(structuredData);
    
    // Clear field values after submission
    if (this.structuredInputFields) {
      this.structuredInputFields.forEach(field => {
        if (Array.isArray(field.value)) {
          field.value = [];
        } else {
          field.value = '';
        }
      });
    }
  }
  
  areRequiredFieldsValid(): boolean {
    if (!this.structuredInputFields) {
      return true;
    }
    
    return !this.structuredInputFields.some(field => {
      if (!field.required) return false;
      
      if (Array.isArray(field.value)) {
        return field.value.length === 0;
      } else {
        return !field.value;
      }
    });
  }
  
  getStageNumberById(stageId: string | undefined): number {
    console.log('Getting stage number for ID:', stageId, 'Current template progress:', this.templateProgress);
    
    // Safely handle undefined cases
    if (!stageId || !this.templateProgress) {
      return 1;  // Default to stage 1 instead of 0 for better UI display
    }
    
    // Convert stageId to number if it's a number string
    const numericId = parseInt(stageId, 10);
    if (!isNaN(numericId)) {
      return numericId;
    }
    
    // If we have a current stage ID that matches, return the current stage number
    if (stageId === this.templateProgress.stageId && 
        typeof this.templateProgress.currentStage === 'number') {
      return this.templateProgress.currentStage;
    }
    
    // If we have a list of completed stages, check the index
    if (this.templateProgress.completedStages && 
        Array.isArray(this.templateProgress.completedStages)) {
        
      const index = this.templateProgress.completedStages.indexOf(stageId);
      if (index !== -1) {
        return index + 1;
      }
    }
    
    // Check if the stageId is a UUID-like string and the current stageId matches
    if (stageId && stageId.includes('-') && this.templateProgress.stageId === stageId) {
      return this.templateProgress.currentStage || 1;
    }
    
    // If all else fails, return the current stage as a fallback
    return this.templateProgress.currentStage || 1;
  }
}