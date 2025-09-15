from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, StringConstraints
from enum import Enum

# Course code pattern: DEPT + 4 digits (e.g., COMS4153)
CourseCodeType = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2,4}\d{4}$")]


class CourseLevel(str, Enum):
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    DOCTORAL = "doctoral"


class CourseTerm(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"


class CourseBase(BaseModel):
    code: CourseCodeType = Field(
        ...,
        description="Course code (department letters + 4 digits).",
        json_schema_extra={"example": "COMS4153"},
    )
    title: str = Field(
        ...,
        description="Course title.",
        json_schema_extra={"example": "Cloud Computing"},
    )
    description: str = Field(
        ...,
        description="Course description.",
        json_schema_extra={"example": "Introduction to cloud computing concepts, architectures, and services."},
    )
    credits: int = Field(
        ...,
        description="Number of credits.",
        ge=0,
        le=6,
        json_schema_extra={"example": 3},
    )
    instructor: str = Field(
        ...,
        description="Primary instructor name.",
        json_schema_extra={"example": "Dr. Jane Smith"},
    )
    department: str = Field(
        ...,
        description="Department offering the course.",
        json_schema_extra={"example": "Computer Science"},
    )
    level: CourseLevel = Field(
        ...,
        description="Course level.",
        json_schema_extra={"example": "graduate"},
    )
    term: CourseTerm = Field(
        ...,
        description="Term when course is offered.",
        json_schema_extra={"example": "fall"},
    )
    year: int = Field(
        ...,
        description="Academic year.",
        ge=2020,
        le=2030,
        json_schema_extra={"example": 2025},
    )
    max_enrollment: Optional[int] = Field(
        None,
        description="Maximum number of students.",
        ge=1,
        json_schema_extra={"example": 50},
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="List of prerequisite course codes.",
        json_schema_extra={"example": ["COMS3157", "COMS3261"]},
    )
    meeting_times: Optional[str] = Field(
        None,
        description="Meeting schedule.",
        json_schema_extra={"example": "MW 10:10-11:25 AM"},
    )
    location: Optional[str] = Field(
        None,
        description="Classroom location.",
        json_schema_extra={"example": "Mudd 633"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "COMS4153",
                    "title": "Cloud Computing",
                    "description": "Introduction to cloud computing concepts, architectures, and services.",
                    "credits": 3,
                    "instructor": "Dr. Jane Smith",
                    "department": "Computer Science",
                    "level": "graduate",
                    "term": "fall",
                    "year": 2025,
                    "max_enrollment": 50,
                    "prerequisites": ["COMS3157", "COMS3261"],
                    "meeting_times": "MW 10:10-11:25 AM",
                    "location": "Mudd 633",
                }
            ]
        }
    }


class CourseCreate(CourseBase):
    """Creation payload for a Course."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "COMS4995",
                    "title": "Special Topics in Computer Science",
                    "description": "Advanced topics in machine learning and artificial intelligence.",
                    "credits": 3,
                    "instructor": "Dr. John Doe",
                    "department": "Computer Science",
                    "level": "graduate",
                    "term": "spring",
                    "year": 2025,
                    "max_enrollment": 30,
                    "prerequisites": ["COMS4771"],
                    "meeting_times": "TR 2:40-3:55 PM",
                    "location": "NWC 501",
                }
            ]
        }
    }


class CourseUpdate(BaseModel):
    """Partial update for a Course; supply only fields to change."""
    code: Optional[CourseCodeType] = Field(
        None, description="Course code.", json_schema_extra={"example": "COMS4111"}
    )
    title: Optional[str] = Field(
        None, json_schema_extra={"example": "Database Systems"}
    )
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Updated course description."}
    )
    credits: Optional[int] = Field(
        None, ge=0, le=6, json_schema_extra={"example": 4}
    )
    instructor: Optional[str] = Field(
        None, json_schema_extra={"example": "Dr. Alice Johnson"}
    )
    department: Optional[str] = Field(
        None, json_schema_extra={"example": "Computer Science"}
    )
    level: Optional[CourseLevel] = Field(
        None, json_schema_extra={"example": "undergraduate"}
    )
    term: Optional[CourseTerm] = Field(
        None, json_schema_extra={"example": "summer"}
    )
    year: Optional[int] = Field(
        None, ge=2020, le=2030, json_schema_extra={"example": 2026}
    )
    max_enrollment: Optional[int] = Field(
        None, ge=1, json_schema_extra={"example": 75}
    )
    prerequisites: Optional[List[str]] = Field(
        None,
        description="Replace the entire prerequisites list.",
        json_schema_extra={"example": ["COMS1004", "COMS3134"]},
    )
    meeting_times: Optional[str] = Field(
        None, json_schema_extra={"example": "TR 1:10-2:25 PM"}
    )
    location: Optional[str] = Field(
        None, json_schema_extra={"example": "Davis Auditorium"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"instructor": "Dr. New Instructor", "max_enrollment": 60},
                {"meeting_times": "MWF 9:00-9:50 AM", "location": "Pupin 301"},
                {"prerequisites": ["COMS3203", "COMS3251"]},
            ]
        }
    }


class CourseRead(CourseBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Course ID.",
        json_schema_extra={"example": "88888888-8888-4888-8888-888888888888"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "88888888-8888-4888-8888-888888888888",
                    "code": "COMS4153",
                    "title": "Cloud Computing",
                    "description": "Introduction to cloud computing concepts, architectures, and services.",
                    "credits": 3,
                    "instructor": "Dr. Jane Smith",
                    "department": "Computer Science",
                    "level": "graduate",
                    "term": "fall",
                    "year": 2025,
                    "max_enrollment": 50,
                    "prerequisites": ["COMS3157", "COMS3261"],
                    "meeting_times": "MW 10:10-11:25 AM",
                    "location": "Mudd 633",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }