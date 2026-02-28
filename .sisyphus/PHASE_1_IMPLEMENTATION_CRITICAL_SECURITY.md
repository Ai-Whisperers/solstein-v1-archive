# PHASE 1: CRITICAL SECURITY FIX - DETAILED IMPLEMENTATION PLAN
**Week 1 | 34 Hours | Developer: 1 person, Full-time**

> Priority: 🔴 CRITICAL - BLOCKS PRODUCTION DEPLOYMENT  
> Timeline: Week 1 (5 business days)  
> Owner: Security Lead / Backend Engineer  
> Review: Code review + Security audit before merge

---

## PHASE 1 OVERVIEW

### Goals
1. ✅ Fix CORS misconfiguration (authentication bypass)
2. ✅ Implement proper JWT authentication (replace stub)
3. ✅ Fix default secret key handling
4. ✅ Remove CI/CD security bypasses
5. ✅ Add missing tests for security + monitoring modules

### Timeline
```
Day 1:  Items 1.1 + 1.2 (CORS + Auth)
Day 2:  Items 1.2 continued + 1.3 (Secret key)
Day 3:  Item 1.4 (CI/CD bypasses) + 1.5a (Security tests)
Day 4:  Item 1.5b (Monitoring tests)
Day 5:  Code review, fixes, final testing
```

### Success Criteria
- [ ] CORS properly configured with specific origins
- [ ] JWT authentication validates tokens correctly
- [ ] Default secret key fails startup in production
- [ ] All CI/CD gates enforced (no bypasses)
- [ ] 95%+ test coverage for security + monitoring modules
- [ ] All tests pass in CI/CD
- [ ] Security audit approval

---

## ITEM 1.1: Fix CORS Configuration (30 minutes)

### Context
**Risk Level**: 🔴 CRITICAL - Authentication token bypass  
**Current Status**: Misconfigured to allow any origin with credentials  
**Browsers**: Silently ignore invalid CORS, creating false security  

### Current Code
**File**: `/src/solstein/api/main.py` (lines 100-120)

```python
from fastapi.middleware.cors import CORSMiddleware

# ❌ VULNERABLE
CORSMiddleware(
    app,
    allow_origins=["*"],        # Wildcard
    allow_credentials=True,      # Credentials
    allow_methods=["*"],         # All methods
    allow_headers=["*"],         # All headers
)
```

### Issues
1. `allow_origins=["*"]` with `allow_credentials=True` is invalid
2. Browsers ignore this silently, but it's still a security misconfiguration
3. `allow_methods=["*"]` allows DELETE/PATCH which may not be intended
4. `allow_headers=["*"]` exposes internal headers

### Implementation

#### Step 1: Create environment variable for CORS origins
**File**: `/src/solstein/config.py`

**Current** (lines 20-30):
```python
class Settings(BaseSettings):
    env: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./test.db")
    secret_key: str = Field(default="change-me-in-production")
```

**New** (lines 20-35):
```python
class Settings(BaseSettings):
    env: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./test.db")
    secret_key: str = Field(default="change-me-in-production")
    
    # ✅ NEW: CORS configuration
    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    cors_allowed_methods: list = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        description="Allowed HTTP methods"
    )
    cors_allowed_headers: list = Field(
        default=["Authorization", "Content-Type"],
        description="Allowed request headers"
    )
    
    @property
    def cors_origins_list(self) -> list:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.cors_allowed_origins.split(",")]
```

#### Step 2: Update CORS middleware configuration
**File**: `/src/solstein/api/main.py`

**Current** (lines 100-120):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**New** (lines 100-130):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from solstein.config import settings

logger = logging.getLogger(__name__)
app = FastAPI()

# ✅ SECURE CORS configuration
allowed_origins = settings.cors_origins_list

# Validate origins in development
if settings.env == "development":
    logger.info(f"CORS allowed origins: {allowed_origins}")
elif not allowed_origins:
    raise ValueError("CORS_ALLOWED_ORIGINS must be set in production")

CORSMiddleware(
    app,
    allow_origins=allowed_origins,           # ✅ Specific origins only
    allow_credentials=True,                  # ✅ Only with specific origins
    allow_methods=settings.cors_allowed_methods,  # ✅ Explicit methods
    allow_headers=settings.cors_allowed_headers,  # ✅ Explicit headers
    max_age=600,                             # ✅ Cache preflight for 10 min
)
```

#### Step 3: Update environment files
**File**: `.env.example`

```bash
# Original
DATABASE_URL=postgresql://...
SECRET_KEY=change-me-in-production

