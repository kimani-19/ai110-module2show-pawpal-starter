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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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
