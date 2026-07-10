from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """A single care activity assigned to a pet, with priority, timing, and completion tracking."""

    task_id: int
    title: str
    description: str
    due_date: datetime
    is_complete: bool = False
    priority: str = "medium"          # low | medium | high
    duration_minutes: int = 30
    category: str = "other"           # feeding | grooming | exercise | medication | other
    recurrence: str = "none"          # none | daily | weekly
    pet: Pet | None = None            # set by Pet.add_task()
    completed_at: datetime | None = None

    def mark_complete(self) -> None:
        """Mark this task as complete by setting is_complete to True."""
        self.is_complete = True
        self.completed_at = datetime.now()

    def reschedule(self, new_date: datetime) -> None:
        """Update the task's due_date to the given new date."""
        self.due_date = new_date

    def is_overdue(self) -> bool:
        """Return True if the task is not complete and its due_date has passed."""
        return not self.is_complete and datetime.now() > self.due_date

    def get_priority_score(self) -> int:
        """Return a numeric score for the priority (low=1, medium=2, high=3) for use in scheduling."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 2)


@dataclass
class Appointment:
    """A scheduled external event (e.g. vet visit) with lifecycle status and reminder support."""

    appointment_id: int
    title: str
    date_time: datetime
    location: str
    vet_name: str
    notes: str = ""
    appointment_type: str = "checkup"  # checkup | vaccination | grooming | dental | emergency | other
    status: str = "scheduled"          # scheduled | confirmed | cancelled | completed
    duration_minutes: int = 60
    pet: Pet | None = None             # set by Pet.add_appointment()

    def reschedule(self, new_datetime: datetime) -> None:
        """Update the appointment's date_time to the given new datetime and reset status to scheduled."""
        self.date_time = new_datetime
        self.status = "scheduled"

    def cancel(self) -> None:
        """Set the appointment status to cancelled."""
        self.status = "cancelled"

    def get_reminder(self) -> str:
        """Return a formatted reminder string showing the appointment title, time remaining, location, and vet name."""
        delta = self.date_time - datetime.now()
        total_seconds = delta.total_seconds()

        if total_seconds < 0:
            timing = "was in the past"
        elif total_seconds < 3600:
            timing = f"in {int(total_seconds // 60)} minute(s)"
        elif total_seconds < 86400:
            timing = f"in {int(total_seconds // 3600)} hour(s)"
        else:
            timing = f"in {delta.days} day(s)"

        pet_name = self.pet.name if self.pet else "your pet"
        return (
            f"Reminder: '{self.title}' for {pet_name} is {timing}. "
            f"Location: {self.location}. Vet: {self.vet_name}."
        )

    def is_upcoming(self) -> bool:
        """Return True if the appointment has not been cancelled and its date_time is in the future."""
        return self.status != "cancelled" and self.date_time > datetime.now()


@dataclass
class Pet:
    """A pet profile that owns collections of tasks and appointments."""

    pet_id: int
    name: str
    species: str
    breed: str
    age: int
    owner: Owner
    weight: float = 0.0
    health_notes: str = ""
    _tasks: list[Task] = field(default_factory=list, init=False, repr=False)
    _appointments: list[Appointment] = field(default_factory=list, init=False, repr=False)

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's internal task list and link the task back to this pet."""
        task.pet = self
        self._tasks.append(task)

    def get_upcoming_tasks(self) -> list[Task]:
        """Return all incomplete tasks whose due_date is in the future, sorted by due date then priority."""
        now = datetime.now()
        pending = [t for t in self._tasks if not t.is_complete and t.due_date >= now]
        return sorted(pending, key=lambda t: (t.due_date, -t.get_priority_score()))

    def get_care_history(self) -> list[Task]:
        """Return all completed tasks sorted by completed_at, most recent first."""
        completed = [t for t in self._tasks if t.is_complete]
        return sorted(completed, key=lambda t: t.completed_at or t.due_date, reverse=True)

    def add_appointment(self, appt: Appointment) -> None:
        """Add an Appointment to this pet's internal appointments list and link it back to this pet."""
        appt.pet = self
        self._appointments.append(appt)

    def get_upcoming_appointments(self) -> list[Appointment]:
        """Return all non-cancelled appointments whose date_time is in the future, sorted by date_time."""
        return sorted(
            [a for a in self._appointments if a.is_upcoming()],
            key=lambda a: a.date_time,
        )


class Owner:
    """The top-level user who manages one or more pets and their care schedules."""

    def __init__(
        self,
        owner_id: int,
        name: str,
        email: str,
        phone: str,
        address: str = "",
    ):
        """Initialise an Owner with personal contact details and an empty pets list."""
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's pets list and set the pet's owner reference to this owner."""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove the pet with the given pet_id from this owner's pets list."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_all_tasks(self) -> list[Task]:
        """Aggregate and return all tasks across every pet this owner has, sorted by due date then priority."""
        all_tasks = [task for pet in self.pets for task in pet._tasks]
        return sorted(all_tasks, key=lambda t: (t.due_date, -t.get_priority_score()))

    def get_all_appointments(self) -> list[Appointment]:
        """Aggregate and return all appointments across every pet this owner has, sorted by date_time."""
        all_appts = [appt for pet in self.pets for appt in pet._appointments]
        return sorted(all_appts, key=lambda a: a.date_time)


class Scheduler:
    """The scheduling brain that builds daily plans and surfaces priority tasks across all pets."""

    def __init__(self, owner: Owner):
        """Bind the scheduler to an Owner so it can access all pets and their tasks."""
        self.owner = owner

    def build_daily_plan(self, date: datetime) -> list[Task]:
        """Collect all pending tasks for the given date across all pets, ordered by priority then due time."""
        all_tasks = self.owner.get_all_tasks()
        todays_tasks = [
            t for t in all_tasks
            if not t.is_complete and t.due_date.date() == date.date()
        ]
        return sorted(todays_tasks, key=lambda t: (-t.get_priority_score(), t.due_date))

    def get_overdue_tasks(self) -> list[Task]:
        """Return all tasks across all pets that are overdue and not yet complete."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(
            [t for t in all_tasks if t.is_overdue()],
            key=lambda t: t.due_date,
        )

    def suggest_next_task(self) -> Task | None:
        """Return the single highest-priority pending task across all pets, or None if none exist."""
        pending = [t for t in self.owner.get_all_tasks() if not t.is_complete]
        if not pending:
            return None
        return sorted(pending, key=lambda t: (-t.get_priority_score(), t.due_date))[0]
