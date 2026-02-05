export class APIError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.details = details;
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

export function getApiUrl(): string {
  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.host}`;
  }

  return (
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_AGENT_API_URL ||
    "http://localhost:8000"
  );
}

function buildUrl(endpoint: string): string {
  if (endpoint.startsWith("http://") || endpoint.startsWith("https://")) {
    return endpoint;
  }

  const baseUrl = getApiUrl();
  if (endpoint.startsWith("/")) {
    return `${baseUrl}${endpoint}`;
  }

  return `${baseUrl}/${endpoint}`;
}

function getAuthHeader(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }

  const token = window.localStorage.getItem("auth_token");
  if (!token) {
    return {};
  }

  return { Authorization: `Bearer ${token}` };
}

function safeJsonParse(text: string): unknown {
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs = 10000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const authHeader = getAuthHeader();
  Object.entries(authHeader).forEach(([key, value]) => {
    if (!headers.has(key)) {
      headers.set(key, value);
    }
  });

  try {
    const response = await fetch(buildUrl(endpoint), {
      ...options,
      headers,
      signal: controller.signal,
    });

    const text = await response.text();
    const payload = safeJsonParse(text);

    if (!response.ok) {
      if (response.status === 401 && typeof window !== "undefined") {
        window.localStorage.removeItem("auth_token");
        if (!window.location.pathname.includes("/login")) {
          window.location.href = "/login";
        }
      }

      const payloadObj = payload as Record<string, unknown> | null;
      throw new APIError(
        (payloadObj?.detail as string) || (payloadObj?.message as string) || "Request failed",
        response.status,
        payload
      );
    }

    return payload as T;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new TimeoutError("Request timed out");
    }
    if (error instanceof SyntaxError) {
      throw new APIError("Invalid JSON response", 500);
    }
    throw new NetworkError(
      error instanceof Error ? error.message : "Network error"
    );
  } finally {
    clearTimeout(timeoutId);
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

  updateTenant: async (tenantId: string, tenantData: Record<string, unknown>) => {
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
  getAuditLogs: async (params: { limit?: number; offset?: number; user_id?: string; tenant_id?: string; action?: string; status?: string; resource_id?: string; feature_key?: string }) => {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.offset) queryParams.append("offset", params.offset.toString());
    if (params.user_id) queryParams.append("user_id", params.user_id);
    if (params.tenant_id) queryParams.append("tenant_id", params.tenant_id);
    if (params.action) queryParams.append("action", params.action);
    if (params.status) queryParams.append("status", params.status);
    if (params.resource_id) queryParams.append("resource_id", params.resource_id);
    if (params.feature_key) queryParams.append("feature_key", params.feature_key);
    
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
    feature_key?: string;
    status?: string;
    metadata?: Record<string, unknown>;
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

  updateTenant: async (tenantId: string, tenantData: Record<string, unknown>) => {
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
      resource_id?: string;
      feature_key?: string;
      start_date?: string;
      end_date?: string;
    } = {}
  ) => {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.offset) queryParams.append("offset", params.offset.toString());
    if (params.action) queryParams.append("action", params.action);
    if (params.user_id) queryParams.append("user_id", params.user_id);
    if (params.resource_id) queryParams.append("resource_id", params.resource_id);
    if (params.feature_key) queryParams.append("feature_key", params.feature_key);
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

  createSubscription: async (subscriptionData: Record<string, unknown>) => {
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
