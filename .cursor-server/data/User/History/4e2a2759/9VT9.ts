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
  
  // Client-side: Use relative URLs to leverage Next.js rewrites
  // This avoids CORS issues and works regardless of how the frontend is accessed
  // Next.js rewrites will proxy /api/* requests to the backend
  // Return empty string to use relative URLs (same origin)
  return '';
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
    // Add mode and credentials for CORS
    const fetchOptions: RequestInit = {
      ...options,
      signal: controller.signal,
      mode: 'cors', // Explicitly set CORS mode
      credentials: 'omit', // Don't send credentials if CORS doesn't allow it
    };
    
    const response = await fetch(url, fetchOptions);
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    // Handle different error types
    if (error instanceof Error) {
      if (error.name === 'AbortError' || error.message.includes('aborted')) {
        const timeoutSeconds = Math.round(timeout / 1000);
        throw new Error(`Request timeout بعد ${timeoutSeconds} ثانية - يرجى المحاولة مرة أخرى`);
      }
      // For network errors, preserve the original error but add context
      if (error.name === 'TypeError' && (error.message.includes('fetch') || error.message.includes('Failed to fetch'))) {
        // Log error details
        console.error('[fetchWithTimeout] Network error:', error.message);
        console.error('[fetchWithTimeout] URL:', url);
        console.error('[fetchWithTimeout] Options:', options);
        
        // Create user-friendly error message
        const errorMsg = error.message || 'Unknown network error';
        throw new Error(`🌐 خطأ في الاتصال بالخادم: ${errorMsg}\n\nURL: ${url}\n\nتحقق من:\n1. أن الباك إند يعمل على http://localhost:8000\n2. أن CORS settings صحيحة\n3. أن الـ network connection يعمل`);
      }
      // Re-throw the error as-is
      throw error;
    } else {
      // Convert non-Error objects to Error
      throw new Error(String(error) || 'Unknown network error');
    }
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
      
      // Build full URL - if apiUrl is empty, use relative URL (Next.js rewrites will handle it)
      const fullUrl = apiUrl ? `${apiUrl}${endpoint}` : endpoint;
      
      // Log request for debugging (only in development)
      if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
        console.log(`[API] ${options.method || 'GET'} ${fullUrl}`);
        console.log(`[API] Headers:`, headers);
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
              if (response.status === 401 || response.status === 403) {
                errorText = `مطلوب تسجيل الدخول (${response.status}). تحقق من أن token المصادقة صحيح.`;
              } else if (response.status === 404) {
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
        // If status is OK but not JSON, it might be an HTML error page or redirect
        if (response.status === 200) {
          // Check if it's actually HTML
          if (text.includes('<html>') || text.includes('<!DOCTYPE')) {
            console.warn('[API] Server returned HTML instead of JSON for endpoint:', endpoint);
            // Return empty object to avoid breaking the app
            return {};
          }
          // If it's not HTML, try to parse as JSON anyway
          try {
            return JSON.parse(text);
          } catch {
            return {};
          }
        }
        // For non-200 status, error was already handled above
        console.warn('[API] Response is not JSON, received:', text.substring(0, 100));
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
      // Ensure we always have an Error object
      if (error instanceof Error) {
        lastError = error;
      } else if (error && typeof error === 'object') {
        // Try to create Error from object
        try {
          const errorMsg = (error as any).message || (error as any).error || (error as any).detail || JSON.stringify(error);
          lastError = new Error(String(errorMsg || 'Unknown error occurred'));
        } catch (e) {
          lastError = new Error(String(error) || 'Unknown error occurred');
        }
      } else {
        lastError = new Error(String(error) || 'Unknown error occurred');
      }
      
      // Log error immediately for debugging (only in development)
      if (process.env.NODE_ENV === 'development' && lastError) {
        console.debug(`[API] Attempt ${attempt + 1}/${retries + 1} failed:`, {
          endpoint,
          error: lastError.message,
          errorName: lastError.name,
          errorStack: lastError.stack
        });
      }
      
      // Don't retry on certain errors
      if (lastError && (
        lastError.message.includes('404') ||
        lastError.message.includes('401') ||
        lastError.message.includes('403') ||
        lastError.message.includes('400')
      )) {
        throw lastError;
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
    // Get error message safely - handle all error types
    let errorMessage = 'Unknown error';
    let errorStack = 'No stack trace';
    let errorName = 'Unknown';
    let errorType: string = typeof lastError;
    
    try {
      if (lastError instanceof Error) {
        errorMessage = lastError.message || String(lastError) || 'Unknown error';
        errorStack = lastError.stack || 'No stack trace';
        errorName = lastError.name || 'Error';
        errorType = lastError.constructor?.name || 'Error';
      } else if (typeof lastError === 'string') {
        errorMessage = lastError;
      } else if (typeof lastError === 'object' && lastError !== null) {
        // Try to extract message from object
        try {
          errorMessage = (lastError as any).message || (lastError as any).error || (lastError as any).detail || JSON.stringify(lastError);
          if (!errorMessage || errorMessage.trim() === '') {
            errorMessage = `Request failed for ${endpoint}`;
          }
        } catch (e) {
          errorMessage = `Request failed for ${endpoint}`;
        }
      } else {
        errorMessage = String(lastError);
      }
    } catch (e) {
      errorMessage = String(lastError);
    }
    
    // Ensure errorMessage is never empty
    if (!errorMessage || errorMessage.trim() === '' || errorMessage === 'Unknown error') {
      errorMessage = `Request failed for ${endpoint}`;
    }
    
    // Always log errors with full context for debugging
    // Don't log 404 errors as they're expected for optional endpoints
    if (!errorMessage.includes('404') && !errorMessage.includes('Not Found')) {
      const apiUrl = getApiUrl();
      
      // Build error details with explicit values to avoid empty object
      const errorDetails: any = {};
      
      // Always include these fields
      errorDetails.endpoint = String(endpoint || 'unknown');
      errorDetails.apiUrl = String(apiUrl || 'unknown');
      errorDetails.error = String(errorMessage || 'Unknown error');
      errorDetails.errorType = String(errorType || 'Unknown');
      errorDetails.errorName = String(errorName || 'Unknown');
      
      // Add timestamp
      errorDetails.timestamp = new Date().toISOString();
      
      // Add stack trace in development mode
      if (process.env.NODE_ENV === 'development' && errorStack && errorStack !== 'No stack trace') {
        errorDetails.stack = String(errorStack);
      }
      
      // Add lastError details if available
      if (lastError) {
        if (typeof lastError === 'object' && lastError !== null) {
          try {
            errorDetails.rawError = JSON.stringify(lastError, Object.getOwnPropertyNames(lastError));
          } catch (e) {
            errorDetails.rawError = String(lastError);
          }
        } else {
          errorDetails.rawError = String(lastError);
        }
      }
      
      // Log with multiple formats to ensure visibility
      // Always log errorDetails first to ensure it's not empty
      if (Object.keys(errorDetails).length > 0) {
        console.error('[API] Request failed:', errorDetails);
      } else {
        // Fallback if errorDetails is empty
        console.error('[API] Request failed:', {
          endpoint: endpoint || 'unknown',
          error: errorMessage || 'Unknown error',
          errorType: errorType || 'Unknown',
          timestamp: new Date().toISOString()
        });
      }
      console.error('[API] Endpoint:', endpoint);
      console.error('[API] Error:', errorMessage);
      console.error('[API] Error Type:', errorType);
      if (Object.keys(errorDetails).length > 0) {
        console.error('[API] Full Error Object:', JSON.stringify(errorDetails, null, 2));
      }
    }
    
    // Handle network errors - check for various network error patterns
    const isNetworkError = 
      errorMessage.includes('Failed to fetch') || 
      errorMessage.includes('NetworkError') ||
      errorMessage.includes('Network request failed') ||
      errorMessage.includes('ERR_INTERNET_DISCONNECTED') ||
      errorMessage.includes('ERR_NETWORK_CHANGED') ||
      errorMessage.includes('ERR_CONNECTION_REFUSED') ||
      errorMessage.includes('ERR_CONNECTION_RESET') ||
      errorMessage.includes('ERR_NAME_NOT_RESOLVED') ||
      (errorMessage.includes('fetch') && !errorMessage.includes('JSON')) ||
      errorMessage.includes('aborted') ||
      errorName === 'TypeError' ||
      (errorName === 'DOMException' && errorMessage.includes('network'));
    
    if (isNetworkError) {
      const apiUrl = getApiUrl();
      const detailedError = `🌐 خطأ في الاتصال بالخادم.

URL: ${apiUrl}${endpoint}
Error: ${errorMessage}
Error Type: ${errorType}

تحقق من:
1. أن الـ Backend يعمل على ${apiUrl}
2. أن CORS settings صحيحة
3. أن الـ network connection يعمل
4. أن الـ firewall لا يحجب الطلبات`;
      console.error('[API] Network error detected:', detailedError);
      throw new Error(detailedError);
    }
    // Handle CORS errors
    if (errorMessage.includes('CORS')) {
      throw new Error('🚫 خطأ CORS. تحقق من إعدادات الـ Backend للسماح بالطلبات من هذا المصدر.');
    }
    // Add endpoint context to error message if not already present
    if (!errorMessage.includes(endpoint)) {
      throw new Error(`${errorMessage} (Endpoint: ${endpoint})`);
    }
    throw lastError;
  }
  
  // This should never happen, but handle it gracefully
  const fallbackError = `Request failed for ${endpoint} - No error details available after ${retries + 1} attempts`;
  console.error('[API] Request failed with no error details:', {
    endpoint,
    apiUrl: getApiUrl(),
    attempts: retries + 1
  });
  throw new Error(fallbackError);
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

  createTenantUser: async (tenantId: string, userData: any) => {
    return apiRequest(`/api/crm/tenants/${tenantId}/users`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
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

  getUser: async (userId: string) => {
    return apiRequest(`/api/identity/users/${userId}`);
  },

  listUsers: async (limit = 100, offset = 0) => {
    return apiRequest(`/api/identity/users?limit=${limit}&offset=${offset}`);
  },

  getUsersCount: async () => {
    return apiRequest('/api/identity/users/count');
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
