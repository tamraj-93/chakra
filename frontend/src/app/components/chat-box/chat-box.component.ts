import { Component, Input, Output, EventEmitter, OnInit, ElementRef, ViewChild, AfterViewChecked, SecurityContext } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { chatMessageAnimation, typingAnimation } from '../../shared/animations';

// Define the Message interface locally
interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
  stageId?: string; // Added to track which stage a message belongs to
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
  template: `
    <div class="chat-container">
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
            <div class="avatar-icon" [ngClass]="message.role === 'user' ? 'user-avatar' : 'assistant-avatar'">
              {{ message.role === 'user' ? 'U' : 'A' }}
            </div>
          </div>
          <div class="message-content">
            <div class="message-sender">{{ message.role === 'user' ? 'You' : 'SLM Assistant' }}</div>
            <div class="message-text" [innerHTML]="formatMessageContent(message.content)">
            </div>
            <div class="message-time" *ngIf="message.timestamp">
              {{ formatTimestamp(message.timestamp) }}
            </div>
          </div>
        </div>
        <div *ngIf="loading" [@typingAnimation]="'active'" class="message message-assistant">
          <div class="message-avatar">
            <div class="avatar-icon assistant-avatar">A</div>
          </div>
          <div class="message-content">
            <div class="message-sender">SLM Assistant</div>
            <div class="typing-indicator">
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
    
    .typing-indicator span {
      height: 8px;
      width: 8px;
      background-color: var(--primary);
      border-radius: 50%;
      margin: 0 2px;
      animation: typing 1.4s infinite;
      opacity: 0.7;
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
  
  // New inputs for template support
  @Input() templateMode = false;
  @Input() templateProgress: TemplateProgress | null = null;
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