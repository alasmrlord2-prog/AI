/**
 * API Client Library
 * Centralized API client functions for all backend services
 */

// Get API base URL
export function getApiUrl(): string {
  if (typeof window !== "undefined") {
    // Client-side: use window location or environment variable
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    return backendUrl;
  }
  // Server-side: use environment variable or default
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
}

// Error types for better error handling
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NetworkError";
  }
}

export class TimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TimeoutError";
  }
}

// Generic API request function with enhanced error handling
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {},
  timeout: number = 10000
): Promise<any> {
  const url = `${getApiUrl()}${endpoint}`;
  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  // Merge existing headers
  if (options.headers) {
    if (options.headers instanceof Headers) {
      options.headers.forEach((value, key) => {
        headers[key] = value;
      });
    } else if (Array.isArray(options.headers)) {
      options.headers.forEach(([key, value]) => {
        headers[key] = value;
      });
    } else {
      Object.assign(headers, options.headers);
    }
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle different response statuses
    if (!response.ok) {
      let errorData: any;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }

      // Handle specific status codes
      if (response.status === 401) {
        // Unauthorized - clear token and redirect to login
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth_token");
          // Don't redirect if already on login page
          if (!window.location.pathname.includes("/login")) {
            window.location.href = "/login";
          }
        }
      }

      throw new APIError(
        errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    // Handle empty responses
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      const text = await response.text();
      if (!text) {
        return null;
      }
      return JSON.parse(text);
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(timeoutId);
    
    // Handle different error types
    if (error.name === "AbortError") {
      throw new TimeoutError(`Request timeout after ${timeout}ms`);
    }
    
    if (error instanceof APIError) {
      throw error;
    }
    
    // Network errors
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new NetworkError("Network error. Please check your connection.");
    }
    
    // Re-throw known errors
    if (error instanceof APIError || error instanceof NetworkError || error instanceof TimeoutError) {
      throw error;
    }
    
    // Wrap unknown errors
    throw new Error(error.message || "An unexpected error occurred");
  }
}

// Identity API Client
export const identityApi = {
  // Authentication
  login: async (email: string, password: string) => {
    return apiRequest("/api/identity/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  // Users
  listUsers: async (limit: number = 100, offset: number = 0) => {
    return apiRequest(`/api/identity/users?limit=${limit}&offset=${offset}`);
  },

  getUser: async (userId: string) => {
    return apiRequest(`/api/identity/users/${userId}`);
  },

  getUsersCount: async () => {
    return apiRequest("/api/identity/users/count");
  },

  // Sessions
  getSessions: async (user_id?: string, active_only: boolean = false) => {
    const params = new URLSearchParams();
    if (user_id) params.append("user_id", user_id);
    if (active_only) params.append("active_only", "true");
    return apiRequest(`/api/identity/sessions?${params.toString()}`);
  },

  revokeSession: async (sessionId: string) => {
    return apiRequest(`/api/identity/sessions/${sessionId}`, {
      method: "DELETE",
    });
  },

  // API Tokens
  listApiTokens: async (tenant_id?: string) => {
    const params = tenant_id ? `?tenant_id=${tenant_id}` : "";
    return apiRequest(`/api/identity/api-tokens${params}`);
  },

  getApiToken: async (tokenId: string) => {
    return apiRequest(`/api/identity/api-tokens/${tokenId}`);
  },

  createApiToken: async (tokenData: {
    name: string;
    tenant_id?: string;
    scopes?: string[];
    expires_at?: string;
  }) => {
    return apiRequest("/api/identity/api-tokens", {
      method: "POST",
      body: JSON.stringify(tokenData),
    });
  },

  revokeApiToken: async (tokenId: string) => {
    return apiRequest(`/api/identity/api-tokens/${tokenId}`, {
      method: "DELETE",
    });
  },

  // Tenants
  listTenants: async () => {
    return apiRequest("/api/identity/tenants");
  },

  getTenant: async (tenantId: string) => {
    return apiRequest(`/api/identity/tenants/${tenantId}`);
  },

  createTenant: async (tenantData: {
    name: string;
    type: string;
    contact_email?: string;
    contact_phone?: string;
  }) => {
    return apiRequest("/api/identity/tenants", {
      method: "POST",
      body: JSON.stringify(tenantData),
    });
  },

  updateTenant: async (tenantId: string, tenantData: any) => {
    return apiRequest(`/api/identity/tenants/${tenantId}`, {
      method: "PUT",
      body: JSON.stringify(tenantData),
    });
  },

  getTenantUsers: async (tenantId: string) => {
    return apiRequest(`/api/identity/tenants/${tenantId}/users`);
  },

  addUserToTenant: async (tenantId: string, userId: string, role: string = "member") => {
    return apiRequest(`/api/identity/tenants/${tenantId}/users`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId, role }),
    });
  },
};

