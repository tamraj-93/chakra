import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

/**
 * A pipe that transforms structured data into visually enhanced HTML
 * This helps with better visualization of structured data in messages
 */
@Pipe({
  name: 'structuredData'
})
export class StructuredDataPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string): SafeHtml {
    // Check if the string contains a JSON object
    try {
      // First, try to detect if this is JSON by checking for start/end markers
      if (
        (value.trim().startsWith('{') && value.trim().endsWith('}')) || 
        (value.trim().startsWith('[') && value.trim().endsWith(']'))
      ) {
        const parsed = JSON.parse(value);
        return this.sanitizer.bypassSecurityTrustHtml(this.formatJsonAsHtml(parsed));
      }
    } catch (e) {
      // Not valid JSON, continue with regular formatting
    }

    // Process regular text formatting
    return this.sanitizer.bypassSecurityTrustHtml(this.formatText(value));
  }

  private formatText(text: string): string {
    // Replace URLs with clickable links
    let formatted = text.replace(
      /(https?:\/\/[^\s]+)/g, 
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Format inline code
    formatted = formatted.replace(
      /`([^`]+)`/g, 
      '<code class="inline-code">$1</code>'
    );

    // Format code blocks
    formatted = formatted.replace(
      /```([^```]+)```/g,
      '<pre class="code-block"><code>$1</code></pre>'
    );

    // Format headers (markdown style)
    formatted = formatted.replace(/^### (.*$)/gm, '<h5>$1</h5>');
    formatted = formatted.replace(/^## (.*$)/gm, '<h4>$1</h4>');
    formatted = formatted.replace(/^# (.*$)/gm, '<h3>$1</h3>');

    // Format bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Format italic
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Format lists (simplified)
    formatted = formatted.replace(/^\s*-\s(.+)$/gm, '<li>$1</li>');
    formatted = formatted.split(/<li>/).join('<ul><li>').split('</li>').join('</li></ul>');
    formatted = formatted.replace(/<\/ul><ul>/g, '');

    return formatted;
  }

  private formatJsonAsHtml(data: any, level = 0): string {
    const indent = '  '.repeat(level);
    
    if (data === null) return '<span class="json-null">null</span>';
    
    if (typeof data === 'boolean') {
      return `<span class="json-boolean">${data}</span>`;
    }
    
    if (typeof data === 'number') {
      return `<span class="json-number">${data}</span>`;
    }
    
    if (typeof data === 'string') {
      // Check if it's a URL
      if (data.match(/^(https?:\/\/[^\s]+)$/)) {
        return `<span class="json-string"><a href="${data}" target="_blank">"${data}"</a></span>`;
      }
      return `<span class="json-string">"${data}"</span>`;
    }
    
    if (Array.isArray(data)) {
      if (data.length === 0) return '[]';
      
      let result = '<span class="json-array-bracket">[</span><div class="json-array">';
      data.forEach((item, index) => {
        result += `<div class="json-array-item">${this.formatJsonAsHtml(item, level + 1)}${
          index < data.length - 1 ? '<span class="json-comma">,</span>' : ''
        }</div>`;
      });
      result += `</div><span class="json-array-bracket">]</span>`;
      return result;
    }
    
    if (typeof data === 'object') {
      const keys = Object.keys(data);
      if (keys.length === 0) return '{}';
      
      let result = '<div class="json-object"><span class="json-brace">{</span>';
      
      keys.forEach((key, index) => {
        result += `<div class="json-property">
          <span class="json-property-name">"${key}"</span>: 
          ${this.formatJsonAsHtml(data[key], level + 1)}${
          index < keys.length - 1 ? '<span class="json-comma">,</span>' : ''
        }</div>`;
      });
      
      result += `<span class="json-brace">}</span></div>`;
      return result;
    }
    
    return String(data);
  }
}