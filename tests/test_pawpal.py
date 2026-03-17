from pawpal_system import Owner, Pet, Task


def test_adding_task_to_pet_increases_task_count() -> None:
	owner = Owner(name="Jordan", email="jordan@example.com", available_time_per_day=60)
	pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
	owner.add_pet(pet)

	starting_count = len(pet.tasks)
	task = Task(name="Evening Walk", category="exercise", duration=20, priority=2, pet=pet)

	owner.add_task(task)

	assert len(pet.tasks) == starting_count + 1


def test_mark_complete_changes_task_status() -> None:
	task = Task(name="Give Medication", category="health", duration=10, priority=1)

	assert task.status == "pending"
	task.mark_complete()

	assert task.status == "completed"
