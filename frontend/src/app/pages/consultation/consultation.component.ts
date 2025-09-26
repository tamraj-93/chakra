import { Component, OnInit } from '@angular/core';
import { ConsultationService } from '../../services/consultation.service';

// Define the Message interface locally
interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
}

@Component({
  selector: 'app-consultation',
  template: `
    <div class="row">
      <div class="col-md-8 mx-auto">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h4>SLA Consultation</h4>
          </div>
          <div class="card-body">
            <p class="card-text">
              Chat with our AI assistant to get personalized SLA recommendations for your service.
            </p>
            
            <app-chat-box
              [messages]="messages"
              [loading]="loading"
              (messageSent)="sendMessage($event)">
            </app-chat-box>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class ConsultationComponent implements OnInit {
  messages: Message[] = [];
  loading = false;
  sessionId?: number;
  
  constructor(private consultationService: ConsultationService) {}
  
  ngOnInit(): void {
    // Add initial system message
    this.messages.push({
      content: 'Hi! I\'m your SLA assistant. How can I help you today?',
      role: 'assistant'
    });
  }
  
  sendMessage(content: string): void {
    // Add user message to chat
    this.messages.push({
      content,
      role: 'user'
    });
    
    this.loading = true;
    
    // Call API
    this.consultationService.sendMessage(content, this.sessionId)
      .subscribe({
        next: (response: any) => {
          this.loading = false;
          
          // Save session ID if it's a new conversation
          if (response.session_id && !this.sessionId) {
            this.sessionId = response.session_id;
          }
          
          // Add assistant response to chat
          this.messages.push({
            content: response.message,
            role: 'assistant'
          });
        },
        error: (error) => {
          this.loading = false;
          console.error('Error sending message:', error);
          
          // Add error message to chat
          this.messages.push({
            content: 'Sorry, there was an error processing your request. Please try again later.',
            role: 'assistant'
          });
        }
      });
  }
}