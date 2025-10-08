import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface Document {
  id: string;
  filename: string;
  title: string;
  industry?: string;
  service_type?: string;
  upload_date: string;
  file_size: number;
  status: 'processed' | 'pending' | 'error';
}

@Component({
  selector: 'app-knowledge-base',
  templateUrl: './knowledge-base.component.html',
  styleUrls: ['./knowledge-base.component.scss']
})
export class KnowledgeBaseComponent implements OnInit {
  documents: Document[] = [];
  isLoading = false;
  uploadProgress = 0;
  isUploading = false;
  selectedFiles: File[] = [];
  selectedDocument: Document | null = null;
  searchQuery = '';
  filterIndustry = '';
  
  industries = ['Healthcare', 'IT', 'Telecom', 'Financial', 'Retail', 'Manufacturing', 'Other'];

  constructor(
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments() {
    this.isLoading = true;
    this.http.get<Document[]>(`${environment.apiUrl}/api/v1/documents`)
      .subscribe({
        next: (response) => {
          this.documents = response;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading documents', error);
          alert('Failed to load documents');
          this.isLoading = false;
        }
      });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFiles = Array.from(input.files);
    }
  }

  uploadFiles() {
    if (!this.selectedFiles.length) {
      alert('No files selected');
      return;
    }

    this.isUploading = true;
    this.uploadProgress = 0;
    
    const formData = new FormData();
    this.selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    this.http.post(`${environment.apiUrl}/api/v1/documents/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress) {
          if (event.total) {
            this.uploadProgress = Math.round(100 * event.loaded / event.total);
          }
        } else if (event.type === HttpEventType.Response) {
          alert('Documents uploaded successfully!');
          this.isUploading = false;
          this.selectedFiles = [];
          // Reset the file input
          const fileInput = document.getElementById('file-upload') as HTMLInputElement;
          if (fileInput) {
            fileInput.value = '';
          }
          // Reload documents after successful upload
          this.loadDocuments();
        }
      },
      error: (error) => {
        console.error('Error uploading documents', error);
        alert('Failed to upload documents');
        this.isUploading = false;
      }
    });
  }

  viewDocument(document: Document) {
    this.selectedDocument = document;
  }

  deleteDocument(id: string) {
    if (confirm('Are you sure you want to delete this document?')) {
      this.http.delete(`${environment.apiUrl}/api/v1/documents/${id}`)
        .subscribe({
          next: () => {
            alert('Document deleted successfully');
            this.loadDocuments();
            if (this.selectedDocument?.id === id) {
              this.selectedDocument = null;
            }
          },
          error: (error) => {
            console.error('Error deleting document', error);
            alert('Failed to delete document');
          }
        });
    }
  }

  clearSearch() {
    this.searchQuery = '';
  }

  get filteredDocuments() {
    return this.documents.filter(doc => {
      const matchesSearch = !this.searchQuery || 
        doc.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        doc.filename.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      const matchesIndustry = !this.filterIndustry || 
        (doc.industry && doc.industry.toLowerCase() === this.filterIndustry.toLowerCase());
      
      return matchesSearch && matchesIndustry;
    });
  }
}