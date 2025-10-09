import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ConsultationService } from '../../services/consultation.service';

// Define the interfaces locally
interface SourceCitation {
  title: string; // Make title required to match the chat-box component
  source: string;
  relevance?: number;
  content_snippet?: string;
}

// Define the Message interface locally
interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
  sources?: SourceCitation[];
}

@Component({
  selector: 'app-consultation',
  template: `
    <div class="row">
      <div class="col-md-8 mx-auto">
        <div class="card">
          <div class="card-header" [ngClass]="{'bg-primary text-white': !isHealthcareConsultation, 'bg-success text-white': isHealthcareConsultation}">
            <div class="d-flex justify-content-between align-items-center">
              <h4>{{ isHealthcareConsultation ? 'Healthcare SLA Consultation' : 'SLA Consultation' }}</h4>
              <div *ngIf="isHealthcareConsultation" class="healthcare-badge">
                <i class="bi bi-shield-check me-1"></i> HIPAA Compliant
              </div>
            </div>
          </div>
          <div class="card-body">
            <p class="card-text" *ngIf="!isHealthcareConsultation">
              Chat with our AI assistant to get personalized SLA recommendations for your service.
            </p>
            <p class="card-text healthcare-intro" *ngIf="isHealthcareConsultation">
              <i class="bi bi-info-circle me-2"></i> 
              This consultation is enhanced with specialized healthcare knowledge to ensure your SLAs meet industry standards and compliance requirements.
            </p>
            
            <app-chat-box
              [messages]="messages"
              [loading]="loading"
              [isHealthcareConsultation]="isHealthcareConsultation"
              (messageSent)="sendMessage($event)">
            </app-chat-box>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .healthcare-badge {
      background-color: rgba(255,255,255,0.3);
      padding: 4px 12px;
      border-radius: 50px;
      font-size: 0.85rem;
      font-weight: 600;
    }
    .healthcare-intro {
      background-color: #F0FDF4;
      border-left: 4px solid #16A34A;
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 16px;
    }
  `]
})
export class ConsultationComponent implements OnInit {
  messages: Message[] = [];
  loading = false;
  sessionId?: number;
  isHealthcareConsultation = false;
  
  constructor(
    private consultationService: ConsultationService,
    private cdr: ChangeDetectorRef
  ) {}
  
  ngOnInit(): void {
    // Check if healthcare template is selected from URL params
    this.checkIfHealthcareConsultation();
    
    // Add initial system message based on consultation type
    if (this.isHealthcareConsultation) {
      this.messages = [{
        content: 'Welcome to the Healthcare SLA consultation! I\'m your specialized healthcare SLA assistant. I can help you create compliant SLAs for healthcare systems that adhere to HIPAA and other regulatory requirements. What type of healthcare service are you looking to create an SLA for?',
        role: 'assistant' as 'assistant',
        timestamp: new Date().toISOString()
      }];
    } else {
      this.messages = [{
        content: 'Hi! I\'m your SLA assistant. How can I help you today?',
        role: 'assistant' as 'assistant',
        timestamp: new Date().toISOString()
      }];
    }
    
    console.log("Initial messages array:", this.messages);
    console.log("Healthcare consultation:", this.isHealthcareConsultation);
    this.cdr.detectChanges();
  }
  
  private checkIfHealthcareConsultation(): void {
    // Check URL for template parameter indicating healthcare template
    const url = window.location.href.toLowerCase();
    if (url.includes('healthcare') || url.includes('health')) {
      this.isHealthcareConsultation = true;
      console.log("Healthcare mode activated via URL params");
      return;
    }
    
    // Check localStorage for template selection
    const selectedTemplate = localStorage.getItem('selectedTemplate');
    if (selectedTemplate && 
        (selectedTemplate.toLowerCase().includes('health') || 
         selectedTemplate.toLowerCase().includes('hipaa') ||
         selectedTemplate.toLowerCase().includes('ehr'))) {
      this.isHealthcareConsultation = true;
      console.log("Healthcare mode activated via localStorage template");
      return;
    }
    
    // Default to false if no evidence of healthcare consultation
    this.isHealthcareConsultation = false;
    console.log("Healthcare mode not activated during initial check");
  }
  
