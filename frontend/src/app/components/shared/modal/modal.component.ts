import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-modal',
  template: `
    <div class="modal-backdrop" [class.show]="isOpen" (click)="closeOnBackdropClick ? close() : null">
      <div class="modal-container" [class.show]="isOpen" (click)="$event.stopPropagation()">
        <div class="modal-content">
          <ng-content></ng-content>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
      z-index: 1040;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.2s, visibility 0.2s;
    }
    
    .modal-backdrop.show {
      opacity: 1;
      visibility: visible;
    }
    
    .modal-container {
      width: 90%;
      max-width: 900px;
      max-height: 90vh;
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2);
      transform: translateY(-20px);
      opacity: 0;
      transition: transform 0.3s, opacity 0.3s;
    }
    
    .modal-container.show {
      transform: translateY(0);
      opacity: 1;
    }
    
    .modal-content {
      width: 100%;
      height: 100%;
      max-height: 90vh;
      overflow-y: auto;
    }
  `]
})
export class ModalComponent {
  @Input() isOpen: boolean = false;
  @Input() closeOnBackdropClick: boolean = true;
  @Output() closed = new EventEmitter<void>();

  close(): void {
    this.closed.emit();
  }
}