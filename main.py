from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Appointment, Scheduler


def print_section(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print('=' * 50)


def print_task(task: Task, index: int) -> None:
    status = "✓ Done" if task.is_complete else ("⚠ Overdue" if task.is_overdue() else "• Pending")
    print(f"  {index}. [{task.priority.upper()}] {task.title}")
    print(f"       Pet      : {task.pet.name if task.pet else 'unassigned'}")
    print(f"       Category : {task.category}")
    print(f"       Due      : {task.due_date.strftime('%I:%M %p')}")
    print(f"       Duration : {task.duration_minutes} min")
    print(f"       Status   : {status}")


def main():
    today = datetime.now()

    # --- Owner ---
    owner = Owner(1, "Jordan", "jordan@pawpal.com", "555-0101", "42 Maple Street")

    # --- Pets ---
    mochi = Pet(1, "Mochi", "dog",  "Shiba Inu",      3, owner, weight=10.5)
    luna  = Pet(2, "Luna",  "cat",  "British Shorthair", 5, owner, weight=4.2,
                health_notes="On daily allergy medication")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Tasks for Mochi (added out of chronological order on purpose, to exercise sort_by_time) ---
    mochi.add_task(Task(
        task_id=3, title="Grooming session", description="Brush coat and trim nails",
        due_date=today.replace(hour=11, minute=0, second=0, microsecond=0),
        priority="medium", duration_minutes=20, category="grooming", recurrence="weekly"
    ))
    mochi.add_task(Task(
        task_id=1, title="Morning walk", description="30 min walk around the block",
        due_date=today.replace(hour=7, minute=30, second=0, microsecond=0),
        priority="high", duration_minutes=30, category="exercise", recurrence="daily"
    ))
    mochi.add_task(Task(
        task_id=2, title="Breakfast feeding", description="One cup of dry kibble",
        due_date=today.replace(hour=8, minute=0, second=0, microsecond=0),
        priority="high", duration_minutes=10, category="feeding", recurrence="daily"
    ))
    mochi.add_task(Task(
        task_id=6, title="Evening walk", description="Short leg-stretch around the yard",
        due_date=today.replace(hour=18, minute=0, second=0, microsecond=0),
        priority="medium", duration_minutes=15, category="exercise"
    ))

    # --- Tasks for Luna ---
    luna.add_task(Task(
        task_id=5, title="Playtime", description="Interactive toy session",
        due_date=today.replace(hour=17, minute=0, second=0, microsecond=0),
        priority="low", duration_minutes=15, category="exercise"
    ))
    luna.add_task(Task(
        task_id=4, title="Allergy medication", description="0.5ml oral solution with food",
        due_date=today.replace(hour=8, minute=30, second=0, microsecond=0),
        priority="high", duration_minutes=5, category="medication", recurrence="daily"
    ))
    # Deliberately clashes with Mochi's "Evening walk" (task 6) at 18:00 to demo conflict detection.
    luna.add_task(Task(
        task_id=7, title="Dinner feeding", description="Wet food + kibble mix",
        due_date=today.replace(hour=18, minute=0, second=0, microsecond=0),
        priority="high", duration_minutes=10, category="feeding", recurrence="daily"
    ))

    # --- Appointment for Mochi ---
    mochi.add_appointment(Appointment(
        appointment_id=1, title="Annual checkup",
        date_time=today + timedelta(days=4),
        location="City Vet Clinic", vet_name="Dr. Patel",
        appointment_type="checkup"
    ))

    # Mark morning walk as already done (it's a daily task, so this also schedules
    # tomorrow's occurrence automatically via Pet.mark_task_complete)
    next_occurrence = mochi.mark_task_complete(1)

    # --- Scheduler ---
    scheduler = Scheduler(owner)

    # ── Header ──────────────────────────────────────────
    print(f"\n{'*' * 50}")
    print(f"  🐾  PawPal+ Daily Report")
    print(f"  {today.strftime('%A, %B %d %Y')}")
    print(f"{'*' * 50}")

    # ── Pets summary ────────────────────────────────────
    print_section("Pets")
    for pet in owner.pets:
        print(f"  • {pet.name} ({pet.breed}, age {pet.age}) — {pet.species}")
        if pet.health_notes:
            print(f"    Note: {pet.health_notes}")

    # ── Today's full schedule ────────────────────────────
    print_section("Today's Schedule")
    daily_plan = scheduler.build_daily_plan(today)
    if daily_plan:
        for i, task in enumerate(daily_plan, 1):
            print_task(task, i)
    else:
        print("  No pending tasks for today.")

    # ── Overdue tasks ────────────────────────────────────
    print_section("Overdue Tasks")
    overdue = scheduler.get_overdue_tasks()
    if overdue:
        for i, task in enumerate(overdue, 1):
            print_task(task, i)
    else:
        print("  No overdue tasks. Great job!")

    # ── Care history ─────────────────────────────────────
    print_section("Care History (Completed Today)")
    for pet in owner.pets:
        history = pet.get_care_history()
        if history:
            for t in history:
                completed = t.completed_at.strftime("%I:%M %p") if t.completed_at else "—"
                print(f"  ✓ {t.title} ({pet.name}) — completed at {completed}")

    # ── Upcoming appointments ────────────────────────────
    print_section("Upcoming Appointments")
    for pet in owner.pets:
        for appt in pet.get_upcoming_appointments():
            print(f"  • {appt.title} for {pet.name}")
            print(f"    {appt.date_time.strftime('%A %B %d')} | {appt.location} | {appt.vet_name}")
            print(f"    {appt.get_reminder()}")

    # ── Next suggested task ──────────────────────────────
    print_section("Suggested Next Task")
    next_task = scheduler.suggest_next_task()
    if next_task:
        print(f"  → {next_task.title} for {next_task.pet.name if next_task.pet else '?'}")
        print(f"    Priority: {next_task.priority} | Due: {next_task.due_date.strftime('%I:%M %p')}")
    else:
        print("  All tasks complete!")

    # ── Sorted by time (tasks were added out of order above) ─
    print_section("All Tasks Sorted by Time")
    for i, task in enumerate(scheduler.sort_by_time(), 1):
        print(
            f"  {i}. {task.due_date.strftime('%a %I:%M %p')} — {task.title} "
            f"({task.pet.name if task.pet else '?'})"
        )

    # ── Filtering demo ───────────────────────────────────
    print_section("Filter Demo: Mochi's Pending Tasks")
    for task in scheduler.filter_tasks(pet_name="Mochi", is_complete=False):
        print(f"  • {task.title} — due {task.due_date.strftime('%I:%M %p')}")

    print_section("Filter Demo: All Completed Tasks")
    completed = scheduler.filter_tasks(is_complete=True)
    if completed:
        for task in completed:
            print(f"  • {task.title} ({task.pet.name if task.pet else '?'})")
    else:
        print("  Nothing completed yet.")

    # ── Conflict detection ───────────────────────────────
    print_section("Schedule Conflicts")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠ {warning}")
    else:
        print("  No conflicts detected.")

    # ── Recurring task demo ──────────────────────────────
    print_section("Recurring Task Demo")
    print("  Completed: 'Morning walk' (daily) for Mochi.")
    if next_occurrence:
        print(
            f"  → Next occurrence auto-scheduled: '{next_occurrence.title}' "
            f"due {next_occurrence.due_date.strftime('%A %I:%M %p')}"
        )
    else:
        print("  → This task does not recur, no follow-up was created.")

    print(f"\n{'=' * 50}\n")


if __name__ == "__main__":
    main()
