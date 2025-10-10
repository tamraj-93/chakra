import { Component, OnInit } from '@angular/core';
import { slideUpAnimation, listAnimation } from '../../shared/animations';
import { AnalyticsService, MetricData, TimeSeriesData, ComplianceData, SLAPerformance } from '../../services/analytics.service';

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
      <!-- Dashboard Header -->
      <div class="section-header" @slideUpAnimation>
        <h2>Healthcare SLA Dashboard</h2>
        <p class="text-muted">Key Metrics & SLA Performance at a Glance</p>
      </div>
      
      <!-- Loading Indicator -->
      <div *ngIf="isLoading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
      
      <!-- Key Metrics -->
      <div *ngIf="!isLoading" class="metrics-row" @listAnimation>
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
      
      <!-- Quick Actions -->
      <div class="quick-actions-container" @slideUpAnimation>
        <h3>Quick Actions</h3>
        <div class="quick-actions">
          <a routerLink="/templates" class="action-button">
            <i class="bi bi-plus-lg"></i>
            <span>New SLA</span>
          </a>
          <a routerLink="/my-slas" class="action-button">
            <i class="bi bi-file-earmark-check"></i>
            <span>View SLAs</span>
          </a>
          <a routerLink="/consultations/new" class="action-button">
            <i class="bi bi-chat-dots"></i>
            <span>New Consultation</span>
          </a>
          <a routerLink="/knowledge-base" class="action-button">
            <i class="bi bi-book"></i>
            <span>Knowledge Base</span>
          </a>
        </div>
      </div>
      
      <!-- Dashboard Tabs -->
      <div class="dashboard-tabs" *ngIf="!isLoading" @slideUpAnimation>
        <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="sla-tab" data-bs-toggle="tab" data-bs-target="#sla-panel" type="button" role="tab">
              SLA Performance
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="activity-tab" data-bs-toggle="tab" data-bs-target="#activity-panel" type="button" role="tab">
              Activity
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="compliance-tab" data-bs-toggle="tab" data-bs-target="#compliance-panel" type="button" role="tab">
              Compliance
            </button>
          </li>
        </ul>
        
        <div class="tab-content">
          <!-- SLA Performance Tab -->
          <div class="tab-pane fade show active" id="sla-panel" role="tabpanel">
            <div class="sla-performance-container">
              <div class="sla-performance-table">
                <div class="sla-table-header">
                  <div class="sla-header-cell">Metric</div>
                  <div class="sla-header-cell">Current Value</div>
                  <div class="sla-header-cell">Threshold</div>
                  <div class="sla-header-cell">Status</div>
                </div>
                <div *ngFor="let metric of slaPerformance" class="sla-table-row">
                  <div class="sla-cell">{{ metric.name }}</div>
                  <div class="sla-cell">{{ metric.currentValue }}{{ metric.unit }}</div>
                  <div class="sla-cell">{{ metric.threshold }}{{ metric.unit }}</div>
                  <div class="sla-cell">
                    <span class="status-indicator" [ngClass]="metric.status">
                      <i class="bi" 
                        [ngClass]="{'bi-check-circle-fill': metric.status === 'success', 
                                  'bi-exclamation-triangle-fill': metric.status === 'warning',
                                  'bi-x-circle-fill': metric.status === 'danger'}"></i>
                      {{ metric.status === 'success' ? 'Compliant' : 
                        metric.status === 'warning' ? 'At Risk' : 'Non-Compliant' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Activity Tab (loaded on demand) -->
          <div class="tab-pane fade" id="activity-panel" role="tabpanel">
            <div class="chart-container">
              <div class="chart-header">
                <h3>Consultations Activity</h3>
                <div class="chart-controls">
                  <select class="form-select" (change)="loadActivityData($event)">
                    <option value="week">Last 7 days</option>
                    <option value="month">Last 30 days</option>
                    <option value="quarter">Last 90 days</option>
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
              
              <!-- Recent Activity -->
              <div class="recent-activity-container">
                <h3>Recent Activity</h3>
                <div class="activity-list">
                  <div class="activity-item">
                    <div class="activity-icon success">
                      <i class="bi bi-check-circle"></i>
                    </div>
                    <div class="activity-content">
                      <div class="activity-title">SLA Compliance Check Passed</div>
                      <div class="activity-details">Healthcare Cloud Platform (HC-2023-001)</div>
                      <div class="activity-time">Today, 10:45 AM</div>
                    </div>
                  </div>
                  <div class="activity-item">
                    <div class="activity-icon warning">
                      <i class="bi bi-exclamation-triangle"></i>
                    </div>
                    <div class="activity-content">
                      <div class="activity-title">Response Time Warning</div>
                      <div class="activity-details">Financial Services API (FS-2023-005)</div>
                      <div class="activity-time">Yesterday, 3:22 PM</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Compliance Tab (loaded on demand) -->
          <div class="tab-pane fade" id="compliance-panel" role="tabpanel">
            <div class="chart-container">
              <div class="chart-header">
                <h3>SLA Compliance by Category</h3>
              </div>
              <div class="compliance-container">
                <div *ngFor="let item of complianceData" class="compliance-item">
                  <div class="compliance-info">
                    <span class="compliance-category">{{ item.category }}</span>
                    <span class="compliance-percentage">{{ item.percentage }}%</span>
                  </div>
                  <div class="compliance-bar-bg">
                    <div class="compliance-bar" [style.width.%]="item.percentage" 
                        [style.background-color]="item.color"></div>
                  </div>
                </div>
              </div>
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
    
    /* Loading indicator */
    .loading-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 3rem 0;
    }
    
    .spinner {
      border: 4px solid rgba(0, 150, 136, 0.1);
      border-radius: 50%;
      border-top: 4px solid var(--primary);
      width: 50px;
      height: 50px;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    /* Metrics Cards */
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
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 12px var(--shadow);
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
    
    /* Dashboard Grid Layout */
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }
    
    /* Chart Container */
    .chart-container {
      background-color: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px var(--shadow);
      height: 100%;
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
    
    /* Compliance Chart */
    .compliance-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-top: 1rem;
    }
    
    .compliance-item {
      width: 100%;
    }
    
    .compliance-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }
    
    .compliance-category {
      font-size: 0.9rem;
      font-weight: 500;
    }
    
    .compliance-percentage {
      font-weight: 600;
    }
    
    .compliance-bar-bg {
      width: 100%;
      height: 8px;
      background-color: #e9ecef;
      border-radius: 4px;
      overflow: hidden;
    }
    
    .compliance-bar {
      height: 100%;
      border-radius: 4px;
      transition: width 0.5s ease;
    }
    
    /* SLA Performance Table */
    .sla-performance-container {
      background-color: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px var(--shadow);
      margin-bottom: 2.5rem;
    }
    
    .sla-performance-container h3 {
      font-size: 1.2rem;
      color: var(--primary);
      margin-bottom: 1.5rem;
    }
    
    .sla-performance-table {
      width: 100%;
      border-collapse: collapse;
    }
    
    .sla-table-header {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      background-color: #f8f9fa;
      border-radius: 4px;
      padding: 0.75rem 1rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }
    
    .sla-table-row {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #e9ecef;
    }
    
    .sla-table-row:last-child {
      border-bottom: none;
    }
    
    .sla-header-cell,
    .sla-cell {
      display: flex;
      align-items: center;
    }
    
    .status-indicator {
      display: flex;
      align-items: center;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: 500;
    }
    
    .status-indicator i {
      margin-right: 0.25rem;
    }
    
    .status-indicator.success {
      background-color: rgba(40, 167, 69, 0.1);
      color: #28a745;
    }
    
    .status-indicator.warning {
      background-color: rgba(255, 193, 7, 0.1);
      color: #ffc107;
    }
    
    .status-indicator.danger {
      background-color: rgba(220, 53, 69, 0.1);
      color: #dc3545;
    }
    
    /* Recent Activity */
    .recent-activity-container {
      background-color: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px var(--shadow);
    }
    
    .recent-activity-container h3 {
      font-size: 1.2rem;
      color: var(--primary);
      margin-bottom: 1.5rem;
    }
    
    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .activity-item {
      display: flex;
      align-items: flex-start;
      padding: 1rem;
      border-radius: 8px;
      background-color: #f8f9fa;
    }
    
    .activity-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      margin-right: 1rem;
    }
    
    .activity-icon.success {
      background-color: rgba(40, 167, 69, 0.1);
      color: #28a745;
    }
    
    .activity-icon.warning {
      background-color: rgba(255, 193, 7, 0.1);
      color: #ffc107;
    }
    
    .activity-icon.info {
      background-color: rgba(13, 110, 253, 0.1);
      color: #0d6efd;
    }
    
    .activity-icon i {
      font-size: 1.2rem;
    }
    
    .activity-content {
      flex: 1;
    }
    
    .activity-title {
      font-weight: 600;
      margin-bottom: 0.25rem;
    }
    
    .activity-details {
      font-size: 0.9rem;
      margin-bottom: 0.25rem;
      color: var(--text-secondary);
    }
    
    .activity-time {
      font-size: 0.8rem;
      color: var(--text-secondary);
    }
    
    /* Quick Actions */
    .quick-actions-container {
      background-color: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px var(--shadow);
      margin-bottom: 2rem;
    }
    
    .quick-actions-container h3 {
      font-size: 1.2rem;
      color: var(--primary);
      margin-bottom: 1.5rem;
    }
    
    .quick-actions {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
    }
    
    .action-button {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      color: var(--text-primary);
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 1.5rem 1rem;
      transition: all 0.3s ease;
    }
    
    .action-button:hover {
      background-color: var(--primary-light);
      color: var(--primary);
      transform: translateY(-3px);
      box-shadow: 0 4px 6px var(--shadow);
    }
    
    .action-button i {
      font-size: 1.8rem;
      margin-bottom: 0.5rem;
    }
    
    /* Dashboard Tabs */
    .dashboard-tabs {
      margin-bottom: 2rem;
    }
    
    .nav-tabs {
      border-bottom: 1px solid #dee2e6;
      margin-bottom: 1.5rem;
    }
    
    .nav-tabs .nav-link {
      color: var(--text-secondary);
      font-weight: 500;
      padding: 0.75rem 1.5rem;
      border: none;
      border-bottom: 3px solid transparent;
      background: transparent;
    }
    
    .nav-tabs .nav-link.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
      background: transparent;
    }
    
    .tab-content > .tab-pane {
      padding: 0.5rem;
    }
    
    @media (max-width: 768px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
      
      .sla-table-header,
      .sla-table-row {
        grid-template-columns: 2fr 1fr 1fr;
      }
      
      .sla-header-cell:nth-child(3),
      .sla-cell:nth-child(3) {
        display: none;
      }
      
      .quick-actions {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  metrics: MetricCard[] = [];
  activityData: TimeSeriesData[] = [];
  complianceData: ComplianceData[] = [];
  slaPerformance: SLAPerformance[] = [];
  
  selectedPeriod: string = 'week';
  isLoading: boolean = true;
  
  constructor(private analyticsService: AnalyticsService) { }

  ngOnInit(): void {
    // Start with pre-loaded mock data to improve initial render time
    this.setInitialMockData();
    // Then load actual data asynchronously
    this.loadDashboardData();
  }
  
  /**
   * Set initial mock data to improve perceived performance
   */
  setInitialMockData(): void {
    // Use mock data immediately for initial render
    this.metrics = [
      {
        title: 'Total Consultations',
        value: '152',
        icon: 'chat-dots',
        trend: { value: 12.5, isPositive: true },
        color: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)'
      },
      {
        title: 'Active SLAs',
        value: '28',
        icon: 'file-earmark-check',
        trend: { value: 8.3, isPositive: true },
        color: 'linear-gradient(135deg, var(--secondary) 0%, var(--secondary-light) 100%)'
      }
    ];
    this.isLoading = false;
  }
  
  loadDashboardData(): void {
    // Load data in stages to improve performance
    
    // Stage 1: Load essential metrics first
    this.analyticsService.getDashboardMetrics().subscribe(data => {
      this.metrics = data;
    });
    
    // Stage 2: Load secondary data after a slight delay
    setTimeout(() => {
      this.loadActivityData(this.selectedPeriod);
    
      // Stage 3: Load less critical data last
      setTimeout(() => {
        // Load SLA compliance data
        this.analyticsService.getSLACompliance().subscribe(data => {
          this.complianceData = data;
        });
        
        // Load SLA performance metrics
        this.analyticsService.getSLAPerformance().subscribe(data => {
          this.slaPerformance = data;
        });
      }, 300);
    }, 100);
  }
  
  loadActivityData(event: Event | string): void {
    // Handle both direct string parameter and event from select
    const period = typeof event === 'string' ? event : (event.target as HTMLSelectElement).value;
    
    this.selectedPeriod = period;
    
    // Add loading indicator to the chart
    const chartPlaceholder = document.querySelector('.chart-placeholder');
    if (chartPlaceholder) {
      chartPlaceholder.classList.add('loading');
    }
    
    this.analyticsService.getConsultationActivity(period).subscribe({
      next: (data) => {
        this.activityData = data;
        // Remove loading indicator
        if (chartPlaceholder) {
          chartPlaceholder.classList.remove('loading');
        }
      },
      error: (error) => {
        console.error('Error loading activity data:', error);
        // Remove loading indicator even on error
        if (chartPlaceholder) {
          chartPlaceholder.classList.remove('loading');
        }
        // Use fallback data on error
        this.activityData = [
          { label: 'Mon', count: 22, percentage: 55 },
          { label: 'Tue', count: 28, percentage: 70 },
          { label: 'Wed', count: 40, percentage: 100 },
          { label: 'Thu', count: 32, percentage: 80 },
          { label: 'Fri', count: 24, percentage: 60 },
          { label: 'Sat', count: 18, percentage: 45 },
          { label: 'Sun', count: 12, percentage: 30 }
        ];
      }
    });
  }
}