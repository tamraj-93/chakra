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
              <h3><i class="bi bi-exclamation-triangle me-2"></i> Document content not available in viewer</h3>
              <p>The document content cannot be displayed properly in the browser viewer. Please use one of these options:</p>
              
              <div class="row mt-4">
                <div class="col-md-6">
                  <div class="card h-100 bg-light border-0">
                    <div class="card-body">
                      <h5 class="mb-3"><i class="bi bi-download me-2"></i> Recommended Option</h5>
                      <p>Download and view the PDF with a dedicated PDF reader like Adobe Reader or Preview.</p>
                      <button class="btn btn-primary mt-2" (click)="exportSLA()">
                        <i class="bi bi-file-earmark-pdf me-2"></i> Export as PDF
                      </button>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="card h-100 bg-light border-0">
                    <div class="card-body">
                      <h5 class="mb-3"><i class="bi bi-list-check me-2"></i> View Document Details</h5>
                      <p>Document type: {{ document.healthcareRelated ? 'Healthcare SLA' : 'Standard SLA' }}</p>
                      <p>Status: <span class="badge" [ngClass]="{
                        'bg-warning': document.status === 'draft',
                        'bg-info': document.status === 'review',
                        'bg-success': document.status === 'approved' || document.status === 'active',
                        'bg-secondary': document.status === 'expired'
                      }">{{ document.status | titlecase }}</span></p>
                      <p>Created: {{ formatDate(document.createdAt) }}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mt-4 text-center text-muted small">
                <i class="bi bi-info-circle me-1"></i> 
                Some browser PDF viewers may not display the content correctly. 
                This is a known issue with certain PDF formats.
              </div>
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
    
    // Show loading message
    const loadingToast = document.createElement('div');
    loadingToast.className = 'toast align-items-center show bg-primary text-white position-fixed bottom-0 end-0 m-3';
    loadingToast.style.zIndex = '9999';
    loadingToast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <span class="spinner-border spinner-border-sm me-2" role="status"></span>
          Generating PDF document...
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    document.body.appendChild(loadingToast);
    
    this.slaDocumentService.exportSLADocumentAsPDF(this.document.id)
      .subscribe({
        next: (blob) => {
          // Remove loading toast
          document.body.removeChild(loadingToast);
          
          // Create blob link to download
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `${this.document?.title.replace(/\s+/g, '-').toLowerCase()}-${this.document?.id}.pdf`;
          
          // Append to html page
          document.body.appendChild(link);
          
          // Force download
          link.click();
          
          // Clean up and remove the link
          link.parentNode!.removeChild(link);
          window.URL.revokeObjectURL(url);
          
          // Show success message
          const successToast = document.createElement('div');
          successToast.className = 'toast align-items-center show bg-success text-white position-fixed bottom-0 end-0 m-3';
          successToast.style.zIndex = '9999';
          successToast.innerHTML = `
            <div class="d-flex">
              <div class="toast-body">
                <i class="bi bi-check-circle me-2"></i>
                PDF downloaded successfully! Check your downloads folder.
              </div>
              <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
          `;
          document.body.appendChild(successToast);
          
          // Auto-remove success toast after 5 seconds
          setTimeout(() => {
            if (document.body.contains(successToast)) {
              document.body.removeChild(successToast);
            }
          }, 5000);
          
          // Add event listener to close button
          const closeBtn = successToast.querySelector('.btn-close');
          if (closeBtn) {
            closeBtn.addEventListener('click', () => {
              document.body.removeChild(successToast);
            });
          }
        },
        error: (err) => {
          // Remove loading toast
          document.body.removeChild(loadingToast);
          
          console.error('Error exporting SLA document:', err);
          
          // Show error toast with more helpful message
          const errorToast = document.createElement('div');
          errorToast.className = 'toast align-items-center show bg-danger text-white position-fixed bottom-0 end-0 m-3';
          errorToast.style.zIndex = '9999';
          errorToast.innerHTML = `
            <div class="d-flex">
              <div class="toast-body">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error generating PDF. If your PDF has no content, try using a PDF viewer like Adobe Reader instead of the browser's built-in viewer.
              </div>
              <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
          `;
          document.body.appendChild(errorToast);
          
          // Auto-remove error toast after 8 seconds
          setTimeout(() => {
            if (document.body.contains(errorToast)) {
              document.body.removeChild(errorToast);
            }
          }, 8000);
          
          // Add event listener to close button
          const closeBtn = errorToast.querySelector('.btn-close');
          if (closeBtn) {
            closeBtn.addEventListener('click', () => {
              document.body.removeChild(errorToast);
            });
          }
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