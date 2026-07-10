from datetime import datetime, date, time

import streamlit as st

# Step 1: bring the backend classes into this script so the UI can call real logic.
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+.

This app is now wired to the backend classes in `pawpal_system.py`. Owner/Pet/Task
objects live in `st.session_state` so they persist across Streamlit reruns, and the
buttons below call real methods instead of just editing UI state.
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

if "pet" not in st.session_state:
    pet = Pet(pet_id=1, name="Mochi", species="dog", breed="", age=0, owner=st.session_state.owner)
    st.session_state.owner.add_pet(pet)
    st.session_state.pet = pet

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0

owner = st.session_state.owner
pet = st.session_state.pet

st.subheader("Owner & Pet Profile")
owner_name = st.text_input("Owner name", value=owner.name)
pet_name = st.text_input("Pet name", value=pet.name)
species_options = ["dog", "cat", "other"]
species = st.selectbox(
    "Species",
    species_options,
    index=species_options.index(pet.species) if pet.species in species_options else 2,
)

if st.button("Save profile"):
    owner.name = owner_name
    pet.name = pet_name
    pet.species = species
    st.success(f"Saved profile for {pet.name} ({owner.name}).")

st.markdown("### Tasks")
st.caption("Tasks are added to the Pet object via Pet.add_task().")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    due_date_input = st.date_input("Due date", value=date.today())

if st.button("Add task"):
    st.session_state.task_counter += 1
    new_task = Task(
        task_id=st.session_state.task_counter,
        title=task_title,
        description="",
        due_date=datetime.combine(due_date_input, time.min),
        priority=priority,
        duration_minutes=int(duration),
    )
    pet.add_task(new_task)
    st.success(f"Added task '{task_title}' to {pet.name}.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "due_date": t.due_date.strftime("%Y-%m-%d"),
                "complete": t.is_complete,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Calls Scheduler.build_daily_plan() for today's date.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan(datetime.now())

    if plan:
        st.write(f"Plan for {pet.name} today, ordered by priority:")
        for t in plan:
            st.markdown(
                f"- **{t.title}** — {t.priority} priority, {t.duration_minutes} min "
                f"(chosen because higher-priority/due-earlier tasks are scheduled first)"
            )
    else:
        st.info("No tasks due today. Add a task with today's due date above.")
