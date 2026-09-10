from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Course
from app.schemas import CourseCreate


def create_course(db: Session, data: CourseCreate) -> Course:
    course = Course(**data.model_dump())
    db.add(course)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(course)
    return course


def list_courses(db: Session, offset: int, limit: int) -> list[Course]:
    statement = (
        select(Course)
        .order_by(Course.id)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def update_course(db: Session, course: Course, changes: dict) -> Course:
    for field, value in changes.items():
        setattr(course, field, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(course)
    return course


def delete_course(db: Session, course: Course) -> None:
    db.delete(course)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise