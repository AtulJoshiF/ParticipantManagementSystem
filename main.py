from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing_extensions import Annotated

import models
from models import Course, Student, StudentCourse
from database import engine, SessionLocal
from routers import auth, course, delete


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(course.router)
app.include_router(delete.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AddCourse(BaseModel):
    name: str
    instructor: str
    description: str


db_dependency = Annotated[Session, Depends(get_db)]


"""
    All the get methods are configured below.
"""


@app.get('/', status_code=status.HTTP_200_OK)
async def get_all_courses(db: db_dependency):
    courses = db.query(Course).all()
    courses_structured = [{'id': course.id, 'course name': course.name, 'instructor': course.instructor,
                           'description': course.description, 'enrolled': len(course.students)} for course in courses]
    return {'courses': courses_structured}


@app.get('/course_names', status_code=status.HTTP_200_OK)
async def get_all_course_names(db: db_dependency):
    courses = db.query(Course).all()
    course_names_structured = [{'id': course.id, 'course name': course.name} for course in courses]
    return{'courses': course_names_structured}


@app.get('/all_students/{page}', status_code=status.HTTP_200_OK)
async def get_all_students_list(db: db_dependency, page: int, limit: int = 10):
    offset = (page - 1)*limit
    students = db.query(Student).offset(offset).limit(limit).all()
    students_structured = [{'id': student.id, 'name': student.name, 'email': student.email, 'courses_enrolled': [course.name for enrollment in student.courses for course in db.query(Course).filter(Course.id == enrollment.course_id)]}for student in students]
    return {'students': students_structured}


@app.get('/all_students/', status_code=status.HTTP_200_OK)
async def get_all_students_list(db: db_dependency, page: int, limit: int):
    offset = (page - 1)*limit
    students = db.query(Student).offset(offset).limit(limit).all()
    students_structured = [{'id': student.id, 'name': student.name, 'email': student.email, 'courses_enrolled': [course.name for enrollment in student.courses for course in db.query(Course).filter(Course.id == enrollment.course_id)]}for student in students]
    return {'students': students_structured}


@app.get('/course_participants/{course_id}', status_code=status.HTTP_200_OK)
async def get_students_enrolled_for_the_course(db: db_dependency, course_id: int):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail='no course found')
    if len(course.students) == 0:
        return {"message": 'no students enrolled'}
    students_enrolled_structured = [{'id': student_course.student.id, 'name': student_course.student.name, 'email': student_course.student.email} for student_course in course.students]
    return {'course': [{'id': course.id, 'name': course.name}], 'students_enrolled': students_enrolled_structured}


"""
    The below get method is used to create courses. As the aim of the task is to 
    manage the students enrolled in the courses, the below method is only used to
    add the courses in the courses table and then being commented.
"""


# @app.post('/add_course',status_code=status.HTTP_201_CREATED)
# async def add_courses(add_course_request: AddCourse, db: db_dependency):
#     add_course_model = Course(
#         name=add_course_request.name,
#         instructor=add_course_request.instructor,
#         description=add_course_request.description
#     )
#     db.add(add_course_model)
#     db.commit()
