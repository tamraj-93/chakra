import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  template: `
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand" routerLink="/">Chakra</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <a class="nav-link" routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Home</a>
            </li>
            <li class="nav-item" *ngIf="isLoggedIn">
              <a class="nav-link" routerLink="/consultation" routerLinkActive="active">Consultation</a>
            </li>
            <li class="nav-item" *ngIf="isLoggedIn">
              <a class="nav-link" routerLink="/template-generator" routerLinkActive="active">Template Generator</a>
            </li>
            <li class="nav-item" *ngIf="isLoggedIn">
              <a class="nav-link" routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item" *ngIf="!isLoggedIn">
              <a class="nav-link" routerLink="/login" routerLinkActive="active">Login</a>
            </li>
            <li class="nav-item" *ngIf="!isLoggedIn">
              <a class="nav-link" routerLink="/register" routerLinkActive="active">Register</a>
            </li>
            <li class="nav-item" *ngIf="isLoggedIn">
              <a class="nav-link" style="cursor: pointer;" (click)="logout()">Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  `,
  styles: []
})
export class NavbarComponent {
  get isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}