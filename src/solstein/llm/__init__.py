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

from .embeddings import (
    batch_generate_embeddings,
    company_to_profile_text,
    generate_company_embedding,
    generate_embedding,
    get_embedding_metadata,
)
from .enhanced_client import (
    EnhancedLLMClient,
    LLMGenerationError,
    get_enhanced_llm_client,
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
from .instructor_client import InstructorClient
from .prompts import PromptManager, get_prompt, get_prompt_manager
from .evaluation import (
    EvalCase,
    EvalDataset,
    EvalResult,
    evaluate_business_analysis,
    evaluate_company_extraction,
    evaluate_research_plan,
    run_evaluation,
)
from .tracing import LLMTracer, TraceRecord, get_tracer, reset_tracer

__all__ = [
    # Enhanced client
    "EnhancedLLMClient",
    "LLMGenerationError",
    "get_enhanced_llm_client",
    # Instructor client (STORY-072)
    "InstructorClient",
    # Tracing (STORY-073)
    "LLMTracer",
    "TraceRecord",
    "get_tracer",
    "reset_tracer",
    # Evaluation (STORY-074)
    "EvalCase",
    "EvalDataset",
    "EvalResult",
    "evaluate_research_plan",
    "evaluate_company_extraction",
    "evaluate_business_analysis",
    "run_evaluation",
    # Prompts (STORY-073)
    "PromptManager",
    "get_prompt",
    "get_prompt_manager",
    # Health checking
    "ProviderHealthChecker",
    "ProviderHealth",
    "ProviderStatus",
    "ProviderError",
    "ProviderErrorType",
    "get_health_checker",
    "reset_health_checker",
    # Embeddings (EPIC-023)
    "generate_embedding",
    "generate_company_embedding",
    "batch_generate_embeddings",
    "company_to_profile_text",
    "get_embedding_metadata",
]
