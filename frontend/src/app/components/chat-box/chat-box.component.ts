import { Component, Input, Output, EventEmitter, OnInit, ElementRef, ViewChild, AfterViewChecked, SecurityContext } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { chatMessageAnimation, typingAnimation } from '../../shared/animations';

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
  animations: [chatMessageAnimation, typingAnimation],
  template: `
    <div class="chat-container">
      <div class="messages-container" #messagesContainer>
        <!-- Debug: Display messages count -->
        <div *ngIf="messages.length === 0" class="text-center text-muted my-4">
          No messages yet
        </div>

        <div *ngFor="let message of messages; let i = index" 
             [@chatMessageAnimation]
             [ngClass]="{'message-user': message.role === 'user', 'message-assistant': message.role === 'assistant'}"
             class="message">
          <div class="message-avatar">
            <div class="avatar-icon" [ngClass]="message.role === 'user' ? 'user-avatar' : 'assistant-avatar'">
              {{ message.role === 'user' ? 'U' : 'A' }}
            </div>
          </div>
          <div class="message-content">
            <div class="message-sender">{{ message.role === 'user' ? 'You' : 'SLM Assistant' }}</div>
            <div class="message-text">
              {{ message.content }}
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
    }
    
    .message-time {
      font-size: 0.75rem;
      color: var(--text-secondary);
      margin-top: 6px;
      text-align: right;
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
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  
  newMessage = '';
  
  constructor(private sanitizer: DomSanitizer) {}
  
  ngOnInit(): void {
    console.log('Chat box initialized with messages:', this.messages);
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
  
  formatMessageContent(content: string): string {
    // Replace URLs with clickable links
    const linkedContent = content.replace(
      /(https?:\/\/[^\s]+)/g, 
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Add basic formatting for code blocks
    const formattedContent = linkedContent.replace(
      /`([^`]+)`/g, 
      '<code class="inline-code">$1</code>'
    );
    
    return this.sanitizer.sanitize(SecurityContext.HTML, formattedContent) || '';
  }
  
  sendMessage(): void {
    if (this.newMessage.trim() && !this.loading) {
      this.messageSent.emit(this.newMessage);
      this.newMessage = '';
    }
  }
}