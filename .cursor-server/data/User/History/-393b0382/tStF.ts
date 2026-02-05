// config/services.ts
// Centralized service configuration - ALL DATA FROM ENDPOINTS, NO HARDCODED VALUES

import { apiRequest } from "@/lib/api";

export type ServiceItem = {
  id: string;
  name: string;
  href: string;
  icon?: string;
  iconComponent?: string; // Lucide icon name for dynamic import
  description?: string;
};

export type ServiceCategory = {
  category: string;
  items: ServiceItem[];
};

// Cache for services to avoid repeated API calls
let servicesCache: ServiceCategory[] | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch services from endpoint - NO HARDCODED VALUES
 */
export async function fetchServices(): Promise<ServiceCategory[]> {
  const now = Date.now();
  
  // Return cached data if still valid
  if (servicesCache && (now - cacheTimestamp) < CACHE_DURATION) {
    return servicesCache;
  }
  
  try {
    // Increased timeout to 30 seconds to handle slow backend responses
    const response = await apiRequest("/api/services/list", { method: "GET" }, 30000);
    const services = response.services || [];
    
    // Update cache
    servicesCache = services;
    cacheTimestamp = now;
    
    return services;
  } catch (error) {
    console.error("Error fetching services from endpoint:", error);
    // Return cached data if available, even if expired, to avoid empty UI
    if (servicesCache) {
      console.warn("Using expired cache due to API error");
      return servicesCache;
    }
    // Return empty array on error, not hardcoded fallback
    return [];
  }
}

/**
 * Get all services - from endpoint, no hardcoded values
 */
export async function getAllServices(): Promise<ServiceItem[]> {
  const services = await fetchServices();
  return services.flatMap((cat) => cat.items);
}

/**
 * Find a service by ID - from endpoint
 */
export async function getServiceById(id: string): Promise<ServiceItem | undefined> {
  const services = await getAllServices();
  return services.find((s) => s.id === id);
}

/**
 * Find a service by href - from endpoint
 */
export async function getServiceByHref(href: string): Promise<ServiceItem | undefined> {
  const services = await getAllServices();
  return services.find((s) => s.href === href || s.href === href.split("?")[0]);
}

/**
 * Get service categories - from endpoint
 */
export async function getServiceCategories(): Promise<string[]> {
  try {
    const response = await apiRequest("/api/services/categories", { method: "GET" }, 10000);
    return response.categories || [];
  } catch (error) {
    console.error("Error fetching service categories:", error);
    return [];
  }
}

// For backward compatibility, export a function that returns services
// This should be used in React components with useState/useEffect
export const getServices = fetchServices;

