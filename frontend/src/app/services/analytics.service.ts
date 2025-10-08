import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface MetricData {
  title: string;
  value: number | string;
  icon: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: string;
}

export interface TimeSeriesData {
  label: string;
  count: number;
  percentage: number;
}

export interface ComplianceData {
  category: string;
  percentage: number;
  color: string;
}

export interface SLAPerformance {
  name: string;
  currentValue: number;
  threshold: number;
  unit: string;
  status: 'success' | 'warning' | 'danger';
}

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private apiUrl = `${environment.apiUrl}/api/analytics`;

  constructor(private http: HttpClient) { }

  /**
   * Get dashboard summary metrics
   */
  getDashboardMetrics(): Observable<MetricData[]> {
    return this.http.get<any>(`${this.apiUrl}/summary`).pipe(
      map(response => response.metrics),
      catchError(error => {
        console.error('Error fetching dashboard metrics:', error);
        // Return mock data if the API fails
        return of(this.getMockMetrics());
      })
    );
  }

  /**
   * Get consultation activity over time
   */
  getConsultationActivity(period: string = 'week'): Observable<TimeSeriesData[]> {
    return this.http.get<any>(`${this.apiUrl}/consultation-activity?period=${period}`).pipe(
      map(response => response.data),
      catchError(error => {
        console.error('Error fetching consultation activity:', error);
        // Return mock data if the API fails
        return of(this.getMockActivityData());
      })
    );
  }

  /**
   * Get SLA compliance data
   */
  getSLACompliance(): Observable<ComplianceData[]> {
    return this.http.get<any>(`${this.apiUrl}/sla-compliance`).pipe(
      map(response => response.data),
      catchError(error => {
        console.error('Error fetching SLA compliance:', error);
        // Return mock data if the API fails
        return of(this.getMockComplianceData());
      })
    );
  }

  /**
   * Get SLA performance metrics
   */
  getSLAPerformance(): Observable<SLAPerformance[]> {
    return this.http.get<any>(`${this.apiUrl}/sla-performance`).pipe(
      map(response => response.metrics),
      catchError(error => {
        console.error('Error fetching SLA performance:', error);
        // Return mock data if the API fails
        return of(this.getMockSLAPerformance());
      })
    );
  }

  /**
   * Mock data for development purposes
   */
  private getMockMetrics(): MetricData[] {
    return [
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
      },
      {
        title: 'Avg. Compliance',
        value: '94.7%',
        icon: 'shield-check',
        trend: { value: 1.2, isPositive: true },
        color: 'linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%)'
      },
      {
        title: 'Templates Used',
        value: '48',
        icon: 'file-earmark-text',
        color: 'linear-gradient(135deg, #26C6DA 0%, #80DEEA 100%)'
      }
    ];
  }

  private getMockActivityData(): TimeSeriesData[] {
    return [
      { label: 'Mon', count: 22, percentage: 55 },
      { label: 'Tue', count: 28, percentage: 70 },
      { label: 'Wed', count: 40, percentage: 100 },
      { label: 'Thu', count: 32, percentage: 80 },
      { label: 'Fri', count: 24, percentage: 60 },
      { label: 'Sat', count: 18, percentage: 45 },
      { label: 'Sun', count: 12, percentage: 30 }
    ];
  }

  private getMockComplianceData(): ComplianceData[] {
    return [
      { category: 'Availability', percentage: 98.2, color: '#4CAF50' },
      { category: 'Performance', percentage: 94.5, color: '#2196F3' },
      { category: 'Security', percentage: 100, color: '#673AB7' },
      { category: 'Support', percentage: 89.8, color: '#FF9800' }
    ];
  }

  private getMockSLAPerformance(): SLAPerformance[] {
    return [
      { 
        name: 'System Availability', 
        currentValue: 99.97, 
        threshold: 99.9, 
        unit: '%', 
        status: 'success' 
      },
      { 
        name: 'Response Time', 
        currentValue: 1.8, 
        threshold: 2.0, 
        unit: 's', 
        status: 'success' 
      },
      { 
        name: 'Resolution Time', 
        currentValue: 3.2, 
        threshold: 4.0, 
        unit: 'hours', 
        status: 'success' 
      },
      { 
        name: 'Security Incidents', 
        currentValue: 0, 
        threshold: 0, 
        unit: '', 
        status: 'success' 
      },
      { 
        name: 'Support Response', 
        currentValue: 18, 
        threshold: 15, 
        unit: 'min', 
        status: 'warning' 
      }
    ];
  }
}