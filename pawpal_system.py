from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: float
    health_conditions: list[str] = field(default_factory=list)
    tasks: list["Task"] = field(default_factory=list)  # back-reference to assigned tasks

    def get_assigned_tasks(self) -> list:
        """Return a copy of tasks currently assigned to this pet."""
        return list(self.tasks)

    def get_special_needs(self) -> list[str]:
        """Return a copy of this pet's health-related special needs."""
        return list(self.health_conditions)


@dataclass
class Task:
    name: str
    category: str
    duration: float          # in minutes
    priority: int            # 1 (highest) to 5 (lowest)
    pet: Pet = None
    recurrence: str = "daily"  # e.g. "daily", "weekly", "as needed"
    status: str = "pending"

    def get_priority(self) -> int:
        """Return this task's priority as an integer."""
        return int(self.priority)

    def is_time_available(self, time: float) -> bool:
        """Return whether the provided available time can fit this task."""
        return time >= self.duration

    def get_estimated_duration(self) -> float:
        """Return the estimated task duration in minutes."""
        return float(self.duration)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"


class Owner:
    def __init__(self, name: str, email: str, available_time_per_day: float, preferences: dict = None):
        self.name = name
        self.email = email
        self.available_time_per_day = available_time_per_day  # in minutes
        self.preferences: dict = preferences or {}
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []
        self.scheduler: "Scheduler" = None  # set after Scheduler is created

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner if it is valid and not already tracked."""
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet instance")

        if pet not in self.pets:
            self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a task to this owner and sync it to the assigned pet."""
        # should also call task.pet.tasks.append(task) to keep Pet in sync
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance")

        if task.pet is not None and task.pet not in self.pets:
            self.add_pet(task.pet)

        if task not in self.tasks:
            self.tasks.append(task)

        if task.pet is not None and task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def get_schedule(self) -> list:
        """Generate and return today's schedule through the scheduler."""
        # delegates to self.scheduler.generate_schedule()
        if self.scheduler is None:
            self.scheduler = Scheduler(self)
        return self.scheduler.generate_schedule()


class Scheduler:
    def __init__(self, owner: Owner):
        """Create a scheduler bound to an owner and their tasks."""
        self.owner = owner
        # pets and tasks are read from owner directly — no duplicate state
        self.daily_schedule: list = []

    def generate_schedule(self) -> list:
        """Build a daily schedule from owner tasks using priority and time limits."""
        available_time = float(self.owner.available_time_per_day)
        remaining_time = available_time
        start_minute = 0.0

        prioritized_tasks = sorted(
            self.owner.tasks,
            key=lambda t: (t.get_priority(), t.get_estimated_duration(), t.name.lower()),
        )

        schedule: list[dict] = []
        for task in prioritized_tasks:
            if not self.can_fit_task(task, remaining_time):
                continue

            duration = task.get_estimated_duration()
            schedule.append(
                {
                    "task": task.name,
                    "pet": task.pet.name if task.pet else None,
                    "category": task.category,
                    "priority": task.get_priority(),
                    "duration": duration,
                    "start_minute": start_minute,
                    "end_minute": start_minute + duration,
                    "recurrence": task.recurrence,
                    "reason": "Selected due to priority and available time.",
                }
            )
            start_minute += duration
            remaining_time -= duration

        self.daily_schedule = schedule
        return list(self.daily_schedule)

    def optimize_schedule(self, constraints: dict) -> list:
        """Build a schedule after filtering tasks with provided constraints."""
        constraints = constraints or {}
        max_time = float(constraints.get("max_time", self.owner.available_time_per_day))
        include_categories = constraints.get("include_categories")
        exclude_categories = set(constraints.get("exclude_categories", []))
        max_priority = constraints.get("max_priority")

        filtered_tasks = []
        for task in self.owner.tasks:
            if include_categories and task.category not in set(include_categories):
                continue
            if task.category in exclude_categories:
                continue
            if max_priority is not None and task.get_priority() > int(max_priority):
                continue
            filtered_tasks.append(task)

        filtered_tasks.sort(key=lambda t: (t.get_priority(), t.get_estimated_duration(), t.name.lower()))

        schedule: list[dict] = []
        remaining_time = max_time
        start_minute = 0.0
        for task in filtered_tasks:
            if not self.can_fit_task(task, remaining_time):
                continue

            duration = task.get_estimated_duration()
            schedule.append(
                {
                    "task": task.name,
                    "pet": task.pet.name if task.pet else None,
                    "category": task.category,
                    "priority": task.get_priority(),
                    "duration": duration,
                    "start_minute": start_minute,
                    "end_minute": start_minute + duration,
                    "recurrence": task.recurrence,
                    "reason": "Included after applying optimization constraints.",
                }
            )
            start_minute += duration
            remaining_time -= duration

        self.daily_schedule = schedule
        return list(self.daily_schedule)

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of scheduled task choices."""
        if not self.daily_schedule:
            return "No tasks are currently scheduled."

        lines = ["PawPal+ Schedule Reasoning:"]
        for item in self.daily_schedule:
            pet_label = f" for {item['pet']}" if item["pet"] else ""
            lines.append(
                (
                    f"- {item['task']}{pet_label}: priority {item['priority']}, "
                    f"{item['duration']} min, {item['reason']}"
                )
            )
        return "\n".join(lines)

    def can_fit_task(self, task: Task, time: float) -> bool:
        """Return whether a task can fit within the remaining time."""
        return task.is_time_available(time)
