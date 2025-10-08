import { Component, Input, Output, EventEmitter } from '@angular/core';
import { TemplateStage } from '../../services/consultation.service';

@Component({
  selector: 'app-template-stage-progress',
  template: `
    <div class="stage-progress-container">
      <h4 class="progress-title">{{ title || 'Consultation Progress' }}</h4>
      
      <!-- Overall Progress -->
      <div class="progress mb-4">
        <div class="progress-bar" 
            [style.width.%]="progressPercentage"
            [ngClass]="{'progress-bar-animated': currentStage > 0 && currentStage < totalStages}">
          {{ progressPercentage }}%
        </div>
      </div>
      
      <!-- Stage List -->
      <div class="stages-list">
        <div *ngFor="let stage of stages; let i = index" 
            class="stage-item"
            [ngClass]="{
              'stage-completed': i < currentStage - 1,
              'stage-current': i === currentStage - 1,
              'stage-upcoming': i > currentStage - 1,
              'stage-animated': i === currentStage - 1
            }"
            (click)="onStageClick(stage, i + 1)">
          <div class="stage-indicator">
            <div class="stage-number" [ngClass]="{'pulse': i === currentStage - 1}">
              <ng-container *ngIf="i < currentStage - 1">
                <i class="bi bi-check-circle-fill"></i>
              </ng-container>
              <ng-container *ngIf="i === currentStage - 1">
                <i class="bi bi-arrow-right-circle-fill"></i>
              </ng-container>
              <ng-container *ngIf="i > currentStage - 1">
                {{ i + 1 }}
              </ng-container>
            </div>
          </div>
          <div class="stage-details">
            <div class="stage-name">{{ stage.name }}</div>
            <div class="stage-status" *ngIf="i === currentStage - 1">
              <span class="badge bg-primary">Current</span>
            </div>
            <div class="stage-status" *ngIf="i < currentStage - 1">
              <span class="badge bg-success">Completed</span>
              <small class="text-muted ms-2">{{getTimeAgo(i)}}</small>
            </div>
            <div class="stage-description" *ngIf="showDescription">
              {{ stage.description }}
            </div>
            <div class="stage-progress" *ngIf="i === currentStage - 1">
              <div class="stage-progress-bar"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Summary Section -->
      <div class="progress-summary mt-4" *ngIf="currentStage > 1">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Consultation Summary</h6>
            <p class="small">
              {{getSummary()}}
            </p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .stage-progress-container {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .progress-title {
      font-size: 1.1rem;
      margin-bottom: 15px;
      color: #495057;
    }
    
    .progress {
      height: 10px;
      background-color: #e9ecef;
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .progress-bar {
      background-color: var(--primary);
      color: white;
      font-size: 0.7rem;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: width 0.6s ease;
    }
    
    .progress-bar-animated {
      animation: progress-bar-stripes 1s linear infinite;
      background-image: linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent);
      background-size: 1rem 1rem;
    }
    
    .stages-list {
      margin-top: 15px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .stage-item {
      display: flex;
      align-items: flex-start;
      padding: 10px;
      border-radius: 6px;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    
    .stage-item:hover {
      background-color: #f0f0f0;
    }
    
    .stage-completed {
      background-color: rgba(var(--primary-rgb), 0.1);
    }
    
    .stage-current {
      background-color: rgba(var(--primary-rgb), 0.2);
      border-left: 3px solid var(--primary);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      transform: translateX(3px);
      transition: all 0.3s ease;
    }
    
    .stage-upcoming {
      color: #6c757d;
      background-color: #ffffff;
      opacity: 0.8;
    }
    
    .stage-animated {
      animation: highlight-stage 2s infinite alternate;
    }
    
    @keyframes highlight-stage {
      from { background-color: rgba(var(--primary-rgb), 0.1); }
      to { background-color: rgba(var(--primary-rgb), 0.3); }
    }
    
    .stage-indicator {
      margin-right: 12px;
    }
    
    .stage-number {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
      font-weight: bold;
      color: white;
      background-color: #adb5bd;
      transition: all 0.3s ease;
    }
    
    .stage-number.pulse {
      animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); }
    }
    
    .stage-completed .stage-number {
      background-color: var(--success);
    }
    
    .stage-current .stage-number {
      background-color: var(--primary);
    }
    
    .stage-details {
      flex: 1;
    }
    
    .stage-name {
      font-weight: 600;
      font-size: 0.95rem;
    }
    
    .stage-description {
      font-size: 0.85rem;
      color: #6c757d;
      margin-top: 4px;
    }
    
    .stage-status {
      margin-top: 5px;
      display: flex;
      align-items: center;
    }
    
    .badge {
      font-size: 0.7rem;
      font-weight: normal;
      padding: 0.25em 0.5em;
    }
    
    .stage-progress {
      margin-top: 8px;
      height: 3px;
      background-color: #e9ecef;
      overflow: hidden;
      border-radius: 3px;
    }
    
    .stage-progress-bar {
      height: 100%;
      width: 30%;
      background-color: var(--primary);
      animation: progress-slide 2s infinite linear;
    }
    
    @keyframes progress-slide {
      0% { margin-left: -30%; }
      100% { margin-left: 100%; }
    }
    
    .bi-check-circle-fill {
      font-size: 1rem;
      color: var(--success);
    }
    
    .bi-arrow-right-circle-fill {
      font-size: 1rem;
      color: white;
    }
    
    .progress-summary {
      transition: all 0.5s ease;
    }
    
    .progress-summary .card {
      border-color: rgba(var(--primary-rgb), 0.2);
      background-color: rgba(var(--primary-rgb), 0.05);
    }
  `]
})
export class TemplateStageProgressComponent {
  @Input() title?: string;
  @Input() stages: TemplateStage[] = [];
  @Input() currentStage = 1;
  @Input() showDescription = true;
  @Input() allowNavigation = false; // Whether to allow clicking on stages for navigation
  @Output() stageSelected = new EventEmitter<{stage: TemplateStage, stageNumber: number}>();
  
