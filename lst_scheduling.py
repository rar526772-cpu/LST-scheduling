from dataclasses import dataclass


@dataclass
class Task:
    name: str
    execution_time: int
    period: int
    deadline: int = None

    def __post_init__(self):
        if self.deadline is None:
            self.deadline = self.period
        self.remaining = self.execution_time
        self.next_release = 0
        self.release_count = 0
        self.absolute_deadline = self.deadline


def compute_slack(task: Task, current_time: int) -> int:
    if task.remaining <= 0:
        return float('inf')
    return task.absolute_deadline - current_time - task.remaining


def lst_schedule(tasks: list, max_time: int):
    schedule = []
    current_time = 0
    idle_periods = []
    deadline_misses = []

    while current_time < max_time:
        for task in tasks:
            if current_time >= task.next_release and task.remaining <= 0:
                task.remaining = task.execution_time
                task.absolute_deadline = task.next_release + task.deadline
                task.next_release += task.period
                task.release_count += 1
            elif task.release_count == 0 and task.next_release == 0:
                task.remaining = task.execution_time
                task.absolute_deadline = task.deadline
                task.next_release = task.period
                task.release_count = 1

        active_tasks = [t for t in tasks if t.remaining > 0]

        if not active_tasks:
            if not idle_periods or idle_periods[-1][1] != current_time:
                idle_periods.append([current_time, current_time + 1])
            else:
                idle_periods[-1][1] = current_time + 1
            current_time += 1
            continue

        slacks = {}
        for task in active_tasks:
            slacks[task.name] = compute_slack(task, current_time)

        min_slack = min(slacks.values())
        selected_tasks = [name for name, s in slacks.items() if s == min_slack]

        if len(selected_tasks) > 1:
            selected = next(t for t in active_tasks if t.name in selected_tasks)
        else:
            selected = next(t for t in active_tasks if t.name == selected_tasks[0])

        if min_slack < 0:
            deadline_misses.append((current_time, selected.name))

        if schedule and schedule[-1][2] == selected.name and schedule[-1][1] == current_time:
            schedule[-1] = (schedule[-1][0], current_time + 1, selected.name)
        else:
            schedule.append((current_time, current_time + 1, selected.name))

        selected.remaining -= 1
        current_time += 1

    return schedule, idle_periods, deadline_misses


def print_results(schedule, idle_periods, deadline_misses, max_time):
    print("\nTask Execution Order:")
    print("-" * 40)
    for i, (start, end, task) in enumerate(schedule, 1):
        print(f"  {i}. [{start:3d} - {end:3d}] -> {task}")

    if idle_periods:
        print("\nIdle Periods:")
        print("-" * 40)
        for start, end in idle_periods:
            print(f"  [{start:3d} - {end:3d}]")

    if deadline_misses:
        print("\nDeadline Misses:")
        print("-" * 40)
        for time, task in deadline_misses:
            print(f"  Time {time}: {task}")
    else:
        print("\nNo Deadline Misses.")

    print("\nGantt Chart:")
    print("-" * 40)
    timeline = [" "] * (max_time + 1)
    for start, end, task in schedule:
        for t in range(start, min(end, max_time + 1)):
            timeline[t] = task[-1]

    bar = "".join(timeline[:max_time + 1])
    print(f"  {bar}")


if __name__ == "__main__":
    tasks = [
        Task(name="T1", execution_time=1, period=4, deadline=4),
        Task(name="T2", execution_time=2, period=5, deadline=5),
        Task(name="T3", execution_time=2, period=6, deadline=6),
    ]

    MAX_TIME = 20

    schedule, idle_periods, deadline_misses = lst_schedule(tasks, MAX_TIME)
    print_results(schedule, idle_periods, deadline_misses, MAX_TIME)
