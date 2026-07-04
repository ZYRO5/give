import apiClient from './api';

export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  created_at: string;
}

export interface Campaign {
  id: string;
  title: string;
  description: string;
  target_amount: number;
  raised_amount: number;
  status: string;
  created_by: string;
  created_at: string;
}

export interface Donation {
  id: string;
  amount: number;
  status: string;
  donor_id: string;
  campaign_id: string;
  created_at: string;
}

export interface Donor {
  id: string;
  user_id: string;
  total_donated: number;
  donation_count: number;
  status: string;
}

// User endpoints
export const userService = {
  register: (data: any) => apiClient.post('/users/register', data),
  getUser: (id: string) => apiClient.get(`/users/${id}`),
  listUsers: (skip: number = 0, limit: number = 10) =>
    apiClient.get('/users', { params: { skip, limit } }),
  updateUser: (id: string, data: any) => apiClient.put(`/users/${id}`, data),
  deleteUser: (id: string) => apiClient.delete(`/users/${id}`),
  getUserProfile: (id: string) => apiClient.get(`/users/${id}/profile`),
  changePassword: (id: string, oldPassword: string, newPassword: string) =>
    apiClient.post(`/users/${id}/change-password`, { oldPassword, newPassword }),
  verifyEmail: (id: string, token: string) =>
    apiClient.post(`/users/${id}/verify-email`, { token }),
  updatePreferences: (id: string, preferences: any) =>
    apiClient.post(`/users/${id}/preferences`, preferences),
  getNotifications: (id: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/users/${id}/notifications`, { params: { skip, limit } }),
  markNotificationAsRead: (userId: string, notificationId: string) =>
    apiClient.post(`/users/${userId}/notifications/${notificationId}/read`),
  getActivityLog: (id: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/users/${id}/activity-log`, { params: { skip, limit } }),
};

// Campaign endpoints
export const campaignService = {
  createCampaign: (data: any) => apiClient.post('/campaigns', data),
  getCampaign: (id: string) => apiClient.get(`/campaigns/${id}`),
  listCampaigns: (skip: number = 0, limit: number = 10, status?: string) =>
    apiClient.get('/campaigns', { params: { skip, limit, status_filter: status } }),
  updateCampaign: (id: string, data: any) => apiClient.put(`/campaigns/${id}`, data),
  deleteCampaign: (id: string) => apiClient.delete(`/campaigns/${id}`),
  getCampaignAnalytics: (id: string) => apiClient.get(`/campaigns/${id}/analytics`),
  shareCampaign: (id: string) => apiClient.post(`/campaigns/${id}/share`),
  createMilestone: (campaignId: string, data: any) =>
    apiClient.post(`/campaigns/${campaignId}/milestones`, data),
  getMilestones: (campaignId: string) => apiClient.get(`/campaigns/${campaignId}/milestones`),
  createUpdate: (campaignId: string, data: any) =>
    apiClient.post(`/campaigns/${campaignId}/updates`, data),
  getCampaignUpdates: (campaignId: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/campaigns/${campaignId}/updates`, { params: { skip, limit } }),
  addComment: (campaignId: string, data: any) =>
    apiClient.post(`/campaigns/${campaignId}/comments`, data),
  getComments: (campaignId: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/campaigns/${campaignId}/comments`, { params: { skip, limit } }),
  searchCampaigns: (query: string, skip: number = 0, limit: number = 10) =>
    apiClient.get('/campaigns/search', { params: { query, skip, limit } }),
};

// Donation endpoints
export const donationService = {
  createDonation: (data: any) => apiClient.post('/donations', data),
  getDonation: (id: string) => apiClient.get(`/donations/${id}`),
  listDonations: (skip: number = 0, limit: number = 10) =>
    apiClient.get('/donations', { params: { skip, limit } }),
  updateDonation: (id: string, data: any) => apiClient.put(`/donations/${id}`, data),
  confirmDonation: (id: string) => apiClient.post(`/donations/${id}/confirm`),
  refundDonation: (id: string, reason?: string) =>
    apiClient.post(`/donations/${id}/refund`, { reason }),
  getDonationReceipt: (id: string) => apiClient.get(`/donations/${id}/receipt`),
  sendReceiptEmail: (id: string) => apiClient.post(`/donations/${id}/send-receipt`),
  sendThankYouEmail: (id: string) => apiClient.post(`/donations/${id}/send-thank-you`),
  getCampaignDonations: (campaignId: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/donations/campaign/${campaignId}/donations`, { params: { skip, limit } }),
  getDonorDonations: (donorId: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/donations/donor/${donorId}/donations`, { params: { skip, limit } }),
  getDonationsSummary: () => apiClient.get('/donations/analytics/summary'),
};

// Donor endpoints
export const donorService = {
  createDonor: (data: any) => apiClient.post('/donors', data),
  getDonor: (id: string) => apiClient.get(`/donors/${id}`),
  listDonors: (skip: number = 0, limit: number = 10) =>
    apiClient.get('/donors', { params: { skip, limit } }),
  updateDonor: (id: string, data: any) => apiClient.put(`/donors/${id}`, data),
  deleteDonor: (id: string) => apiClient.delete(`/donors/${id}`),
  getDonorDonations: (id: string, skip: number = 0, limit: number = 10) =>
    apiClient.get(`/donors/${id}/donations`, { params: { skip, limit } }),
  getDonorStatistics: (id: string) => apiClient.get(`/donors/${id}/statistics`),
  generateTaxCertificate: (id: string, year: number) =>
    apiClient.post(`/donors/${id}/tax-certificate`, { year }),
  getDonorInsights: (id: string) => apiClient.get(`/donors/${id}/insights`),
  sendThankYouMessage: (id: string) => apiClient.post(`/donors/${id}/send-thank-you`),
  getDonorImpactSummary: (id: string) => apiClient.get(`/donors/${id}/impact-summary`),
  searchDonors: (query: string, skip: number = 0, limit: number = 10) =>
    apiClient.get('/donors/search', { params: { query, skip, limit } }),
};

// Report endpoints
export const reportService = {
  getDashboardSummary: () => apiClient.get('/reports/dashboard/summary'),
  getDonorsReport: (startDate?: string, endDate?: string) =>
    apiClient.get('/reports/donors/report', { params: { start_date: startDate, end_date: endDate } }),
  getCampaignsReport: (startDate?: string, endDate?: string) =>
    apiClient.get('/reports/campaigns/report', { params: { start_date: startDate, end_date: endDate } }),
  getDonationsReport: (startDate?: string, endDate?: string) =>
    apiClient.get('/reports/donations/report', { params: { start_date: startDate, end_date: endDate } }),
  getFinancialSummary: () => apiClient.get('/reports/financial/summary'),
  getDemographicsReport: () => apiClient.get('/reports/demographics/report'),
  getCategoryReport: () => apiClient.get('/reports/category/report'),
  getGrowthReport: (months: number = 12) =>
    apiClient.get('/reports/growth/report', { params: { months } }),
  generateMonthlyReport: (year: number, month: number) =>
    apiClient.post('/reports/generate/monthly', { year, month }),
  exportReportCSV: (type: string) =>
    apiClient.get('/reports/export/csv', { params: { report_type: type } }),
};

// Auth endpoints
export const authService = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  refreshToken: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
