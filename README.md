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
  3. [MEDIUM] Grooming session
       Pet      : Mochi
       Category : grooming
       Due      : 11:00 AM
       Duration : 20 min
       Status   : ⚠ Overdue
  4. [LOW] Playtime
       Pet      : Luna
       Category : exercise
       Due      : 05:00 PM
       Duration : 15 min
       Status   : ⚠ Overdue

==================================================
  Care History (Completed Today)
==================================================
  ✓ Morning walk (Mochi) — completed at 07:54 PM

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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
