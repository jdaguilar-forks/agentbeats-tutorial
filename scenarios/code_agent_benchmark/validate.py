"""Quick validation test for the code benchmark setup."""

import sys
import json
from pathlib import Path

# Add evaluator src to path
sys.path.insert(0, str(Path(__file__).parent / "evaluator" / "src"))

from utils.task_loader import TaskLoader


def test_task_loading():
    """Test that tasks can be loaded successfully."""
    tasks_dir = Path(__file__).parent / "tasks"
    loader = TaskLoader(str(tasks_dir))

    # Load all code generation tasks
    tasks = loader.load_tasks_by_category("code_generation")

    print(f"✓ Loaded {len(tasks)} code generation tasks")

    # Validate task structure
    for task in tasks:
        required_fields = [
            "id",
            "category",
            "difficulty",
            "title",
            "prompt",
            "test_code",
        ]
        for field in required_fields:
            assert field in task, f"Task {task.get('id', '?')} missing field: {field}"

        print(f"  ✓ {task['id']}: {task['title']} ({task['difficulty']})")

    print(f"\\n✓ All {len(tasks)} tasks validated successfully!")
    return True


def test_task_json_format():
    """Test that all task JSON files are valid."""
    tasks_dir = Path(__file__).parent / "tasks" / "code_generation"

    json_files = list(tasks_dir.glob("*.json"))
    print(f"\\nValidating {len(json_files)} JSON task files...")

    for json_file in sorted(json_files):
        with open(json_file) as f:
            data = json.load(f)
        print(f"  ✓ {json_file.name} is valid JSON")

    print(f"\\n✓ All JSON files are valid!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Code Agent Benchmark - Validation Tests")
    print("=" * 60)
    print()

    try:
        test_task_json_format()
        test_task_loading()
        print()
        print("=" * 60)
        print("✓ ALL VALIDATION TESTS PASSED!")
        print("=" * 60)
    except Exception as e:
        print(f"\\n✗ Validation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
