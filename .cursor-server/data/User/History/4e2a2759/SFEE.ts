// Shared API utility functions

export const getApiUrl = (): string => {
  // Server-side: Use Docker service name or environment variable
  if (typeof window === 'undefined') {
    // Server-side rendering - use Docker service name or env var
    if (process.env.BACKEND_URL) {
      return process.env.BACKEND_URL;
    }
    if (process.env.NEXT_PUBLIC_BACKEND_URL) {
      return process.env.NEXT_PUBLIC_BACKEND_URL;
    }
    // Default to Docker service name
    return "http://backend:8000";
  }
  
  // Client-side: Use environment variable first
  if (process.env.NEXT_PUBLIC_AGENT_API_URL) {
    const envUrl = process.env.NEXT_PUBLIC_AGENT_API_URL;
    if (envUrl.startsWith('http://') || envUrl.startsWith('https://')) {
      return envUrl;
    }
  }
  if (process.env.NEXT_PUBLIC_BACKEND_URL) {
    const envUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (envUrl.startsWith('http://') || envUrl.startsWith('https://')) {
      return envUrl;
    }
  }
  
  // Client-side: Use the same hostname and protocol as the frontend
  // Next.js rewrites will proxy /api/* requests to backend on server-side
  // For client-side, we need to use the same origin so rewrites work
  const hostname = window.location.hostname;
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  const port = window.location.port;
  
  // Production domain - use same hostname (nginx proxies /api to backend)
  if (hostname === "ai-agent.bankid-sy.com" || hostname.includes("bankid-sy.com")) {
    return `${protocol}//${hostname}${port ? `:${port}` : ''}`;
  }
  
  // Development: Use same origin so Next.js rewrites can proxy to backend
  // This works because Next.js rewrites handle /api/* on the server
  // The browser makes request to same origin, Next.js server proxies to backend
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Use same origin - Next.js rewrites will handle the proxying
    return `${protocol}//${hostname}${port ? `:${port}` : ''}`;
  }
  
  // Fallback: Use same origin (Next.js rewrites will handle /api/*)
  return `${protocol}//${hostname}${port ? `:${port}` : ''}`;
};

export const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem("auth_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  
  return headers;
};

export const fetchWithTimeout = async (
  url: string,
  options: RequestInit = {},
  timeout: number = 30000 // Increased to 30 seconds for better reliability
): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && (error.name === 'AbortError' || error.message.includes('aborted'))) {
      const timeoutSeconds = Math.round(timeout / 1000);
      throw new Error(`Request timeout بعد ${timeoutSeconds} ثانية - يرجى المحاولة مرة أخرى`);
    }
    throw error;
  }
};

