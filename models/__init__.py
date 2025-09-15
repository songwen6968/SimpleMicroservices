from .person import PersonBase, PersonCreate, PersonRead, PersonUpdate
from .address import AddressBase, AddressCreate, AddressRead, AddressUpdate
from .course import CourseBase, CourseCreate, CourseRead, CourseUpdate
from .health import Health

__all__ = [
    "PersonBase", "PersonCreate", "PersonRead", "PersonUpdate",
    "AddressBase", "AddressCreate", "AddressRead", "AddressUpdate",
    "CourseBase", "CourseCreate", "CourseRead", "CourseUpdate",
    "Health",
]