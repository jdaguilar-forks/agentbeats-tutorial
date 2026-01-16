"""Test stdlib filtering for BigCodeBench tasks."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "evaluator" / "src"))

from utils.bigcodebench_loader import BigCodeBenchLoader
from utils.stdlib_filter import filter_stdlib_tasks, is_stdlib_only


def main():
    print("=" * 70)
    print("BigCodeBench Stdlib Filtering Test")
    print("=" * 70)
    print()

    # Load all tasks
    loader = BigCodeBenchLoader()
    all_tasks = loader.load_tasks()

    print(f"Total tasks loaded: {len(all_tasks)}")
    print()

    # Filter to stdlib only
    stdlib_tasks = filter_stdlib_tasks(all_tasks)

    print(f"Stdlib-only tasks: {len(stdlib_tasks)}")
    print(f"Percentage: {(len(stdlib_tasks) / len(all_tasks)) * 100:.1f}%")
    print()

    # Show difficulty distribution for stdlib tasks
    difficulties = {}
    for task in stdlib_tasks:
        diff = task["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("Stdlib tasks difficulty distribution:")
    for difficulty, count in sorted(difficulties.items()):
        percentage = (count / len(stdlib_tasks)) * 100
        print(f"  {difficulty}: {count} ({percentage:.1f}%)")
    print()

    # Show first 10 stdlib tasks
    print("=" * 70)
    print("Sample Stdlib Tasks (first 10)")
    print("=" * 70)
    for i, task in enumerate(stdlib_tasks[:10], 1):
        print(f"{i}. {task['id']}")
        print(f"   Title: {task['title'][:60]}...")
        print(f"   Difficulty: {task['difficulty']}")
        print(f"   Libraries: {', '.join(task['required_libs'])}")
        print()

    # Show some examples of non-stdlib tasks
    non_stdlib_tasks = [
        t for t in all_tasks if not is_stdlib_only(t.get("required_libs", []))
    ]
    print("=" * 70)
    print("Sample Non-Stdlib Tasks (first 5)")
    print("=" * 70)
    for i, task in enumerate(non_stdlib_tasks[:5], 1):
        print(f"{i}. {task['id']}")
        print(f"   Libraries: {', '.join(task['required_libs'])}")
        non_stdlib_libs = [
            lib
            for lib in task["required_libs"]
            if lib not in ["random", "itertools", "collections"]
        ]
        print(f"   Non-stdlib: {', '.join(non_stdlib_libs[:5])}")
        print()

    print("=" * 70)
    print(f"✓ Filtering complete! {len(stdlib_tasks)} stdlib tasks ready to use")
    print("=" * 70)


if __name__ == "__main__":
    main()
