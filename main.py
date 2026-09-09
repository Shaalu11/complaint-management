from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import Student, Complaint
from schemas import ComplaintCreate, ComplaintResponse, ComplaintUpdate, SignupRequest, LoginRequest, TokenResponse
from auth import create_access_token, verify_password, hash_password, get_current_student




app = FastAPI()


@app.get("/health")
def health():
    return {"status": "success"}


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

    return new_complaint


@app.get("/complaints", response_model=list[ComplaintResponse])
async def get_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Complaint)
        .order_by(Complaint.id)
        .offset(skip)
        .limit(limit)
    )

    complaints = result.scalars().all()

    return complaints


@app.get(
    "/complaints/{complaint_id}",
    response_model=ComplaintResponse
)
async def get_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )

    complaint = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail=f"Complaint with ID {complaint_id} not found"
        )

    return complaint

@app.patch(
    "/complaints/{complaint_id}",
    response_model=ComplaintResponse
)
async def update_complaint(
    complaint_id: int,
    complaint_update: ComplaintUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )

    complaint = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail=f"Complaint with ID {complaint_id} not found"
        )

    update_data = complaint_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(complaint, field, value)

    await db.commit()
    await db.refresh(complaint)

    return complaint

@app.delete("/complaints/{complaint_id}")
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )

    complaint = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail=f"Complaint with ID {complaint_id} not found"
        )

    await db.delete(complaint)

    await db.commit()

    return {
        "message": f"Complaint {complaint_id} deleted successfully"
    }


@app.post("/signup")
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
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

    hashed_password = hash_password(
        signup_data.password
    )

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

@app.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
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

    access_token = create_access_token(
        student.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }