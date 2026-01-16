"""Task loader utility for loading task definitions from JSON files."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class TaskLoader:
    """Loads and manages task definitions."""

    def __init__(self, tasks_dir: str):
        self.tasks_dir = Path(tasks_dir)

    def load_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load a single task by ID."""
        # Search through all category directories
        for category_dir in self.tasks_dir.iterdir():
            if not category_dir.is_dir():
                continue

            for task_file in category_dir.glob("*.json"):
                task_data = json.loads(task_file.read_text())
                if task_data.get("id") == task_id:
                    return task_data

        return None

    def load_tasks_by_category(
        self,
        category: str,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Load tasks from a specific category."""
        category_dir = self.tasks_dir / category
        if not category_dir.exists():
            return []

        tasks = []
        for task_file in sorted(category_dir.glob("*.json")):
            task_data = json.loads(task_file.read_text())

            # Filter by difficulty if specified
            if difficulty and task_data.get("difficulty") != difficulty:
                continue

            tasks.append(task_data)

            # Apply limit if specified
            if limit and len(tasks) >= limit:
                break

        return tasks

    def load_all_tasks(self) -> List[Dict[str, Any]]:
        """Load all available tasks."""
        tasks = []
        for category_dir in self.tasks_dir.iterdir():
            if not category_dir.is_dir():
                continue

            for task_file in category_dir.glob("*.json"):
                task_data = json.loads(task_file.read_text())
                tasks.append(task_data)

        return tasks
