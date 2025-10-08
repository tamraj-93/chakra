import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  template: `
    <div class="jumbotron bg-light rounded-3 p-5 mb-4">
      <h1 class="display-4">Welcome to Chakra</h1>
      <p class="lead">
        Your AI assistant for Service Level Management (SLM) that helps create, manage,
        and optimize your Service Level Agreements (SLAs).
      </p>
      <hr class="my-4">
      <p>
        Start a consultation to discover the right SLAs for your service or
        generate SLA templates based on industry best practices.
      </p>
      <div class="d-flex gap-3">
        <a class="btn btn-primary btn-lg" routerLink="/consultation">
          Start Consultation
        </a>
        <a class="btn btn-info btn-lg" routerLink="/templates">
          Template Consultations
        </a>
        <a class="btn btn-secondary btn-lg" routerLink="/template-generator">
          Generate SLA Template
        </a>
      </div>
    </div>
    
    <div class="row">
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body">
            <h5 class="card-title">SLA Discovery</h5>
            <p class="card-text">
              Chat with our AI assistant to understand which SLAs are right for your business.
            </p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body">
            <h5 class="card-title">Template Generation</h5>
            <p class="card-text">
              Create customized SLA documents based on industry best practices.
            </p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body">
            <h5 class="card-title">Performance Analysis</h5>
            <p class="card-text">
              Analyze SLA performance and get recommendations for improvements.
            </p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class HomeComponent {
  constructor() {}
}