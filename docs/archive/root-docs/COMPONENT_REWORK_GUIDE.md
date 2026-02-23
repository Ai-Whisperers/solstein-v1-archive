# 🔧 DETAILED COMPONENT REWORK GUIDE
**What Changes, What Stays, What Gets Deleted**

---

## 🎯 QUICK DECISION MATRIX

| Component | Status | Action | Why |
|-----------|--------|--------|-----|
| **PyProject Dependencies** | ❌ Keep some | **Update** | Remove SQLAlchemy, Alembic; keep FastAPI, agents |
| **FastAPI Routes** | ✅ Keep | **Refactor** | Remove DB logic, keep business logic |
| **SQLAlchemy ORM** | ❌ Delete | **DELETE** | Supabase handles persistence |
| **Alembic Migrations** | ❌ Delete | **DELETE** | Supabase migrations replace |
| **Agents** | ✅ Keep | **Update** | Change data destination to Supabase |
| **Scorers** | ✅ Keep | **Keep as-is** | Pure Python logic, no changes |
| **Supabase Client** | ✅ Keep | **Expand** | Build out service layer |
| **Frontend Auth** | ❌ Replace | **Replace JWT** | Use Supabase Auth |
| **Frontend API Calls** | ❌ Replace | **Replace endpoints** | Use Supabase JS client |
| **Real-time Features** | ✅ Add | **Add** | Supabase subscriptions |

---

## 📝 COMPONENT-BY-COMPONENT REWORK

### **1. DEPENDENCIES & PYPROJECT.TOML**

#### ❌ DELETE These Dependencies
```toml
[REMOVE from dependencies]
sqlalchemy>=2.0          # Supabase handles SQL
alembic>=1.12           # Supabase handles migrations
psycopg2-binary>=2.9    # Supabase handles connection
redis                   # May not be needed
celery                  # Being phased out (if using)
```

#### ✅ KEEP These Dependencies
```toml
[KEEP]
pydantic>=2.0           # Input validation
fastapi>=0.104          # API framework
uvicorn[standard]       # Server
supabase>=2.3           # DATABASE operations
aiohttp>=3.9            # HTTP client (for agents)
requests>=2.31          # Fallback HTTP
beautifulsoup4>=4.12    # Web scraping (agents)
lxml>=4.9               # XML parsing (agents)
```

#### ➕ ADD These Dependencies
```toml
[ADD]
postgrest>=0.12         # Postgrest SDK (better than raw supabase)
python-jose>=3.3        # For token validation (if needed)
python-multipart>=0.0   # Form parsing
httpx>=0.24             # Async HTTP (preferred over requests)
```

#### **Updated Dependencies Section:**
```toml
dependencies = [
    # Core
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "fastapi>=0.104",
    "uvicorn[standard]>=0.24",
    
    # Database (Supabase)
    "supabase>=2.3",
    "postgrest>=0.12",
    
    # External APIs & Data
    "aiohttp>=3.9",
    "httpx>=0.24",
    "requests>=2.31",
    "beautifulsoup4>=4.12",
    "lxml>=4.9",
    
    # Utilities
    "pandas>=2.0",
    "openpyxl>=3.1",
    "rich>=13.0",
    "loguru>=0.7",
    "python-dotenv>=1.0",
    "click>=8.1",
    "python-jose>=3.3",
]
```

---

### **2. BACKEND API LAYER (src/solstein/api/)**

#### **main.py - No Changes Needed**
```python
# ✅ KEEP: FastAPI app, routers, middleware
# ✅ KEEP: Lifespan events
# ✅ KEEP: Exception handlers
# ❌ REMOVE: Database session injection (no longer needed)

# Before:
app = FastAPI()
app.add_middleware(...)
@app.lifespan
async def lifespan(app):
    # Create DB pool
    yield
    # Close DB pool

# After:
app = FastAPI()
app.add_middleware(...)
@app.lifespan
async def lifespan(app):
    # Initialize Supabase client
    get_supabase()
    yield
    # (Supabase auto-closes)
```

#### **routers/companies.py - Refactor**
```python
# BEFORE (with database logic):
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from solstein.core.database_models import Company

@router.get("/companies")
async def get_companies(db: AsyncSession = Depends()):
    stmt = select(Company).limit(100)
    result = await db.execute(stmt)
    return result.scalars().all()

# AFTER (with Supabase service layer):
from solstein.services.company_service import CompanyService

@router.get("/companies")
async def get_companies(service: CompanyService = Depends()):
    companies = await service.get_companies(limit=100)
    return companies
```