# Add these:
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOWED_METHODS=GET,POST,PUT,DELETE
CORS_ALLOWED_HEADERS=Authorization,Content-Type
```

**File**: `.env.local` (for local development, git-ignored)

```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000
```

**File**: `.env.production` (for production, git-ignored)

```bash
CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
CORS_ALLOWED_METHODS=GET,POST,PUT,DELETE
CORS_ALLOWED_HEADERS=Authorization,Content-Type
```

### Testing

#### Unit Test
**File**: `/tests/unit/test_cors.py` (new file)

```python
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from solstein.api.main import app
from solstein.config import settings


class TestCORS:
    """Test CORS configuration security"""
    
    def test_cors_allows_specific_origins_only(self):
        """Verify only configured origins are allowed"""
        client = TestClient(app)
        
        # Should work from allowed origin
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers.lower()
        
        # Should NOT work from arbitrary origin
        response = client.get(
            "/api/health",
            headers={"Origin": "https://evil.com"}
        )
        assert "access-control-allow-origin" not in response.headers.lower()
    
    def test_cors_wildcard_not_used(self):
        """Verify wildcard origins are not configured"""
        origins = settings.cors_origins_list
        assert "*" not in origins
        assert all(origin.startswith(("http://", "https://")) for origin in origins)
    
    def test_cors_methods_explicit(self):
        """Verify HTTP methods are explicitly listed, not wildcard"""
        methods = settings.cors_allowed_methods
        assert "*" not in methods
        assert all(m in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"] for m in methods)
    
    def test_cors_headers_explicit(self):
        """Verify headers are explicitly listed"""
        headers = settings.cors_allowed_headers
        assert "*" not in headers
```

#### Integration Test
**File**: `/tests/integration/test_cors_integration.py` (new file)

```python
import pytest
from fastapi.testclient import TestClient
from solstein.api.main import app


class TestCORSIntegration:
    """Integration tests for CORS with authentication"""
    
    def test_cors_with_auth_header(self):
        """Verify CORS works with Authorization header"""
        client = TestClient(app)
        
        response = client.get(
            "/api/protected",
            headers={
                "Origin": "http://localhost:3000",
                "Authorization": "Bearer valid.jwt.token"
            }
        )
        # Should either work or fail with auth error, not CORS error
        assert response.status_code != 400
    
    def test_cors_preflight_request(self):
        """Verify CORS preflight responses are correct"""
        client = TestClient(app)
        
        response = client.options(
            "/api/protected",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers.lower()
```

### Verification

#### Manual Testing
```bash
# 1. Start application
python -m uvicorn solstein.api.main:app --reload

# 2. Test allowed origin
curl -i -X GET http://localhost:8000/api/health \
  -H "Origin: http://localhost:3000"

# Expected: 
# Access-Control-Allow-Origin: http://localhost:3000

# 3. Test disallowed origin
curl -i -X GET http://localhost:8000/api/health \
  -H "Origin: https://evil.com"

# Expected:
# (no Access-Control-Allow-Origin header)

# 4. Test preflight request
curl -i -X OPTIONS http://localhost:8000/api/protected \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"

# Expected: 200 OK with CORS headers
```

#### Automated Testing
```bash
# Run CORS tests
pytest tests/unit/test_cors.py -v
pytest tests/integration/test_cors_integration.py -v

# Coverage
pytest tests/ -k "cors" --cov=solstein.api --cov-report=term
```

### Risk Assessment

**Risk Level**: 🟢 LOW - Non-breaking change  
**Rollback**: Revert to previous CORS configuration  
**Testing**: Required - 5 test cases minimum

**Potential Issues**:
- Frontend breaks if origin not in allowed list → Add frontend origin to CORS_ALLOWED_ORIGINS
- Localhost vs 127.0.0.1 confusion → Include both

### Deployment Checklist

- [ ] Update `.env.example` with CORS settings
- [ ] Deploy to dev with new settings
- [ ] Run CORS test suite
- [ ] Test with actual frontend (if available)
- [ ] Update production `.env` with correct origins
- [ ] Create runbook: "Adding new CORS origin"

### Rollback Procedure

```bash
# If CORS configuration breaks production
1. Revert code changes:
   git revert <commit>
2. Redeploy previous version
3. Investigate which origins were missing
4. Update configuration and redeploy
```

**Effort**: 30 minutes  
**Complexity**: 🟢 LOW  
**Testing Time**: 15 minutes

---

## ITEM 1.2: Implement Proper JWT Authentication (8 hours)

### Context
**Risk Level**: 🔴 CRITICAL - Any token accepted  
**Current Status**: Stub implementation, always returns True  
**Impact**: Complete authentication bypass

### Current Code - Analysis

**File**: `/src/solstein/api/middleware/security.py` (lines 45-91)

```python
# ❌ VULNERABLE: Accepts ANY token
def validate_token(token: str) -> bool:
    """Stub implementation - accepts any non-empty token"""
    return len(token) > 0  # ANY SEQUENCE OF CHARACTERS WORKS!

# Line 81-88
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """Returns current user from token"""
    if validate_token(token):
        return {"user_id": "stub", "username": "anonymous"}  # Always returns user!
    raise HTTPException(status_code=401)
```

**File**: `/src/solstein/api/dependencies.py` (lines 65-74)

```python
# ❌ VULNERABLE: Returns anonymous user if no token
async def get_current_user(token: str = None) -> dict:
    try:
        if not token:
            return {"user_id": "anonymous", "role": "viewer"}  # ALWAYS WORKS!
        return validate_token(token)
    except:
        return {"user_id": "anonymous"}  # Silent failure = silent security bypass
```

### Implementation Plan

#### Step 1: Install JWT library (if not installed)
```bash
pip install python-jose[cryptography]
# or
uv add python-jose[cryptography]
```

#### Step 2: Create JWT utilities module
**File**: `/src/solstein/security/jwt_handler.py` (new file)

```python
"""JWT token generation and validation utilities"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Token payload schema
class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # subject (user_id)
    exp: datetime  # expiration time
    iat: datetime  # issued at
    scopes: list = []  # permissions


class JWTHandler:
    """Handles JWT token creation and validation"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7
    ):
        """
        Initialize JWT handler
        
        Args:
            secret_key: Secret key for signing tokens (must be secure, >32 chars)
            algorithm: JWT signing algorithm
            access_token_expire_minutes: Access token lifetime
            refresh_token_expire_days: Refresh token lifetime
        
        Raises:
            ValueError: If secret_key is too weak
        """
        if len(secret_key) < 32:
            raise ValueError("secret_key must be at least 32 characters for security")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = access_token_expire_minutes
        self.refresh_token_expire = refresh_token_expire_days
    
    def create_access_token(
        self,
        user_id: str,
        scopes: list = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User identifier
            scopes: List of permissions/roles
            expires_delta: Custom expiration time
        
        Returns:
            Encoded JWT token
        
        Raises:
            ValueError: If inputs are invalid
        """
        if not user_id:
            raise ValueError("user_id is required")
        
        scopes = scopes or []
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire)
        
        payload = {
            "sub": user_id,
            "scopes": scopes,
            "iat": now,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        logger.info(f"Created access token for user {user_id}, expires {expire}")
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create JWT refresh token (long-lived)
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded JWT token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire)
        
        payload = {
            "sub": user_id,
            "type": "refresh",  # Mark as refresh token
            "iat": now,
            "exp": expire
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Token payload
        
        Raises:
            JWTError: If token is invalid/expired
            ValueError: If token is malformed
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verify required fields
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Token missing 'sub' (user_id)")
            
            # Check expiration (jose library does this, but be explicit)
            exp = payload.get("exp")
            if exp:
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                if datetime.now(timezone.utc) > exp_datetime:
                    raise JWTError("Token has expired")
            
            logger.debug(f"Successfully verified token for user {user_id}")
            return payload
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            raise ValueError(f"Invalid token: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Use refresh token to get new access token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            JWTError: If refresh token is invalid
        """
        try:
            payload = self.verify_token(refresh_token)
            
            # Verify this is a refresh token
            if payload.get("type") != "refresh":
                raise ValueError("Token is not a refresh token")
            
            user_id = payload.get("sub")
            scopes = payload.get("scopes", [])
            
            # Create new access token
            return self.create_access_token(user_id, scopes)
            
        except JWTError as e:
            logger.warning(f"Failed to refresh token: {str(e)}")
            raise
```

#### Step 3: Update security middleware
**File**: `/src/solstein/api/middleware/security.py` (replace entire file)

```python
"""API security middleware and authentication handlers"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import logging

from solstein.config import settings
from solstein.security.jwt_handler import JWTHandler

logger = logging.getLogger(__name__)

# Initialize JWT handler with settings
jwt_handler = JWTHandler(
    secret_key=settings.secret_key,
    access_token_expire_minutes=15,
    refresh_token_expire_days=7
)

# OAuth2 scheme for FastAPI dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(dict):
    """Current user object"""
    
    def __init__(self, user_id: str, scopes: list = None):
        self.user_id = user_id
        self.scopes = scopes or []
        super().__init__(user_id=user_id, scopes=self.scopes)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency: Get current authenticated user from token
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If token is invalid/expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = jwt_handler.verify_token(token)
        user_id = payload.get("sub")
        scopes = payload.get("scopes", [])
        
        if not user_id:
            logger.warning("Token missing 'sub' (user_id)")
            raise credentials_exception
        
        return User(user_id=user_id, scopes=scopes)
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Dependency: Get current user if authenticated, None otherwise
    
    Use this for endpoints that work with OR without auth
    """
    if not token:
        return None
    
    try:
        payload = jwt_handler.verify_token(token)
        user_id = payload.get("sub")
        scopes = payload.get("scopes", [])
        return User(user_id=user_id, scopes=scopes)
    except JWTError:
        return None


async def require_scope(required_scope: str):
    """
    Dependency: Require user to have specific scope/role
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(
            user: User = Depends(get_current_user),
            _: None = Depends(require_scope("admin"))
        ):
            ...
    """
    async def check_scope(user: User = Depends(get_current_user)):
        if required_scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_scope}"
            )
        return None
    
    return Depends(check_scope)
