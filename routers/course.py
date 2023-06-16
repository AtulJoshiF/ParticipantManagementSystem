from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated

from database import SessionLocal
from models import Course, Student, StudentCourse

from .auth import get_current_user

router = APIRouter(
    prefix='/course',
    tags=['course']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post('/enroll', status_code=status.HTTP_200_OK)
async def enroll_for_course(db: db_dependency, student: user_dependency, course: str = Form(...)):
    if student is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    course_to_enroll = db.query(Course).filter(Course.name == course).first()

    if course_to_enroll is None:
        raise HTTPException(status_code=404, detail='Course not available!')

    students_enrolled = len(course_to_enroll.students)

    student_to_enroll = db.query(Student).filter(Student.id == student.get('id')).first()

    courses_enrolled = student_to_enroll.courses

    existing_course = (
        db.query(StudentCourse)
        .filter(StudentCourse.student_id == student_to_enroll.id)
        .filter(StudentCourse.course.has(name=course))
        .first()
    )
    if existing_course:
        return {'message': 'You have already enrolled for this course.'}

    limit_per_course = 10
    limit_per_student = 2

    student_enrolled_course_count = len(courses_enrolled)
    if student_enrolled_course_count == limit_per_student:
        return {'message': 'You have enrolled two courses which is the limit'}

    if students_enrolled == limit_per_course:
        return {'message': 'Enrollment limit achieved for the course!'}

    students_course_model = StudentCourse(
        student=student_to_enroll,
        course=course_to_enroll
    )

    db.add(students_course_model)
    db.commit()
    return {'message': 'Enrollement successful!'}


@router.delete("/unenroll", status_code=status.HTTP_200_OK)
async def unenroll_for_course(db: db_dependency, student: user_dependency, course: str = Form(...)):
    if student is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    student_to_unenroll = db.query(Student).filter(Student.id == student.get('id')).first()

    course_to_unenroll = db.query(Course).filter(Course.name == course).first()

    if course_to_unenroll is None:
        raise HTTPException(status_code=404, detail='Course not available!')

    course_to_unenroll = (
        db.query(StudentCourse)
        .filter(StudentCourse.student_id == student_to_unenroll.id)
        .filter(StudentCourse.course.has(name=course))
        .first()
    )

    if not course_to_unenroll:
        return {'message': 'Course enrollment not found.'}

    db.delete(course_to_unenroll)
    db.commit()

    return {'message': 'Course unenrollment successful!'}
