import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env
load_dotenv()

# Choose API provider
print("Select API provider:")
print("1. OpenRouter")
print("2. Groq")
choice = input("Enter choice (1 or 2): ").strip()

if choice == "1":
    # OpenRouter configuration
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    provider_name = "OpenRouter"

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing from .env")
    if not base_url:
        raise ValueError("OPENROUTER_BASE_URL is missing from .env")
    if not model:
        raise ValueError("OPENROUTER_MODEL is missing from .env")

elif choice == "2":
    # Groq configuration
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    model = "openai/gpt-oss-20b"  # Groq model
    provider_name = "Groq"

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

else:
    raise ValueError("Invalid choice. Please enter 1 or 2.")

# Create client
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# Get user input
user_question = input("\nEnter your question: ").strip()

# Send test request
response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": user_question
        }
    ]
)

# Print response
print(f"\n{provider_name} response:")
print(response.choices[0].message.content)