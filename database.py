import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


# Load environment variables
load_dotenv()


# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


# Create async database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session