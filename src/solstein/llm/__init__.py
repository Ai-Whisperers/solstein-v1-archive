"""LLM module with health checking and failover.

Provides enhanced LLM clients with:
- Proactive health monitoring
- Automatic provider failover
- Rate limit detection and handling
- Credit/quota exhaustion detection
- Cost tracking per request

Usage:
    from ..llm import get_enhanced_llm_client, ProviderHealthChecker

    client = get_enhanced_llm_client()
    result = await client.generate("Your prompt here")
"""

from .enhanced_client import (
    EnhancedLLMClient,
    LLMGenerationError,
    UsageTracker,
    get_enhanced_llm_client,
    get_usage_tracker,
    reset_usage_tracker,
)
from .health_checker import (
    ProviderError,
    ProviderErrorType,
    ProviderHealth,
    ProviderHealthChecker,
    ProviderStatus,
    get_health_checker,
    reset_health_checker,
)

__all__ = [
    # Enhanced client
    "EnhancedLLMClient",
    "LLMGenerationError",
    "get_enhanced_llm_client",
    # Usage tracking
    "UsageTracker",
    "get_usage_tracker",
    "reset_usage_tracker",
    # Health checking
    "ProviderHealthChecker",
    "ProviderHealth",
    "ProviderStatus",
    "ProviderError",
    "ProviderErrorType",
    "get_health_checker",
    "reset_health_checker",
]
