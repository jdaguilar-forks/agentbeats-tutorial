"""Test BigCodeBench loader."""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent / "evaluator" / "src"))

from utils.bigcodebench_loader import BigCodeBenchLoader


def main():
    print("=" * 70)
    print("BigCodeBench Loader Test")
    print("=" * 70)
    print()

    # Initialize loader
    loader = BigCodeBenchLoader()
    print()

    # Load first 5 tasks
    print("Loading first 5 tasks...")
    tasks = loader.load_tasks(limit=5)
    print(f"✓ Loaded {len(tasks)} tasks")
    print()

    # Display tasks
    for i, task in enumerate(tasks, 1):
        print(f"Task {i}: {task['id']}")
        print(f"  Original ID: {task['original_id']}")
        print(f"  Title: {task['title']}")
        print(f"  Difficulty: {task['difficulty']}")
        print(f"  Required libs: {', '.join(task['required_libs'])}")
        print(f"  Solution length: {len(task['reference_solution'])} chars")
        print()

    # Get statistics
    print("=" * 70)
    print("Dataset Statistics")
    print("=" * 70)
    stats = loader.get_statistics()
    print(f"Total tasks: {stats['total_tasks']}")
    print(f"Unique libraries: {stats['unique_libraries']}")
    print(f"Difficulty distribution:")
    for difficulty, count in sorted(stats["difficulties"].items()):
        percentage = (count / stats["total_tasks"]) * 100
        print(f"  {difficulty}: {count} ({percentage:.1f}%)")
    print()
    print(f"Common libraries: {', '.join(stats['common_libraries'][:10])}")
    print()

    print("=" * 70)
    print("✓ BigCodeBench loader test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
