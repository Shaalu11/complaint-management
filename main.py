from fastapi import FastAPI,Depends, HTTPException
from schemas import ComplaintCreate, ComplaintResponse
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from db_models import Student,Complaint
from sqlalchemy import select
app = FastAPI()

complaints = []

@app.get("/health")
def health():
    return {"status": "success"}

@app.post("/complaints",response_model=ComplaintResponse,status_code=201)
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