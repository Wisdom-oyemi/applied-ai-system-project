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
        pass

    def get_special_needs(self) -> list[str]:
        pass


@dataclass
class Task:
    name: str
    category: str
    duration: float          # in minutes
    priority: int            # 1 (highest) to 5 (lowest)
    pet: Pet = None
    recurrence: str = "daily"  # e.g. "daily", "weekly", "as needed"

    def get_priority(self) -> int:
        pass

    def is_time_available(self, time: float) -> bool:
        pass

    def get_estimated_duration(self) -> float:
        pass


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
        pass

    def add_task(self, task: Task) -> None:
        # should also call task.pet.tasks.append(task) to keep Pet in sync
        pass

    def get_schedule(self) -> list:
        # delegates to self.scheduler.generate_schedule()
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        # pets and tasks are read from owner directly — no duplicate state
        self.daily_schedule: list = []

    def generate_schedule(self) -> list:
        pass

    def optimize_schedule(self, constraints: dict) -> list:
        pass

    def explain_reasoning(self) -> str:
        pass

    def can_fit_task(self, task: Task, time: float) -> bool:
        pass
