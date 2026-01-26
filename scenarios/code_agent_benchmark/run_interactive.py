#!/usr/bin/env python3
"""Entry point for the AI Code Agent Benchmark interactive wizard."""

import os
import sys
from pathlib import Path

# Add the project root and current folder to path
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from wizard.launcher import BenchmarkWizard


def main():
    """Run the benchmark wizard."""
    try:
        wizard = BenchmarkWizard(root_dir=str(project_root))
        wizard.run()
    except KeyboardInterrupt:
        print("\n👋 Good Bye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
