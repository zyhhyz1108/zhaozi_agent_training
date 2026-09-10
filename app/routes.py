from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app import repositories
from app.database import get_db
from app.schemas import CourseCreate, CourseRead, CourseUpdate


router = APIRouter(prefix="/courses", tags=["课程"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=CourseRead, status_code=201)
def create_course(data: CourseCreate, db: DbSession):
    return repositories.create_course(db, data)


@router.get("", response_model=list[CourseRead])
def list_courses(
    db: DbSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return repositories.list_courses(db, offset, limit)


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: Annotated[int, Path(gt=0)],
    db: DbSession,
):
    course = repositories.get_course(db, course_id)

    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    return course


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: Annotated[int, Path(gt=0)],
    data: CourseUpdate,
    db: DbSession,
):
    course = repositories.get_course(db, course_id)

    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(status_code=400, detail="请至少提供一个修改字段")

    return repositories.update_course(db, course, changes)


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: Annotated[int, Path(gt=0)],
    db: DbSession,
):
    course = repositories.get_course(db, course_id)

    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    repositories.delete_course(db, course)
    return Response(status_code=204)