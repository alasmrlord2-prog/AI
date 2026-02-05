"""Identity Service - Business logic for Users, Tenants, Sessions."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import secrets

from app.identity.models import User, Tenant, TenantUser, Session, APIToken, Department, Project
from app.identity.schemas import (
    UserCreate, UserUpdate, TenantCreate, TenantUpdate,
    TenantUserCreate, APITokenCreate
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import get_settings

settings = get_settings()


class IdentityService:
    """Service for managing identity (users, tenants, sessions)."""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")

        # Create user
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            status="pending"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # If tenant_id provided, create TenantUser relationship
        if user_data.tenant_id:
            tenant_user = TenantUser(
                tenant_id=user_data.tenant_id,
                user_id=user.id,
                role="member",
                status="active"
            )
            db.add(tenant_user)
            db.commit()

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def list_users(db: Session, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users with pagination."""
        return db.query(User).offset(offset).limit(limit).all()

    @staticmethod
    def count_users(db: Session) -> int:
        """Get total count of users."""
        return db.query(User).count()

    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        if user.status != "active":
            return None

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def create_tenant(db: Session, tenant_data: TenantCreate) -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(
            name=tenant_data.name,
            type=tenant_data.type,
            contact_email=tenant_data.contact_email,
            contact_phone=tenant_data.contact_phone,
            status="trial"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant

    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    @staticmethod
    def update_tenant(db: Session, tenant_id: UUID, tenant_data: TenantUpdate) -> Optional[Tenant]:
        """Update tenant."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return None

        update_data = tenant_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)

        tenant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(tenant)
        return tenant

    @staticmethod
    def get_tenant_users(db: Session, tenant_id: UUID) -> List[TenantUser]:
        """Get all users for a tenant."""
        return db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.status == "active"
        ).all()

    @staticmethod
    def add_user_to_tenant(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        role: str = "member"
    ) -> TenantUser:
        """Add user to tenant."""
        # Check if already exists
        existing = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()

        if existing:
            existing.role = role
            existing.status = "active"
            db.commit()
            db.refresh(existing)
            return existing

        tenant_user = TenantUser(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            status="active",
            accepted_at=datetime.utcnow()
        )
        db.add(tenant_user)
        db.commit()
        db.refresh(tenant_user)
        return tenant_user

    @staticmethod
    def create_session(
        db: Session,
        user_id: UUID,
        token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_hours: int = 24
    ) -> Session:
        """Create a new session."""
        session = Session(
            user_id=user_id,
            token=token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_active_sessions(db: Session, user_id: UUID) -> List[Session]:
        """Get all active sessions for a user."""
        return db.query(Session).filter(
            Session.user_id == user_id,
            Session.is_active == True,
            Session.expires_at > datetime.utcnow()
        ).all()

    @staticmethod
    def get_all_sessions(db: Session, user_id: UUID) -> List[Session]:
        """Get all sessions for a user (including expired and revoked)."""
        return db.query(Session).filter(
            Session.user_id == user_id
        ).order_by(Session.created_at.desc()).all()

    @staticmethod
    def revoke_session(db: Session, session_id: UUID) -> bool:
        """Revoke a session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return False

        session.is_active = False
        db.commit()
        return True

    @staticmethod
    def create_api_token(
        db: Session,
        user_id: UUID,
        token_data: APITokenCreate
    ) -> tuple[APIToken, str]:
        """Create API token and return token object + plain token."""
        # Generate token
        plain_token = secrets.token_urlsafe(32)
        token_hash = get_password_hash(plain_token)  # Hash the token

        api_token = APIToken(
            user_id=user_id,
            tenant_id=token_data.tenant_id,
            name=token_data.name,
            token_hash=token_hash,
            scopes=",".join(token_data.scopes) if token_data.scopes else None,
            expires_at=token_data.expires_at,
            is_active=True
        )
        db.add(api_token)
        db.commit()
        db.refresh(api_token)

        # Return token object and plain token (only shown once)
        return api_token, plain_token

    @staticmethod
    def verify_api_token(db: Session, token: str) -> Optional[APIToken]:
        """Verify API token."""
        # Get all active tokens and check hash
        tokens = db.query(APIToken).filter(
            APIToken.is_active == True,
            APIToken.expires_at > datetime.utcnow() if APIToken.expires_at else True
        ).all()

        for api_token in tokens:
            if verify_password(token, api_token.token_hash):
                # Update last used
                api_token.last_used_at = datetime.utcnow()
                db.commit()
                return api_token

        return None

    @staticmethod
    def create_department(
        db: Session,
        tenant_id: UUID,
        name: str,
        description: Optional[str] = None,
        parent_department_id: Optional[UUID] = None
    ) -> Department:
        """Create a department."""
        department = Department(
            tenant_id=tenant_id,
            name=name,
            description=description,
            parent_department_id=parent_department_id
        )
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def create_project(
        db: Session,
        tenant_id: UUID,
        name: str,
        description: Optional[str] = None,
        department_id: Optional[UUID] = None
    ) -> Project:
        """Create a project."""
        project = Project(
            tenant_id=tenant_id,
            department_id=department_id,
            name=name,
            description=description
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

