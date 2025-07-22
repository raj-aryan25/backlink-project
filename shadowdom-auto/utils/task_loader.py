import json


class task_loader:
    def __init__(self, task_file):
        self.task_file = task_file
        self.tasks = self.load_tasks()
        self.steps = self.get_steps()

    def load_tasks(self):
        try:
            with open(self.task_file, "r") as file:
                tasks = json.load(file)
            return tasks["tasks"]
        except FileNotFoundError:
            print(f"Error: The file {self.task_file} does not exist.")
            return []
        except json.JSONDecodeError:
            print(f"Error: The file {self.task_file} is not a valid JSON.")
            return []

    def get_tasks(self):
        return self.tasks

    # def get_urls(self):
    #     urls = []
    #     for task in self.tasks:
    #         urls.append(task.get("url", ""))
    #     return urls

    def get_steps(self):
        steps = []
        for task in self.tasks:
            url = task.get("url", "")
            actions = []
            details = {}
            for action in task.get("actions", []):
                actions.append(action.get("task", ""))
                if "fill" in action.get("task"):
                    details = action.get("details", {})
            steps.append({"url": url, "actions": actions, "details": details})
        return steps


# Example usage:
# if __name__ == "__main__":
#     loader = task_loader("../tasks/tasks.json")
#     tasks = loader.get_tasks()
#     print(tasks)
#     steps = loader.get_steps()
#     print(steps)
