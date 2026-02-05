"""Shared login flow with MFA and session handling."""
from __future__ import annotations

import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.core.brute_force_protection import BruteForceProtection
from app.core.cache import cache_key, set_cache, get_cache, delete_cache
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.core.session_manager import SessionManager
from app.identity import service as identity_service
from app.identity.models import Tenant

logger = logging.getLogger(__name__)
settings = get_settings()

_MFA_TICKET_TTL_SECONDS = 300
_LOCAL_MFA_TICKETS: Dict[str, Dict[str, Any]] = {}
_LOCAL_TENANT_TICKETS: Dict[str, Dict[str, Any]] = {}

brute_force_protection = BruteForceProtection()


def _store_mfa_ticket(payload: Dict[str, Any]) -> str:
    ticket = secrets.token_urlsafe(32)
    payload = {
        **payload,
        "expires_at": time.time() + _MFA_TICKET_TTL_SECONDS,
    }
    _LOCAL_MFA_TICKETS[ticket] = payload

    cache_key_str = cache_key("mfa_ticket", ticket=ticket)
    set_cache(cache_key_str, payload, ttl=_MFA_TICKET_TTL_SECONDS)
    return ticket


def _consume_mfa_ticket(ticket: str) -> Optional[Dict[str, Any]]:
    cache_key_str = cache_key("mfa_ticket", ticket=ticket)
    cached = get_cache(cache_key_str)
    if cached:
        delete_cache(cache_key_str)
        return cached

    payload = _LOCAL_MFA_TICKETS.pop(ticket, None)
    if not payload:
        return None
    if payload.get("expires_at", 0) < time.time():
        return None
    return payload


def _store_tenant_ticket(payload: Dict[str, Any]) -> str:
    ticket = secrets.token_urlsafe(32)
    payload = {
        **payload,
        "expires_at": time.time() + _MFA_TICKET_TTL_SECONDS,
    }
    _LOCAL_TENANT_TICKETS[ticket] = payload

    cache_key_str = cache_key("tenant_ticket", ticket=ticket)
    set_cache(cache_key_str, payload, ttl=_MFA_TICKET_TTL_SECONDS)
    return ticket


def _consume_tenant_ticket(ticket: str) -> Optional[Dict[str, Any]]:
    cache_key_str = cache_key("tenant_ticket", ticket=ticket)
    cached = get_cache(cache_key_str)
    if cached:
        delete_cache(cache_key_str)
        return cached

    payload = _LOCAL_TENANT_TICKETS.pop(ticket, None)
    if not payload:
        return None
    if payload.get("expires_at", 0) < time.time():
        return None
    return payload


def _verify_mfa_code(user, mfa_code: str) -> bool:
    if not user.mfa_secret:
        return False


def _build_tenant_summaries(db: Session, tenant_users) -> list[dict]:
    tenant_ids = [tu.tenant_id for tu in tenant_users]
    tenants = (
        db.query(Tenant)
        .filter(Tenant.id.in_(tenant_ids))
        .all()
    )
    tenant_by_id = {str(tenant.id): tenant for tenant in tenants}
    summaries = []
    for tenant_user in tenant_users:
        tenant = tenant_by_id.get(str(tenant_user.tenant_id))
        if not tenant:
            continue
        summaries.append({
            "id": tenant.id,
            "name": tenant.name,
            "status": tenant.status,
        })
    return summaries
    try:
        import pyotp
    except Exception as exc:
        logger.error("pyotp is required for MFA verification: %s", exc)
        return False

    try:
        totp = pyotp.TOTP(user.mfa_secret)
        return bool(totp.verify(mfa_code, valid_window=1))
    except Exception as exc:
        logger.warning("Failed to verify MFA code: %s", exc)
        return False


def _issue_tokens(
    db: Session,
    user,
    tenant,
    role: str,
    request: Request,
    permissions_version: int,
) -> Dict[str, Any]:
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(tenant.id),
        "role": role,
        "type": "access",
        "permissions_version": permissions_version,
    }
    access_token = create_access_token(token_data)

    refresh_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(tenant.id),
        "permissions_version": permissions_version,
    }
    refresh_token = create_refresh_token(
        refresh_token_data,
        expires_delta=timedelta(days=30),
    )

    access_expires = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    refresh_expires = datetime.utcnow() + timedelta(days=30)

    try:
        SessionManager.create_session(
            db,
            user.id,
            tenant.id,
            access_token,
            refresh_token,
            access_expires,
            refresh_expires,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as session_error:
        logger.warning("Session creation failed (non-critical): %s", session_error)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": int(settings.JWT_EXPIRATION_HOURS * 3600),
    }


