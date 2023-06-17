from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


"""
    A many to many relationship between the courses table and student table is 
    established by using the junction table student_course
"""


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True)
    instructor = Column(String)
    description = Column(String)

    students = relationship("StudentCourse", back_populates="course")


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    courses = relationship("StudentCourse", back_populates="student")


class StudentCourse(Base):
    __tablename__ = 'student_course'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)

    student = relationship("Student", back_populates="courses")
    course = relationship("Course", back_populates="students")