export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {},
  timeout: number = 30000, // Increased to 30 seconds for better reliability
  retries: number = 2 // Retry failed requests up to 2 times
): Promise<any> => {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const apiUrl = getApiUrl();
      const headers = getAuthHeaders();
      
      const fullUrl = `${apiUrl}${endpoint}`;
      
      // Log request for debugging (always in development, sometimes in production)
      if (process.env.NODE_ENV === 'development' || typeof window !== 'undefined') {
        console.log(`[API] ${options.method || 'GET'} ${fullUrl} (timeout: ${timeout}ms, attempt: ${attempt + 1}/${retries + 1})`);
        console.log(`[API] API URL: ${apiUrl}, Endpoint: ${endpoint}`);
      }
      
      const response = await fetchWithTimeout(
        fullUrl,
        {
          ...options,
          headers: {
            ...headers,
            ...(options.headers || {}),
          },
        },
        timeout
      );

      // Check content type before parsing
      const contentType = response.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');
      
      if (!response.ok) {
        let errorText = '';
        try {
          const responseText = await response.text();
          if (isJson) {
            try {
              const errorData = JSON.parse(responseText);
              errorText = errorData.detail || errorData.message || errorData.error || JSON.stringify(errorData);
            } catch {
              errorText = responseText;
            }
          } else {
            // If it's HTML, extract meaningful error
            if (responseText.includes('<html>') || responseText.includes('<!DOCTYPE')) {
              if (response.status === 404) {
                errorText = `Endpoint غير موجود: ${endpoint}. تحقق من أن الـ Backend يعمل والـ route صحيح.`;
              } else if (response.status === 500) {
                errorText = 'خطأ في السيرفر (500). تحقق من Backend logs.';
              } else {
                errorText = `HTTP ${response.status}: خطأ في السيرفر`;
              }
            } else {
              errorText = responseText;
            }
          }
        } catch (e) {
          errorText = `HTTP ${response.status}: Failed to read error response`;
        }
        throw new Error(errorText || `HTTP ${response.status}: Unknown error`);
      }

      // Only try to parse JSON if content-type is JSON
      if (!isJson) {
        const text = await response.text();
        console.warn('Response is not JSON, received:', text.substring(0, 100));
        throw new Error(`الخادم أرجع HTML بدلاً من JSON. تحقق من أن الـ endpoint صحيح: ${endpoint}`);
      }

      try {
        const text = await response.text();
        return JSON.parse(text);
      } catch (e) {
        // If JSON parsing fails, show clear error
        console.error('JSON parsing error:', e);
        throw new Error(`فشل في تحليل JSON من الخادم. الـ endpoint قد يكون غير صحيح: ${endpoint}. تحقق من أن الـ Backend يعمل.`);
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Don't retry on certain errors
      if (error instanceof Error && (
        error.message.includes('404') ||
        error.message.includes('401') ||
        error.message.includes('403') ||
        error.message.includes('400')
      )) {
        throw error;
      }
      
      // If this is the last attempt, throw the error
      if (attempt === retries) {
        break;
      }
      
      // Wait before retrying (exponential backoff)
      const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
      if (process.env.NODE_ENV === 'development') {
        console.debug(`[API] Retrying request after ${delay}ms...`);
      }
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // If we get here, all retries failed
  if (lastError) {
    // Log the error for debugging
    console.error('[API] Request failed:', {
      endpoint,
      apiUrl: getApiUrl(),
      error: lastError.message,
      stack: lastError.stack
    });
    
    // Handle network errors
    if (lastError.message.includes('Failed to fetch') || 
        lastError.message.includes('NetworkError') ||
        lastError.message.includes('Network request failed') ||
        lastError.message.includes('ERR_INTERNET_DISCONNECTED') ||
        lastError.message.includes('ERR_NETWORK_CHANGED') ||
        lastError.message.includes('fetch')) {
      const apiUrl = getApiUrl();
      throw new Error(`🌐 خطأ في الاتصال بالخادم.\n\nURL: ${apiUrl}${endpoint}\n\nتحقق من:\n1. أن الـ Backend يعمل على ${apiUrl}\n2. أن CORS settings صحيحة\n3. أن الـ network connection يعمل`);
    }
    // Handle CORS errors
    if (lastError.message.includes('CORS')) {
      throw new Error('🚫 خطأ CORS. تحقق من إعدادات الـ Backend للسماح بالطلبات من هذا المصدر.');
    }
    // Add endpoint context to error message if not already present
    if (!lastError.message.includes(endpoint)) {
      throw new Error(`${lastError.message} (Endpoint: ${endpoint})`);
    }
    throw lastError;
  }
  
  throw new Error('Unknown error occurred');
};

// ==================== CRM API Wrappers ====================

export const crmApi = {
  // Tenants
  listTenants: async (limit = 100, offset = 0) => {
    return apiRequest(`/api/crm/tenants?limit=${limit}&offset=${offset}`, {}, 30000);
  },

  getTenantDashboard: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/dashboard`, {}, 30000);
  },

  getTenantSummary: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/summary`);
  },

  // Users
  getTenantUsers: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/users`);
  },

  // Departments & Projects
  getTenantDepartments: async (tenantId: string) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/departments`);
  },

  getTenantProjects: async (tenantId: string, departmentId?: string) => {
    const params = departmentId ? `?department_id=${departmentId}` : '';
    return apiRequest(`/api/crm/tenants/${tenantId}/projects${params}`);
  },

  // Usage & Analytics
  getTenantUsage: async (tenantId: string, days = 30) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/usage?days=${days}`);
  },

  // Incidents
  getTenantIncidents: async (tenantId: string, limit = 50, offset = 0) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/incidents?limit=${limit}&offset=${offset}`);
  },

  // Audit Logs
  getTenantAuditLogs: async (
    tenantId: string,
    options: {
      limit?: number;
      offset?: number;
      action?: string;
      user_id?: string;
      start_date?: string;
      end_date?: string;
    } = {}
  ) => {
    const params = new URLSearchParams();
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.offset) params.append('offset', options.offset.toString());
    if (options.action) params.append('action', options.action);
    if (options.user_id) params.append('user_id', options.user_id);
    if (options.start_date) params.append('start_date', options.start_date);
    if (options.end_date) params.append('end_date', options.end_date);
    
    const queryString = params.toString();
    return apiRequest(`/api/crm/tenants/${tenantId}/audit-logs${queryString ? `?${queryString}` : ''}`);
  },
};

