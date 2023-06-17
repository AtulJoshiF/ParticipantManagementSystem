from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated

from database import SessionLocal
from models import Course, Student, StudentCourse

from .auth import get_current_user


router = APIRouter(prefix='/delete', tags=['delete'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


"""
    A student can delete his registry.
    All enrolled courses by the particular student will also be unenrolled.
"""


@router.delete("/student", status_code=status.HTTP_200_OK)
async def delete_student(db: db_dependency, student: user_dependency):
    if student is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    student_to_delete = db.query(Student).filter(Student.id == student.get('id')).first()

    db.query(StudentCourse).filter(StudentCourse.student_id == student_to_delete.id).delete()

    db.delete(student_to_delete)
    db.commit()

    return {"message": "Student and all associated course enrollments deleted successfully"}