  private detectHealthcareContext(message: string): void {
    // If already in healthcare mode, no need to check
    if (this.isHealthcareConsultation) {
      return;
    }
    
    // Check for healthcare-related keywords in the user's message
    const healthcareKeywords = [
      'healthcare', 'health', 'hospital', 'clinic', 'medical', 'patient', 
      'doctor', 'physician', 'hipaa', 'ehr', 'emr', 'phi', 'protected health', 
      'telemedicine', 'telehealth', 'medicare', 'medicaid', 'health insurance'
    ];
    
    const lowerMessage = message.toLowerCase();
    for (const keyword of healthcareKeywords) {
      if (lowerMessage.includes(keyword)) {
        console.log(`Healthcare keyword detected: ${keyword}`);
        this.isHealthcareConsultation = true;
        return;
      }
    }
  }
  
  sendMessage(content: string): void {
    if (!content || content.trim() === '') {
      return;
    }
    
    console.log("Sending message:", content);
    
    // Check for healthcare related keywords to activate healthcare mode
    this.detectHealthcareContext(content);
    
    // Add user message to chat
    const userMessage = {
      content,
      role: 'user' as 'user',
      timestamp: new Date().toISOString()
    };
    
    this.messages = [...this.messages, userMessage];
    console.log("Messages array after adding user message:", this.messages);
    this.cdr.detectChanges();
    
    this.loading = true;
    
    // Call API
    this.consultationService.sendMessage(content, this.sessionId)
      .subscribe({
        next: (response: any) => {
          this.loading = false;
          console.log('Consultation response:', response);
          
          // Save session ID if it's a new conversation
          if (response.session_id && !this.sessionId) {
            this.sessionId = response.session_id;
          }
          
          // Extract the message content - handle different response formats
          let messageContent = '';
          if (typeof response.message === 'string') {
            messageContent = response.message;
          } else if (response.message && typeof response.message.text === 'string') {
            messageContent = response.message.text;
          } else if (response.text) {
            messageContent = response.text;
          } else {
            console.error('Unable to find message content in response:', response);
            messageContent = "I apologize, but I encountered an unexpected response format. Please try again.";
          }
          
          // Add assistant response to chat
          const assistantMessage: Message = {
            content: messageContent,
            role: 'assistant' as 'assistant',
            timestamp: new Date().toISOString()
          };
          
          // Process sources from different possible response formats
          let sourcesData = null;
          if (response.sources && Array.isArray(response.sources)) {
            sourcesData = response.sources;
          } else if (response.message && response.message.sources && Array.isArray(response.message.sources)) {
            sourcesData = response.message.sources;
          }
          
          // If we found sources, add them to the message
          if (sourcesData && sourcesData.length > 0) {
            console.log('Sources found in response:', sourcesData);
            
            // Format sources for display
            assistantMessage.sources = sourcesData.map((source: any) => {
              // Handle different source formats
              if (typeof source === 'string') {
                return { 
                  title: 'Document', // Always provide a title
                  source: source, 
                  relevance: 1.0 
                };
              }
              
              // Ensure title is always provided and not undefined
              const title = source.title || source.name || 'Healthcare Document';
              
              return {
                title: title, // This will always have a value now
                source: source.source || source.path || source.id || 'Unknown',
                relevance: source.relevance || 1.0,
                content_snippet: source.content_snippet || source.snippet || source.text || null
              };
            });
            
            // If we receive sources and weren't already in healthcare mode, switch to it
            if (!this.isHealthcareConsultation) {
              this.isHealthcareConsultation = true;
              console.log("Healthcare consultation mode activated due to sources in response");
              // Force change detection
              this.cdr.detectChanges();
            }
          }
          
          // Add the message to the chat
          this.messages = [...this.messages, assistantMessage];
          console.log("Messages array after adding assistant response:", this.messages);
          this.cdr.detectChanges();
          
          this.messages = [...this.messages, assistantMessage];
          console.log("Messages array after adding assistant response:", this.messages);
          this.cdr.detectChanges();
        },
        error: (error) => {
          this.loading = false;
          console.error('Error sending message:', error);
          
          // Add error message to chat
          const errorMessage = {
            content: 'Sorry, there was an error processing your request. Please try again later.',
            role: 'assistant' as 'assistant',
            timestamp: new Date().toISOString()
          };
          this.messages = [...this.messages, errorMessage];
          console.log("Messages array after adding error message:", this.messages);
          this.cdr.detectChanges();
        }
      });
  }
}