#### **routers/scoring.py - Refactor**
```python
# BEFORE:
@router.post("/score")
async def calculate_score(
    company_id: str,
    db: AsyncSession = Depends()
):
    company = db.query(Company).filter(...).first()
    signals = db.query(Signal).filter(...).all()
    # Calculate score...
    db.add(CompanyScore(...))
    await db.commit()

# AFTER:
@router.post("/score")
async def calculate_score(
    company_id: str,
    service: ScoreService = Depends()
):
    signals = await service.get_signals(company_id)
    # Calculate score (pure Python)...
    await service.save_score(company_id, score_result)
    return score_result
```

#### **All Routers Pattern:**
```python
# OLD PATTERN (BAD):
class CompanyRouter:
    async def get_companies(self, db: Session):
        return db.query(Company).all()  # Direct DB access

# NEW PATTERN (GOOD):
class CompanyRouter:
    async def get_companies(self, service: CompanyService = Depends()):
        return await service.get_companies()  # Via service layer
```

---

### **3. SERVICE LAYER (NEW) - src/solstein/services/**

#### **CREATE: supabase_service.py**
```python
"""Supabase interaction layer - handles all database access."""

from supabase import Client
from solstein.core.supabase_client import get_supabase

class SupabaseService:
    """Base service for Supabase operations."""
    
    def __init__(self, client: Client = Depends(get_supabase)):
        self.client = client
    
    async def get_one(self, table: str, id: str):
        """Get single record."""
        result = await self.client.table(table).select("*").eq("id", id).single()
        return result.data
    
    async def get_many(self, table: str, filters: dict = None, limit: int = 100):
        """Get multiple records."""
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        result = await query.limit(limit)
        return result.data
    
    async def insert(self, table: str, data: dict):
        """Insert record."""
        result = await self.client.table(table).insert([data])
        return result.data[0]
    
    async def update(self, table: str, id: str, data: dict):
        """Update record."""
        result = await self.client.table(table).update(data).eq("id", id)
        return result.data[0]
    
    async def delete(self, table: str, id: str):
        """Delete record."""
        await self.client.table(table).delete().eq("id", id)
```

#### **CREATE: company_service.py**
```python
"""Company data operations."""

from solstein.services.supabase_service import SupabaseService

class CompanyService(SupabaseService):
    """Handle company-related database operations."""
    
    async def get_companies(self, limit: int = 100):
        """Get all companies."""
        return await self.get_many("companies", limit=limit)
    
    async def get_company(self, company_id: str):
        """Get single company."""
        return await self.get_one("companies", company_id)
    
    async def search_companies(self, query: str):
        """Full-text search companies."""
        # Uses Supabase full-text search
        result = await self.client.table("companies").select("*").ilike("name", f"%{query}%")
        return result.data
    
    async def update_company(self, company_id: str, data: dict):
        """Update company data."""
        return await self.update("companies", company_id, {
            **data,
            "last_updated": datetime.now().isoformat()
        })
```

#### **CREATE: score_service.py**
```python
"""Scoring data operations."""

from solstein.services.supabase_service import SupabaseService

class ScoreService(SupabaseService):
    """Handle scoring-related database operations."""
    
    async def get_signals(self, company_id: str) -> list:
        """Get all signals for company."""
        return await self.get_many("signals", filters={"company_id": company_id})
    
    async def save_signal(self, company_id: str, signal_data: dict):
        """Save signal extracted from external source."""
        return await self.insert("signals", {
            "company_id": company_id,
            **signal_data
        })
    
    async def save_score(self, company_id: str, score_result: dict):
        """Save calculated score."""
        return await self.insert("company_scores", {
            "company_id": company_id,
            "calculated_at": datetime.now().isoformat(),
            "overall_score": score_result["overall_score"],
            "growth_momentum_score": score_result["growth"],
            "financial_health_score": score_result["financial"],
            "competitive_position_score": score_result["competitive"],
            "classification": classify(score_result["overall_score"]),
            "confidence": score_result["confidence"],
            "signal_summary": score_result["signals"],
            "methodology_version": "1.0"
        })
    
    async def get_company_score(self, company_id: str):
        """Get latest score for company."""
        result = await self.client.table("company_scores").select("*").eq("company_id", company_id).order("calculated_at", desc=True).limit(1).single()
        return result.data
```

#### **CREATE: signal_service.py**
```python
"""Signal storage and retrieval."""

from solstein.services.supabase_service import SupabaseService

class SignalService(SupabaseService):
    """Handle signal operations."""
    
    async def save_signals_batch(self, company_id: str, signals: list):
        """Save multiple signals at once."""
        prepared = [
            {
                "company_id": company_id,
                **signal
            }
            for signal in signals
        ]
        result = await self.client.table("signals").insert(prepared)
        return result.data
```

