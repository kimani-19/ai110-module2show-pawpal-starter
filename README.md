# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run `python3 main.py` to see the full daily report in the terminal:

```
**************************************************
  🐾  PawPal+ Daily Report
  Thursday, July 09 2026
**************************************************

==================================================
  Pets
==================================================
  • Mochi (Shiba Inu, age 3) — dog
  • Luna (British Shorthair, age 5) — cat
    Note: On daily allergy medication

==================================================
  Today's Schedule
==================================================
  1. [HIGH] Breakfast feeding
       Pet      : Mochi
       Category : feeding
       Due      : 08:00 AM
       Duration : 10 min
       Status   : ⚠ Overdue
  2. [HIGH] Allergy medication
       Pet      : Luna
       Category : medication
       Due      : 08:30 AM
       Duration : 5 min
       Status   : ⚠ Overdue
  3. [HIGH] Dinner feeding
       Pet      : Luna
       Category : feeding
       Due      : 06:00 PM
       Duration : 10 min
       Status   : ⚠ Overdue
  4. [MEDIUM] Grooming session
       Pet      : Mochi
       Category : grooming
       Due      : 11:00 AM
       Duration : 20 min
       Status   : ⚠ Overdue
  5. [MEDIUM] Evening walk
       Pet      : Mochi
       Category : exercise
       Due      : 06:00 PM
       Duration : 15 min
       Status   : ⚠ Overdue
  6. [LOW] Playtime
       Pet      : Luna
       Category : exercise
       Due      : 05:00 PM
       Duration : 15 min
       Status   : ⚠ Overdue

==================================================
  Care History (Completed Today)
==================================================
  ✓ Morning walk (Mochi) — completed at 09:44 PM

==================================================
  Upcoming Appointments
==================================================
  • Annual checkup for Mochi
    Monday July 13 | City Vet Clinic | Dr. Patel
    Reminder: 'Annual checkup' for Mochi is in 3 day(s). Location: City Vet Clinic. Vet: Dr. Patel.

==================================================
  Suggested Next Task
==================================================
  → Breakfast feeding for Mochi
    Priority: high | Due: 08:00 AM

==================================================
  All Tasks Sorted by Time
==================================================
  1. Thu 07:30 AM — Morning walk (Mochi)
  2. Fri 07:30 AM — Morning walk (Mochi)
  3. Thu 08:00 AM — Breakfast feeding (Mochi)
  4. Thu 08:30 AM — Allergy medication (Luna)
  5. Thu 11:00 AM — Grooming session (Mochi)
  6. Thu 05:00 PM — Playtime (Luna)
  7. Thu 06:00 PM — Dinner feeding (Luna)
  8. Thu 06:00 PM — Evening walk (Mochi)

==================================================
  Filter Demo: Mochi's Pending Tasks
==================================================
  • Breakfast feeding — due 08:00 AM
  • Grooming session — due 11:00 AM
  • Evening walk — due 06:00 PM
  • Morning walk — due 07:30 AM

==================================================
  Filter Demo: All Completed Tasks
==================================================
  • Morning walk (Mochi)

==================================================
  Schedule Conflicts
==================================================
  ⚠ Conflict at 06:00 PM: 'Dinner feeding' (Luna), 'Evening walk' (Mochi) are all scheduled at the same time.

==================================================
  Recurring Task Demo
==================================================
  Completed: 'Morning walk' (daily) for Mochi.
  → Next occurrence auto-scheduled: 'Morning walk' due Friday 07:30 AM

==================================================
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The suite (`tests/test_pawpal.py`, 25 tests) covers:

- **Task lifecycle** — `mark_complete()` sets `is_complete`/`completed_at`; adding a task links it to the right `Pet`.
- **Sorting correctness** — `Pet.get_upcoming_tasks()` and `Owner.get_all_tasks()` return tasks in chronological order across different days (not just time-of-day), including deterministic tie-breaking when two tasks share a due date; `Scheduler.sort_by_time()`, `suggest_next_task()`, and `build_daily_plan()` all exclude completed tasks correctly.
- **Recurrence logic** — completing a `daily` or `weekly` task auto-schedules the next occurrence on the correct date, and this chains correctly across repeated completions (the new task's ID is derived from the full task list, not just the current pet).
- **Conflict detection** — `Scheduler.detect_conflicts()` flags two or more tasks at the exact same `due_date`, ignores completed tasks, and handles tasks with no pet assigned without crashing.
- **Filtering** — `Scheduler.filter_tasks()` by pet name and/or completion status, including an unknown pet name returning an empty list.
- **Appointment lifecycle** — `reschedule()` resets status to `scheduled`, `cancel()` removes it from `get_upcoming_appointments()`, and `get_reminder()` falls back gracefully when no pet is assigned.
- **Edge cases** — a pet with no tasks/appointments at all returns empty collections everywhere instead of raising.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/kimani19/Documents/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collecting ... collected 25 items

tests/test_pawpal.py::test_mark_complete_sets_is_complete PASSED         [  4%]
tests/test_pawpal.py::test_mark_complete_stamps_completed_at PASSED      [  8%]
tests/test_pawpal.py::test_add_task_increases_task_count PASSED          [ 12%]
tests/test_pawpal.py::test_add_task_links_pet_reference PASSED           [ 16%]
tests/test_pawpal.py::test_sort_by_time_orders_earliest_first PASSED     [ 20%]
tests/test_pawpal.py::test_get_upcoming_tasks_returns_chronological_order PASSED [ 24%]
tests/test_pawpal.py::test_get_all_tasks_orders_chronologically_across_pets PASSED [ 28%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 32%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [ 36%]
tests/test_pawpal.py::test_detect_conflicts_flags_tasks_at_same_time PASSED [ 40%]
tests/test_pawpal.py::test_detect_conflicts_ignores_completed_tasks PASSED [ 44%]
tests/test_pawpal.py::test_mark_task_complete_schedules_next_daily_occurrence PASSED [ 48%]
tests/test_pawpal.py::test_mark_task_complete_returns_none_for_non_recurring_task PASSED [ 52%]
tests/test_pawpal.py::test_empty_pet_returns_empty_collections_not_errors PASSED [ 56%]
tests/test_pawpal.py::test_mark_task_complete_schedules_next_weekly_occurrence PASSED [ 60%]
tests/test_pawpal.py::test_mark_task_complete_chains_across_multiple_completions PASSED [ 64%]
tests/test_pawpal.py::test_get_upcoming_tasks_orders_same_due_date_by_priority PASSED [ 68%]
tests/test_pawpal.py::test_suggest_next_task_ignores_completed_tasks PASSED [ 72%]
tests/test_pawpal.py::test_build_daily_plan_excludes_completed_and_other_days PASSED [ 76%]
tests/test_pawpal.py::test_filter_tasks_by_unknown_pet_name_returns_empty PASSED [ 80%]
tests/test_pawpal.py::test_detect_conflicts_lists_all_clashing_tasks PASSED [ 84%]
tests/test_pawpal.py::test_detect_conflicts_handles_task_with_no_pet_assigned PASSED [ 88%]
tests/test_pawpal.py::test_appointment_reschedule_resets_status_to_scheduled PASSED [ 92%]
tests/test_pawpal.py::test_appointment_cancel_excludes_it_from_upcoming PASSED [ 96%]
tests/test_pawpal.py::test_get_reminder_falls_back_to_generic_pet_name_when_unassigned PASSED [100%]

============================== 25 passed in 0.03s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

All 25 tests pass, covering sorting, recurrence, conflict detection, filtering, and the full task/appointment lifecycle, including edge cases like empty pets and unassigned tasks. Not a full 5 stars because conflict detection is exact-time-match only — it doesn't catch overlapping task *durations* (e.g. a 20-minute task at 11:00 AM and a 15-minute task starting at 11:10 AM), a known tradeoff documented in `reflection.md` (section 2b).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by time-of-day (`due_date.time()`), earliest first — independent of which calendar date each task falls on. |
| Filtering | `Scheduler.filter_tasks(pet_name=, is_complete=)` | Filters the owner's tasks by pet name and/or completion status; either argument can be omitted to skip that filter. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups pending tasks by exact `due_date` and returns a plain-string warning for each group of 2+ clashing tasks (same pet or different pets), instead of raising an exception. Only exact time matches are caught — see the tradeoff noted in `reflection.md` (2b). |
| Recurring tasks | `Task.get_next_due_date()`, `Pet.mark_task_complete()` | When a task with `recurrence="daily"` or `"weekly"` is completed via `Pet.mark_task_complete(task_id)`, a new `Task` is automatically created and added for the next occurrence (`due_date + timedelta(days=1)` or `+ timedelta(weeks=1)`). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
