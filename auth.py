import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import Student


# Load variables from .env
load_dotenv()


# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


# Make sure the secret exists
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")


# Password hashing
password_hash = PasswordHash.recommended()


# OAuth2 token configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# --------------------------------------------------
# PASSWORD FUNCTIONS
# --------------------------------------------------

def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure hash.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Check whether a plain-text password
    matches the stored password hash.
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# --------------------------------------------------
# JWT FUNCTION
# --------------------------------------------------

def create_access_token(student_id: int) -> str:
    """
    Create a JWT access token containing
    the student's ID.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        hours=1
    )

    payload = {
        "sub": str(student_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# --------------------------------------------------
# GET CURRENT LOGGED-IN STUDENT
# --------------------------------------------------

async def get_current_student(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify the JWT token and return the
    currently logged-in student.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        # Get student ID from token
        student_id = payload.get("sub")

        if student_id is None:
            raise credentials_exception

        student_id = int(student_id)

    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    # Find student in database
    result = await db.execute(
        select(Student).where(
            Student.id == student_id
        )
    )

    student = result.scalar_one_or_none()

    if student is None:
        raise credentials_exception

    return student