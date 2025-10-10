import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import jsPDF from 'jspdf';

export interface SLADocument {
  id: string;
  title: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  status: 'draft' | 'review' | 'approved' | 'active' | 'expired';
  content: any;
  sessionId?: number;
  templateId?: string;
  healthcareRelated: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SlaDocumentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Generate SLA document from consultation
  generateSLADocument(sessionId: number): Observable<SLADocument> {
    return this.http.post<SLADocument>(`${this.apiUrl}/sla-documents/generate/${sessionId}`, {})
      .pipe(
        catchError(error => {
          console.error('Error generating SLA document:', error);
          // For the hackathon, we'll generate a mock document if the backend is not implemented
          return of(this.generateMockSLADocument(sessionId));
        })
      );
  }

  // Get all SLA documents for current user
  getSLADocuments(): Observable<SLADocument[]> {
    return this.http.get<SLADocument[]>(`${this.apiUrl}/sla-documents`)
      .pipe(
        catchError(error => {
          console.error('Error fetching SLA documents:', error);
          // For the hackathon, return mock data if endpoint not implemented
          return of(this.getMockSLADocuments());
        })
      );
  }

  // Get single SLA document by ID
  getSLADocument(id: string): Observable<SLADocument> {
    return this.http.get<SLADocument>(`${this.apiUrl}/sla-documents/${id}`)
      .pipe(
        catchError(error => {
          console.error(`Error fetching SLA document ${id}:`, error);
          // Mock fallback
          const mockDocs = this.getMockSLADocuments();
          const doc = mockDocs.find(d => d.id === id);
          return of(doc || mockDocs[0]);
        })
      );
  }

  // Update SLA document status
  updateSLADocumentStatus(id: string, status: SLADocument['status']): Observable<SLADocument> {
    return this.http.patch<SLADocument>(`${this.apiUrl}/sla-documents/${id}/status`, { status })
      .pipe(
        catchError(error => {
          console.error(`Error updating SLA document ${id}:`, error);
          // Mock update for hackathon
          const mockDocs = this.getMockSLADocuments();
          const docIndex = mockDocs.findIndex(d => d.id === id);
          if (docIndex >= 0) {
            mockDocs[docIndex].status = status;
            return of(mockDocs[docIndex]);
          }
          return of(mockDocs[0]);
        })
      );
  }