---

### **4. AGENTS LAYER (src/solstein/agents/)**

#### **Pattern Change: Remove Database Writes, Keep Data Transformation**
```python
# BEFORE (WRONG - Agent writes to DB):
class GitHubAgent(BaseDataGatheringAgent):
    async def execute(self, company: Company):
        data = await self.fetch_github(company)
        # ❌ BAD: Agent writes to database
        db.add(Signal(...))
        await db.commit()
        return data

# AFTER (CORRECT - Agent returns data, router saves):
class GitHubAgent(BaseDataGatheringAgent):
    async def execute(self, company: Company) -> list[dict]:
        data = await self.fetch_github(company)
        # ✅ GOOD: Agent only transforms data
        return self._transform_to_signals(data)
```

#### **Updated Agent Structure:**
```python
class GitHubAgent(BaseDataGatheringAgent):
    """Fetch GitHub data, return signal format."""
    
    async def execute(self, company: Company) -> dict:
        """Fetch and transform GitHub data."""
        try:
            repo_data = await self.fetch_repo(company.github_url)
            # Transform to signal format
            return {
                "category": "technical",
                "signal_name": "github_stars",
                "signal_value": repo_data["stars"],
                "source": "github-api",
                "raw_data": repo_data
            }
        except Exception as e:
            logger.error(f"GitHub agent failed: {e}")
            raise

# Router calls agent and saves:
@router.post("/refresh/{company_id}")
async def refresh_company(company_id: str, service: SignalService = Depends()):
    agent = GitHubAgent()
    signals = await agent.execute(company)
    # Router saves signals to Supabase
    await service.save_signals_batch(company_id, [signals])
```

#### **All 10 Agents - Same Pattern:**
```python
# 1. GitHubAgent - GitHub API → signals
# 2. CompaniesHouseAgent - Companies House API → signals
# 3. WebSearchAgent - Web search → signals
# 4. LinkedInAgent - LinkedIn data → signals
# 5. SECEdgarAgent - SEC filings → signals
# 6. PatentsAgent - Patent data → signals
# 7. NewsAgent - News APIs → signals
# 8. JobsAgent - Job boards → signals
# 9. TechTrendsAgent - Tech trends → signals
# 10. WebsiteAgent - Website analysis → signals

# ALL: Fetch external data, transform to signal format, return
# NONE: Write to database (router does that)
```

---

### **5. DATABASE LAYER (COMPLETE REWORK)**

#### **❌ DELETE THESE FILES**
```
src/solstein/core/database.py          # No longer used
src/solstein/core/database_models.py   # SQLAlchemy ORM
src/solstein/core/database_service.py  # Old database service
alembic/                               # All migrations
alembic.ini                            # Alembic config
```

#### **✅ REPLACE WITH SUPABASE MIGRATIONS**
```bash
# Instead of Alembic migrations, use Supabase SQL:

supabase/migrations/
├── 001_initial_schema.sql
│   ├── CREATE TABLE users (Supabase managed)
│   ├── CREATE TABLE companies (...)
│   ├── CREATE TABLE company_scores (...)
│   ├── CREATE TABLE signals (...)
│   └── CREATE TABLE market_snapshots (...)
│
├── 002_rls_policies.sql
│   ├── ALTER TABLE companies ENABLE ROW LEVEL SECURITY
│   ├── CREATE POLICY users_see_own_companies ON companies
│   └── CREATE POLICY admins_see_all ON companies
│
├── 003_indexes.sql
│   ├── CREATE INDEX companies_name_idx ON companies(name)
│   ├── CREATE INDEX signals_company_id_idx ON signals(company_id)
│   └── CREATE INDEX scores_company_id_idx ON company_scores(company_id)
│
└── 004_full_text_search.sql
    ├── CREATE TSVECTOR companies_search
    └── CREATE INDEX companies_search_idx
```

#### **✅ KEEP supabase_client.py**
```python
# This file is now THE main database interface
# Expand it from 37 lines to include service layer

from supabase import Client, create_client

class SupabaseConnection:
    _instance: Client | None = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            settings = get_settings()
            cls._instance = create_client(
                settings.supabase.url,
                settings.supabase.key
            )
        return cls._instance

def get_supabase() -> Client:
    return SupabaseConnection.get_client()
```

---

### **6. FRONTEND LAYER (dashboard/)**

#### **❌ REMOVE**
```typescript
// DELETE: Custom API client for backend
// DELETE: JWT token handling
// DELETE: Manual auth state management

// Before:
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Authorization': `Bearer ${token}`
    }
})

// After:
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
```

