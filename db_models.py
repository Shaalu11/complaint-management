from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    room_number: Mapped[str] = mapped_column(String(20))

    complaints = relationship("Complaint", back_populates="student")


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str]
    category: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="Pending")

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


    student = relationship("Student", back_populates="complaints")