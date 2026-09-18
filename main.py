import logging

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import Student, Complaint

from schemas import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
    SignupRequest,
    TokenResponse
)

from auth import (
    create_access_token,
    verify_password,
    hash_password,
    get_current_student
)

from notification_service import notification_service
from escalation_service import escalation_service


# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="Hostel Complaint Management API",
    description="""
## Hostel Complaint Management API

A RESTful API for managing hostel complaints.

### Features

- Student registration and authentication
- JWT-based authorization
- Create, view, update, and delete complaints
- Complaint search and filtering
- Pagination
- Notification service integration
- Complaint escalation service
- Automated testing
- PostgreSQL database with Alembic migrations

### Authentication

Protected endpoints require a JWT access token.

Use the `/login` endpoint to obtain an access token and then authorize
requests using the **Bearer Token** authentication scheme.
""",
    version="1.0.0",
    contact={
        "name": "Hostel Complaint Management System"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Check API and database health",
    description="Checks whether the API and PostgreSQL database are available."
)
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        logger.exception("Health check failed")

        return {
            "status": "unhealthy",
            "database": "unavailable"
        }


# ==================================================
# CREATE COMPLAINT
# ==================================================

@app.post(
    "/complaints",
    response_model=ComplaintResponse,
    status_code=201,
    tags=["Complaints"],
    summary="Create a new complaint",
    description=(
        "Create a new complaint for the logged-in student. "
        "The complaint will be automatically escalated and "
        "a notification will be sent to the student upon "
        "successful creation."
    )
)
async def create_complaint(
    complaint: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    try:
        # Create complaint
        new_complaint = Complaint(
            title=complaint.title,
            description=complaint.description,
            category=complaint.category,
            student_id=current_student.id,
            status="Pending"
        )

        db.add(new_complaint)

        # Save complaint
        await db.commit()
        await db.refresh(new_complaint)

        # Send notification
        await notification_service.send_complaint_notification(
            student_email=current_student.email,
            complaint_id=new_complaint.id,
            title=new_complaint.title
        )

        # Escalate complaint
        await escalation_service.escalate_complaint(
            complaint_id=new_complaint.id,
            category=new_complaint.category,
            title=new_complaint.title
        )

        return new_complaint

    except HTTPException:
        raise

    except Exception:
        await db.rollback()

        logger.exception(
            "Failed to create complaint for student %s",
            current_student.id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create complaint"
        )


# ==================================================
# GET ALL COMPLAINTS
# Only complaints belonging to logged-in student
# ==================================================

@app.get(
    "/complaints",
    response_model=list[ComplaintResponse],
    tags=["Complaints"],
    summary="Get all complaints",
    description=(
        "Retrieve complaints belonging to the logged-in student. "
        "Supports category filtering, status filtering, search, "
        "and pagination."
    )
)
async def get_complaints(
    category: str | None = None,
    status: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    # Start query with ownership restriction
    query = select(Complaint).where(
        Complaint.student_id == current_student.id
    )

    # Filter by category
    if category:
        query = query.where(
            Complaint.category == category
        )

    # Filter by status
    if status:
        query = query.where(
            Complaint.status == status
        )

    # Search title and description
    if search:
        query = query.where(
            Complaint.title.ilike(f"%{search}%") |
            Complaint.description.ilike(f"%{search}%")
        )

    # Stable ordering and pagination
    query = (
        query
        .order_by(Complaint.id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)

    complaints = result.scalars().all()

    return complaints


# ==================================================
# GET SINGLE COMPLAINT
# Only owner can view it
# ==================================================

@app.get(
    "/complaints/{complaint_id}",
    response_model=ComplaintResponse,
    tags=["Complaints"],
    summary="Get a specific complaint",
    description=(
        "Retrieve details of a specific complaint belonging "
        "to the logged-in student."
    )
)
async def get_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.student_id == current_student.id
        )
    )

    complaint = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return complaint


# ==================================================
# UPDATE COMPLAINT
# Only owner can update it
# ==================================================

@app.patch(
    "/complaints/{complaint_id}",
    response_model=ComplaintResponse,
    tags=["Complaints"],
    summary="Update a specific complaint",
    description=(
        "Update details of a specific complaint belonging "
        "to the logged-in student."
    )
)
async def update_complaint(
    complaint_id: int,
    complaint_update: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.student_id == current_student.id
        )
    )

    complaint = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    try:
        # Get only fields provided by the user
        update_data = complaint_update.model_dump(
            exclude_unset=True
        )

        # Update complaint fields
        for field, value in update_data.items():
            setattr(complaint, field, value)

        await db.commit()
        await db.refresh(complaint)

        return complaint

    except Exception:
        await db.rollback()

        logger.exception(
            "Failed to update complaint %s",
            complaint_id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to update complaint"
        )


# ==================================================
# DELETE COMPLAINT
# Only owner can delete it
# ==================================================

@app.delete(
    "/complaints/{complaint_id}",
    tags=["Complaints"],
    summary="Delete a specific complaint",
    description=(
        "Delete a specific complaint belonging to the "
        "logged-in student."
    )
)
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.student_id == current_student.id
        )
    )

    complaint = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    try:
        await db.delete(complaint)

        await db.commit()

        return {
            "message": f"Complaint {complaint_id} deleted successfully"
        }

    except Exception:
        await db.rollback()

        logger.exception(
            "Failed to delete complaint %s",
            complaint_id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete complaint"
        )


# ==================================================
# SIGNUP
# ==================================================

@app.post(
    "/signup",
    tags=["Authentication"],
    summary="Register a new student account",
    description=(
        "Create a new student account with a unique username "
        "and email. Passwords are securely hashed before storage."
    )
)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check whether username already exists
    result = await db.execute(
        select(Student).where(
            Student.username == signup_data.username
        )
    )

    existing_student = result.scalar_one_or_none()

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Check whether email already exists
    result = await db.execute(
        select(Student).where(
            Student.email == signup_data.email
        )
    )

    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password before storing it
    hashed_password = hash_password(
        signup_data.password
    )

    # Create student
    student = Student(
        username=signup_data.username,
        password_hash=hashed_password,
        name=signup_data.name,
        email=signup_data.email,
        room_number=signup_data.room_number
    )

    db.add(student)

    await db.commit()
    await db.refresh(student)

    return {
        "message": "Account created successfully",
        "username": student.username
    }


# ==================================================
# LOGIN
# ==================================================

@app.post(
    "/login",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Authenticate a student and obtain an access token",
    description=(
        "Authenticate a student using their username and password. "
        "Returns a JWT access token upon successful authentication."
    )
)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Find student by username
    result = await db.execute(
        select(Student).where(
            Student.username == login_data.username
        )
    )

    student = result.scalar_one_or_none()

    if student is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(
        login_data.password,
        student.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create JWT access token
    access_token = create_access_token(
        student.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }