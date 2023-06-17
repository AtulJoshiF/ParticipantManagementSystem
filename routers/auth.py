from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, ValidationError
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Course, Student
from starlette import status
from typing_extensions import Annotated


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


SECRET_KEY = 'abcdefghijklmnpamasystuvwxyz1234567890!@#$%^&*()_+-='
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


"""
    Students can register and login through the following post methods.
    JWT are used for authorization and authentication of students.
    Email is considered to be unique and used for logging in.
"""


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CreateStudentRequest(BaseModel):
    name: str = Field(min_length=4)
    email: EmailStr
    password: str = Field(min_length=6)


db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def authenticate_student(email: str, password: str, db):
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        return False
    if not bcrypt_context.verify(password, student.hashed_password):
        return False
    return student


def create_access_token(name: str, email: int, student_id: int, expires_delta: timedelta):
    encode = {'sub': email, 'id': student_id, 'name': name}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_email: str = payload.get('sub')
        student_id: int = payload.get('id')
        student_name: str = payload.get('name')
        if student_email is None or student_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'name': student_name, 'id': student_id, 'email': student_email}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


@router.post("/create_student", status_code=status.HTTP_201_CREATED)
async def create_student(create_student_request: CreateStudentRequest, db: db_dependency):

    # Check if a user with the same email already exists
    existing_email = db.query(Student).filter(Student.email == create_student_request.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    try:
        create_student_model = Student(
            name=create_student_request.name,
            email=create_student_request.email,
            hashed_password=bcrypt_context.hash(create_student_request.password)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.add(create_student_model)
    db.commit()

    return {'message': 'student created successfully!'}


@router.post("/login", response_model=Token)
async def login_for_access_with_email(response: Response,
                           form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    student = authenticate_student(form_data.username, form_data.password, db)
    if not student:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(student.name, student.email, student.id, timedelta(minutes=20))
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {'access_token': token, 'token_type': 'bearer'}

