"""Environment template for SolStein configuration.

Extracted from config.py (STORY-079) to keep that file under the 500-line limit.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

ENV_TEMPLATE = """# SolStein Configuration
# Copy this file to .env and update values

# Environment
ENVIRONMENT=development
DEBUG=true

# Database (legacy, kept for SQLAlchemy compatibility)
DATABASE__URL=postgresql://<user>:<password>@localhost:5432/solstein
DATABASE__POOL_SIZE=20
DATABASE__ECHO=false

# Supabase
SUPABASE__URL=https://your-project.supabase.co
SUPABASE__KEY=sb_secret_your_key
SUPABASE__ANON_KEY=sb_publishable_your_key
SUPABASE__DB_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres

# Temporal
TEMPORAL__HOST_URL=localhost:7233
TEMPORAL__NAMESPACE=default
TEMPORAL__API_KEY=

# API
API__HOST=0.0.0.0
API__PORT=8000
API__DEBUG=true
API__CORS_ORIGINS=["http://localhost:3000"]
API__API_PREFIX=/api/v1

# Security
SECURITY__SECRET_KEY=replace-with-a-strong-32-char-min-secret
SECURITY__ALGORITHM=HS256
SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOGGING__LEVEL=INFO
LOGGING__FORMAT=json
LOGGING__FILE_PATH=data/output/logs/solstein.log
LOGGING__ROTATION="500 MB"
LOGGING__RETENTION="30 days"

# Data
DATA__DATA_DIR=data
DATA__CACHE_DIR=.cache
DATA__EXPORT_DIR=exports

# External APIs (optional)
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk_...
# FIREWORKS_API_KEY=fw_...
# PERPLEXITY_API_KEY=pplx-...  # (currently unused)

# Feature flags (safe cutover controls)
# FEATURE_NEW_CLASSIFIER=false
# FEATURE_NEW_READINESS_GATE=false
# FEATURE_NEW_UNIFIED_LOADER=false  # DEPRECATED (STORY-256): ignored by registry

# LLM Runtime (optional)
# LLM_PROVIDER=auto  # auto|ollama|fireworks|openai|groq|none
# OLLAMA_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2:latest
# OPENAI_MODEL=gpt-4o-mini
# GROQ_MODEL=llama-3.3-70b-versatile
# FIREWORKS_MODEL=qwen2-72b-instruct
"""


def create_env_template(output_path: Path = Path(".env.example")) -> None:
    """Create .env template file."""
    output_path.write_text(ENV_TEMPLATE)
    logger.info(f"Created environment template at {output_path}")
