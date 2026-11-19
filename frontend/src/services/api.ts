import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// Request interceptor: Attach JWT Bearer token if present
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("securemind_access_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Automated token refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry && typeof window !== "undefined") {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("securemind_refresh_token");

      if (refreshToken) {
        try {
          const resp = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          const newAccess = resp.data.access;
          localStorage.setItem("securemind_access_token", newAccess);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          }
          return apiClient(originalRequest);
        } catch (refreshErr) {
          // Token expired completely; clear tokens
          localStorage.removeItem("securemind_access_token");
          localStorage.removeItem("securemind_refresh_token");
        }
      }
    }
    return Promise.reject(error);
  }
);

// ==========================================
// API Helper Services
// ==========================================

export const api = {
  // Auth
  auth: {
    login: (credentials: { email: string; password: string }) =>
      apiClient.post("/auth/login/", credentials),
    register: (payload: any) => apiClient.post("/auth/register/", payload),
    me: () => apiClient.get("/auth/me/"),
    switchOrg: (organization_id: string) =>
      apiClient.post("/auth/switch-org/", { organization_id }),
  },

  // Assets
  assets: {
    list: () => apiClient.get("/assets/"),
    create: (payload: { name: string; base_url: string; domain?: string }) =>
      apiClient.post("/assets/", payload),
    createChallenge: (assetId: string, challenge_type: string) =>
      apiClient.post(`/assets/${assetId}/challenge/`, { challenge_type }),
    verify: (assetId: string, challengeId?: string) =>
      apiClient.post(`/assets/${assetId}/verify/`, { challenge_id: challengeId }),
    getScopeRules: (assetId: string) => apiClient.get(`/assets/${assetId}/scope_rules/`),
  },

  // Scans
  scans: {
    list: () => apiClient.get("/scans/"),
    create: (payload: { asset: string; scan_type: string; config_overrides?: any }) =>
      apiClient.post("/scans/", payload),
    approve: (scanId: string) => apiClient.post(`/scans/${scanId}/approve/`),
    cancel: (scanId: string) => apiClient.post(`/scans/${scanId}/cancel/`),
  },

  // Findings
  findings: {
    list: (params?: { severity?: string; verification_status?: string; scan?: string }) =>
      apiClient.get("/findings/", { params }),
    get: (findingId: string) => apiClient.get(`/findings/${findingId}/`),
  },

  // Remediation
  remediation: {
    list: () => apiClient.get("/remediation/"),
    updateStatus: (remediationId: string, status: string, notes?: string) =>
      apiClient.patch(`/remediation/${remediationId}/`, {
        status,
        developer_notes: notes,
      }),
  },

  // Reports
  reports: {
    list: () => apiClient.get("/reports/"),
    generate: (scanId: string, report_type: string = "technical_full") =>
      apiClient.post("/reports/", { scan: scanId, report_type }),
    downloadUrl: (reportId: string) => `${API_BASE_URL}/reports/${reportId}/download/`,
  },

  // AI Agent Orchestration Telemetry
  agents: {
    listExecutions: (params?: { scan?: string; agent_name?: string }) =>
      apiClient.get("/agents/executions/", { params }),
    listWorkflowStates: () => apiClient.get("/agents/workflow-states/"),
  },

  // Organizations & Team
  organizations: {
    list: () => apiClient.get("/organizations/"),
    getMembers: (orgId: string) => apiClient.get(`/organizations/${orgId}/members/`),
    inviteMember: (orgId: string, payload: { email: string; role: string }) =>
      apiClient.post(`/organizations/${orgId}/members/`, payload),
  },
};
