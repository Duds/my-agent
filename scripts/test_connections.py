
import os
import sys

print("DEBUG: 1. Core library imports start")
import asyncio
from dotenv import load_dotenv
print("DEBUG: 2. Core library imports end")

# Add parent directory to path
sys.path.insert(0, os.getcwd())
print(f"DEBUG: 3. sys.path updated: {os.getcwd()}")

print("DEBUG: 4. Custom adapter import start")
from core.adapters_remote import AnthropicAdapter, MistralAdapter, MoonshotAdapter
print("DEBUG: 5. Custom adapter import end")

async def main():
    print("DEBUG: 6. Main started")
    load_dotenv()
    print("DEBUG: 7. .env loaded")
    print("DEBUG: 8. Test finished")

if __name__ == "__main__":
    print("DEBUG: 9. loop start")
    asyncio.run(main())
