from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Appointment, Scheduler


def make_owner():
    return Owner(1, "Jordan", "jordan@pawpal.com", "555-0101")


def make_pet(owner):
    pet = Pet(1, "Mochi", "dog", "Shiba Inu", 3, owner)
    owner.add_pet(pet)
    return pet


def make_task(task_id=1, hours_from_now=2, priority="medium"):
    return Task(
        task_id=task_id,
        title="Morning walk",
        description="Walk around the block",
        due_date=datetime.now() + timedelta(hours=hours_from_now),
        priority=priority,
    )


# --- Test 1: mark_complete() changes the task's status ---

def test_mark_complete_sets_is_complete():
    task = make_task()
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_mark_complete_stamps_completed_at():
    task = make_task()
    assert task.completed_at is None
    task.mark_complete()
    assert task.completed_at is not None
    assert isinstance(task.completed_at, datetime)


# --- Test 2: adding a task to a Pet increases that pet's task count ---

def test_add_task_increases_task_count():
    owner = make_owner()
    pet = make_pet(owner)
    assert len(pet._tasks) == 0
    pet.add_task(make_task(task_id=1))
    assert len(pet._tasks) == 1
    pet.add_task(make_task(task_id=2))
    assert len(pet._tasks) == 2


def test_add_task_links_pet_reference():
    owner = make_owner()
    pet = make_pet(owner)
    task = make_task()
    pet.add_task(task)
    assert task.pet is pet


# --- Test 3: Scheduler.sort_by_time() orders by time-of-day, not full date ---

def test_sort_by_time_orders_earliest_first():
    owner = make_owner()
    pet = make_pet(owner)
    now = datetime.now()
    late = Task(1, "Evening walk", "", now.replace(hour=18, minute=0))
    early = Task(2, "Morning walk", "", now.replace(hour=7, minute=30))
    mid = Task(3, "Breakfast", "", now.replace(hour=8, minute=0))
    for t in (late, early, mid):
        pet.add_task(t)

    ordered = Scheduler(owner).sort_by_time()
    assert [t.task_id for t in ordered] == [2, 3, 1]


# --- Test 3b: get_upcoming_tasks()/get_all_tasks() order tasks chronologically across days ---

def test_get_upcoming_tasks_returns_chronological_order():
    owner = make_owner()
    pet = make_pet(owner)
    base = datetime.now()
    in_three_days = Task(1, "Vet visit", "", base + timedelta(days=3))
    in_one_hour = Task(2, "Morning walk", "", base + timedelta(hours=1))
    tomorrow = Task(3, "Grooming", "", base + timedelta(days=1))
    for t in (in_three_days, in_one_hour, tomorrow):
        pet.add_task(t)

    ordered = pet.get_upcoming_tasks()
    assert [t.task_id for t in ordered] == [2, 3, 1]


def test_get_all_tasks_orders_chronologically_across_pets():
    owner = make_owner()
    mochi = make_pet(owner)
    luna = Pet(2, "Luna", "cat", "British Shorthair", 5, owner)
    owner.add_pet(luna)
    base = datetime.now()
    mochi.add_task(Task(1, "Vet visit", "", base + timedelta(days=2)))
    luna.add_task(Task(2, "Feeding", "", base + timedelta(hours=1)))

    ordered = owner.get_all_tasks()
    assert [t.task_id for t in ordered] == [2, 1]


# --- Test 4: Scheduler.filter_tasks() filters by pet name and completion status ---

def test_filter_tasks_by_pet_name():
    owner = make_owner()
    mochi = make_pet(owner)
    luna = Pet(2, "Luna", "cat", "British Shorthair", 5, owner)
    owner.add_pet(luna)
    mochi.add_task(make_task(task_id=1))
    luna.add_task(make_task(task_id=2))

    filtered = Scheduler(owner).filter_tasks(pet_name="Luna")
    assert [t.task_id for t in filtered] == [2]


