# pip install openai python-dotenv requests httpx fastapi uvicorn pydantic

from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

models = [m.id for m in client.models.list().data]
print(f"Models (2):: {models} ")


# Make your first API call
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Say hello in 5 words"}
    ]
)

# Parse response
print(response.choices[0].message.content)
# Output: "Hello, nice to meet you today!"

# Key info from response
print(f"Model: {response.model}")
print(f"Tokens used: {response.usage.total_tokens}")
print(f"Stop reason: {response.choices[0].finish_reason}")
