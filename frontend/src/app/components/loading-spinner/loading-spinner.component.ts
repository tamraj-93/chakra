import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  template: `
    <div class="d-flex justify-content-center align-items-center">
      <div class="spinner-container text-center p-5">
        <div class="spinner-border" role="status" [ngClass]="size">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted" *ngIf="message">{{ message }}</p>
      </div>
    </div>
  `,
  styles: [`
    .spinner-container {
      min-height: 200px;
    }
  `]
})
export class LoadingSpinnerComponent {
  @Input() message: string = '';
  @Input() size: string = 'spinner-border-lg';
}