## API Router Example
```python
"""
Items API router.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..core.security import get_current_user
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Read items."""
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@router.post("/", response_model=schemas.Item)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create an item."""
    db_item = crud.get_item_by_name(db, name=item.name)
    if db_item:
        raise HTTPException(
            status_code=400,
            detail="Item with this name already exists",
        )
    return crud.create_item(db=db, item=item, owner_id=current_user.id)


@router.get("/{item_id}", response_model=schemas.Item)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Read a single item."""
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
```

## Database Configuration
```python
"""
Database configuration and utilities.
"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db",
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Pydantic Models
```python
"""
Database models and Pydantic schemas.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


# Pydantic schemas
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# SQLAlchemy models
class ItemModel(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    description = Column(String, nullable=True)
    price = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("ItemModel", back_populates="owner")
```

## Configuration
```python
"""
Application configuration.
"""

from typing import List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    PROJECT_DESCRIPTION: str = "A FastAPI REST API project"
    VERSION: str = "0.1.0"
    
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./test.db"
    
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    ALGORITHM: str = "HS256"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    ALLOWED_HOSTS: List[str] = ["*"]
    
    class Config:
        case_sensitive = True


settings = Settings()
```

## Development Commands
```bash
# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=fastapi_project

# Run the application
uvicorn src.fastapi_project.main:app --reload

# Run with custom host and port
uvicorn src.fastapi_project.main:app --reload --host 0.0.0.0 --port 8000
```