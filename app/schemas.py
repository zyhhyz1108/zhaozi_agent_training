from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CourseStatus = Literal["not_started", "in_progress", "completed"]


class CourseCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    status: CourseStatus = "not_started"


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    status: CourseStatus


class CourseUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(default="", min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    status: CourseStatus = "not_started"