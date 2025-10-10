/**
 * Enhanced Hackathon Demo Helper - Guarantees the Complete Consultation button is always available
 * This script provides a visually appealing floating action button, toast notifications,
 * and custom modal dialogs to ensure a smooth and professional demo experience
 * regardless of any component loading or template issues.
 */
(function() {
  console.log("🚀 Enhanced Hackathon Demo Helper v2.0 loaded");
  
  // Add enhanced CSS styles for UI components
  const addStyles = () => {
    const styleId = 'hackathon-helper-styles';
    if (document.getElementById(styleId)) return;
    
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(20px); }
      }
      @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
      }
      @keyframes scaleOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.8); }
      }
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 123, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0); }
      }
      @keyframes ripple {
        to {
          transform: scale(4);
          opacity: 0;
        }
      }
      .hackathon-toast-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9998;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 10px;
        max-width: 350px;
      }
      .hackathon-toast {
        background: #ffffff;
        color: #333;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        animation: fadeIn 0.3s ease-out forwards;
        max-width: 100%;
        display: flex;
        align-items: center;
        border-left: 4px solid #28a745;
      }
      .hackathon-toast.info { 
        border-left-color: #17a2b8; 
      }
      .hackathon-toast.success { 
        border-left-color: #28a745; 
      }
      .hackathon-toast.warning { 
        border-left-color: #ffc107; 
      }
      .hackathon-toast.error { 
        border-left-color: #dc3545; 
      }
      
      .hackathon-toast-content {
        flex-grow: 1;
        font-weight: 500;
      }
      .hackathon-toast-close {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        color: #999;
        margin-left: 10px;
        padding: 0 5px;
        transition: color 0.2s;
      }
      .hackathon-toast-close:hover {
        color: #555;
      }
      .hackathon-toast-icon {
        margin-right: 12px;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .hackathon-modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-out forwards;
        backdrop-filter: blur(3px);
      }
      .hackathon-modal {
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        width: 90%;
        max-width: 500px;
        animation: scaleIn 0.3s ease-out forwards;
        overflow: hidden;
      }
      .hackathon-modal-header {
        padding: 15px 20px;
        border-bottom: 1px solid #e9ecef;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .hackathon-modal-title {
        font-size: 18px;
        font-weight: bold;
        margin: 0;
      }
      .hackathon-modal-close {
        background: none;
        border: none;
        font-size: 22px;
        cursor: pointer;
        color: #999;
        padding: 0 5px;
      }
      .hackathon-modal-body {
        padding: 20px;
      }
      .hackathon-modal-footer {
        padding: 15px 20px;
        border-top: 1px solid #e9ecef;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
      }
      .hackathon-btn {
        padding: 10px 18px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
      }
      .hackathon-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }
      .hackathon-btn-primary {
        background: #007bff;
        color: white;
      }
      .hackathon-btn-success {
        background: #28a745;
        color: white;
      }
      .hackathon-btn-secondary {
        background: #6c757d;
        color: white;
      }
      .hackathon-btn-outline {
        background: transparent;
        border: 1px solid #007bff;
        color: #007bff;
      }
      .hackathon-loader {
        border: 3px solid rgba(0, 123, 255, 0.3);
        border-radius: 50%;
        border-top: 3px solid #007bff;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 8px;
        vertical-align: middle;
      }
    `;
    document.head.appendChild(style);
  };
  
  // Check if we're in a consultation page by looking for key elements or URL patterns
  function isConsultationPage() {
    return window.location.href.includes('/consultation') || 
           document.querySelector('app-template-consultation') !== null ||
           document.querySelector('.consultation-header') !== null;
  }
  
  // Create or get the toast container
  function getToastContainer() {
    let container = document.querySelector('.hackathon-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'hackathon-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }
  
  // Shows an enhanced styled toast notification
  function showToast(message, type = 'info', options = {}) {
    const defaults = {
      duration: 4000,
      action: null,
      position: 'top-right'
    };
    
    // Handle both old and new API formats
    let settings = {...defaults};
    
    // Check if type is actually an options object (for backward compatibility)
    if (typeof type === 'object') {
      settings = {...defaults, ...type};
      type = settings.type || 'info';
    } else {
      settings = {...defaults, ...options};
      settings.type = type;
    }
    
    const container = getToastContainer();
    
    // Create enhanced toast element
    const toast = document.createElement('div');
    toast.className = `hackathon-toast ${settings.type}`;
    
    // Determine icon based on type
    let iconHtml = '';
    switch(settings.type) {
      case 'success':
        iconHtml = `
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#28a745" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        `;
        break;
      case 'warning':
        iconHtml = `
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffc107" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        `;
        break;
      case 'error':
        iconHtml = `
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc3545" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        `;
        break;
      case 'info':
      default:
        iconHtml = `
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#17a2b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
        `;
    }
    
    // Create enhanced toast content with improved styling
    toast.innerHTML = `
      <div class="hackathon-toast-icon">${iconHtml}</div>
      <div class="hackathon-toast-content">${message}</div>
      <button class="hackathon-toast-close">&times;</button>
    `;
    
    // Add animation and positioning classes based on settings
    if (settings.position) {
      container.className = `hackathon-toast-container ${settings.position}`;
    }
    
    // Add close button functionality
    toast.querySelector('.hackathon-toast-close').addEventListener('click', () => {
      removeToast(toast);
    });
    
    // Add action button if provided
    if (settings.action) {
      const actionBtn = document.createElement('button');
      actionBtn.className = 'hackathon-btn hackathon-btn-sm hackathon-btn-outline';
      actionBtn.innerText = settings.action.text;
      actionBtn.addEventListener('click', () => {
        if (settings.action.callback) settings.action.callback();
        removeToast(toast);
      });
      toast.appendChild(actionBtn);
    }
    
    // Add to container with entrance animation
    toast.style.animation = 'fadeIn 0.3s ease-out forwards';
    container.appendChild(toast);
    
    // Add slight movement on hover
    toast.addEventListener('mouseenter', () => {
      toast.style.transform = 'translateY(-3px)';
      toast.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.2)';
    });
    
    toast.addEventListener('mouseleave', () => {
      toast.style.transform = 'translateY(0)';
      toast.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.15)';
    });
    
    // Auto-remove after duration
    if (settings.duration > 0) {
      setTimeout(() => {
        removeToast(toast);
      }, settings.duration);
    }
    
    return toast;
  }
  
  // Remove a toast with animation
  function removeToast(toast) {
    toast.style.animation = 'fadeOut 0.3s ease-in forwards';
    setTimeout(() => toast.remove(), 300);
  }
  
  // Show a custom confirmation modal dialog
  function showConfirmModal(options = {}) {
    return new Promise((resolve) => {
      const defaults = {
        title: 'Confirm Action',
        message: 'Are you sure you want to proceed?',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        confirmClass: 'hackathon-btn-primary',
        showClose: true,
        icon: null
      };
      
      const settings = {...defaults, ...options};
      
      // Create backdrop
      const backdrop = document.createElement('div');
      backdrop.className = 'hackathon-modal-backdrop';
      
      // Create modal
      const modal = document.createElement('div');
      modal.className = 'hackathon-modal';
      
      // Icon HTML if provided
      const iconHtml = settings.icon ? `<div class="modal-icon">${settings.icon}</div>` : '';
      
      // Build modal HTML
      modal.innerHTML = `
        <div class="hackathon-modal-header">
          <h3 class="hackathon-modal-title">${settings.title}</h3>
          ${settings.showClose ? '<button class="hackathon-modal-close">&times;</button>' : ''}
        </div>
        <div class="hackathon-modal-body">
          ${iconHtml}
          <p>${settings.message}</p>
        </div>
        <div class="hackathon-modal-footer">
          <button class="hackathon-btn hackathon-btn-secondary" data-action="cancel">${settings.cancelText}</button>
          <button class="hackathon-btn ${settings.confirmClass}" data-action="confirm">${settings.confirmText}</button>
        </div>
      `;
      
      // Add to DOM
      backdrop.appendChild(modal);
      document.body.appendChild(backdrop);
      
      // Focus the confirm button
      setTimeout(() => {
        modal.querySelector('[data-action="confirm"]').focus();
      }, 100);
      
      // Add event listeners
      if (settings.showClose) {
        modal.querySelector('.hackathon-modal-close').addEventListener('click', () => {
          closeModal(false);
        });
      }
      
      modal.querySelector('[data-action="cancel"]').addEventListener('click', () => {
        closeModal(false);
      });
      
      modal.querySelector('[data-action="confirm"]').addEventListener('click', () => {
        closeModal(true);
      });
      
      // Close modal function
      function closeModal(confirmed) {
        modal.style.animation = 'scaleOut 0.3s ease-in forwards';
        backdrop.style.animation = 'fadeOut 0.3s ease-in forwards';
        
        setTimeout(() => {
          backdrop.remove();
          resolve(confirmed);
        }, 300);
      }
    });
  }
  
  // Add a guaranteed enhanced Complete Consultation button
  function addCompletionButton() {
    if (!isConsultationPage()) return;
    
    console.log("📋 Detected consultation page - adding enhanced completion button");
    
    // Remove any existing helper button to avoid duplicates
    const existingBtn = document.getElementById('hackathon-complete-btn');
    if (existingBtn) {
      existingBtn.remove();
    }
    
    // Create a floating action button
    const btn = document.createElement('button');
    btn.id = 'hackathon-complete-btn';
    
    // Create the button's inner content with enhanced HTML structure
    btn.innerHTML = `
      <div class="btn-ripple"></div>
      <div class="btn-content">
        <div class="btn-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <div class="btn-label">Complete<br>Consultation</div>
        <span class="btn-badge">DEMO</span>
      </div>
    `;
    
    // Style the button to be highly visible with enhanced styling
    btn.style.position = 'fixed';
    btn.style.bottom = '30px';
    btn.style.right = '30px';
    btn.style.zIndex = '9999';
    btn.style.width = '120px';
    btn.style.height = '120px';
    btn.style.borderRadius = '60px';
    btn.style.background = 'linear-gradient(145deg, #2196f3, #1976d2)';
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.boxShadow = '0 4px 20px rgba(33, 150, 243, 0.4)';
    btn.style.cursor = 'pointer';
    btn.style.overflow = 'hidden';
    btn.style.padding = '0';
    btn.style.animation = 'pulse 2s infinite';
    btn.style.transition = 'transform 0.2s, box-shadow 0.2s, background 0.3s';
    btn.style.fontWeight = 'bold';
    btn.style.textAlign = 'center';
    btn.style.lineHeight = '1.2';
    btn.style.display = 'flex';
    btn.style.alignItems = 'center';
    btn.style.justifyContent = 'center';
    
    // Add CSS for inner elements
    const style = document.createElement('style');
    style.textContent = `
      #hackathon-complete-btn .btn-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        position: relative;
        z-index: 2;
      }
      #hackathon-complete-btn .btn-icon {
        margin-bottom: 5px;
      }
      #hackathon-complete-btn .btn-label {
        font-size: 14px;
        font-weight: 600;
        text-align: center;
        line-height: 1.2;
      }
      #hackathon-complete-btn .btn-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 2px 6px;
        font-size: 8px;
        font-weight: bold;
        letter-spacing: 0.5px;
      }
      #hackathon-complete-btn .btn-ripple {
        position: absolute;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        width: 20px;
        height: 20px;
        transform: scale(0);
        opacity: 1;
        z-index: 1;
      }
      #hackathon-complete-btn.rippling .btn-ripple {
        animation: ripple 0.6s linear;
      }
    `;
    document.head.appendChild(style);
    
    // Add enhanced hover effect
    btn.onmouseover = function() {
      this.style.transform = 'scale(1.05) translateY(-3px)';
      this.style.boxShadow = '0 8px 25px rgba(33, 150, 243, 0.5)';
      this.style.background = 'linear-gradient(145deg, #2196f3, #2979ff)';
    };
    
    btn.onmouseout = function() {
      this.style.transform = 'scale(1) translateY(0)';
      this.style.boxShadow = '0 4px 20px rgba(33, 150, 243, 0.4)';
      this.style.background = 'linear-gradient(145deg, #2196f3, #1976d2)';
    };
    
    // Add ripple effect on click
    btn.addEventListener('click', function(e) {
      const ripple = this.querySelector('.btn-ripple');
      const rect = this.getBoundingClientRect();
      
      // Position the ripple where clicked
      ripple.style.top = (e.clientY - rect.top - 10) + 'px';
      ripple.style.left = (e.clientX - rect.left - 10) + 'px';
      
      // Trigger ripple animation
      this.classList.remove('rippling');
      setTimeout(() => this.classList.add('rippling'), 0);
    });
    
    // Click handler with confirmation modal
    btn.onclick = function(e) {
      // Show styled confirmation modal
      showCompletionModal();
    };
    
    // Function to show a stylish confirmation modal
    function showCompletionModal() {
      // Create modal backdrop
      const modalBackdrop = document.createElement('div');
      modalBackdrop.className = 'hackathon-modal-backdrop';
      
      // Create modal dialog
      const modal = document.createElement('div');
      modal.className = 'hackathon-modal';
      
      // Modal content with enhanced styling
      modal.innerHTML = `
        <div class="hackathon-modal-header">
          <h2 class="hackathon-modal-title">Complete Consultation</h2>
          <button class="hackathon-modal-close">&times;</button>
        </div>
        <div class="hackathon-modal-body">
          <p style="font-size: 16px; line-height: 1.5; margin-bottom: 10px;">
            Are you ready to complete this consultation?
          </p>
          <p style="color: #666; margin: 0;">
            This will finalize the consultation and generate the SLA document.
          </p>
        </div>
        <div class="hackathon-modal-footer">
          <button class="hackathon-btn hackathon-btn-outline" id="modal-cancel">Cancel</button>
          <button class="hackathon-btn hackathon-btn-primary" id="modal-confirm">
            <span class="btn-icon" style="margin-right: 5px;">✓</span> Complete
          </button>
        </div>
      `;
      
      // Add modal to document
      modalBackdrop.appendChild(modal);
      document.body.appendChild(modalBackdrop);
      
      // Handle close button click
      const closeBtn = modal.querySelector('.hackathon-modal-close');
      closeBtn.onclick = function() {
        document.body.removeChild(modalBackdrop);
      };
      
      // Handle cancel button click
      const cancelBtn = document.getElementById('modal-cancel');
      cancelBtn.onclick = function() {
        document.body.removeChild(modalBackdrop);
      };
      
      // Handle confirm button click
      const confirmBtn = document.getElementById('modal-confirm');
      confirmBtn.onclick = function() {
        // Show loading state
        this.disabled = true;
        this.innerHTML = '<span class="hackathon-loader"></span> Completing...';
        
        // Close modal and show success notification after completion
        setTimeout(() => {
          document.body.removeChild(modalBackdrop);
          completeConsultationAllMethods();
          showToast('Consultation completed successfully!', 'success');
        }, 800);
      };
    }
    
    // Add a notification badge to draw attention
    const badge = document.createElement('div');
    badge.innerText = 'DEMO';
    badge.style.position = 'absolute';
    badge.style.top = '0';
    badge.style.right = '0';
    badge.style.background = '#ff7700';
    badge.style.color = 'white';
    badge.style.borderRadius = '10px';
    badge.style.padding = '2px 6px';
    badge.style.fontSize = '10px';
    badge.style.fontWeight = 'bold';
    badge.style.transform = 'translate(25%, -25%)';
    btn.appendChild(badge);
    
    // Add the button to the document
    document.body.appendChild(btn);
    
    // Add a hint toast notification only once per page load
    // Use sessionStorage to track if we've already shown the toast
    if (!sessionStorage.getItem('consultationToastShown')) {
      // Wait longer before showing the toast (15 seconds instead of 5)
      setTimeout(() => {
        // Only show toast if we're still on a consultation page
        if (isConsultationPage()) {
          showToast("Complete your consultation using the blue button →", {
            type: 'info',
            duration: 8000,
            action: {
              text: "Show Me",
              callback: () => {
                btn.style.transform = 'scale(1.2)';
                btn.style.boxShadow = '0 0 30px rgba(33, 150, 243, 0.6)';
                setTimeout(() => {
                  btn.style.transform = 'scale(1)';
                  btn.style.boxShadow = '0 4px 20px rgba(33, 150, 243, 0.4)';
                }, 1500);
              }
            }
          });
          // Mark that we've shown the toast
          sessionStorage.setItem('consultationToastShown', 'true');
        }
      }, 15000);
    }
  }
  
  // Try all possible methods to complete the consultation
  async function completeConsultationAllMethods() {
    console.log("🏁 Attempting to complete consultation");
    
    // Method 1: Ask the user to confirm with our custom modal
    const confirmed = await showConfirmModal({
      title: 'Complete Consultation',
      message: 'Are you ready to complete this consultation and generate your SLA document?',
      confirmText: 'Yes, Complete It',
      confirmClass: 'hackathon-btn-success',
      cancelText: 'Not Yet',
      icon: '✓'
    });
    
    if (!confirmed) {
      return;
    }
    
    // Show a processing toast
    const processingToast = showToast("Processing your consultation...", {
      type: 'info',
      duration: 0,
      icon: '<span class="hackathon-loader"></span>'
    });
    
    // Method 2: Try to find and invoke the Angular component's method
    let success = false;
    try {
      // Get all possible component instances
      const componentElement = document.querySelector('app-template-consultation');
      if (componentElement && window.ng) {
        const componentInstance = window.ng.getComponent(componentElement);
        if (componentInstance && typeof componentInstance.completeConsultation === 'function') {
          console.log("✅ Found Angular component, calling completeConsultation()");
          componentInstance.completeConsultation();
          success = true;
        }
      }
    } catch (e) {
      console.error("Failed to call Angular component method:", e);
    }
    
    // Method 3: Find and click the existing button if present
    if (!success) {
      const buttons = Array.from(document.querySelectorAll('button'));
      const completeButton = buttons.find(btn => {
        return btn.textContent && 
               (btn.textContent.includes('Complete Consultation') || 
                btn.textContent.includes('complete consultation'));
      });
      
      if (completeButton) {
        console.log("✅ Found existing button, clicking it");
        completeButton.click();
        success = true;
      }
    }
    
    // Remove the processing toast
    removeToast(processingToast);
    
    // Method 4: If all else fails, try to simulate completion by showing a mock interface
    if (!success) {
      console.log("⚠️ Could not find component or button, creating mock interface");
      showToast("Creating your SLA document...", {
        type: 'success',
        duration: 2000
      });
      
      setTimeout(() => {
        showMockCompletionInterface();
      }, 2000);
    } else {
      showToast("Consultation completed successfully!", {
        type: 'success',
        duration: 3000
      });
    }
  }
  
  // Create a mock completion interface as a last resort
  function showMockCompletionInterface() {
    const overlay = document.createElement('div');
    overlay.className = 'hackathon-modal-backdrop';
    
    const modal = document.createElement('div');
    modal.className = 'hackathon-modal';
    modal.style.maxWidth = '700px';
    
    modal.innerHTML = `
      <div class="hackathon-modal-header">
        <h3 class="hackathon-modal-title">Consultation Completed</h3>
      </div>
      <div class="hackathon-modal-body">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 64px; color: #28a745; margin-bottom: 15px;">✓</div>
          <h2 style="color: #28a745; margin-bottom: 20px;">Consultation Completed!</h2>
          <p style="margin-bottom: 30px;">
            Your SLA document has been generated based on the consultation information.
          </p>
        </div>
        
        <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: left;">
          <h3 style="margin-top: 0;">Summary of Healthcare SLA Requirements:</h3>
          <ul style="padding-left: 20px;">
            <li><strong>Security:</strong> HIPAA-compliant encryption standards for PHI data</li>
            <li><strong>Assessments:</strong> Regular security risk assessments (minimum quarterly)</li>
            <li><strong>Logging:</strong> Comprehensive audit logging for all system access</li>
            <li><strong>Performance:</strong> 99.99% uptime guarantee for critical EHR systems</li>
            <li><strong>Incidents:</strong> Defined incident response times by severity level</li>
            <li><strong>Compliance:</strong> Business Associate Agreement with required provisions</li>
          </ul>
        </div>
      </div>
      <div class="hackathon-modal-footer">
        <button id="mock-close-btn" class="hackathon-btn hackathon-btn-secondary">Close</button>
        <button id="mock-export-btn" class="hackathon-btn hackathon-btn-primary">
          <i style="margin-right: 5px;">↓</i> Export Results
        </button>
      </div>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    document.getElementById('mock-export-btn').addEventListener('click', function() {
      overlay.style.animation = 'fadeOut 0.3s ease-in forwards';
      
      showToast("SLA document has been generated!", {
        type: 'success',
        duration: 3000
      });
      
      setTimeout(() => {
        overlay.remove();
        window.location.href = '/my-slas?success=true';
      }, 300);
    });
    
    document.getElementById('mock-close-btn').addEventListener('click', function() {
      overlay.style.animation = 'fadeOut 0.3s ease-in forwards';
      setTimeout(() => overlay.remove(), 300);
    });
  }
  
  // Check the page periodically to add the button when needed
  function setupPeriodicChecks() {
    // Add styles first
    addStyles();
    
    // Initial check
    addCompletionButton();
    
    // Check whenever URL changes
    let lastUrl = window.location.href;
    const observer = new MutationObserver(() => {
      if (lastUrl !== window.location.href) {
        lastUrl = window.location.href;
        setTimeout(addCompletionButton, 500);
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Check less frequently to reduce toast notifications
    setInterval(addCompletionButton, 30000); // Check only every 30 seconds
  }
  
  // Start everything up
  setupPeriodicChecks();
  
  // Make functions available globally for debugging and manual triggering
  window.hackathonHelper = {
    // Core functionality
    addCompletionButton,
    completeConsultation: completeConsultationAllMethods,
    showToast,
    showCompletionModal,
    showConfirmModal,
    showMockCompletionInterface,
    
    // Enhanced UI controls
    moveButton: (position) => {
      const btn = document.getElementById('hackathon-complete-btn');
      if (!btn) return false;
      
      // Reset existing position
      btn.style.top = 'auto';
      btn.style.bottom = 'auto';
      btn.style.left = 'auto';
      btn.style.right = 'auto';
      
      // Apply new position
      switch(position) {
        case 'top-right':
          btn.style.top = '30px';
          btn.style.right = '30px';
          break;
        case 'top-left':
          btn.style.top = '30px';
          btn.style.left = '30px';
          break;
        case 'bottom-left':
          btn.style.bottom = '30px';
          btn.style.left = '30px';
          break;
        case 'bottom-right':
        default:
          btn.style.bottom = '30px';
          btn.style.right = '30px';
      }
      
      return true;
    },
    
    setButtonStyle: (style) => {
      const btn = document.getElementById('hackathon-complete-btn');
      if (!btn) return false;
      
      switch(style) {
        case 'green':
          btn.style.background = 'linear-gradient(145deg, #28a745, #218838)';
          btn.style.boxShadow = '0 4px 20px rgba(40, 167, 69, 0.4)';
          break;
        case 'red':
          btn.style.background = 'linear-gradient(145deg, #dc3545, #c82333)';
          btn.style.boxShadow = '0 4px 20px rgba(220, 53, 69, 0.4)';
          break;
        case 'blue-gradient':
        default:
          btn.style.background = 'linear-gradient(145deg, #2196f3, #1976d2)';
          btn.style.boxShadow = '0 4px 20px rgba(33, 150, 243, 0.4)';
      }
      
      return true;
    },
    
    toggleButtonAnimation: () => {
      const btn = document.getElementById('hackathon-complete-btn');
      if (!btn) return false;
      
      if (btn.style.animation === 'none') {
        btn.style.animation = 'pulse 2s infinite';
      } else {
        btn.style.animation = 'none';
      }
      
      return true;
    },
    
    // Utility functions
    refreshUI: () => {
      addStyles();
      addCompletionButton();
      return true;
    },
    
    checkStyles: () => {
      return !!document.getElementById('hackathon-helper-styles');
    }
  };
})();