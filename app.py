from datetime import datetime, date, time

import streamlit as st

# Step 1: bring the backend classes into this script so the UI can call real logic.
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. This app is wired to the backend classes in `pawpal_system.py` —
Owner/Pet/Task objects live in `st.session_state` so they persist across Streamlit
reruns, and every button below calls a real `Scheduler` method instead of just
sorting/filtering the list inline in the UI.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# Step 2: manage application "memory". Streamlit reruns this whole script on every
# interaction, so we only construct the Owner/Pet once and then reuse the same
# instances from st.session_state on every subsequent run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=1, name="Jordan", email="", phone="")

if "pets" not in st.session_state:
    mochi = Pet(pet_id=1, name="Mochi", species="dog", breed="", age=0, owner=st.session_state.owner)
    st.session_state.owner.add_pet(mochi)
    st.session_state.pets = [mochi]

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0

if "pet_counter" not in st.session_state:
    st.session_state.pet_counter = 1

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner & Pets")
owner_name = st.text_input("Owner name", value=owner.name)
if st.button("Save owner name"):
    owner.name = owner_name
    st.success(f"Saved owner name: {owner.name}.")

with st.expander("Manage pets", expanded=False):
    for pet in owner.pets:
        st.write(f"• **{pet.name}** ({pet.species})")

    st.markdown("**Add a pet**")
    new_pet_col1, new_pet_col2 = st.columns(2)
    with new_pet_col1:
        new_pet_name = st.text_input("New pet name", key="new_pet_name")
    with new_pet_col2:
        new_pet_species = st.selectbox("New pet species", ["dog", "cat", "other"], key="new_pet_species")
    if st.button("Add pet"):
        if new_pet_name.strip():
            st.session_state.pet_counter += 1
            new_pet = Pet(
                pet_id=st.session_state.pet_counter,
                name=new_pet_name.strip(),
                species=new_pet_species,
                breed="",
                age=0,
                owner=owner,
            )
            owner.add_pet(new_pet)
            st.success(f"Added {new_pet.name} to your pets.")
        else:
            st.warning("Enter a pet name before adding.")

st.divider()

st.subheader("Add a Task")
st.caption("Tasks are added to a Pet object via Pet.add_task().")

pet_names = [p.name for p in owner.pets]
task_pet_name = st.selectbox("Pet", pet_names)
task_pet = next(p for p in owner.pets if p.name == task_pet_name)

col1, col2 = st.columns(2)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    category = st.selectbox("Category", ["feeding", "grooming", "exercise", "medication", "other"], index=2)
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"], index=0)

col3, col4 = st.columns(2)
with col3:
    due_date_input = st.date_input("Due date", value=date.today())
with col4:
    due_time_input = st.time_input("Due time", value=time(hour=9, minute=0))

if st.button("Add task"):
    st.session_state.task_counter += 1
    new_task = Task(
        task_id=st.session_state.task_counter,
        title=task_title,
        description="",
        due_date=datetime.combine(due_date_input, due_time_input),
        priority=priority,
        duration_minutes=int(duration),
        category=category,
        recurrence=recurrence,
    )
    task_pet.add_task(new_task)
    st.success(f"Added task '{task_title}' to {task_pet.name}.")

st.divider()

st.subheader("Tasks")

all_tasks = owner.get_all_tasks()

if not all_tasks:
    st.info("No tasks yet. Add one above.")
else:
    # Step 3: reflect the algorithmic layer -- sorting and filtering both call real
    # Scheduler methods rather than re-implementing the logic here in the UI.
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        sort_by_time = st.checkbox("Sort by time-of-day", value=False)
    with filter_col2:
        filter_pet_option = st.selectbox("Filter by pet", ["All"] + pet_names)
    with filter_col3:
        filter_status_option = st.selectbox("Filter by status", ["All", "Pending", "Complete"])

    status_arg = {"All": None, "Pending": False, "Complete": True}[filter_status_option]
    pet_arg = None if filter_pet_option == "All" else filter_pet_option
    display_tasks = scheduler.filter_tasks(pet_name=pet_arg, is_complete=status_arg)

    if sort_by_time:
        display_tasks = scheduler.sort_by_time(display_tasks)
        st.caption("Sorted by Scheduler.sort_by_time() -- earliest time-of-day first, across all dates.")
    else:
        st.caption("Sorted chronologically by due date via Scheduler.filter_tasks().")

    if display_tasks:
        st.table(
            [
                {
                    "pet": t.pet.name if t.pet else "unassigned",
                    "title": t.title,
                    "priority": t.priority,
                    "category": t.category,
                    "due": t.due_date.strftime("%a %I:%M %p"),
                    "duration_min": t.duration_minutes,
                    "complete": t.is_complete,
                }
                for t in display_tasks
            ]
        )
    else:
        st.info("No tasks match the current filters.")

    # Let a user mark a pending task complete to exercise Pet.mark_task_complete()
    # (and, for recurring tasks, watch the next occurrence get auto-scheduled).
    pending_tasks = [t for t in all_tasks if not t.is_complete]
    if pending_tasks:
        st.markdown("**Mark a task complete**")
        task_labels = {
            f"{t.title} ({t.pet.name if t.pet else '?'}, due {t.due_date.strftime('%a %I:%M %p')})": t
            for t in pending_tasks
        }
        chosen_label = st.selectbox("Task", list(task_labels.keys()), key="complete_task_select")
        if st.button("Mark complete"):
            chosen_task = task_labels[chosen_label]
            pet_of_task = chosen_task.pet
            next_occurrence = pet_of_task.mark_task_complete(chosen_task.task_id)
            if next_occurrence:
                st.success(
                    f"Completed '{chosen_task.title}'. Next occurrence auto-scheduled for "
                    f"{next_occurrence.due_date.strftime('%A %I:%M %p')}."
                )
            else:
                st.success(f"Completed '{chosen_task.title}'.")
            st.rerun()

    # Conflict warnings: Scheduler.detect_conflicts() flags pending tasks that share
    # the exact same due_date, which is the situation a pet owner most needs a heads
    # up about (two care actions they cannot both be present for at the same moment).
    st.markdown("**Conflict check**")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")
    else:
        st.success("No scheduling conflicts detected.")

st.divider()

st.subheader("Build Today's Schedule")
st.caption("Calls Scheduler.build_daily_plan() for today's date, ordered by priority then due time.")

if st.button("Generate schedule"):
    plan = scheduler.build_daily_plan(datetime.now())

    if plan:
        st.write(f"Today's plan, ordered by priority (highest first):")
        for t in plan:
            st.markdown(
                f"- **{t.title}** ({t.pet.name if t.pet else '?'}) — {t.priority} priority, "
                f"{t.duration_minutes} min, due {t.due_date.strftime('%I:%M %p')}"
            )

        plan_conflicts = scheduler.detect_conflicts(plan)
        if plan_conflicts:
            for warning in plan_conflicts:
                st.warning(f"⚠️ {warning}")
        else:
            st.success("No conflicts in today's plan.")
    else:
        st.info("No tasks due today. Add a task with today's due date above.")

    overdue = scheduler.get_overdue_tasks()
    if overdue:
        st.warning(
            "⚠️ Overdue: " + ", ".join(f"'{t.title}' ({t.pet.name if t.pet else '?'})" for t in overdue)
        )
