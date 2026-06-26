from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    task_id: int
    title: str
    description: str
    due_date: datetime
    pet: Pet
    is_complete: bool = False
    priority: str = "medium"          # low | medium | high
    duration_minutes: int = 30
    category: str = "other"           # feeding | grooming | exercise | medication | other
    recurrence: str = "none"          # none | daily | weekly

    def mark_complete(self) -> None:
        """Mark this task as complete by setting is_complete to True."""
        pass

    def reschedule(self, _new_date: datetime) -> None:
        """Update the task's due_date to the given new date."""
        pass

    def is_overdue(self) -> bool:
        """Return True if the task is not complete and its due_date has passed."""
        pass

    def get_priority_score(self) -> int:
        """Return a numeric score for the priority (low=1, medium=2, high=3) for use in scheduling."""
        pass


@dataclass
class Appointment:
    appointment_id: int
    title: str
    date_time: datetime
    location: str
    vet_name: str
    pet: Pet
    notes: str = ""
    appointment_type: str = "checkup"  # checkup | vaccination | grooming | dental | emergency | other
    status: str = "scheduled"          # scheduled | confirmed | cancelled | completed
    duration_minutes: int = 60

    def reschedule(self, new_datetime: datetime) -> None:
        """Update the appointment's date_time to the given new datetime and reset status to scheduled."""
        pass

    def cancel(self) -> None:
        """Set the appointment status to cancelled."""
        pass

    def get_reminder(self) -> str:
        """Return a formatted reminder string showing the appointment title, time remaining, location, and vet name."""
        pass

    def is_upcoming(self) -> bool:
        """Return True if the appointment has not been cancelled and its date_time is in the future."""
        pass


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    breed: str
    age: int
    owner: Owner
    weight: float = 0.0
    health_notes: str = ""
    _tasks: list[Task] = field(default_factory=list, repr=False)
    _appointments: list[Appointment] = field(default_factory=list, repr=False)

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's internal task list and link the task back to this pet."""
        pass

    def get_upcoming_tasks(self) -> list[Task]:
        """Return all incomplete tasks whose due_date is in the future, sorted by due date then priority."""
        pass

    def get_care_history(self) -> list[Task]:
        """Return all completed tasks sorted by due_date, most recent first."""
        pass

    def add_appointment(self, appt: Appointment) -> None:
        """Add an Appointment to this pet's internal appointments list and link it back to this pet."""
        pass

    def get_upcoming_appointments(self) -> list[Appointment]:
        """Return all non-cancelled appointments whose date_time is in the future, sorted by date_time."""
        pass


class Owner:
    def __init__(
        self,
        owner_id: int,
        name: str,
        email: str,
        phone: str,
        address: str = "",
    ):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's pets list and set the pet's owner reference to this owner."""
        pass

    def remove_pet(self, pet_id: int) -> None:
        """Remove the pet with the given pet_id from this owner's pets list."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Aggregate and return all tasks across every pet this owner has, sorted by due date then priority."""
        pass

    def get_all_appointments(self) -> list[Appointment]:
        """Aggregate and return all appointments across every pet this owner has, sorted by date_time."""
        pass