// ==================== Identity API Wrappers ====================

export const identityApi = {
  // Users
  createUser: async (userData: any) => {
    return apiRequest('/api/identity/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  listUsers: async (limit = 100, offset = 0) => {
    return apiRequest(`/api/identity/users?limit=${limit}&offset=${offset}`);
  },

  getUsersCount: async () => {
    return apiRequest('/api/identity/users/count');
  },

  getUser: async (userId: string) => {
    return apiRequest(`/api/identity/users/${userId}`);
  },

  updateUser: async (userId: string, userData: any) => {
    return apiRequest(`/api/identity/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },

  // Tenants
  createTenant: async (tenantData: any) => {
    return apiRequest('/api/identity/tenants', {
      method: 'POST',
      body: JSON.stringify(tenantData),
    });
  },

  getTenant: async (tenantId: string) => {
    return apiRequest(`/api/identity/tenants/${tenantId}`);
  },

  updateTenant: async (tenantId: string, tenantData: any) => {
    return apiRequest(`/api/identity/tenants/${tenantId}`, {
      method: 'PUT',
      body: JSON.stringify(tenantData),
    });
  },

  getTenantUsers: async (tenantId: string) => {
    return apiRequest(`/api/identity/tenants/${tenantId}/users`);
  },

  addUserToTenant: async (tenantId: string, userId: string, role = 'member') => {
    return apiRequest(`/api/identity/tenants/${tenantId}/users?user_id=${userId}&role=${role}`, {
      method: 'POST',
    });
  },

  // Sessions
  getSessions: async (userId?: string) => {
    // userId is optional - if not provided, uses authenticated user from token
    const params = userId ? `?user_id=${userId}` : '';
    return apiRequest(`/api/identity/sessions${params}`);
  },

  revokeSession: async (sessionId: string) => {
    return apiRequest(`/api/identity/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  },

  // API Tokens
  createApiToken: async (tokenData: any) => {
    // user_id is automatically extracted from authentication token
    return apiRequest('/api/identity/api-tokens', {
      method: 'POST',
      body: JSON.stringify(tokenData),
    });
  },

  listApiTokens: async (tenantId?: string) => {
    // user_id is automatically extracted from authentication token
    const params = tenantId ? `?tenant_id=${tenantId}` : '';
    return apiRequest(`/api/identity/api-tokens${params}`);
  },

  getApiToken: async (tokenId: string) => {
    // user_id is automatically extracted from authentication token
    return apiRequest(`/api/identity/api-tokens/${tokenId}`);
  },

  revokeApiToken: async (tokenId: string) => {
    // user_id is automatically extracted from authentication token
    return apiRequest(`/api/identity/api-tokens/${tokenId}`, {
      method: 'DELETE',
    });
  },

  // Departments & Projects
  createDepartment: async (tenantId: string, departmentData: any) => {
    return apiRequest(`/api/identity/tenants/${tenantId}/departments`, {
      method: 'POST',
      body: JSON.stringify(departmentData),
    });
  },

  createProject: async (tenantId: string, projectData: any) => {
    return apiRequest(`/api/identity/tenants/${tenantId}/projects`, {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  },
};

// ==================== Subscription API Wrappers ====================

export const subscriptionApi = {
  // Plans
  createPlan: async (planData: any) => {
    return apiRequest('/api/subscription/plans', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  },

  getPlans: async () => {
    return apiRequest('/api/subscription/plans');
  },

  getPlan: async (planId: string) => {
    return apiRequest(`/api/subscription/plans/${planId}`);
  },

  // Subscriptions
  createSubscription: async (subscriptionData: any) => {
    return apiRequest('/api/subscription/subscriptions', {
      method: 'POST',
      body: JSON.stringify(subscriptionData),
    });
  },

  getSubscriptionStatus: async (tenantId: string) => {
    return apiRequest(`/api/subscription/tenants/${tenantId}/subscription`);
  },

  // Usage
  getUsage: async (subscriptionId: string, resourceType?: string) => {
    const params = resourceType ? `?resource_type=${resourceType}` : '';
    return apiRequest(`/api/subscription/subscriptions/${subscriptionId}/usage${params}`);
  },

  incrementUsage: async (subscriptionId: string, resourceType: string, amount = 1) => {
    return apiRequest(`/api/subscription/subscriptions/${subscriptionId}/usage/increment?resource_type=${resourceType}&amount=${amount}`, {
      method: 'POST',
    });
  },

  checkUsageLimit: async (subscriptionId: string, resourceType: string, requestedAmount = 1) => {
    return apiRequest(`/api/subscription/subscriptions/${subscriptionId}/usage/check`, {
      method: 'POST',
      body: JSON.stringify({ resource_type: resourceType, requested_amount: requestedAmount }),
    });
  },
};

// ==================== Access API Wrappers ====================

export const accessApi = {
  // Roles
  getRoles: async () => {
    return apiRequest('/api/access/roles', {}, 30000); // 30 second timeout
  },

  createRole: async (roleData: any) => {
    return apiRequest('/api/access/roles', {
      method: 'POST',
      body: JSON.stringify(roleData),
    });
  },

  // Permissions
  getPermissions: async () => {
    return apiRequest('/api/access/permissions', {}, 30000);
  },

  // User Roles
  getUserRoles: async (userId: string, tenantId?: string) => {
    const params = tenantId ? `?user_id=${userId}&tenant_id=${tenantId}` : `?user_id=${userId}`;
    return apiRequest(`/api/access/user-roles${params}`, {}, 30000);
  },

  assignRole: async (userRoleData: any) => {
    return apiRequest('/api/access/user-roles', {
      method: 'POST',
      body: JSON.stringify(userRoleData),
    });
  },
};

// ==================== Policy API Wrappers ====================

export const policyApi = {
  // Relation Tuples
  createRelationTuple: async (tupleData: any) => {
    return apiRequest('/api/policy/relations', {
      method: 'POST',
      body: JSON.stringify(tupleData),
    });
  },

  getRelations: async (options: {
    subject_type?: string;
    subject_id?: string;
    object_type?: string;
    object_id?: string;
    tenant_id?: string;
  } = {}) => {
    const params = new URLSearchParams();
    Object.entries(options).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    const queryString = params.toString();
    return apiRequest(`/api/policy/relations${queryString ? `?${queryString}` : ''}`, {}, 30000);
  },

  checkRelation: async (checkData: any) => {
    return apiRequest('/api/policy/check', {
      method: 'POST',
      body: JSON.stringify(checkData),
    }, 30000);
  },

  // Policy Rules
  createPolicyRule: async (ruleData: any) => {
    return apiRequest('/api/policy/rules', {
      method: 'POST',
      body: JSON.stringify(ruleData),
    }, 30000);
  },

  getPolicyRules: async (tenantId?: string) => {
    const params = tenantId ? `?tenant_id=${tenantId}` : '';
    return apiRequest(`/api/policy/rules${params}`, {}, 30000);
  },
};
