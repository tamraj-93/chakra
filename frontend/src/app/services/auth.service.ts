import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

// Define interfaces locally
interface User {
  id: number;
  email: string;
  name?: string;
  isActive: boolean;
  createdAt: string;
}

interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUser: User | null = null;

  constructor(private http: HttpClient) {
    // Check if user is already logged in
    const userData = localStorage.getItem('user');
    if (userData) {
      this.currentUser = JSON.parse(userData);
    }
  }

  /**
   * Login user with email and password
   */
  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap(response => {
          this.storeUserData(response);
        })
      );
  }

  /**
   * Register a new user
   */
  register(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/register`, { email, password })
      .pipe(
        tap(response => {
          this.storeUserData(response);
        })
      );
  }

  /**
   * Logout the current user
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.currentUser = null;
  }

  /**
   * Get the current user information
   */
  getCurrentUser(): User | null {
    return this.currentUser;
  }

  /**
   * Check if user is logged in
   */
  isLoggedIn(): boolean {
    return !!this.currentUser;
  }

  /**
   * Get the authentication token
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Store user data in local storage
   */
  private storeUserData(response: AuthResponse): void {
    localStorage.setItem('token', response.accessToken);
    localStorage.setItem('user', JSON.stringify(response.user));
    this.currentUser = response.user;
  }
}