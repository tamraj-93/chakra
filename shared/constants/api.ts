/**
 * Constants for API endpoints
 */
export const API_ENDPOINTS = {
  BASE_URL: 'http://localhost:8000',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
  },
  USERS: {
    BASE: '/users',
    ME: '/users/me',
  },
  CONSULTATION: {
    BASE: '/consultation',
    CHAT: '/consultation/chat',
    SESSIONS: '/consultation/sessions',
  },
  TEMPLATES: {
    BASE: '/templates',
    METRICS: '/templates/metrics',
  }
};

/**
 * Industry categories for SLA templates
 */
export const INDUSTRIES = [
  'E-commerce',
  'Healthcare',
  'Financial Services',
  'Manufacturing',
  'Information Technology',
  'Telecommunications',
  'Education',
  'Government',
  'Retail',
  'Energy',
];

/**
 * Service types
 */
export const SERVICE_TYPES = [
  'Web Application',
  'Mobile Application',
  'API Service',
  'Database Service',
  'Infrastructure',
  'Cloud Service',
  'Managed Service',
  'Support Service',
];

/**
 * SLA Metric categories
 */
export const METRIC_CATEGORIES = {
  AVAILABILITY: 'availability',
  PERFORMANCE: 'performance',
  SECURITY: 'security',
  SUPPORT: 'support',
};