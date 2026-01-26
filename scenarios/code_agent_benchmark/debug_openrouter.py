"""Debug OpenRouter connection and model generation."""

import os
from dotenv import load_dotenv
from litellm import completion

# Load environment variables
load_dotenv()

# Setup API Key
openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY", "")
if openrouter_api_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
    print(f"✅ Found OPEN_ROUTER_API_KEY (length: {len(openrouter_api_key)})")
else:
    print("❌ OPEN_ROUTER_API_KEY not found in .env")
    exit(1)

# Configuration
model = "openrouter/google/gemma-2-9b-it:free"
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a python function that adds two numbers."},
]

print(f"\nTesting generation with model: {model}")
print("-" * 50)

try:
    response = completion(model=model, messages=messages, timeout=60)

    print("✅ Success! Response received:")
    print("-" * 50)
    print(response.choices[0].message.content)
    print("-" * 50)

except Exception as e:
    print(f"\n❌ Generation failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")

    # Check for common issues
    error_str = str(e).lower()
    if "401" in error_str:
        print("\nPossible cause: Invalid API Key")
    elif "404" in error_str:
        print("\nPossible cause: Model not found (check model ID)")
    elif "429" in error_str:
        print("\nPossible cause: Rate limit exceeded (free tier?)")
    elif "context_length_exceeded" in error_str:
        print("\nPossible cause: Context length exceeded")
