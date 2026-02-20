"""
API Dependencies.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.repositories import CompanyRepository
from ..data.repositories import JsonFileRepository
        pass
