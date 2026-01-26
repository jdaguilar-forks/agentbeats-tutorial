#!/usr/bin/env python3
"""Test script to verify Open Router configuration."""

import os
from dotenv import load_dotenv
from litellm import completion

# Load environment variables
load_dotenv()

# Configure litellm for Open Router
openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY", "")
if openrouter_api_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
else:
    print("✗ OPEN_ROUTER_API_KEY not found in environment variables")
    exit(1)

os.environ["LITELLM_DROP_PARAMS"] = "True"
os.environ["LITELLM_SET_VERBOSE"] = "True"

def test_openrouter_connection():
    """Test basic Open Router connection."""
    print("Testing Open Router connection...")

    try:
        # Simple test prompt - need to specify Open Router provider
        response = completion(
            model="openrouter/qwen/qwen3-coder:free",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Write a Python function to add two numbers."},
            ],
            temperature=0.2,
        )

        print("✓ Open Router connection successful!")
        print(f"Model used: {response.model}")
        print(f"Response length: {len(response.choices[0].message.content)} characters")
        print("Sample response:")
        print(response.choices[0].message.content[:100] + "...")

        return True

    except Exception as e:
        print(f"✗ Open Router connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_connection()
    if success:
        print("\n✓ Open Router is properly configured!")
    else:
        print("\n✗ Open Router configuration failed. Check your API key and network connection.")