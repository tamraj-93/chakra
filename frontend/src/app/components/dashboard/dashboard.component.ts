import { Component, OnInit } from '@angular/core';
import { slideUpAnimation, listAnimation } from '../../shared/animations';

interface MetricCard {
  title: string;
  value: number | string;
  icon: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: string;
}

@Component({
  selector: 'app-dashboard',
  animations: [slideUpAnimation, listAnimation],
  template: `
    <div class="dashboard-container">
      <div class="section-header" @slideUpAnimation>
        <h2>SLM Assistant Dashboard</h2>
        <p class="text-muted">Analytics and performance metrics</p>
      </div>
      
      <div class="metrics-row" @listAnimation>
        <div *ngFor="let metric of metrics; let i = index" class="metric-card" 
             [style.background]="metric.color">
          <div class="metric-icon">
            <i [class]="'bi bi-' + metric.icon"></i>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">{{ metric.title }}</h3>
            <div class="metric-value">{{ metric.value }}</div>
            <div *ngIf="metric.trend" class="metric-trend" 
                 [class.positive]="metric.trend.isPositive"
                 [class.negative]="!metric.trend.isPositive">
              <i [class]="metric.trend.isPositive ? 'bi bi-arrow-up' : 'bi bi-arrow-down'"></i>
              {{ metric.trend.value }}%
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-container" @slideUpAnimation>
        <div class="chart-header">
          <h3>Consultations Activity</h3>
          <div class="chart-controls">
            <select class="form-select">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 90 days</option>
            </select>
          </div>
        </div>
        <div class="chart-placeholder">
          <div class="chart-bars">
            <div *ngFor="let day of activityData" class="chart-bar" 
                 [style.height.%]="day.percentage">
              <div class="bar-tooltip">{{ day.count }} consultations</div>
            </div>
          </div>
          <div class="chart-labels">
            <div *ngFor="let day of activityData" class="chart-label">
              {{ day.label }}
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .section-header {
      margin-bottom: 2rem;
      text-align: center;
    }
    
    .section-header h2 {
      color: var(--primary);
      margin-bottom: 0.5rem;
    }
    
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }
    
    .metric-card {
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      position: relative;
      overflow: hidden;
      box-shadow: 0 4px 6px var(--shadow);
      color: white;
    }
    
    .metric-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background-color: rgba(255, 255, 255, 0.2);
      margin-right: 1rem;
    }
    
    .metric-icon i {
      font-size: 1.5rem;
      color: white;
    }
    
    .metric-content {
      flex: 1;
    }
    
    .metric-title {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.25rem;
      opacity: 0.9;
    }
    
    .metric-value {
      font-size: 1.8rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }
    
    .metric-trend {
      font-size: 0.9rem;
      display: flex;
      align-items: center;
    }
    
    .metric-trend i {
      margin-right: 0.25rem;
    }
    
    .positive {
      color: rgba(255, 255, 255, 0.9);
    }
    
    .negative {
      color: rgba(255, 255, 255, 0.9);
    }
    
    .chart-container {
      background-color: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px var(--shadow);
    }
    
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }
    
    .chart-header h3 {
      margin-bottom: 0;
      font-size: 1.2rem;
      color: var(--primary);
    }
    
    .chart-controls .form-select {
      width: auto;
      padding: 0.375rem 2.25rem 0.375rem 0.75rem;
      font-size: 0.9rem;
    }
    
    .chart-placeholder {
      height: 250px;
      position: relative;
    }
    
    .chart-bars {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      height: 200px;
    }
    
    .chart-bar {
      width: 8%;
      background-color: var(--primary-light);
      border-radius: 4px 4px 0 0;
      position: relative;
      min-height: 10px;
      transition: height 0.5s ease;
    }
    
    .chart-bar:hover .bar-tooltip {
      opacity: 1;
      transform: translateY(0);
    }
    
    .bar-tooltip {
      position: absolute;
      top: -30px;
      left: 50%;
      transform: translateX(-50%) translateY(10px);
      background-color: var(--primary-dark);
      color: white;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.8rem;
      opacity: 0;
      transition: all 0.2s ease;
    }
    
    .chart-labels {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
    }
    
    .chart-label {
      width: 8%;
      text-align: center;
      font-size: 0.8rem;
      color: var(--text-secondary);
    }
  `]
})
export class DashboardComponent implements OnInit {
  metrics: MetricCard[] = [
    {
      title: 'Total Consultations',
      value: '152',
      icon: 'chat-dots',
      trend: { value: 12.5, isPositive: true },
      color: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)'
    },
    {
      title: 'Active Users',
      value: '37',
      icon: 'people',
      trend: { value: 8.3, isPositive: true },
      color: 'linear-gradient(135deg, var(--secondary) 0%, var(--secondary-light) 100%)'
    },
    {
      title: 'Avg. Response Time',
      value: '1.8s',
      icon: 'clock',
      trend: { value: 5.2, isPositive: false },
      color: 'linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%)'
    },
    {
      title: 'Templates Used',
      value: '48',
      icon: 'file-earmark-text',
      color: 'linear-gradient(135deg, #26C6DA 0%, #80DEEA 100%)'
    }
  ];
  
  activityData = [
    { label: 'Mon', count: 22, percentage: 55 },
    { label: 'Tue', count: 28, percentage: 70 },
    { label: 'Wed', count: 40, percentage: 100 },
    { label: 'Thu', count: 32, percentage: 80 },
    { label: 'Fri', count: 24, percentage: 60 },
    { label: 'Sat', count: 18, percentage: 45 },
    { label: 'Sun', count: 12, percentage: 30 }
  ];
  
  constructor() { }

  ngOnInit(): void { }
}