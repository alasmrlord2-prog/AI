"""Billing API endpoints."""
from fastapi import APIRouter, Depends
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/invoices")
def get_invoices(current_user: dict = Depends(get_current_user)):
    """Get all invoices."""
    # Mock data for now - replace with actual database queries
    invoices = [
        {
            "id": "inv_001",
            "tenant_id": "tenant_1",
            "tenant_name": "Acme Corp",
            "amount": 1500.00,
            "currency": "USD",
            "status": "paid",
            "due_date": "2024-01-15",
            "created_at": "2024-01-01T00:00:00Z",
            "items": [
                {"description": "Basic Plan - January", "quantity": 1, "price": 1500.00}
            ]
        },
        {
            "id": "inv_002",
            "tenant_id": "tenant_2",
            "tenant_name": "Tech Solutions",
            "amount": 2500.00,
            "currency": "USD",
            "status": "pending",
            "due_date": "2024-02-15",
            "created_at": "2024-02-01T00:00:00Z",
            "items": [
                {"description": "Pro Plan - February", "quantity": 1, "price": 2500.00}
            ]
        },
        {
            "id": "inv_003",
            "tenant_id": "tenant_3",
            "tenant_name": "Startup Inc",
            "amount": 500.00,
            "currency": "USD",
            "status": "overdue",
            "due_date": "2024-01-10",
            "created_at": "2023-12-15T00:00:00Z",
            "items": [
                {"description": "Starter Plan - December", "quantity": 1, "price": 500.00}
            ]
        }
    ]
    return {"invoices": invoices}


@router.get("/subscriptions")
def get_subscriptions(current_user: dict = Depends(get_current_user)):
    """Get all subscriptions."""
    # Mock data for now - replace with actual database queries
    subscriptions = [
        {
            "id": "sub_001",
            "tenant_id": "tenant_1",
            "tenant_name": "Acme Corp",
            "plan": "Basic",
            "status": "active",
            "current_period_start": "2024-01-01",
            "current_period_end": "2024-02-01",
            "amount": 1500.00,
            "currency": "USD"
        },
        {
            "id": "sub_002",
            "tenant_id": "tenant_2",
            "tenant_name": "Tech Solutions",
            "plan": "Pro",
            "status": "active",
            "current_period_start": "2024-02-01",
            "current_period_end": "2024-03-01",
            "amount": 2500.00,
            "currency": "USD"
        },
        {
            "id": "sub_003",
            "tenant_id": "tenant_3",
            "tenant_name": "Startup Inc",
            "plan": "Starter",
            "status": "cancelled",
            "current_period_start": "2023-12-01",
            "current_period_end": "2024-01-01",
            "amount": 500.00,
            "currency": "USD"
        }
    ]
    return {"subscriptions": subscriptions}


@router.get("/payment-methods")
def get_payment_methods(current_user: dict = Depends(get_current_user)):
    """Get payment methods."""
    # Mock data for now - replace with actual database queries
    payment_methods = [
        {
            "id": "pm_001",
            "type": "card",
            "last4": "4242",
            "brand": "Visa",
            "expiry_month": 12,
            "expiry_year": 2025,
            "is_default": True
        },
        {
            "id": "pm_002",
            "type": "card",
            "last4": "8888",
            "brand": "Mastercard",
            "expiry_month": 6,
            "expiry_year": 2026,
            "is_default": False
        },
        {
            "id": "pm_003",
            "type": "manual",
            "is_default": False,
            "account_name": "Cash Payment",
            "account_number": "N/A"
        },
        {
            "id": "pm_004",
            "type": "electronic",
            "is_default": False,
            "provider": "Payment Gateway API",
            "account_name": "Electronic Payment",
            "account_number": "EP-2024-001"
        },
        {
            "id": "pm_005",
            "type": "bank_transfer",
            "is_default": False,
            "bank_name": "البنك المركزي",
            "account_name": "Company Account",
            "account_number": "1234567890"
        },
        {
            "id": "pm_006",
            "type": "sham_cash",
            "is_default": False,
            "account_name": "Sham Cash Wallet",
            "account_number": "SC-987654321"
        }
    ]
    return {"payment_methods": payment_methods}


@router.post("/payment-methods/{payment_method_id}/set-default")
def set_default_payment_method(payment_method_id: str, current_user: dict = Depends(get_current_user)):
    """Set a payment method as default."""
    # Mock implementation - in real app, update database
    return {"success": True, "message": f"Payment method {payment_method_id} set as default"}