  // Track when each stage was completed
  private stageCompletionTimes: Date[] = [];

  ngOnChanges(changes: any): void {
    // When currentStage changes, record the time of completion for the previous stage
    if (changes.currentStage && changes.currentStage.previousValue !== changes.currentStage.currentValue) {
      const previousStage = changes.currentStage.previousValue;
      if (previousStage > 0 && previousStage <= this.totalStages) {
        this.stageCompletionTimes[previousStage - 1] = new Date();
      }
    }
  }

  get totalStages(): number {
    return this.stages.length;
  }

  get progressPercentage(): number {
    if (this.totalStages === 0) return 0;
    return Math.round(((this.currentStage - 1) / this.totalStages) * 100);
  }

  onStageClick(stage: TemplateStage, stageNumber: number): void {
    // Only emit if navigation is allowed and the stage is completed or current
    if (this.allowNavigation && stageNumber <= this.currentStage) {
      this.stageSelected.emit({ stage, stageNumber });
    }
  }
  
  getTimeAgo(stageIndex: number): string {
    const completionTime = this.stageCompletionTimes[stageIndex];
    if (!completionTime) return '';
    
    const now = new Date();
    const diff = now.getTime() - completionTime.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'just now';
    if (minutes === 1) return '1 minute ago';
    if (minutes < 60) return `${minutes} minutes ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours === 1) return '1 hour ago';
    return `${hours} hours ago`;
  }
  
  getSummary(): string {
    const completedStages = Math.max(0, this.currentStage - 1);
    const remainingStages = this.totalStages - completedStages;
    
    if (completedStages === 0) {
      return `Starting your consultation with ${this.totalStages} stages.`;
    } else if (completedStages === this.totalStages) {
      return `Consultation complete! All ${this.totalStages} stages finished.`;
    } else {
      return `You've completed ${completedStages} of ${this.totalStages} stages. ${remainingStages} remaining.`;
    }
  }
}