def test_filter_tasks_by_completion_status():
    owner = make_owner()
    pet = make_pet(owner)
    done = make_task(task_id=1)
    done.mark_complete()
    pending = make_task(task_id=2)
    pet.add_task(done)
    pet.add_task(pending)

    assert [t.task_id for t in Scheduler(owner).filter_tasks(is_complete=True)] == [1]
    assert [t.task_id for t in Scheduler(owner).filter_tasks(is_complete=False)] == [2]


# --- Test 5: Scheduler.detect_conflicts() flags same-time tasks without crashing ---

def test_detect_conflicts_flags_tasks_at_same_time():
    owner = make_owner()
    mochi = make_pet(owner)
    luna = Pet(2, "Luna", "cat", "British Shorthair", 5, owner)
    owner.add_pet(luna)
    due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    mochi.add_task(Task(1, "Evening walk", "", due))
    luna.add_task(Task(2, "Dinner", "", due))

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Evening walk" in warnings[0] and "Dinner" in warnings[0]


def test_detect_conflicts_ignores_completed_tasks():
    owner = make_owner()
    pet = make_pet(owner)
    due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    t1 = Task(1, "Evening walk", "", due)
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(Task(2, "Dinner", "", due))

    assert Scheduler(owner).detect_conflicts() == []


# --- Test 6: Pet.mark_task_complete() auto-schedules the next recurring occurrence ---

def test_mark_task_complete_schedules_next_daily_occurrence():
    owner = make_owner()
    pet = make_pet(owner)
    due = datetime.now().replace(hour=7, minute=30, second=0, microsecond=0)
    task = Task(1, "Morning walk", "", due, recurrence="daily")
    pet.add_task(task)

    next_task = pet.mark_task_complete(1)

    assert task.is_complete is True
    assert next_task is not None
    assert next_task.due_date == due + timedelta(days=1)
    assert next_task.recurrence == "daily"
    assert next_task in pet._tasks


def test_mark_task_complete_returns_none_for_non_recurring_task():
    owner = make_owner()
    pet = make_pet(owner)
    task = make_task(task_id=1)
    pet.add_task(task)

    assert pet.mark_task_complete(1) is None
    assert task.is_complete is True


# --- Edge case: a pet with no tasks/appointments at all ---

def test_empty_pet_returns_empty_collections_not_errors():
    owner = make_owner()
    pet = make_pet(owner)

    assert pet.get_upcoming_tasks() == []
    assert pet.get_care_history() == []
    assert pet.get_upcoming_appointments() == []
    assert Scheduler(owner).suggest_next_task() is None
    assert Scheduler(owner).build_daily_plan(datetime.now()) == []
    assert Scheduler(owner).get_overdue_tasks() == []
    assert Scheduler(owner).detect_conflicts() == []


# --- Edge case: weekly recurrence (only daily was covered before) ---

def test_mark_task_complete_schedules_next_weekly_occurrence():
    owner = make_owner()
    pet = make_pet(owner)
    due = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    task = Task(1, "Grooming", "", due, recurrence="weekly")
    pet.add_task(task)

    next_task = pet.mark_task_complete(1)

    assert next_task is not None
    assert next_task.due_date == due + timedelta(weeks=1)
    assert next_task.recurrence == "weekly"


# --- Edge case: completing a recurring task twice chains a third occurrence ---

def test_mark_task_complete_chains_across_multiple_completions():
    owner = make_owner()
    pet = make_pet(owner)
    due = datetime.now().replace(hour=7, minute=30, second=0, microsecond=0)
    task = Task(1, "Morning walk", "", due, recurrence="daily")
    pet.add_task(task)

    second = pet.mark_task_complete(1)
    third = pet.mark_task_complete(second.task_id)

    assert third is not None
    assert third.due_date == due + timedelta(days=2)
    assert third.task_id != task.task_id != second.task_id
    assert len(pet._tasks) == 3


# --- Edge case: two tasks due at the exact same moment sort deterministically ---

