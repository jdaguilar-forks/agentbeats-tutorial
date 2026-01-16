"""BigCodeBench task loader for AgentBeats framework."""

from typing import List, Dict, Any, Optional
import ast
from datasets import load_dataset


class BigCodeBenchLoader:
    """Loads and manages BigCodeBench tasks."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize BigCodeBench loader.

        Args:
            cache_dir: Optional directory to cache downloaded dataset
        """
        self.dataset = None
        self.cache_dir = cache_dir
        self._load_dataset()

    def _load_dataset(self):
        """Load BigCodeBench dataset from Hugging Face."""
        print("Loading BigCodeBench dataset...")
        self.dataset = load_dataset("bigcode/bigcodebench", cache_dir=self.cache_dir)
        print(f"✓ Loaded BigCodeBench with {len(self.dataset['v0.1.2'])} tasks")

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single task by ID.

        Args:
            task_id: Task ID (e.g., "BigCodeBench/0")

        Returns:
            Task dictionary or None if not found
        """
        # Search through all splits
        for split_name in self.dataset.keys():
            for task in self.dataset[split_name]:
                if task["task_id"] == task_id:
                    return self._format_task(task)
        return None

    def load_tasks(
        self,
        split: str = "v0.1.2",
        limit: Optional[int] = None,
        task_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Load tasks from BigCodeBench.

        Args:
            split: Dataset split to use (default: v0.1.2, latest version)
            limit: Maximum number of tasks to load
            task_ids: Optional list of specific task IDs to load

        Returns:
            List of task dictionaries in AgentBeats format
        """
        if split not in self.dataset:
            available = list(self.dataset.keys())
            raise ValueError(f"Split '{split}' not found. Available: {available}")

        tasks = []
        for idx, task in enumerate(self.dataset[split]):
            # Filter by task_ids if provided
            if task_ids and task["task_id"] not in task_ids:
                continue

            tasks.append(self._format_task(task))

            # Apply limit if specified
            if limit and len(tasks) >= limit:
                break

        return tasks

    def _parse_libs(self, task: Dict[str, Any]) -> List[str]:
        """
        Parse the 'libs' field from the task, which can be a list or a string representation of a list.
        """
        libs = task.get("libs")
        if isinstance(libs, list):
            return libs
        elif isinstance(libs, str):
            try:
                parsed_libs = ast.literal_eval(libs)
                if isinstance(parsed_libs, list):
                    return parsed_libs
            except (ValueError, SyntaxError):
                pass  # Fall through to return empty list
        return []

    def _format_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert BigCodeBench task to AgentBeats format.

        Args:
            task: Raw task from BigCodeBench dataset

        Returns:
            Task formatted for AgentBeats benchmark
        """
        # Extract task ID number for our internal ID
        task_num = task["task_id"].split("/")[-1]

        return {
            "id": f"bigcodebench_{task_num}",
            "original_id": task["task_id"],
            "category": "code_generation",
            "difficulty": self._estimate_difficulty(task),
            "title": self._extract_title(task),
            "description": task["instruct_prompt"],
            "prompt": task["complete_prompt"],
            "test_code": task["test"],
            "reference_solution": task["canonical_solution"],
            "entry_point": task["entry_point"],
            "required_libs": self._parse_libs(task),
            "metadata": {
                "time_limit_seconds": 120,  # BigCodeBench tasks can be complex
                "max_tokens": 2000,
                "tags": ["bigcodebench"]
                + (self._parse_libs(task)[:3]),  # Use parsed libs for tags
                "source": "BigCodeBench",
            },
        }

    def _extract_title(self, task: Dict[str, Any]) -> str:
        """Extract a short title from the task description."""
        description = task["instruct_prompt"]
        # Take first sentence or first 80 chars
        first_sentence = description.split(".")[0]
        if len(first_sentence) > 80:
            return first_sentence[:77] + "..."
        return first_sentence

    def _estimate_difficulty(self, task: Dict[str, Any]) -> str:
        """
        Estimate task difficulty based on heuristics.

        Args:
            task: Task dictionary

        Returns:
            "easy", "medium", or "hard"
        """
        # Heuristics for difficulty estimation
        num_libs = len(task["libs"])
        solution_length = len(task["canonical_solution"])
        test_length = len(task["test"])

        # Simple heuristic based on complexity indicators
        complexity_score = 0

        # More libraries = potentially more complex
        if num_libs >= 3:
            complexity_score += 2
        elif num_libs >= 2:
            complexity_score += 1

        # Longer solutions are usually more complex
        if solution_length > 500:
            complexity_score += 2
        elif solution_length > 250:
            complexity_score += 1

        # More comprehensive tests suggest complexity
        if test_length > 2000:
            complexity_score += 1

        # Map score to difficulty
        if complexity_score >= 4:
            return "hard"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "easy"

    def get_statistics(self, split: str = "v0.1.2") -> Dict[str, Any]:
        """
        Get dataset statistics.

        Args:
            split: Dataset split to analyze

        Returns:
            Dictionary with statistics
        """
        tasks = self.load_tasks(split=split)

        # Count by difficulty
        difficulties = {}
        for task in tasks:
            diff = task["difficulty"]
            difficulties[diff] = difficulties.get(diff, 0) + 1

        # Get unique libraries
        all_libs = set()
        for task in tasks:
            all_libs.update(task["required_libs"])

        return {
            "total_tasks": len(tasks),
            "difficulties": difficulties,
            "unique_libraries": len(all_libs),
            "common_libraries": sorted(all_libs)[:20],  # Top 20
        }
