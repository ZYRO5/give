/**
 * Frontend Utilities
 */

/**
 * Format a number as currency
 */
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  });
  return formatter.format(amount);
};

/**
 * Format a date string
 */
export const formatDate = (date: string | Date, format: string = 'MMM DD, YYYY'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Calculate time difference
 */
export const calculateTimeAgo = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const seconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  const intervals: { [key: string]: number } = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
  };

  for (const [name, value] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / value);
    if (interval >= 1) {
      return `${interval} ${name}${interval > 1 ? 's' : ''} ago`;
    }
  }

  return 'Just now';
};

/**
 * Calculate percentage
 */
export const calculatePercentage = (value: number, total: number): number => {
  return total === 0 ? 0 : Math.round((value / total) * 100);
};

/**
 * Truncate text
 */
export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Capitalize first letter
 */
export const capitalize = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1);
};

/**
 * Format phone number
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.substring(0, 3)}) ${cleaned.substring(3, 6)}-${cleaned.substring(6)}`;
  }
  return phone;
};

/**
 * Validate email
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate URL
 */
export const validateURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Generate random ID
 */
export const generateRandomId = (length: number = 10): string => {
  return Math.random().toString(36).substring(2, 2 + length);
};

/**
 * Debounce function
 */
export const debounce = (func: Function, wait: number) => {
  let timeout: NodeJS.Timeout;
  return (...args: any[]) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle function
 */
export const throttle = (func: Function, limit: number) => {
  let inThrottle: boolean;
  return (...args: any[]) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Sort array of objects by key
 */
export const sortByKey = (array: any[], key: string, ascending: boolean = true): any[] => {
  return [...array].sort((a, b) => {
    if (a[key] < b[key]) return ascending ? -1 : 1;
    if (a[key] > b[key]) return ascending ? 1 : -1;
    return 0;
  });
};

/**
 * Filter array of objects by key-value
 */
export const filterByKey = (array: any[], key: string, value: any): any[] => {
  return array.filter((item) => item[key] === value);
};

/**
 * Group array by key
 */
export const groupByKey = (array: any[], key: string): { [key: string]: any[] } => {
  return array.reduce((result, item) => {
    const group = item[key];
    if (!result[group]) {
      result[group] = [];
    }
    result[group].push(item);
    return result;
  }, {});
};

/**
 * Local storage utilities
 */
export const storage = {
  set: (key: string, value: any) => {
    localStorage.setItem(key, JSON.stringify(value));
  },
  get: (key: string) => {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  },
  remove: (key: string) => {
    localStorage.removeItem(key);
  },
  clear: () => {
    localStorage.clear();
  },
};

/**
 * Copy to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
};

/**
 * Download file
 */
export const downloadFile = (data: any, filename: string, format: string = 'json') => {
  let content = '';
  if (format === 'json') {
    content = JSON.stringify(data, null, 2);
  } else if (format === 'csv') {
    content = data;
  }

  const element = document.createElement('a');
  element.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(content)}`);
  element.setAttribute('download', filename);
  element.style.display = 'none';
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
};

/**
 * Parse query parameters
 */
export const parseQueryParams = (query: string): { [key: string]: string } => {
  const params: { [key: string]: string } = {};
  const searchParams = new URLSearchParams(query);
  searchParams.forEach((value, key) => {
    params[key] = value;
  });
  return params;
};

/**
 * Build query string
 */
export const buildQueryString = (params: { [key: string]: any }): string => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      query.append(key, String(value));
    }
  });
  return query.toString();
};

/**
 * Check if value is empty
 */
export const isEmpty = (value: any): boolean => {
  return (
    value === null ||
    value === undefined ||
    value === '' ||
    (Array.isArray(value) && value.length === 0) ||
    (typeof value === 'object' && Object.keys(value).length === 0)
  );
};

/**
 * Deep clone object
 */
export const deepClone = (obj: any): any => {
  return JSON.parse(JSON.stringify(obj));
};
