import logging
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import Student, Complaint

from schemas import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
    SignupRequest,
    LoginRequest,
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI()


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():
    return {"status": "success"}


# ==================================================
# CREATE COMPLAINT
# ==================================================

@app.post(
    "/complaints",
    response_model=ComplaintResponse,
    status_code=201
)
async def create_complaint(
    complaint: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    try:
        new_complaint = Complaint(
            title=complaint.title,
            description=complaint.description,
            category=complaint.category,
            student_id=current_student.id,
            status="Pending"
        )

        db.add(new_complaint)

        await db.commit()

        await db.refresh(new_complaint)

        await notification_service.send_complaint_notification(
            student_email=current_student.email,
            complaint_id=new_complaint.id,
            title=new_complaint.title
        )

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

@app.get("/complaints", response_model=list[ComplaintResponse])
async def get_complaints(
    category: str | None = None,
    status: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Complaint)

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
    response_model=ComplaintResponse
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
    response_model=ComplaintResponse
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
        update_data = complaint_update.model_dump(
            exclude_unset=True
        )

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

@app.delete("/complaints/{complaint_id}")
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

@app.post("/signup")
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

@app.post("/login", response_model=TokenResponse)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
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

    if not verify_password(
        login_data.password,
        student.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(student.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }