/**
 * Configuration for API endpoints
 * In development: uses Vite proxy (relative URLs)
 * In production: uses absolute URLs from environment variable
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Helper function to build API URLs
 * @param {string} path - API path (e.g., '/api/auth/login')
 * @returns {string} - Complete URL
 */
export function getApiUrl(path) {
  // In production, VITE_API_URL should be set (e.g., 'https://backend.onrender.com')
  // In development, it's empty and uses Vite's proxy
  return `${API_BASE_URL}${path}`;
}
