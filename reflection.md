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

The scheduler considers three constraints, in this order of importance:

1. **Priority** (`low`/`medium`/`high`, scored 1–3 by `Task.get_priority_score()`) — the primary sort key for `build_daily_plan()` and `suggest_next_task()`. A medication task and a playtime task due at the same hour should not be treated as interchangeable, so priority dominates.
2. **Time** (`due_date`) — the tie-breaker within a priority tier, and the sole key for `sort_by_time()` when the question is "what's next" rather than "what matters most." Time is also what `detect_conflicts()` groups on, since two tasks literally cannot both happen at the same instant.
3. **Completion status** — every scheduler method excludes completed tasks before applying priority/time ordering, so a finished task never re-appears in a plan or a conflict warning.

Priority was chosen as the dominant constraint over pure chronological order because a pet owner's real failure mode is missing something *important* (medication, a vet-mandated task), not just something *early*. Two low-effort tasks being slightly out of time order costs little; a high-priority task getting buried under lower-priority-but-earlier ones costs more. "Owner preference" (e.g. a preferred walk time) was considered but not implemented — there was no preference data on `Owner` to hang it off of, and adding a rule that isn't backed by a real field would have been dead code, so it was left as a possible extension rather than a constraint the scheduler currently enforces.

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

The most effective use of the AI assistant was as a **design reviewer**, not a code generator: pasting the class skeleton from Phase 1 and asking it to find structural problems before any scheduling logic was written. That single pass surfaced all four issues listed in Section 1b — the `Task.pet`/`Appointment.pet` circular-dependency, the missing `init=False` on private dataclass fields, the missing `completed_at` timestamp, and the absence of a `Scheduler` class. Those are exactly the kind of mistakes that are cheap to fix before any logic depends on them and expensive to fix after. The next most useful mode was **targeted implementation review** — asking "what edge cases does `detect_conflicts()`/`mark_task_complete()` miss?" turned directly into the edge-case tests in Section 4 (task with no pet, chained recurrence, empty pet). Broad open-ended prompts ("make this better") were much less useful than specific ones naming a method and asking what could break it.

**b. Judgment and verification**

The clearest rejected suggestion was for `detect_conflicts()`. When asked how to make conflict detection more robust, the AI's first suggestion was interval-overlap detection: sort tasks by start time and sweep-line-compare `[start, start + duration)` ranges so a 20-minute task at 11:00 and a 15-minute task at 11:10 would both be flagged, even though their `due_date` values differ. That is a genuinely more correct model of "conflict," but it was **not** adopted for this iteration — it trades an O(n) dict-grouping pass for either an O(n²) pairwise scan or a sweep-line algorithm, and for a single owner with a handful of pets and a few tasks a day, that complexity wasn't justified yet. Instead, the simpler exact-`due_date`-match version was kept, and the limitation was written down explicitly (Section 2b, and in the README) rather than silently accepted. Verification here meant reasoning about the actual data volume the app would see, not just which algorithm was "more correct" in the abstract — the more sophisticated suggestion is documented as the obvious next step if task volume grows, rather than being either blindly adopted or discarded.

Separately, keeping design-review conversations, implementation conversations, and test-writing conversations in **separate chat sessions** (rather than one long thread) helped avoid a subtle failure mode: an AI assistant that's just spent an hour deep in scheduling-logic details tends to keep suggesting logic tweaks even when what's actually needed is a fresh, adversarial read of "what's wrong with this class design" or "what test is missing." Starting a new session for each phase reset that context so the AI's suggestions matched the actual task at hand instead of anchoring on whatever it had been discussing five messages earlier.

---

## 4. Testing and Verification

**a. What you tested**

`tests/test_pawpal.py` grew from 11 to 25 tests, organized around the three behaviors
that matter most for a scheduler: **sorting correctness**, **recurrence logic**, and
**conflict detection**, plus the task/appointment lifecycle they all depend on.

