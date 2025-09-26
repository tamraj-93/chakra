import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';

// Define the Message interface locally
interface Message {
  id?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  sessionId?: number;
  timestamp?: string;
}

@Component({
  selector: 'app-chat-box',
  template: `
    <div class="chat-container">
      <div class="messages-container">
        <div *ngFor="let message of messages" 
             [ngClass]="{'message-user': message.role === 'user', 'message-assistant': message.role === 'assistant'}"
             class="message">
          <strong>{{ message.role === 'user' ? 'You' : 'Assistant' }}:</strong>
          <p>{{ message.content }}</p>
        </div>
        <div *ngIf="loading" class="message message-assistant">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
      
      <div class="input-container">
        <form (ngSubmit)="sendMessage()">
          <div class="input-group">
            <input type="text" class="form-control" 
                   placeholder="Type your message..." 
                   [(ngModel)]="newMessage"
                   name="newMessage"
                   [disabled]="loading">
            <button class="btn btn-primary" 
                    type="submit"
                    [disabled]="!newMessage || loading">
              Send
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
      height: 500px;
      border: 1px solid #dee2e6;
      border-radius: 0.25rem;
    }
    
    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
      display: flex;
      flex-direction: column;
    }
    
    .message {
      margin-bottom: 1rem;
      padding: 0.75rem;
      border-radius: 0.5rem;
      max-width: 80%;
    }
    
    .message-user {
      align-self: flex-end;
      background-color: #d1ecf1;
    }
    
    .message-assistant {
      align-self: flex-start;
      background-color: #f8f9fa;
    }
    
    .input-container {
      padding: 1rem;
      border-top: 1px solid #dee2e6;
    }
    
    .typing-indicator {
      display: flex;
      align-items: center;
    }
    
    .typing-indicator span {
      height: 8px;
      width: 8px;
      background-color: #6c757d;
      border-radius: 50%;
      margin: 0 2px;
      animation: typing 1s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
      animation-delay: 0.4s;
    }
    
    @keyframes typing {
      0% { opacity: 0.3; transform: translateY(0); }
      50% { opacity: 1; transform: translateY(-5px); }
      100% { opacity: 0.3; transform: translateY(0); }
    }
  `]
})
export class ChatBoxComponent implements OnInit {
  @Input() messages: Message[] = [];
  @Input() loading = false;
  @Output() messageSent = new EventEmitter<string>();
  
  newMessage = '';
  
  constructor() {}
  
  ngOnInit(): void {}
  
  sendMessage(): void {
    if (this.newMessage.trim() && !this.loading) {
      this.messageSent.emit(this.newMessage);
      this.newMessage = '';
    }
  }
}