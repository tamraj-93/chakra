import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  template: `
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header bg-primary text-white">
              <h4 class="mb-0">Register</h4>
            </div>
            <div class="card-body">
              <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
                <div class="mb-3">
                  <label for="name" class="form-label">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="name" 
                    formControlName="name" 
                    placeholder="Enter your full name">
                  <div *ngIf="registerForm.get('name')?.touched && registerForm.get('name')?.invalid" class="text-danger">
                    <small *ngIf="registerForm.get('name')?.errors?.['required']">Name is required</small>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    formControlName="email" 
                    placeholder="Enter your email">
                  <div *ngIf="registerForm.get('email')?.touched && registerForm.get('email')?.invalid" class="text-danger">
                    <small *ngIf="registerForm.get('email')?.errors?.['required']">Email is required</small>
                    <small *ngIf="registerForm.get('email')?.errors?.['email']">Please enter a valid email</small>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    formControlName="password" 
                    placeholder="Enter your password">
                  <div *ngIf="registerForm.get('password')?.touched && registerForm.get('password')?.invalid" class="text-danger">
                    <small *ngIf="registerForm.get('password')?.errors?.['required']">Password is required</small>
                    <small *ngIf="registerForm.get('password')?.errors?.['minlength']">Password must be at least 6 characters</small>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="confirmPassword" 
                    formControlName="confirmPassword" 
                    placeholder="Confirm your password">
                  <div *ngIf="registerForm.get('confirmPassword')?.touched && registerForm.get('confirmPassword')?.invalid" class="text-danger">
                    <small *ngIf="registerForm.get('confirmPassword')?.errors?.['required']">Confirm Password is required</small>
                  </div>
                  <div *ngIf="registerForm.errors?.['passwordMismatch'] && registerForm.get('confirmPassword')?.touched" class="text-danger">
                    <small>Passwords do not match</small>
                  </div>
                </div>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-primary" 
                    [disabled]="registerForm.invalid || isLoading">
                    <span *ngIf="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Register
                  </button>
                </div>
                
                <div *ngIf="errorMessage" class="alert alert-danger mt-3">
                  {{ errorMessage }}
                </div>
              </form>
              
              <div class="mt-3 text-center">
                <p>Already have an account? <a routerLink="/login">Login</a></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class RegisterComponent {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  
  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.formBuilder.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }
  
  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password')?.value;
    const confirmPassword = form.get('confirmPassword')?.value;
    
    return password === confirmPassword ? null : { passwordMismatch: true };
  }
  
  onSubmit(): void {
    if (this.registerForm.invalid) {
      return;
    }
    
    this.isLoading = true;
    this.errorMessage = '';
    
    const { email, password } = this.registerForm.value;
    
    this.authService.register(email, password).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/login'], { 
          queryParams: { registered: true } 
        });
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.error?.detail || 'Registration failed. Please try again.';
      }
    });
  }
}
