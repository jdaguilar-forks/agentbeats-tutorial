"""Script to explore BigCodeBench dataset structure."""

from datasets import load_dataset

print("=" * 60)
print("BigCodeBench Dataset Exploration")
print("=" * 60)
print()

# Load dataset
print("Loading BigCodeBench dataset from Hugging Face...")
try:
    dataset = load_dataset("bigcode/bigcodebench")
    print(f"✓ Dataset loaded successfully!")
    print()

    # Show splits
    print("Available splits:")
    for split_name in dataset.keys():
        print(f"  - {split_name}: {len(dataset[split_name])} examples")
    print()

    # Get first example from any available split
    split_names = list(dataset.keys())
    if split_names:
        split = split_names[0]
        example = dataset[split][0]

        print(f"Example task fields:")
        for key in example.keys():
            value = example[key]
            if isinstance(value, str) and len(value) > 100:
                print(f"  - {key}: {type(value).__name__} (length: {len(value)})")
            else:
                print(f"  - {key}: {value}")
        print()

        # Show first task details
        print("=" * 60)
        print("Sample Task")
        print("=" * 60)
        print(f"Task ID: {example.get('task_id', 'N/A')}")
        print()
        if "instruct_prompt" in example:
            print("Instruct Prompt:")
            print(example["instruct_prompt"][:500])
            print()
        if "complete_prompt" in example:
            print("Complete Prompt (first 300 chars):")
            print(example["complete_prompt"][:300])
            print()
        if "test" in example:
            print("Tests (first 300 chars):")
            print(example["test"][:300])
            print()
        if "libs" in example:
            print(f"Required libraries: {example['libs']}")
            print()

except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    import traceback

    traceback.print_exc()
