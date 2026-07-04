/**
 * API Error Handling
 */

export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Handle API errors
 */
export const handleAPIError = (error: any): APIError => {
  if (error.response) {
    const { status, data } = error.response;
    return new APIError(
      status,
      data?.code || 'UNKNOWN_ERROR',
      data?.message || error.message,
      data?.details
    );
  }

  if (error.request) {
    return new APIError(0, 'NO_RESPONSE', 'No response from server');
  }

  return new APIError(500, 'ERROR', error.message);
};

/**
 * Retry logic for failed requests
 */
export const retryRequest = async (
  fn: () => Promise<any>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<any> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise((resolve) => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};

/**
 * Timeout wrapper
 */
export const withTimeout = async (
  promise: Promise<any>,
  timeoutMs: number = 10000
): Promise<any> => {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Request timeout')), timeoutMs)
  );
  return Promise.race([promise, timeout]);
};

/**
 * Form validation
 */
export const validateForm = (data: any, rules: { [key: string]: any }): { [key: string]: string } => {
  const errors: { [key: string]: string } = {};

  for (const field in rules) {
    const value = data[field];
    const fieldRules = rules[field];

    // Required
    if (fieldRules.required && !value) {
      errors[field] = `${field} is required`;
      continue;
    }

    // Min length
    if (fieldRules.minLength && value?.length < fieldRules.minLength) {
      errors[field] = `${field} must be at least ${fieldRules.minLength} characters`;
    }

    // Max length
    if (fieldRules.maxLength && value?.length > fieldRules.maxLength) {
      errors[field] = `${field} must not exceed ${fieldRules.maxLength} characters`;
    }

    // Email
    if (fieldRules.email && !validateEmail(value)) {
      errors[field] = `${field} must be a valid email`;
    }

    // Pattern
    if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
      errors[field] = `${field} is invalid`;
    }

    // Custom validator
    if (fieldRules.custom) {
      const customError = fieldRules.custom(value);
      if (customError) {
        errors[field] = customError;
      }
    }
  }

  return errors;
};

/**
 * Email validation
 */
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Pagination utilities
 */
export const getPaginationInfo = (
  totalItems: number,
  pageSize: number = 10
) => {
  return {
    totalPages: Math.ceil(totalItems / pageSize),
    hasNextPage: (page: number) => page < Math.ceil(totalItems / pageSize),
    hasPreviousPage: (page: number) => page > 1,
  };
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Analytics tracking
 */
export const trackEvent = (eventName: string, eventData?: any) => {
  // TODO: Implement analytics tracking
  console.log(`[Analytics] ${eventName}`, eventData);
};

/**
 * Performance monitoring
 */
export const measurePerformance = async (
  name: string,
  fn: () => Promise<any>
): Promise<any> => {
  const start = performance.now();
  try {
    const result = await fn();
    const duration = performance.now() - start;
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[Performance] ${name}: ${duration.toFixed(2)}ms (ERROR)`);
    throw error;
  }
};
