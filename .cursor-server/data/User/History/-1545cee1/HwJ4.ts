import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || '';
  const pathname = request.nextUrl.pathname;

  // CRM domain - ensure /crm prefix
  if (hostname.includes('crm.bankid-sy.com')) {
    // If accessing root, redirect to /crm
    if (pathname === '/') {
      return NextResponse.redirect(new URL('/crm', request.url));
    }
    // If path is exactly /crm, allow it (it will be handled by /app/crm/page.tsx)
    if (pathname === '/crm') {
      return NextResponse.next();
    }
    // If path doesn't start with /crm, add it
    if (!pathname.startsWith('/crm') && !pathname.startsWith('/_next') && !pathname.startsWith('/api') && !pathname.startsWith('/favicon')) {
      return NextResponse.redirect(new URL(`/crm${pathname}`, request.url));
    }
  }
  
  // AAA domain - ensure /aaa prefix
  if (hostname.includes('aaa.bankid-sy.com')) {
    // If accessing root, redirect to /aaa
    if (pathname === '/') {
      return NextResponse.redirect(new URL('/aaa', request.url));
    }
    // If path is exactly /aaa, allow it (it will be handled by /app/aaa/page.tsx)
    if (pathname === '/aaa') {
      return NextResponse.next();
    }
    // If path doesn't start with /aaa, add it
    if (!pathname.startsWith('/aaa') && !pathname.startsWith('/_next') && !pathname.startsWith('/api') && !pathname.startsWith('/favicon')) {
      return NextResponse.redirect(new URL(`/aaa${pathname}`, request.url));
    }
  }

  // Allow the request to proceed
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