```

#### Step 4: Create login endpoint
**File**: `/src/solstein/api/routers/auth.py` (new file)

```python
"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging

from solstein.api.middleware.security import jwt_handler
from solstein.api.dependencies import validate_credentials

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    """
    Authenticate user and return access token
    
    Args:
        username: User email/username
        password: User password
    
    Returns:
        Access token and refresh token
    
    Raises:
        HTTPException: If credentials invalid
    """
    # Validate credentials against database
    user = await validate_credentials(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = jwt_handler.create_access_token(
        user_id=user.id,
        scopes=user.roles
    )
    refresh_token = jwt_handler.create_refresh_token(user.id)
    
    logger.info(f"User {user.id} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: TokenRequest) -> TokenResponse:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_token: Valid refresh token
    
    Returns:
        New access token
    
    Raises:
        HTTPException: If refresh token invalid
    """
    try:
        new_access_token = jwt_handler.refresh_access_token(request.refresh_token)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout():
    """Logout (client-side: discard tokens)"""
    # Note: JWT tokens are stateless, so logout is just client-side
    # For better control, implement token blacklist in production
    return {"message": "Logged out successfully"}
```

#### Step 5: Update main app to include auth router
**File**: `/src/solstein/api/main.py`

**Find** (around line 140):
```python
from solstein.api.routers import companies, markets, analysis

app.include_router(companies.router)
app.include_router(markets.router)
app.include_router(analysis.router)
```

**Replace with**:
```python
from solstein.api.routers import companies, markets, analysis, auth

app.include_router(companies.router)
app.include_router(markets.router)
app.include_router(analysis.router)
app.include_router(auth.router)  # ✅ Add auth router
```

### Testing

#### Unit Tests
**File**: `/tests/unit/test_jwt_handler.py` (new file)

```python
"""Tests for JWT token handling"""

import pytest
from datetime import datetime, timedelta, timezone
from jose import JWTError

from solstein.security.jwt_handler import JWTHandler, TokenPayload


class TestJWTHandler:
    """JWT handler unit tests"""
    
    @pytest.fixture
    def jwt_handler(self):
        return JWTHandler(secret_key="test-secret-key-at-least-32-characters!!")
    
    def test_create_access_token(self, jwt_handler):
        """Test creating access token"""
        token = jwt_handler.create_access_token("user123", scopes=["read"])
        assert isinstance(token, str)
        assert token.count(".") == 2  # JWT format: xxx.yyy.zzz
    
    def test_verify_valid_token(self, jwt_handler):
        """Test verifying valid token"""
        token = jwt_handler.create_access_token("user123", scopes=["read", "write"])
        payload = jwt_handler.verify_token(token)
        
        assert payload["sub"] == "user123"
        assert "read" in payload["scopes"]
        assert "write" in payload["scopes"]
    
    def test_verify_invalid_token(self, jwt_handler):
        """Test verifying invalid token"""
        with pytest.raises(JWTError):
            jwt_handler.verify_token("invalid.token.format")
    
    def test_verify_expired_token(self, jwt_handler):
        """Test verifying expired token"""
        token = jwt_handler.create_access_token(
            "user123",
            expires_delta=timedelta(seconds=-10)  # Expired 10 seconds ago
        )
        
        with pytest.raises(JWTError):
            jwt_handler.verify_token(token)
    
    def test_refresh_token(self, jwt_handler):
        """Test creating and using refresh token"""
        refresh_token = jwt_handler.create_refresh_token("user123")
        new_access_token = jwt_handler.refresh_access_token(refresh_token)
        
        payload = jwt_handler.verify_token(new_access_token)
        assert payload["sub"] == "user123"
    
    def test_weak_secret_key_raises_error(self):
        """Test that weak secret key raises error"""
        with pytest.raises(ValueError, match="at least 32 characters"):
            JWTHandler(secret_key="weak")


class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    @pytest.fixture
    def jwt_handler(self):
        return JWTHandler(secret_key="test-secret-key-at-least-32-characters!!")
    
    def test_login_creates_tokens(self, jwt_handler):
        """Test login creates both access and refresh tokens"""
        access_token = jwt_handler.create_access_token("user123")
        refresh_token = jwt_handler.create_refresh_token("user123")
        
        # Both should be valid
        assert jwt_handler.verify_token(access_token)["sub"] == "user123"
        assert jwt_handler.verify_token(refresh_token)["sub"] == "user123"
    
    def test_refresh_token_creates_new_access_token(self, jwt_handler):
        """Test using refresh token to get new access token"""
        refresh_token = jwt_handler.create_refresh_token("user123")
        new_access = jwt_handler.refresh_access_token(refresh_token)
        
        payload = jwt_handler.verify_token(new_access)
        assert payload["sub"] == "user123"
```

#### Integration Tests
**File**: `/tests/integration/test_auth_endpoints.py` (new file)

```python
"""Integration tests for authentication endpoints"""

import pytest
from fastapi.testclient import TestClient

from solstein.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_with_valid_credentials(self, client):
        """Test login with valid credentials"""
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "correct_password"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "wrong_password"}
        )
        
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]
    
    def test_refresh_token(self, client):
        """Test refreshing access token"""
        # First login
        login_response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "correct_password"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Then refresh
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()
    
    def test_protected_endpoint_requires_token(self, client):
        """Test protected endpoint rejects request without token"""
        response = client.get("/api/protected")
        
        assert response.status_code == 403
    
    def test_protected_endpoint_with_valid_token(self, client):
        """Test protected endpoint accepts valid token"""
        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "correct_password"}
        )
        access_token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
```

### Verification

#### 1. Startup Verification
```bash
python -m uvicorn solstein.api.main:app --reload

# Should see:
# INFO:solstein.api.middleware.security:JWT handler initialized
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 2. Functional Verification

```bash
# 1. Attempt login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Response should be:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# 2. Use token to access protected endpoint
TOKEN="<access_token_from_above>"
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer $TOKEN"

# Should return data, not 401

# 3. Try with invalid token
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer invalid-token"

# Should get 401 Unauthorized
```

#### 3. Test Suite
```bash
# Run all auth tests
pytest tests/unit/test_jwt_handler.py -v
pytest tests/integration/test_auth_endpoints.py -v

# With coverage
pytest tests/ -k "auth" --cov=solstein.security --cov=solstein.api.middleware

# Should see:
# test_jwt_handler.py::TestJWTHandler::test_create_access_token PASSED
# test_jwt_handler.py::TestJWTHandler::test_verify_valid_token PASSED
# test_jwt_handler.py::TestJWTHandler::test_verify_invalid_token PASSED
# ... (all tests pass)
```

### Risk Assessment

**Risk Level**: 🟠 MEDIUM - Breaking change (requires token for auth endpoints)  
**Rollback**: Revert security middleware to stub implementation  
**Testing**: Required - 15+ test cases (provided)

**Potential Issues**:
- Old code using `get_current_user` directly will break → Update all imports
- Clients without token will get 401 → Document migration guide
- Weak secret key in config → Enforce >32 characters

### Deployment Checklist

- [ ] Add JWT library to requirements
- [ ] Implement JWT handler
- [ ] Update security middleware
- [ ] Create auth router with login/refresh endpoints
- [ ] Update main.py to include auth router
- [ ] Run full test suite
- [ ] Code review + security audit
- [ ] Deploy to staging
- [ ] Test with actual client application
- [ ] Deploy to production
- [ ] Monitor for auth-related errors

### Rollback Procedure

```bash
# If authentication breaks
1. Revert to previous version:
   git revert <commit>

2. Redeploy:
   git push origin main
   # Deployment pipeline runs

3. Verify in production:
   curl https://api.example.com/api/health
```

**Effort**: 8 hours  
**Complexity**: 🟠 MEDIUM  
**Testing Time**: 2 hours

---