def perform_login(
    db: Session,
    email: str,
    password: str,
    request: Request,
    mfa_code: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Authenticate user and return token payload or MFA challenge."""
    client_ip = request.client.host if request.client else "unknown"

    if not brute_force_protection.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    lockout_check = brute_force_protection.check_lockout(email)
    if lockout_check["locked"]:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {lockout_check['remaining_seconds']} seconds.",
        )

    try:
        user = identity_service.IdentityService.authenticate_user(db, email, password)
        if not user:
            attempt_result = brute_force_protection.record_failed_attempt(email, client_ip)
            if attempt_result["locked"]:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked after {attempt_result.get('remaining_attempts', 0)} failed attempts.",
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        tenant_users = identity_service.IdentityService.get_user_tenant_memberships(db, user.id)
        if not tenant_users:
            brute_force_protection.record_failed_attempt(email, client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant assignments",
            )

        if user.mfa_enabled:
            if not mfa_code:
                mfa_ticket = _store_mfa_ticket({
                    "user_id": str(user.id),
                    "email": user.email,
                })
                try:
                    AuditService.log_login(
                        db,
                        email=user.email,
                        status="mfa_required",
                        user_id=user.id,
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent"),
                    )
                except Exception:
                    logger.warning("Failed to write MFA-required login log", exc_info=True)

                return {
                    "access_token": "",
                    "refresh_token": None,
                    "expires_in": 0,
                    "requires_mfa": True,
                    "mfa_ticket": mfa_ticket,
                    "user": user,
                    "tenant": None,
                    "requires_tenant_selection": False,
                    "tenant_ticket": None,
                    "tenants": None,
                }

            if not _verify_mfa_code(user, mfa_code):
                brute_force_protection.record_failed_attempt(email, client_ip)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code",
                )

        selected_tenant_user = None
        if tenant_id:
            selected_tenant_user = next(
                (tu for tu in tenant_users if str(tu.tenant_id) == str(tenant_id)),
                None,
            )
            if not selected_tenant_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not assigned to the specified tenant",
                )
        elif len(tenant_users) > 1:
            tenant_ticket = _store_tenant_ticket({
                "user_id": str(user.id),
                "tenant_ids": [str(tu.tenant_id) for tu in tenant_users],
            })
            return {
                "access_token": "",
                "refresh_token": None,
                "expires_in": 0,
                "requires_mfa": False,
                "mfa_ticket": None,
                "requires_tenant_selection": True,
                "tenant_ticket": tenant_ticket,
                "tenants": _build_tenant_summaries(db, tenant_users),
                "user": user,
                "tenant": None,
            }
        else:
            selected_tenant_user = tenant_users[0]

        tenant = identity_service.IdentityService.get_tenant_by_id(db, selected_tenant_user.tenant_id)
        if not tenant:
            brute_force_protection.record_failed_attempt(email, client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant not found",
            )

        tokens = _issue_tokens(
            db,
            user,
            tenant,
            selected_tenant_user.role,
            request,
            selected_tenant_user.permissions_version or 1,
        )
        brute_force_protection.clear_attempts(email)

        try:
            AuditService.log_login(
                db,
                email=user.email,
                status="success",
                user_id=user.id,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                mfa_used=bool(user.mfa_enabled),
                mfa_method="totp" if user.mfa_enabled else None,
            )
            AuditService.log_action(
                db,
                action="login_success",
                user_id=user.id,
                tenant_id=tenant.id,
                endpoint=request.url.path,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                metadata={"email": user.email},
                status="success",
            )
        except Exception:
            logger.warning("Failed to write login audit log", exc_info=True)

        return {
            **tokens,
            "requires_mfa": False,
            "mfa_ticket": None,
            "requires_tenant_selection": False,
            "tenant_ticket": None,
            "tenants": None,
            "user": user,
            "tenant": tenant,
        }
    except HTTPException as http_exc:
        try:
            AuditService.log_login(
                db,
                email=email,
                status="blocked" if http_exc.status_code == status.HTTP_423_LOCKED else "failed",
                failure_reason=str(http_exc.detail),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
            )
        except Exception:
            logger.warning("Failed to write login audit log", exc_info=True)
        raise
    except Exception as exc:
        logger.error("Login error: %s", exc, exc_info=True)
        brute_force_protection.record_failed_attempt(email, client_ip)
        try:
            AuditService.log_login(
                db,
                email=email,
                status="failed",
                failure_reason="login_error",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
            )
        except Exception:
            logger.warning("Failed to write login audit log", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        ) from exc


def verify_mfa_ticket(
    db: Session,
    request: Request,
    mfa_ticket: str,
    mfa_code: str,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = _consume_mfa_ticket(mfa_ticket)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA ticket",
        )

    try:
        user_id = UUID(payload["user_id"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA ticket",
        ) from exc

    user = identity_service.IdentityService.get_user_by_id(db, user_id)
    if not user or not user.mfa_enabled or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA verification failed",
        )

    if not _verify_mfa_code(user, mfa_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code",
        )

    tenant_users = identity_service.IdentityService.get_user_tenant_memberships(db, user.id)
    if not tenant_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no tenant assignments",
        )

    selected_tenant_user = None
    if tenant_id:
        selected_tenant_user = next(
            (tu for tu in tenant_users if str(tu.tenant_id) == str(tenant_id)),
            None,
        )
        if not selected_tenant_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to the specified tenant",
            )
    elif len(tenant_users) > 1:
        tenant_ticket = _store_tenant_ticket({
            "user_id": str(user.id),
            "tenant_ids": [str(tu.tenant_id) for tu in tenant_users],
        })
        return {
            "access_token": "",
            "refresh_token": None,
            "expires_in": 0,
            "requires_tenant_selection": True,
            "tenant_ticket": tenant_ticket,
            "tenants": _build_tenant_summaries(db, tenant_users),
            "user": user,
            "tenant": None,
        }
    else:
        selected_tenant_user = tenant_users[0]

    tenant = identity_service.IdentityService.get_tenant_by_id(db, selected_tenant_user.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant not found",
        )

    tokens = _issue_tokens(
        db,
        user,
        tenant,
        selected_tenant_user.role,
        request,
        selected_tenant_user.permissions_version or 1,
    )
    brute_force_protection.clear_attempts(user.email)

    try:
        AuditService.log_login(
            db,
            email=user.email,
            status="success",
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            mfa_used=True,
            mfa_method="totp",
        )
    except Exception:
        logger.warning("Failed to write MFA login audit log", exc_info=True)

    return {
        **tokens,
        "requires_tenant_selection": False,
        "tenant_ticket": None,
        "tenants": None,
        "user": user,
        "tenant": tenant,
    }


def verify_tenant_ticket(
    db: Session,
    request: Request,
    tenant_ticket: str,
    tenant_id: str,
) -> Dict[str, Any]:
    payload = _consume_tenant_ticket(tenant_ticket)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired tenant ticket",
        )

    user_id = payload.get("user_id")
    tenant_ids = payload.get("tenant_ids") or []
    if not user_id or str(tenant_id) not in tenant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant selection not allowed",
        )

    user = identity_service.IdentityService.get_user_by_id(db, UUID(user_id))
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not eligible for tenant selection",
        )

    tenant = identity_service.IdentityService.get_tenant_by_id(db, UUID(tenant_id))
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    tenant_users = identity_service.IdentityService.get_user_tenant_memberships(db, user.id)
    tenant_user = next((tu for tu in tenant_users if str(tu.tenant_id) == str(tenant_id)), None)
    if not tenant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not assigned to tenant",
        )

    tokens = _issue_tokens(
        db,
        user,
        tenant,
        tenant_user.role,
        request,
        tenant_user.permissions_version or 1,
    )
    return {
        **tokens,
        "requires_tenant_selection": False,
        "tenant_ticket": None,
        "tenants": None,
        "user": user,
        "tenant": tenant,
    }
