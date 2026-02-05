import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Users storage (JSON file - يمكن تحويله لـ DB لاحقاً)
USERS_FILE = "memory/users.json"

# Default roles
ROLES = {
    "viewer": {"tools": [], "approve": False},
    "dev": {"tools": ["read_file", "check_service"], "approve": False},
    "devops": {"tools": ["read_file", "check_service", "run_shell"], "approve": True},
    "admin": {"tools": ["*"], "approve": True},
}

def load_users() -> Dict:
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        # Create default admin user
        default_users = {
            "admin@example.com": {
                "email": "admin@example.com",
                "password_hash": pwd_context.hash("admin123"),  # Change this!
                "name": "Admin",
                "role": "admin",
                "created_at": datetime.utcnow().isoformat(),
            }
        }
        save_users(default_users)
        return default_users
    
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: Dict):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user"""
    users = load_users()
    user = users.get(email)
    
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    return {
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }

def create_user(email: str, password: str, name: str, role: str = "viewer") -> Dict:
    """Create new user"""
    users = load_users()
    
    if email in users:
        raise ValueError("User already exists")
    
    if role not in ROLES:
        raise ValueError(f"Invalid role. Must be one of: {list(ROLES.keys())}")
    
    users[email] = {
        "email": email,
        "password_hash": get_password_hash(password),
        "name": name,
        "role": role,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    save_users(users)
    return users[email]

def check_permission(user_role: str, tool_name: str) -> bool:
    """Check if user has permission to use a tool"""
    if user_role not in ROLES:
        return False
    
    allowed_tools = ROLES[user_role]["tools"]
    if "*" in allowed_tools:
        return True
    
    return tool_name in allowed_tools

def can_approve(user_role: str) -> bool:
    """Check if user can approve actions"""
    if user_role not in ROLES:
        return False
    return ROLES[user_role]["approve"]

