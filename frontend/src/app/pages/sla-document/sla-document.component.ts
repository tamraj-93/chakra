import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SlaDocumentService, SLADocument } from '../../services/sla-document.service';

@Component({
  selector: 'app-sla-document',
  template: `
    <div class="container mt-4">
      <!-- Loading State -->
      <div *ngIf="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error State -->
      <div *ngIf="error" class="alert alert-danger">
        {{ error }}
        <button class="btn btn-sm btn-outline-danger ms-3" (click)="navigateBack()">Go Back</button>
      </div>

      <!-- SLA Document -->
      <div *ngIf="!loading && !error && document" class="sla-document">
        <!-- Header -->
        <div class="row mb-4">
          <div class="col">
            <button class="btn btn-outline-secondary mb-3" (click)="navigateBack()">
              <i class="bi bi-arrow-left"></i> Back to My SLAs
            </button>
            <h2 [ngClass]="{'text-success': document.healthcareRelated}">{{ document.title }}</h2>
            <p class="text-muted">{{ document.description }}</p>
            <div class="d-flex align-items-center">
              <span class="badge me-2" [ngClass]="{
                'bg-warning': document.status === 'draft',
                'bg-info': document.status === 'review',
                'bg-success': document.status === 'approved' || document.status === 'active',
                'bg-secondary': document.status === 'expired'
              }">{{ document.status | titlecase }}</span>
              <div *ngIf="document.healthcareRelated" class="badge bg-success">
                <i class="bi bi-heart-pulse me-1"></i> Healthcare SLA
              </div>
              <span class="small text-muted ms-auto">
                Last updated: {{ formatDate(document.updatedAt) }}
              </span>
            </div>
          </div>
          <div class="col-auto">
            <div class="btn-group">
              <button class="btn btn-primary" (click)="exportSLA()">
                <i class="bi bi-download me-1"></i> Export as PDF
              </button>
              <button class="btn btn-primary dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown">
                <span class="visually-hidden">Toggle Dropdown</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#">Export as Word</a></li>
                <li><a class="dropdown-item" href="#">Share Link</a></li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Document Content -->
        <div class="card mb-4">
          <div class="card-body">
            <div *ngIf="document.content && document.content.sections">
              <div *ngFor="let section of document.content.sections" class="mb-4">
                <h3>{{ section.title }}</h3>
                <div class="content-section">
                  {{ section.content }}
                </div>
              </div>
            </div>
            <div *ngIf="!document.content || !document.content.sections" class="alert alert-warning">
              <h3>Document content not available</h3>
              <p>The document content could not be loaded properly. Please try using the "Export as PDF" button to view the document.</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="d-flex justify-content-between mb-5">
          <button class="btn btn-outline-secondary" (click)="navigateBack()">
            <i class="bi bi-arrow-left"></i> Back
          </button>
          <div>
            <button class="btn btn-outline-primary me-2" (click)="updateStatus('review')" *ngIf="document.status === 'draft'">
              Submit for Review
            </button>
            <button class="btn btn-success me-2" (click)="updateStatus('approved')" *ngIf="document.status === 'review'">
              Approve SLA
            </button>
            <button class="btn btn-primary" (click)="updateStatus('active')" *ngIf="document.status === 'approved'">
              Activate SLA
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .content-section {
      white-space: pre-line;
    }
    
    .card {
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
  `]
})
export class SlaDocumentComponent implements OnInit {
  document: SLADocument | null = null;
  loading = true;
  error: string | null = null;
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private slaDocumentService: SlaDocumentService
  ) {}
  
  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadDocument(id);
    } else {
      this.error = 'No document ID provided';
      this.loading = false;
    }
  }
  
  loadDocument(id: string): void {
    this.slaDocumentService.getSLADocument(id)
      .subscribe({
        next: (document) => {
          this.document = document;
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load SLA document. It may have been deleted or you may not have permission to access it.';
          this.loading = false;
          console.error('Error loading SLA document:', err);
        }
      });
  }
  
  updateStatus(status: SLADocument['status']): void {
    if (!this.document) return;
    
    this.slaDocumentService.updateSLADocumentStatus(this.document.id, status)
      .subscribe({
        next: (updated) => {
          this.document = updated;
        },
        error: (err) => {
          console.error('Error updating SLA status:', err);
          alert('Failed to update SLA status. Please try again.');
        }
      });
  }
  
  exportSLA(): void {
    if (!this.document) return;
    
    this.slaDocumentService.exportSLADocumentAsPDF(this.document.id)
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `${this.document?.title.replace(/\s+/g, '-').toLowerCase()}-${this.document?.id}.pdf`;
          document.body.appendChild(link);
          link.click();
          link.parentNode!.removeChild(link);
          window.URL.revokeObjectURL(url);
        },
        error: (err) => {
          console.error('Error exporting SLA document:', err);
          alert('Error exporting document. Please try again.');
        }
      });
  }
  
  navigateBack(): void {
    this.router.navigate(['/my-slas']);
  }
  
  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }
}