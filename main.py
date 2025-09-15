from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health
from models.course import CourseCreate, CourseRead, CourseUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
courses: Dict[UUID, CourseRead] = {}

app = FastAPI(
    title="Person/Address/Course API",
    description="Demo FastAPI app using Pydantic v2 models for Person, Address, and Course",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]

# -----------------------------------------------------------------------------
# Course endpoints
# -----------------------------------------------------------------------------
@app.get("/courses", response_model=List[CourseRead], summary="List all courses", tags=["courses"])
def list_courses(
    code: Optional[str] = Query(None, description="Filter by course code"),
    title: Optional[str] = Query(None, description="Filter by course title"),
    instructor: Optional[str] = Query(None, description="Filter by instructor name"),
    department: Optional[str] = Query(None, description="Filter by department"),
    level: Optional[str] = Query(None, description="Filter by course level"),
    term: Optional[str] = Query(None, description="Filter by term"),
    year: Optional[int] = Query(None, description="Filter by year"),
):
    """
    Retrieve a list of all courses with optional filtering parameters.
    """
    results = list(courses.values())
    
    if code is not None:
        results = [c for c in results if c.code == code]
    if title is not None:
        results = [c for c in results if title.lower() in c.title.lower()]
    if instructor is not None:
        results = [c for c in results if instructor.lower() in c.instructor.lower()]
    if department is not None:
        results = [c for c in results if department.lower() in c.department.lower()]
    if level is not None:
        results = [c for c in results if c.level == level]
    if term is not None:
        results = [c for c in results if c.term == term]
    if year is not None:
        results = [c for c in results if c.year == year]
    
    return results

@app.post("/courses", response_model=CourseRead, status_code=201, summary="Create a new course", tags=["courses"])
def create_course(course: CourseCreate):
    """
    Create a new course with the provided information.
    """
    course_read = CourseRead(**course.model_dump())
    courses[course_read.id] = course_read
    return course_read

@app.get("/courses/{course_id}", response_model=CourseRead, summary="Get a specific course", tags=["courses"])
def get_course(
    course_id: UUID = Path(..., description="The UUID of the course to retrieve")
):
    """
    Retrieve details of a specific course by its ID.
    """
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    return courses[course_id]

@app.put("/courses/{course_id}", response_model=CourseRead, summary="Update a course", tags=["courses"])
def update_course(
    course_id: UUID = Path(..., description="The UUID of the course to update"),
    update: CourseUpdate = ...,
):
    """
    Update a course's information. Only provided fields will be updated.
    """
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    stored = courses[course_id].model_dump()
    update_data = update.model_dump(exclude_unset=True)
    if update_data:
        stored.update(update_data)
        stored["updated_at"] = datetime.utcnow()
        courses[course_id] = CourseRead(**stored)
    return courses[course_id]

@app.delete("/courses/{course_id}", status_code=204, summary="Delete a course", tags=["courses"])
def delete_course(
    course_id: UUID = Path(..., description="The UUID of the course to delete")
):
    """
    Delete a course from the system.
    """
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    del courses[course_id]
    return None

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address/Course API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
