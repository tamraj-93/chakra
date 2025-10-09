import { Component, OnInit } from '@angular/core';
import { SlaDocumentService, SLADocument } from '../../services/sla-document.service';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-my-slas',
  template: `
    <div class="container mt-4">
      <!-- Success Message -->
      <div *ngIf="showSuccessMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        <i class="bi bi-check-circle me-2"></i> <strong>Success!</strong> Your SLA document has been generated successfully.
        <button type="button" class="btn-close" (click)="dismissSuccessMessage()" aria-label="Close"></button>
      </div>
      
      <div class="row mb-4">
        <div class="col">
          <h2>My SLAs</h2>
          <p class="text-muted">Manage your Service Level Agreements</p>
        </div>
        <div class="col-auto">
          <button class="btn btn-outline-primary me-2" (click)="navigateToTemplates()">
            <i class="bi bi-file-earmark-plus"></i> Create New SLA
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error State -->
      <div *ngIf="error" class="alert alert-danger">
        {{ error }}
      </div>

      <!-- Empty State -->
      <div *ngIf="!loading && !error && (!slaDocuments || slaDocuments.length === 0)" class="text-center my-5 py-5">
        <div class="empty-state">
          <i class="bi bi-file-earmark-text display-1 text-muted"></i>
          <h3 class="mt-4">No SLAs Yet</h3>
          <p class="text-muted">You haven't created any SLAs yet. Start a consultation to create your first SLA.</p>
          <button class="btn btn-primary mt-3" (click)="navigateToTemplates()">Start Consultation</button>
        </div>
      </div>

      <!-- SLA List -->
      <div *ngIf="!loading && !error && slaDocuments && slaDocuments.length > 0" class="sla-list">
        <!-- Filters -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row g-3 align-items-center">
              <div class="col-md-4">
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input type="text" class="form-control" placeholder="Search SLAs..." [(ngModel)]="searchTerm">
                </div>
              </div>
              <div class="col-md-3">
                <select class="form-select" [(ngModel)]="statusFilter">
                  <option value="all">All Statuses</option>
                  <option value="draft">Draft</option>
                  <option value="review">Under Review</option>
                  <option value="approved">Approved</option>
                  <option value="active">Active</option>
                  <option value="expired">Expired</option>
                </select>
              </div>
              <div class="col-md-3">
                <select class="form-select" [(ngModel)]="typeFilter">
                  <option value="all">All Types</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="col-md-2 text-end">
                <button class="btn btn-outline-secondary" (click)="resetFilters()">
                  <i class="bi bi-x-circle"></i> Reset
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- SLA Cards -->
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
          <div *ngFor="let sla of filteredSLAs" class="col">
            <div class="card h-100" [ngClass]="{'border-success': sla.healthcareRelated}">
              <div class="card-header" [ngClass]="{'bg-success text-white': sla.healthcareRelated}">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="badge" [ngClass]="{
                    'bg-warning': sla.status === 'draft',
                    'bg-info': sla.status === 'review',
                    'bg-success': sla.status === 'approved' || sla.status === 'active',
                    'bg-secondary': sla.status === 'expired'
                  }">{{ sla.status | titlecase }}</span>
                  <div *ngIf="sla.healthcareRelated" class="healthcare-badge">
                    <i class="bi bi-heart-pulse me-1"></i> Healthcare
                  </div>
                </div>
              </div>
              <div class="card-body">
                <h5 class="card-title">{{ sla.title }}</h5>
                <p class="card-text">{{ sla.description }}</p>
                <div class="small text-muted mb-3">
                  <div><strong>Created:</strong> {{ formatDate(sla.createdAt) }}</div>
                  <div><strong>Updated:</strong> {{ formatDate(sla.updatedAt) }}</div>
                </div>
              </div>
              <div class="card-footer bg-transparent">
                <div class="d-flex justify-content-between">
                  <button class="btn btn-sm btn-primary" (click)="viewSLA(sla.id)">
                    <i class="bi bi-eye"></i> View
                  </button>
                  <div class="btn-group">
                    <button class="btn btn-sm btn-outline-secondary" (click)="exportSLA(sla.id)">
                      <i class="bi bi-download"></i> Export
                    </button>
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown">
                      <span class="visually-hidden">Toggle Dropdown</span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                      <li><button class="dropdown-item" (click)="updateStatus(sla.id, 'review')">Mark for Review</button></li>
                      <li><button class="dropdown-item" (click)="updateStatus(sla.id, 'approved')">Mark as Approved</button></li>
                      <li><button class="dropdown-item" (click)="updateStatus(sla.id, 'active')">Mark as Active</button></li>
                      <li><hr class="dropdown-divider"></li>
                      <li><button class="dropdown-item text-danger" (click)="deleteSLA(sla.id)">Delete</button></li>
                    </ul>
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
    .healthcare-badge {
      background-color: #16a34a;
      color: white;
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      font-weight: 600;
    }
    
    .empty-state {
      padding: 3rem;
    }
    
    .card-title {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  `]
})
export class MySLAsComponent implements OnInit {
  slaDocuments: SLADocument[] = [];
  loading = true;
  error: string | null = null;
  showSuccessMessage = false;
  
  // Filters
  searchTerm = '';
  statusFilter = 'all';
  typeFilter = 'all';
  
  constructor(
    private slaDocumentService: SlaDocumentService,
    private router: Router,
    private route: ActivatedRoute
  ) {}
  
  ngOnInit(): void {
    this.loadSLAs();
    
    // Check if we're coming from a consultation completion
    // Use query parameter to check if we should show success message
    this.route.queryParams.subscribe(params => {
      if (params['fromConsultation'] === 'true') {
        this.showSuccessMessage = true;
        // Auto-dismiss after 10 seconds
        setTimeout(() => this.showSuccessMessage = false, 10000);
      }
    });
  }
  
  // Dismiss success message manually
  dismissSuccessMessage(): void {
    this.showSuccessMessage = false;
  }
  
  loadSLAs(): void {
    this.loading = true;
    this.slaDocumentService.getSLADocuments()
      .subscribe({
        next: (documents) => {
          this.slaDocuments = documents;
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load SLA documents. Please try again later.';
          this.loading = false;
          console.error('Error loading SLA documents:', err);
        }
      });
  }
  
  get filteredSLAs(): SLADocument[] {
    return this.slaDocuments.filter(sla => {
      // Apply search filter
      const matchesSearch = !this.searchTerm || 
        sla.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        sla.description.toLowerCase().includes(this.searchTerm.toLowerCase());
        
      // Apply status filter
      const matchesStatus = this.statusFilter === 'all' || sla.status === this.statusFilter;
      
      // Apply type filter
      const matchesType = this.typeFilter === 'all' || 
        (this.typeFilter === 'healthcare' && sla.healthcareRelated) ||
        (this.typeFilter === 'other' && !sla.healthcareRelated);
        
      return matchesSearch && matchesStatus && matchesType;
    });
  }
  
  resetFilters(): void {
    this.searchTerm = '';
    this.statusFilter = 'all';
    this.typeFilter = 'all';
  }
  
  viewSLA(id: string): void {
    this.router.navigate(['/sla-documents', id]);
  }
  
  exportSLA(id: string): void {
    this.slaDocumentService.exportSLADocumentAsPDF(id)
      .subscribe({
        next: (blob) => {
          // Create blob link to download
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `sla-document-${id}.pdf`;
          
          // Append to html page
          document.body.appendChild(link);
          
          // Force download
          link.click();
          
          // Clean up and remove the link
          link.parentNode!.removeChild(link);
          window.URL.revokeObjectURL(url);
        },
        error: (err) => {
          console.error('Error exporting SLA document:', err);
          alert('Error exporting document. Please try again.');
        }
      });
  }
  
  updateStatus(id: string, status: SLADocument['status']): void {
    this.slaDocumentService.updateSLADocumentStatus(id, status)
      .subscribe({
        next: (updated) => {
          // Update the document in the list
          const index = this.slaDocuments.findIndex(d => d.id === id);
          if (index >= 0) {
            this.slaDocuments[index] = updated;
          }
        },
        error: (err) => {
          console.error('Error updating SLA status:', err);
          alert('Failed to update SLA status. Please try again.');
        }
      });
  }
  
  deleteSLA(id: string): void {
    if (confirm('Are you sure you want to delete this SLA? This action cannot be undone.')) {
      // For hackathon, just remove from the local array
      this.slaDocuments = this.slaDocuments.filter(d => d.id !== id);
    }
  }
  
  navigateToTemplates(): void {
    this.router.navigate(['/templates']);
  }
  
  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }
}