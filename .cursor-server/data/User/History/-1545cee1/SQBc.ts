import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || '';
  const pathname = request.nextUrl.pathname;

  // If accessing root path, redirect based on hostname
  if (pathname === '/') {
    // CRM domain - redirect to /crm
    if (hostname.includes('crm.bankid-sy.com')) {
      return NextResponse.redirect(new URL('/crm', request.url));
    }
    
    // AAA domain - redirect to /aaa
    if (hostname.includes('aaa.bankid-sy.com')) {
      return NextResponse.redirect(new URL('/aaa', request.url));
    }
    
    // Dashboard domain - stay on root (default behavior)
    // No redirect needed for ai-agent.bankid-sy.com or dashboard.bankid-sy.com
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

