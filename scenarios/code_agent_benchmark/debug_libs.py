"""Quick script to check libs field type."""

from datasets import load_dataset
import ast

dataset = load_dataset("bigcode/bigcodebench")
example = dataset["v0.1.2"][0]

print(f"libs field: {example['libs']}")
print(f"libs type: {type(example['libs'])}")
print(f"libs length: {len(example['libs'])}")

# Try parsing as pythonlist
if isinstance(example["libs"], str):
    try:
        parsed = ast.literal_eval(example[" libs"])
        print(f"Parsed as list: {parsed}")
    except:
        print("Could not parse as list")
