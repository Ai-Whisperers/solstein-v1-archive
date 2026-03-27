"""WebSocket package for realtime updates (EPIC-024)."""

from .manager import ConnectionManager, manager
from .routes import router

__all__ = ["ConnectionManager", "manager", "router"]