- **Sorting** — `get_upcoming_tasks()` and `Owner.get_all_tasks()` return tasks in
  chronological order across *different days*, not just time-of-day on the same day
  (`sort_by_time()` was already covered but only tests the HH:MM case). Also tested:
  same-priority same-instant ties break deterministically, and completed tasks never
  leak into `suggest_next_task()` / `build_daily_plan()`.
- **Recurrence** — completing a `daily` task spawns the next occurrence exactly one
  day later; completing a `weekly` task spawns one exactly one week later; and
  completing the *auto-generated follow-up* itself chains a third occurrence with a
  correctly incremented `task_id`. This last case matters because `mark_task_complete()`
  computes the new ID via `max(owner.get_all_tasks()) + 1` — a subtle cross-object
  dependency that a single-completion test wouldn't catch.
- **Conflict detection** — flags two tasks at the exact same `due_date`, scales to
  three simultaneous clashes (not just pairs), ignores completed tasks, and doesn't
  crash on a task with `pet=None` (the "unassigned" label in the warning string).
- **Edge cases** — an empty pet (no tasks/appointments at all) returns `[]`/`None`
  everywhere instead of raising, and the `Appointment` lifecycle (reschedule resets
  status, cancel removes it from "upcoming") was untested before this pass.

These were important because the scheduler's value proposition *is* correct ordering
and conflict-flagging — a bug there silently produces a wrong daily plan rather than
an obvious crash, so it needs direct test coverage rather than relying on manual
spot-checks in the Streamlit UI.

**b. Confidence**

Fairly confident in the exact-match logic covered above — all 25 tests pass and each
one pins down a specific, previously-unverified behavior rather than re-testing the
happy path. The known gap is the tradeoff already noted in Section 2: conflict
detection only catches identical `due_date` values, not overlapping durations, so
that's the next edge case worth testing (and implementing) if task volume grows —
e.g. two tasks 10 minutes apart where the first's `duration_minutes` runs into the
second's start time.

---

## 5. Reflection

**a. What went well**

The recurrence logic in `Pet.mark_task_complete()` is the part I'm most satisfied with, specifically how the tests exposed a subtlety the implementation itself doesn't advertise: the next task's ID is computed from `owner.get_all_tasks()` (every pet's tasks) rather than from `self._tasks` (just this pet's). That's a genuine cross-object dependency — get it wrong and two pets could eventually generate colliding task IDs — and it only surfaced because the test suite deliberately chained multiple completions across pets instead of testing one completion in isolation (Section 4a). Catching that kind of bug through a test built to exercise it, rather than through manual spot-checking in the Streamlit UI, is the outcome the design was aiming for.

**b. What you would improve**

Given another iteration, I'd implement the overlap-aware conflict detection described in Section 2b instead of leaving it as documented future work — right now `detect_conflicts()` would miss a 20-minute grooming session at 11:00 AM clashing with a 15-minute walk starting at 11:10 AM, which is a real gap for a busy pet owner juggling multiple tasks. I'd also add owner-level preferences (e.g. a preferred time window per task category) as an actual field on `Owner` so the scheduler's priority-then-time ordering (Section 2a) could be refined by a third constraint instead of stopping at two.

**c. Key takeaway**

Being the "lead architect" with an AI assistant meant the value came from deciding *what to ask* and *what to keep*, not from writing every line. The AI was consistently good at generating options (an overlap-detection algorithm, a longer test list, a UML update) but had no way to know which of those options fit the actual constraints of this project — a single owner, a handful of pets, a classroom deadline. That judgment call was mine every time: keep the simple O(n) conflict check and write down the tradeoff, rather than adopt the more "correct" but heavier algorithm just because it was suggested. The discipline this project reinforced is that reviewing and rejecting AI suggestions with a stated reason is itself part of the design work, not a detour from it — and writing that reason down (in this reflection, in code comments, in the README) is what keeps the system coherent instead of turning into whatever the AI proposed most recently.
