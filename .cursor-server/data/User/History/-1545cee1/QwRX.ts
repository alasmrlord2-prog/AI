import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || '';
  const pathname = request.nextUrl.pathname;

  // Skip middleware for static files, API routes, and Next.js internals
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/favicon') ||
    pathname.startsWith('/static') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // CRM domain - ensure /crm prefix
  if (hostname.includes('crm.bankid-sy.com')) {
    // If accessing root, redirect to /crm
    if (pathname === '/') {
      return NextResponse.redirect(new URL('/crm', request.url));
    }
    // Allow /crm and all paths starting with /crm
    if (pathname.startsWith('/crm')) {
      return NextResponse.next();
    }
    // If path doesn't start with /crm, add it
    return NextResponse.redirect(new URL(`/crm${pathname}`, request.url));
  }
  
  // AAA domain - ensure /aaa prefix
  if (hostname.includes('aaa.bankid-sy.com')) {
    // If accessing root, redirect to /aaa
    if (pathname === '/') {
      return NextResponse.redirect(new URL('/aaa', request.url));
    }
    // Allow /aaa and all paths starting with /aaa
    if (pathname.startsWith('/aaa')) {
      return NextResponse.next();
    }
    // If path doesn't start with /aaa, add it
    return NextResponse.redirect(new URL(`/aaa${pathname}`, request.url));
  }

  // Allow the request to proceed for other domains
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

