from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import Student, Complaint
from schemas import ComplaintCreate, ComplaintResponse


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
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Student).where(Student.id == complaint.student_id)
    )

    student = result.scalar_one_or_none()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID {complaint.student_id} does not exist"
        )

    new_complaint = Complaint(
        title=complaint.title,
        description=complaint.description,
        category=complaint.category,
        student_id=complaint.student_id,
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