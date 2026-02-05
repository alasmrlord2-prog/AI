"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

const PUBLIC_PATHS = ["/login", "/crm/login", "/aaa/login"];
const FEATURES_KEY = "tenant_features";
const FEATURES_UPDATED_EVENT = "tenant-features-updated";

const isPublicPath = (pathname: string) =>
  PUBLIC_PATHS.some((path) => pathname.startsWith(path));

const getLoginPath = (pathname: string) => {
  if (pathname.startsWith("/crm")) return "/crm/login";
  if (pathname.startsWith("/aaa")) return "/aaa/login";
  return "/login";
};

const parseJwtPayload = (token: string) => {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const payload = JSON.parse(atob(parts[1]));
    return payload;
  } catch {
    return null;
  }
};

const isTokenExpired = (token: string) => {
  const payload = parseJwtPayload(token);
  if (!payload?.exp) return false;
  return Date.now() >= payload.exp * 1000;
};

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!pathname) return;

    if (isPublicPath(pathname)) {
      setReady(true);
      return;
    }

    const token = localStorage.getItem("auth_token");
    if (!token || isTokenExpired(token)) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem(FEATURES_KEY);
      router.replace(getLoginPath(pathname));
      return;
    }

    const loadFeatures = async () => {
      try {
        const response = await fetch("/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            localStorage.removeItem("auth_token");
            localStorage.removeItem(FEATURES_KEY);
            router.replace(getLoginPath(pathname));
            return;
          }
          setReady(true);
          return;
        }

        const data = await response.json();
        localStorage.setItem(FEATURES_KEY, JSON.stringify(data.features || {}));
        window.dispatchEvent(new Event(FEATURES_UPDATED_EVENT));
      } catch {
        // Keep UI accessible even if feature fetch fails.
      } finally {
        setReady(true);
      }
    };

    void loadFeatures();
  }, [pathname, router]);

  if (!ready) {
    return null;
  }

  return <>{children}</>;
}
