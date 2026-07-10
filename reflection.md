# PawPal+ Project Reflection

## 1. System Design

Three core actions the user should be able to perform are: adding a pet to the system, scheduling a walk for that pet, and viewing today's tasks or upcoming appointments in one place.

**a. Initial design**

The system is built around four classes: Owner, Pet, Task, and Appointment.

**Owner** is the top-level user of the system. It holds the owner's personal details (name, email, phone, address) and maintains a list of their pets. Its responsibilities are managing the pet roster (adding and removing pets) and providing a single point of access to all tasks and appointments across every pet they own.

**Pet** sits at the centre of the design and acts as the link between the owner and their care activities. It stores the animal's profile (species, breed, age, weight, health notes) and is responsible for managing two collections — tasks and appointments — that belong to it. It exposes methods to retrieve upcoming tasks, past care history, and upcoming appointments.

**Task** represents a single care action that needs to be performed for a pet, such as feeding, exercise, grooming, or medication. It carries scheduling information (due date, duration, recurrence) and a priority level that the scheduler uses to order work. Its responsibilities are tracking completion state, signalling when it is overdue, and returning a numeric priority score.

**Appointment** represents a scheduled external event, typically a vet visit. It holds the location, vet name, appointment type, and a status that moves through its lifecycle (scheduled → confirmed → cancelled/completed). Its responsibilities are managing rescheduling and cancellation, and generating a human-readable reminder string.

**b. Design changes**

After reviewing the skeleton with an AI coding assistant, four issues were identified and addressed:

**1. `Task.pet` and `Appointment.pet` made optional (default `None`)**
Both fields were originally required constructor arguments. This created a circular dependency: you need a `Pet` object to create a `Task`, but the task may not be assigned to a pet yet. Making them optional and letting `Pet.add_task()` / `Pet.add_appointment()` set the link decouples object creation from assignment.

**2. `Pet._tasks` and `Pet._appointments` marked `init=False`**
`dataclass` fields with a leading underscore are intended to be private, but they still appeared as constructor parameters without `init=False`. Adding `init=False` hides them from the constructor, meaning only `add_task()` and `add_appointment()` can populate them — which is the correct interface.

**3. `completed_at` field added to `Task`**
`get_care_history()` is meant to show when care actually happened, but the only date field was `due_date` (when it was planned). These are different: a task due Monday could be completed on Wednesday. `completed_at` is set by `mark_complete()` and gives the history method accurate data to sort on.

**4. `Scheduler` class added**
The original design had no class to own the scheduling logic. `get_upcoming_tasks()` on `Pet` returns a list, but nothing builds an actual ordered daily plan. A `Scheduler` class was added to give this core responsibility a dedicated home, keeping the scheduling logic separate from the data model classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

`Scheduler.detect_conflicts()` only flags tasks whose `due_date` matches **exactly**
(down to the minute) — it does not check whether two tasks' durations *overlap*. A
20-minute grooming session at 11:00 AM and a 15-minute walk at 11:10 AM genuinely
conflict (the second starts before the first ends), but as implemented they would not
be flagged, because their `due_date` values differ.

This tradeoff is reasonable for now because exact-match grouping is O(n) (a single
pass building a `dict` keyed by `due_date`), while true overlap detection means
comparing every task's `[start, start + duration)` interval against every other
task's interval — either an O(n²) pairwise scan or a sweep-line algorithm that sorts
by start time and tracks active intervals. For a single owner with a handful of pets
and a few tasks a day, exact-match conflicts (e.g. two recurring daily tasks that
happen to land on the same clock time) are the more common and more obviously
actionable case, so the simpler check was implemented first. Overlap-aware detection
is a reasonable next iteration if task volume grows.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
