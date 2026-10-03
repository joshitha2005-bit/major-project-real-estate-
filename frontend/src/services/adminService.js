import api from './api';

export const adminService = {
  // 1. Admin Authentication
  login: async (identifier, password) => {
    const response = await api.post('/admin/login', {
      identifier: identifier.trim(),
      password
    });
    if (response.data?.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('admin_token', response.data.access_token);
      localStorage.setItem('admin_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
  },

  getCurrentAdmin: () => {
    const raw = localStorage.getItem('admin_user');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('admin_token') || localStorage.getItem('token');
    const user = adminService.getCurrentAdmin();
    return Boolean(token && user && user.role === 'ADMIN');
  },

  // 2. Dashboard KPIs
  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  // 3. Properties Management
  getProperties: async (params = {}) => {
    const response = await api.get('/admin/properties', { params });
    return response.data;
  },

  getPropertyDetails: async (propertyId) => {
    const response = await api.get(`/admin/properties/${propertyId}`);
    return response.data;
  },

  toggleVisibility: async (propertyId, visibility_status) => {
    const response = await api.patch(`/admin/properties/${propertyId}/visibility`, {
      visibility_status
    });
    return response.data;
  },

  updateOwnerContact: async (propertyId, data) => {
    const response = await api.patch(`/admin/properties/${propertyId}/owner-contact`, data);
    return response.data;
  },

  // 4. Leads Management
  getLeads: async (params = {}) => {
    const response = await api.get('/admin/leads', { params });
    return response.data;
  },

  getLeadDetails: async (leadId) => {
    const response = await api.get(`/admin/leads/${leadId}`);
    return response.data;
  },

  updateLead: async (leadId, data) => {
    const response = await api.patch(`/admin/leads/${leadId}`, data);
    return response.data;
  },

  approveLead: async (leadId) => {
    const response = await api.post(`/admin/leads/${leadId}/approve`);
    return response.data;
  },

  rejectLead: async (leadId) => {
    const response = await api.post(`/admin/leads/${leadId}/reject`);
    return response.data;
  },

  markLeadSpam: async (leadId) => {
    const response = await api.post(`/admin/leads/${leadId}/mark-spam`);
    return response.data;
  },

  sendLeadToOwner: async (leadId) => {
    const response = await api.post(`/admin/leads/${leadId}/send-owner`);
    return response.data;
  },

  downloadLeadPdf: async (leadId, leadCode = 'Report') => {
    const response = await api.get(`/admin/leads/${leadId}/report-pdf`, {
      responseType: 'blob'
    });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `AI_Property_Lead_Report_${leadCode}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    return true;
  },

  // 5. Site Visits
  getSiteVisits: async (params = {}) => {
    const response = await api.get('/admin/site-visits', { params });
    return response.data;
  },

  updateSiteVisit: async (visitId, data) => {
    const response = await api.patch(`/admin/site-visits/${visitId}`, data);
    return response.data;
  },

  // 5b. Subscriptions
  getSubscriptions: async () => {
    const response = await api.get('/admin/subscriptions');
    return response.data;
  },

  // 6. Audit Logs
  getAuditLogs: async (limit = 50) => {
    const response = await api.get('/admin/audit-logs', { params: { limit } });
    return response.data;
  }
};

export default adminService;