// Audit API Client
export const auditApi = {
  getAuditLogs: async (params: { limit?: number; offset?: number; user_id?: string; tenant_id?: string; action?: string; status?: string }) => {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.offset) queryParams.append("offset", params.offset.toString());
    if (params.user_id) queryParams.append("user_id", params.user_id);
    if (params.tenant_id) queryParams.append("tenant_id", params.tenant_id);
    if (params.action) queryParams.append("action", params.action);
    if (params.status) queryParams.append("status", params.status);
    
    const query = queryParams.toString();
    return apiRequest(`/api/audit/logs${query ? `?${query}` : ""}`);
  },

  getAuditLog: async (logId: string) => {
    return apiRequest(`/api/audit/logs/${logId}`);
  },

  createAuditLog: async (logData: {
    action: string;
    user_id?: string;
    tenant_id?: string;
    resource_type?: string;
    resource_id?: string;
    status?: string;
    metadata?: any;
  }) => {
    return apiRequest("/api/audit/logs", {
      method: "POST",
      body: JSON.stringify(logData),
    });
  },

  // Login Logs
  getLoginLogs: async (params: { limit?: number; offset?: number; email?: string; status?: string }) => {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.offset) queryParams.append("offset", params.offset.toString());
    if (params.email) queryParams.append("email", params.email);
    if (params.status) queryParams.append("status", params.status);
    
    const query = queryParams.toString();
    return apiRequest(`/api/audit/login-logs${query ? `?${query}` : ""}`);
  },
};

// CRM API Client
export const crmApi = {
  // Tenants
  listTenants: async (limit: number = 100, offset: number = 0) => {
    return apiRequest(`/api/crm/tenants?limit=${limit}&offset=${offset}`);
  },

  getTenant: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/dashboard`);
  },

  createTenant: async (tenantData: {
    name: string;
    type: string;
    contact_email?: string;
    contact_phone?: string;
  }) => {
    return apiRequest("/api/crm/tenants", {
      method: "POST",
      body: JSON.stringify(tenantData),
    });
  },

  updateTenant: async (tenantId: string, tenantData: any) => {
    return apiRequest(`/api/crm/tenants/${tenantId}`, {
      method: "PUT",
      body: JSON.stringify(tenantData),
    });
  },

  // Tenant Users
  getTenantUsers: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/users`);
  },

  createTenantUser: async (tenantId: string, userData: {
    email: string;
    password: string;
    full_name?: string;
    role?: string;
  }) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/users`, {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  // Subscriptions
  getTenantSubscription: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/subscription`);
  },

  // Incidents
  getTenantIncidents: async (tenantId: string, limit: number = 100, offset: number = 0) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/incidents?limit=${limit}&offset=${offset}`);
  },

  // Dashboard & Summary
  getTenantDashboard: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/dashboard`);
  },

  getTenantSummary: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/summary`);
  },

  // Departments
  getTenantDepartments: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/departments`);
  },

  // Projects
  getTenantProjects: async (tenantId: string, departmentId?: string) => {
    const params = departmentId ? `?department_id=${departmentId}` : "";
    return apiRequest(`/api/crm/tenants/${tenantId}/projects${params}`);
  },

  // Usage Analytics
  getTenantUsage: async (tenantId: string, days: number = 30) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/usage?days=${days}`);
  },

  // Audit Logs
  getTenantAuditLogs: async (
    tenantId: string,
    params: {
      limit?: number;
      offset?: number;
      action?: string;
      user_id?: string;
      start_date?: string;
      end_date?: string;
    } = {}
  ) => {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.offset) queryParams.append("offset", params.offset.toString());
    if (params.action) queryParams.append("action", params.action);
    if (params.user_id) queryParams.append("user_id", params.user_id);
    if (params.start_date) queryParams.append("start_date", params.start_date);
    if (params.end_date) queryParams.append("end_date", params.end_date);
    
    const query = queryParams.toString();
    return apiRequest(`/api/crm/tenants/${tenantId}/audit-logs${query ? `?${query}` : ""}`);
  },
};

// Subscription API Client
export const subscriptionApi = {
  listSubscriptions: async (limit: number = 100, offset: number = 0) => {
    return apiRequest(`/api/subscriptions?limit=${limit}&offset=${offset}`);
  },

  getSubscription: async (subscriptionId: string) => {
    return apiRequest(`/api/subscriptions/${subscriptionId}`);
  },

  createSubscription: async (subscriptionData: any) => {
    return apiRequest("/api/subscriptions", {
      method: "POST",
      body: JSON.stringify(subscriptionData),
    });
  },
};

// Access API Client
export const accessApi = {
  listRoles: async () => {
    return apiRequest("/api/access/roles");
  },

  getRole: async (roleId: string) => {
    return apiRequest(`/api/access/roles/${roleId}`);
  },

  listPermissions: async () => {
    return apiRequest("/api/access/permissions");
  },
};

// Policy API Client
export const policyApi = {
  listPolicies: async () => {
    return apiRequest("/api/policies");
  },

  getPolicy: async (policyId: string) => {
    return apiRequest(`/api/policies/${policyId}`);
  },
};