  // Export SLA document as PDF
  exportSLADocumentAsPDF(id: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/sla-documents/${id}/export/pdf`, { responseType: 'blob' })
      .pipe(
        catchError(error => {
          console.error(`Error exporting SLA document ${id} as PDF:`, error);
          // Generate a more detailed sample PDF with actual content using jsPDF
          const doc = this.getMockSLADocuments().find(d => d.id === id);
          
          // Create a sample PDF with actual content from the mock document
          const title = doc?.title || 'Service Level Agreement';
          const description = doc?.description || 'SLA Document';
          const isHealthcare = doc?.healthcareRelated || false;
          
          // Generate content sections based on type
          const securitySection = isHealthcare 
            ? "- Encryption: All PHI must be encrypted at rest and in transit using AES-256\n"
              + "- Access Control: Role-based access control with MFA required\n"
              + "- Audit Logging: All data access must be logged and accessible for review\n"
              + "- Risk Assessments: Performed quarterly as per HIPAA Security Rule requirements"
            : "- Encryption: All sensitive data encrypted at rest and in transit\n"
              + "- Access Control: Role-based access with authentication required\n"
              + "- Audit Logging: System access logs maintained for 90 days";
          
          const serviceOverview = isHealthcare 
            ? "This SLA covers Electronic Health Record (EHR) hosting services compliant with HIPAA regulations."
            : "This SLA covers all services provided as outlined in the accompanying contract.";
            
          const hipaaMetric = isHealthcare 
            ? "- HIPAA Compliance: Guaranteed full compliance with all regulations\n" 
            : "";
            
          const disasterRecoveryExtra = isHealthcare
            ? "- Patient Data Protection: Special procedures for PHI protection during recovery\n"
            : "";
            
          const healthcareCompliant = isHealthcare 
            ? "HEALTHCARE COMPLIANT: YES\n" 
            : "";
            
          // Create PDF using jsPDF
          const pdf = new jsPDF();
          
          // Add title
          pdf.setFontSize(20);
          pdf.setFont('helvetica', 'bold');
          pdf.text(title, 20, 20);
          
          // Add line under title
          pdf.setDrawColor(0);
          pdf.setLineWidth(0.5);
          pdf.line(20, 25, 190, 25);
          
          // Add description
          pdf.setFontSize(12);
          pdf.setFont('helvetica', 'normal');
          pdf.text(description, 20, 35);
          
          // Add status and healthcare compliance
          pdf.setFontSize(11);
          let yPosition = 45;
          
          pdf.setFont('helvetica', 'bold');
          pdf.text("STATUS: " + (doc?.status?.toUpperCase() || "DRAFT"), 20, yPosition);
          yPosition += 7;
          
          if (isHealthcare) {
            pdf.text("HEALTHCARE COMPLIANT: YES", 20, yPosition);
            yPosition += 7;
          }
          
          pdf.text("Created: " + new Date().toLocaleDateString(), 20, yPosition);
          yPosition += 15;
          
          // Document Sections Title
          pdf.setFontSize(14);
          pdf.setFont('helvetica', 'bold');
          pdf.text("DOCUMENT SECTIONS:", 20, yPosition);
          yPosition += 10;
          
          // 1. Service Overview
          pdf.setFontSize(12);
          pdf.setFont('helvetica', 'bold');
          pdf.text("1. SERVICE OVERVIEW", 20, yPosition);
          yPosition += 7;
          
          pdf.setFont('helvetica', 'normal');
          pdf.text(serviceOverview, 25, yPosition, { maxWidth: 165 });
          yPosition += 15;
          
          // 2. Performance Metrics
          pdf.setFont('helvetica', 'bold');
          pdf.text("2. PERFORMANCE METRICS", 20, yPosition);
          yPosition += 7;
          
          pdf.setFont('helvetica', 'normal');
          pdf.text("- Availability: 99.9% uptime guaranteed", 25, yPosition);
          yPosition += 7;
          pdf.text("- Response Time: < 500ms for standard transactions", 25, yPosition);
          yPosition += 7;
          
          if (isHealthcare) {
            pdf.text("- HIPAA Compliance: Guaranteed full compliance with all regulations", 25, yPosition);
            yPosition += 7;
          }
          yPosition += 8;
          
          // 3. Support Levels
          pdf.setFont('helvetica', 'bold');
          pdf.text("3. SUPPORT LEVELS", 20, yPosition);
          yPosition += 7;
          
          pdf.setFont('helvetica', 'normal');
          pdf.text("- Critical Issues: Response within 15 minutes", 25, yPosition);
          yPosition += 7;
          pdf.text("- Major Issues: Response within 1 hour", 25, yPosition);
          yPosition += 7;
          pdf.text("- Minor Issues: Response within 24 hours", 25, yPosition);
          yPosition += 15;
          
          // 4. Security Requirements
          pdf.setFont('helvetica', 'bold');
          pdf.text("4. SECURITY REQUIREMENTS", 20, yPosition);
          yPosition += 7;
          
          pdf.setFont('helvetica', 'normal');
          const securityLines = securitySection.split('\n');
          securityLines.forEach(line => {
            pdf.text(line, 25, yPosition);
            yPosition += 7;
          });
          yPosition += 8;
          
          // 5. Disaster Recovery
          pdf.setFont('helvetica', 'bold');
          pdf.text("5. DISASTER RECOVERY", 20, yPosition);
          yPosition += 7;
          
          pdf.setFont('helvetica', 'normal');
          pdf.text("- Recovery Time Objective (RTO): 4 hours", 25, yPosition);
          yPosition += 7;
          pdf.text("- Recovery Point Objective (RPO): 15 minutes", 25, yPosition);
          yPosition += 7;
          
          if (isHealthcare) {
            pdf.text("- Patient Data Protection: Special procedures for PHI protection during recovery", 25, yPosition);
            yPosition += 7;
          }
          yPosition += 15;
          
          // Footer
          pdf.setFontSize(10);
          pdf.setTextColor(100);
          pdf.text("Generated with Chakra SLA Management Platform", 20, 280);
          
          // Add page number
          pdf.setFont('helvetica', 'italic');
          pdf.text(`Page 1`, 180, 280);
          
          // Create a PDF blob with actual content
          const pdfOutput = pdf.output('blob');
          return of(pdfOutput);
        })
      );
  }

  // Helper methods to generate mock data for hackathon demo
  private generateMockSLADocument(sessionId: number): SLADocument {
    const isHealthcare = Math.random() > 0.5;
    const title = isHealthcare ? 'Healthcare EHR Hosting SLA' : 'Cloud Service SLA';
    
    return {
      id: `sla-${Date.now()}`,
      title: title,
      description: isHealthcare ? 
        'Service Level Agreement for Electronic Health Record Hosting with HIPAA Compliance' :
        'Service Level Agreement for Cloud Services',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'draft',
      content: {
        sections: [
          {
            title: 'Service Overview',
            content: 'This SLA covers the terms and conditions for providing...'
          },
          {
            title: 'Performance Metrics',
            content: 'The service will maintain 99.9% uptime...'
          },
          {
            title: 'Security Requirements',
            content: isHealthcare ? 
              'HIPAA compliance requirements include encryption of data at rest and in transit...' :
              'Security measures include encryption and access controls...'
          }
        ]
      },
      sessionId: sessionId,
      healthcareRelated: isHealthcare
    };
  }

  private getMockSLADocuments(): SLADocument[] {
    return [
      {
        id: 'sla-1',
        title: 'Healthcare EHR Hosting SLA',
        description: 'Service Level Agreement for Electronic Health Record Hosting with HIPAA Compliance',
        createdAt: '2025-09-30T14:30:00Z',
        updatedAt: '2025-09-30T14:30:00Z',
        status: 'active',
        content: { 
          sections: [
            {
              title: 'Service Overview',
              content: 'This SLA covers the terms and conditions for providing Electronic Health Record (EHR) hosting services in compliance with HIPAA regulations and other applicable healthcare standards.'
            },
            {
              title: 'Performance Metrics',
              content: 'The service will maintain 99.99% uptime, critical for healthcare operations where access to patient records is essential for care delivery.'
            },
            {
              title: 'Security Requirements',
              content: 'HIPAA compliance requirements include encryption of data at rest and in transit, strict access controls, regular security audits, and comprehensive audit logging of all PHI access events.'
            }
          ]
        },
        healthcareRelated: true
      },
      {
        id: 'sla-2',
        title: 'Telemedicine Platform SLA',
        description: 'Service Level Agreement for Telemedicine Platform with Video Quality Standards',
        createdAt: '2025-09-25T10:15:00Z',
        updatedAt: '2025-09-25T10:15:00Z',
        status: 'review',
        content: { 
          sections: [
            {
              title: 'Service Overview',
              content: 'This SLA covers the terms and conditions for telemedicine platform services, ensuring high-quality video consultations between healthcare providers and patients.'
            },
            {
              title: 'Video Quality Standards',
              content: 'Video quality must maintain minimum resolution of 720p with frame rate of 30fps. Audio quality must maintain minimum 44kHz sampling rate with echo cancellation.'
            },
            {
              title: 'HIPAA Compliance',
              content: 'All video sessions are encrypted end-to-end and no recordings are stored unless explicitly authorized by both patient and provider with appropriate consent documentation.'
            }
          ]
        },
        healthcareRelated: true
      },
      {
        id: 'sla-3',
        title: 'Cloud Backup Service SLA',
        description: 'Service Level Agreement for Enterprise Cloud Backup Solutions',
        createdAt: '2025-09-15T09:45:00Z',
        updatedAt: '2025-09-15T09:45:00Z',
        status: 'draft',
        content: { 
          sections: [
            {
              title: 'Service Overview',
              content: 'This SLA covers the terms and conditions for enterprise cloud backup solutions, ensuring data integrity and availability.'
            },
            {
              title: 'Backup Schedule and Retention',
              content: 'Daily incremental backups with weekly full backups. Retention policy includes 30 days of daily backups, 12 weeks of weekly backups, and 7 years of monthly backups.'
            },
            {
              title: 'Recovery Time Objectives',
              content: 'Critical systems: 4 hours RTO. Important systems: 12 hours RTO. Non-critical systems: 24 hours RTO.'
            }
          ]
        },
        healthcareRelated: false
      }
    ];
  }
}