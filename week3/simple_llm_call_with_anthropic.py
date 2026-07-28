# claude_example.py
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Single message
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say hello in 5 words"}
    ]
)

print(response.content[0].text)

# Multi-turn conversation
messages = []

def chat_claude(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=messages
    )
    
    assistant_message = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

# Use it
print(chat_claude("What is 2+2?"))
print(chat_claude("What is that plus 5?"))  # Context preserved