import axios from 'axios';

const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  }
  return 'http://localhost:8000';
};

const API_BASE = import.meta.env.VITE_API_URL || getApiBaseUrl();

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  me: () => api.get('/api/auth/me'),
};

// ── System ────────────────────────────────────────────
export const systemApi = {
  health: () => api.get('/api/health'),
  stubsStatus: () => api.get('/api/stubs/status'),
};

// ── Land Parcels ──────────────────────────────────────
export const parcelsApi = {
  list: (district?: string) =>
    api.get('/api/land-parcels', { params: { district, limit: 100 } }),
  get: (id: string) => api.get(`/api/land-parcels/${id}`),
};

// ── Developers ─────────────────────────────────────────
export const developersApi = {
  list: () => api.get('/api/developers'),
};

// ── Proposals ─────────────────────────────────────────
export const proposalsApi = {
  list: (params?: Record<string, string>) =>
    api.get('/api/proposals', { params }),
  get: (id: string) => api.get(`/api/proposals/${id}`),
  create: (data: Record<string, unknown>) => api.post('/api/proposals', data),
  analyze: (id: string) => api.post(`/api/proposals/${id}/analyze`),
  analysisStatus: (id: string) => api.get(`/api/proposals/${id}/analysis-status`),
  decision: (id: string, action: string, notes?: string) =>
    api.patch(`/api/proposals/${id}/decision`, { action, notes }),
  delete: (id: string) => api.delete(`/api/proposals/${id}`),
  auditLog: (id: string) => api.get(`/api/proposals/${id}/audit-log`),
  reportUrl: (id: string) => `${API_BASE}/api/proposals/${id}/report`,
};

// ── Dashboard ─────────────────────────────────────────
export const dashboardApi = {
  summary: () => api.get('/api/dashboard/summary'),
  districtMap: () => api.get('/api/dashboard/district-map'),
  conflictAlerts: () => api.get('/api/dashboard/conflict-alerts'),
  rtgsStatus: () => api.get('/api/dashboard/rtgs-status'),
  officerScores: (limit?: number) => api.get('/api/dashboard/officer-scores', { params: { limit: limit || 10 } }),
  developerTracking: () => api.get('/api/dashboard/developer-tracking'),
};

// ── Users ─────────────────────────────────────────────
export const usersApi = {
  list: () => api.get('/api/users'),
  get: (id: string) => api.get(`/api/users/${id}`),
  create: (data: Record<string, unknown>) => api.post('/api/users', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/api/users/${id}`, data),
  deactivate: (id: string) => api.delete(`/api/users/${id}`),
};

// ── Recommendations ───────────────────────────────────
export const recommendationsApi = {
  sites: (projectType: string, capacityMw: number, districts: string[]) =>
    api.get('/api/recommendations/sites', {
      params: { project_type: projectType, capacity_mw: capacityMw, districts: districts.join(',') },
    }),
  developers: (parcelId: string) =>
    api.get('/api/recommendations/developers', { params: { parcel_id: parcelId } }),
  policyInsights: () => api.get('/api/recommendations/policy-insights'),
};

// ── Predictions ───────────────────────────────────────
export const predictionsApi = {
  conflicts: (parcelId: string) =>
    api.get('/api/predictions/conflicts', { params: { parcel_id: parcelId } }),
  gridCongestion: (district: string) =>
    api.get('/api/predictions/grid-congestion', { params: { district } }),
  environmentalRisk: (parcelId: string) =>
    api.get('/api/predictions/environmental-risk', { params: { parcel_id: parcelId } }),
  demandSupplyGap: () => api.get('/api/predictions/demand-supply-gap'),
};
