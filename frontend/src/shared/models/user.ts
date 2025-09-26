/**
 * Defines the structure of a User object
 */
export interface User {
  id: number;
  email: string;
  isActive: boolean;
}

/**
 * Data required to create a new user
 */
export interface UserCreate {
  email: string;
  password: string;
}

/**
 * User authentication response
 */
export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}