from fastapi import FastAPI
from models import ComplaintCreate, ComplaintResponse
app = FastAPI()

complaints = []

@app.get("/health")
def health():
    return {"status": "success"}

@app.post("/complaints",response_model=ComplaintResponse)
def create_complaint(complaint:ComplaintCreate):
    new_id = len(complaints) + 1
    new_complaint = {
        "id":new_id,
        "title":complaint.title,
        "description":complaint.description,
        "category":complaint.category,
        "status":"Pending",
        "student_id":complaint.student_id
    }

    complaints.append(new_complaint)

    return new_complaint