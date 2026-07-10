from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


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
