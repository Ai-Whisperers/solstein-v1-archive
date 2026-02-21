"""
Worker entry point for Solstein Intelligence Engine.

NOTE: Temporal integration has been replaced by the native 
LangGraph StateMachine inside FastAPI. This entrypoint is disabled.
"""

import asyncio
from loguru import logger
from .config import get_settings

async def run_worker() -> None:
    """Log worker status."""
    settings = get_settings()
    logger.error("Temporal worker disabled - Replaced by LangGraph Native StateMachine")
    logger.info(f"Environment: {settings.environment}")
    return

if __name__ == "__main__":
    asyncio.run(run_worker())