#### **✅ ADD**
```typescript
// NEW: Supabase client initialization
// NEW: Supabase Auth provider
// NEW: Real-time subscriptions
// NEW: RLS-aware queries

// File: src/lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

export default supabase

// File: src/app/layout.tsx
import { SupabaseProvider } from '@/components/SupabaseProvider'

export default function RootLayout() {
    return (
        <html>
            <body>
                <SupabaseProvider>
                    {/* All pages */}
                </SupabaseProvider>
            </body>
        </html>
    )
}

// File: src/app/(auth)/login/page.tsx
import { supabase } from '@/lib/supabase/client'

export default function LoginPage() {
    const handleLogin = async (email: string, password: string) => {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
        })
        // Supabase handles everything
    }
}

// File: src/app/(protected)/companies/page.tsx
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase/client'

export default function CompaniesPage() {
    const [companies, setCompanies] = useState([])
    
    useEffect(() => {
        // Real-time subscription
        const subscription = supabase
            .from('companies')
            .on('*', (payload) => {
                setCompanies(prev => [...prev, payload.new])
            })
            .subscribe()
        
        return () => subscription.unsubscribe()
    }, [])
    
    return (
        // Real-time updated list
    )
}
```

#### **Migration Timeline:**
```
Week 1:
├─ Install @supabase/supabase-js
├─ Create Supabase provider
└─ Update environment variables

Week 2:
├─ Migrate auth to Supabase Auth
├─ Update login/signup pages
└─ Update session management

Week 3:
├─ Replace all API calls with Supabase queries
├─ Add real-time subscriptions
└─ Add search functionality

Week 4:
├─ Remove custom JWT handling
├─ Remove custom API client
└─ Full integration tests
```

---

### **7. CONFIGURATION (src/solstein/config.py)**

#### **❌ REMOVE THESE**
```python
# REMOVE: DatabaseConfig
class DatabaseConfig(BaseModel):
    url: str = Field(...)  # No longer needed
    pool_size: int = Field(...)  # Supabase manages
    echo: bool = Field(...)  # Not applicable

# REMOVE: RedisConfig (unless caching on backend)
class RedisConfig(BaseModel):
    url: str = Field(...)  # Not needed
    cache_ttl: int = Field(...)  # Not needed

# REMOVE: TemporalConfig (if not using)
class TemporalConfig(BaseModel):
    host_url: str = Field(...)  # Not used
```

#### **✅ KEEP & UPDATE**
```python
# KEEP: SupabaseConfig (expand it)
class SupabaseConfig(BaseModel):
    """Supabase configuration - now primary database."""
    
    url: str = Field(...)           # Supabase project URL
    key: str = Field(...)           # Service role key (backend only)
    anon_key: str = Field(...)      # Anon key (frontend only)
    jwt_secret: str = Field(...)    # Optional: if validating tokens

# KEEP: APIConfig
class APIConfig(BaseModel):
    """API configuration."""
    # No changes needed

# KEEP: SecurityConfig
class SecurityConfig(BaseModel):
    """Security configuration."""
    # Can use Supabase JWT validation instead of custom
    # Optional: keep if custom validation needed
```

#### **Environment Variables:**
```bash
# BEFORE:
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
TEMPORAL_HOST=localhost:7233

# AFTER:
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ0eXAiOiJKV1QiLCJhbGc...  (service role)
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGc...  (anon key)
```

---

## 📊 SUMMARY TABLE

| File/Directory | Current | Action | Effort |
|---|---|---|---|
| `pyproject.toml` | 114 lines | Update dependencies | 1 day |
| `src/solstein/api/routers/` | 1,098 lines | Refactor to use services | 3 days |
| `src/solstein/services/` | NEW | Create service layer | 2 days |
| `src/solstein/agents/` | 60 agents | Update to return data | 1 day |
| `src/solstein/core/database.py` | 48 lines | ❌ DELETE | - |
| `src/solstein/core/database_models.py` | 52 lines | ❌ DELETE | - |
| `src/solstein/core/database_service.py` | 43 lines | ❌ DELETE | - |
| `src/solstein/core/supabase_client.py` | 37 lines | Keep & expand | 1 day |
| `src/solstein/config.py` | 369 lines | Update (remove DB config) | 1 day |
| `alembic/` | Many files | ❌ DELETE | - |
| `dashboard/` | 476+ files | Update auth & API calls | 5 days |
| `supabase/migrations/` | NEW | Create SQL migrations | 1 day |

**Total Effort: ~2 weeks for full migration**

---

**Ready for component-by-component implementation.**

🔧 **REWORK COMPLETE. START WITH SERVICES LAYER.**
