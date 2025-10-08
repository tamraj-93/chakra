import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ExportService {
  private apiUrl = `${environment.apiUrl}/api/templates`;

  constructor(private http: HttpClient) { }

  /**
   * Export a template as PDF
   * @param templateId The ID of the template to export
   * @returns Observable with PDF data in base64 format
   */
  exportTemplatePdf(templateId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${templateId}/export?format=pdf`);
  }

  /**
   * Download and save a PDF file from base64 content
   * @param base64Data Base64-encoded PDF data
   * @param filename The filename to use for the download
   */
  downloadPdf(base64Data: string, filename: string): void {
    if (!base64Data) {
      console.error('No PDF data provided');
      alert('Error: The PDF document could not be generated. Please try again.');
      return;
    }
    
    try {
      // Convert base64 to blob
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });

      // Make sure the blob has content
      if (blob.size === 0) {
        console.error('Generated PDF has zero size');
        alert('Error: The generated PDF is empty. Please try again.');
        return;
      }

      // Create a download link and trigger it
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      link.click();

      // Clean up
      setTimeout(() => {
        window.URL.revokeObjectURL(link.href);
      }, 100);
    } catch (error) {
      console.error('PDF download error:', error);
      alert('Error downloading PDF. Please try again.');
    }
  }

  /**
   * Open the PDF in a new tab/window
   * @param base64Data Base64-encoded PDF data
   */
  openPdfInNewTab(base64Data: string): void {
    if (!base64Data) {
      console.error('No PDF data provided');
      alert('Error: The PDF document could not be generated. Please try again.');
      return;
    }
    
    try {
      const pdfWindow = window.open("");
      if (pdfWindow) {
        pdfWindow.document.write(
          `<iframe width='100%' height='100%' src='data:application/pdf;base64,${base64Data}'></iframe>`
        );
      } else {
        alert('Please enable pop-ups to view the PDF');
      }
    } catch (error) {
      console.error('Error opening PDF:', error);
      alert('Error opening PDF. Please try again.');
    }
  }
}