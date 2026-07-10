from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task


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
