import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict

try:
    from jose import JWTError, jwt
    JWT_AVAILABLE = True
except ImportError:
    print("Warning: python-jose not available, using fallback")
    JWT_AVAILABLE = False
    class JWTError(Exception):
        pass
    def jwt_encode(data, key, algorithm):
        import base64
        import hmac
        payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip('=')
        sig = hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{sig}"
    def jwt_decode(token, key, algorithm):
        import base64
        parts = token.split('.')
        if len(parts) != 2:
            raise JWTError("Invalid token")
        payload = parts[0]
        sig = parts[1]
        expected_sig = hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if sig != expected_sig:
            raise JWTError("Invalid signature")
        decoded = base64.urlsafe_b64decode(payload + '==').decode()
        return json.loads(decoded)

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    BCRYPT_AVAILABLE = True
except ImportError:
    print("Warning: passlib not available, using fallback")
    BCRYPT_AVAILABLE = False
    class CryptContext:
        def hash(self, password):
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()
        def verify(self, plain, hashed):
            import hashlib
            return hashlib.sha256(plain.encode()).hexdigest() == hashed
    pwd_context = CryptContext()

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
    try:
        if not os.path.exists(USERS_FILE):
            # Create default admin user
            default_password = "admin123"
            if BCRYPT_AVAILABLE:
                password_hash = pwd_context.hash(default_password)
            else:
                import hashlib
                password_hash = hashlib.sha256(default_password.encode()).hexdigest()
            
            default_users = {
                "admin@example.com": {
                    "email": "admin@example.com",
                    "password_hash": password_hash,
                    "name": "Admin",
                    "role": "admin",
                    "created_at": datetime.utcnow().isoformat(),
                }
            }
            save_users(default_users)
            return default_users
        
        # File exists, load it
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        import traceback
        traceback.print_exc()
        return {}

def save_users(users: Dict):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    try:
        if BCRYPT_AVAILABLE:
            return pwd_context.verify(plain_password, hashed_password)
        else:
            # Fallback: simple hash comparison
            import hashlib
            test_hash = hashlib.sha256(plain_password.encode()).hexdigest()
            return test_hash == hashed_password
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

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
    
    to_encode.update({"exp": int(expire.timestamp())})
    if JWT_AVAILABLE:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else:
        encoded_jwt = jwt_encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        if JWT_AVAILABLE:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt_decode(token, SECRET_KEY, ALGORITHM)
            # Check expiration
            if "exp" in payload:
                exp_time = datetime.fromtimestamp(payload["exp"])
                if datetime.utcnow() > exp_time:
                    return None
        return payload
    except (JWTError, Exception) as e:
        print(f"Token verification error: {e}")
        return None

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user"""
    try:
        users = load_users()
        if not users:
            print("No users found, creating default admin...")
            users = load_users()  # Try again after creation
        
        user = users.get(email)
        
        if not user:
            print(f"User not found: {email}")
            print(f"Available users: {list(users.keys())}")
            return None
        
        # Debug: print hash comparison
        stored_hash = user.get("password_hash", "")
        is_valid = verify_password(password, stored_hash)
        
        if not is_valid:
            print(f"Password verification failed for {email}")
            # Try to rehash if using fallback
            if not BCRYPT_AVAILABLE:
                import hashlib
                test_hash = hashlib.sha256(password.encode()).hexdigest()
                if test_hash == stored_hash:
                    print("Password matches with fallback method")
                    is_valid = True
        
        if not is_valid:
            return None
        
        return {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }
    except Exception as e:
        print(f"Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return None

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