def test_get_upcoming_tasks_orders_same_due_date_by_priority():
    owner = make_owner()
    pet = make_pet(owner)
    due = datetime.now() + timedelta(hours=1)
    low = Task(1, "Feed", "", due, priority="low")
    high = Task(2, "Medicate", "", due, priority="high")
    pet.add_task(low)
    pet.add_task(high)

    ordered = pet.get_upcoming_tasks()
    assert [t.task_id for t in ordered] == [2, 1]


# --- Edge case: suggest_next_task / build_daily_plan ignore completed tasks ---

def test_suggest_next_task_ignores_completed_tasks():
    owner = make_owner()
    pet = make_pet(owner)
    done = make_task(task_id=1, priority="high")
    done.mark_complete()
    pending = make_task(task_id=2, priority="low")
    pet.add_task(done)
    pet.add_task(pending)

    suggestion = Scheduler(owner).suggest_next_task()
    assert suggestion is not None
    assert suggestion.task_id == 2


def test_build_daily_plan_excludes_completed_and_other_days():
    owner = make_owner()
    pet = make_pet(owner)
    today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    done_today = Task(1, "Feed", "", today)
    done_today.mark_complete()
    pending_today = Task(2, "Walk", "", today)
    pending_tomorrow = Task(3, "Vet", "", tomorrow)

    pet.add_task(done_today)
    pet.add_task(pending_today)
    pet.add_task(pending_tomorrow)

    plan = Scheduler(owner).build_daily_plan(today)
    assert [t.task_id for t in plan] == [2]


# --- Edge case: filtering by a pet name that doesn't exist ---

def test_filter_tasks_by_unknown_pet_name_returns_empty():
    owner = make_owner()
    pet = make_pet(owner)
    pet.add_task(make_task(task_id=1))

    assert Scheduler(owner).filter_tasks(pet_name="NotARealPet") == []


# --- Edge case: detect_conflicts with three tasks clashing at once ---

def test_detect_conflicts_lists_all_clashing_tasks():
    owner = make_owner()
    mochi = make_pet(owner)
    luna = Pet(2, "Luna", "cat", "British Shorthair", 5, owner)
    owner.add_pet(luna)
    due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    mochi.add_task(Task(1, "Evening walk", "", due))
    luna.add_task(Task(2, "Dinner", "", due))
    luna.add_task(Task(3, "Medication", "", due))

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert all(name in warnings[0] for name in ("Evening walk", "Dinner", "Medication"))


def test_detect_conflicts_handles_task_with_no_pet_assigned():
    owner = make_owner()
    due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    unassigned_tasks = [Task(1, "Evening walk", "", due), Task(2, "Dinner", "", due)]

    warnings = Scheduler(owner).detect_conflicts(unassigned_tasks)
    assert len(warnings) == 1
    assert "unassigned" in warnings[0]


# --- Edge case: Appointment lifecycle (reschedule, cancel, upcoming filtering) ---

def test_appointment_reschedule_resets_status_to_scheduled():
    appt = Appointment(1, "Checkup", datetime.now() + timedelta(days=1), "Clinic", "Dr. Lee")
    appt.status = "confirmed"
    new_time = datetime.now() + timedelta(days=3)

    appt.reschedule(new_time)

    assert appt.date_time == new_time
    assert appt.status == "scheduled"


def test_appointment_cancel_excludes_it_from_upcoming():
    owner = make_owner()
    pet = make_pet(owner)
    appt = Appointment(1, "Checkup", datetime.now() + timedelta(days=1), "Clinic", "Dr. Lee")
    pet.add_appointment(appt)
    assert pet.get_upcoming_appointments() == [appt]

    appt.cancel()

    assert appt.status == "cancelled"
    assert pet.get_upcoming_appointments() == []


def test_get_reminder_falls_back_to_generic_pet_name_when_unassigned():
    appt = Appointment(1, "Checkup", datetime.now() + timedelta(hours=2), "Clinic", "Dr. Lee")
    assert "your pet" in appt.get_reminder()
