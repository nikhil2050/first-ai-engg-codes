# Phase 1: LLM Foundations - Practical Coding Tutorial
## AI Backend Engineering Roadmap

---

## What You'll Build in Phase 1

- ✅ Connect to OpenAI/Claude API
- ✅ Make your first API call to an LLM
- ✅ Parse and handle responses
- ✅ Understand tokens and costs
- ✅ Build a simple chatbot
- ✅ Error handling for LLM calls

**Time**: 3-4 hours  
**Prerequisites**: Python, FastAPI basics, API concepts  
**Goal**: Comfortable calling LLMs from your code

---

## 1. Setup & Environment

### 1.1 Install Required Libraries

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install openai python-dotenv requests httpx fastapi uvicorn pydantic
```

### 1.2 Get API Keys

**Option A: OpenAI (Paid)**
- Go to https://platform.openai.com/api/keys
- Create API key
- Set billing limits to avoid surprises

**Option B: Anthropic Claude (Paid)**
- Go to https://console.anthropic.com/keys
- Create API key

**Option C: Free alternatives**
- Ollama (local LLM) - Free, runs on your machine
- HuggingFace Inference API - Limited free tier

### 1.3 Environment Variables

```bash
# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Or for Claude
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Add to .gitignore (NEVER commit keys!)
echo ".env" >> .gitignore
```

---

## 2. Your First LLM Call

### 2.1 Simple OpenAI API Call

```python
# simple_llm_call.py
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
```

**Run it**:
```bash
python simple_llm_call.py
```

**What happens**:
1. Client connects to OpenAI
2. Sends your message
3. LLM processes it
4. Returns response with metadata

---

## 3. Understanding the Response

### 3.1 Response Structure

```python
response = client.chat.completions.create(...)

# Response object contains:
response.id                          # Unique ID
response.model                       # Which model was used
response.choices[0].message.content  # ✅ The actual response
response.choices[0].finish_reason    # Why it stopped ("stop", "length")
response.usage.prompt_tokens         # Tokens in your prompt
response.usage.completion_tokens     # Tokens in response
response.usage.total_tokens          # Total (≈ cost)
```

### 3.2 Token Counting (Important for Cost!)

```python
# Tokens ≈ words (roughly)
# 1 token ≈ 4 characters ≈ 0.75 words

# Example costs (as of 2024):
# gpt-3.5-turbo: $0.50 per 1M input tokens, $1.50 per 1M output
# gpt-4: $30 per 1M input, $60 per 1M output

def estimate_cost(prompt_tokens, completion_tokens, model="gpt-3.5-turbo"):
    if model == "gpt-3.5-turbo":
        input_cost = (prompt_tokens / 1_000_000) * 0.50
        output_cost = (completion_tokens / 1_000_000) * 1.50
    elif model == "gpt-4":
        input_cost = (prompt_tokens / 1_000_000) * 30
        output_cost = (completion_tokens / 1_000_000) * 60
    
    total = input_cost + output_cost
    return total

# Example
tokens = estimate_cost(100, 50)
print(f"Cost: ${tokens:.6f}")
```

---

## 4. Building a Simple Chatbot

### 4.1 Multi-turn Conversation

```python
# chatbot.py
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history
messages = []

def chat(user_input: str) -> str:
    """Send message and get response"""
    # Add user message to history
    messages.append({"role": "user", "content": user_input})
    
    # Get response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7  # Creativity (0-1)
    )
    
    # Extract response
    assistant_message = response.choices[0].message.content
    
    # Add assistant response to history
    messages.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

# Interactive chatbot
print("Chatbot (type 'quit' to exit)")
print("-" * 40)

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        break
    
    response = chat(user_input)
    print(f"Bot: {response}\n")
```

**Run it**:
```bash
python chatbot.py
```

**Key concept**: Store `messages` list to maintain context. LLM sees entire conversation.

---

## 5. Error Handling for LLM Calls

### 5.1 Common Errors & How to Handle

```python
from openai import OpenAI, APIError, RateLimitError, AuthenticationError
from dotenv import load_dotenv
import os
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Call LLM with error handling and retry logic"""
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                timeout=30  # Prevent hanging
            )
            return response.choices[0].message.content
        
        except AuthenticationError:
            # ❌ Invalid API key
            print("Error: Invalid API key. Check OPENAI_API_KEY")
            return None
        
        except RateLimitError:
            # ❌ Too many requests
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        
        except APIError as e:
            # ❌ Server error (500)
            print(f"API error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
        
        except Exception as e:
            # ❌ Unexpected error
            print(f"Unexpected error: {e}")
            return None
    
    print("Failed after retries")
    return None

# Test it
result = call_llm_with_retry("Hello, how are you?")
print(result)
```

---

## 6. Pydantic Models for LLM Responses

### 6.1 Structured Output Parsing

```python
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define expected response structure
class MovieReview(BaseModel):
    title: str
    rating: float  # 1-10
    summary: str
    recommendation: str  # "watch", "skip"

def get_movie_review(movie_name: str) -> MovieReview:
    """Get structured review from LLM"""
    
    prompt = f"""
    Review the movie "{movie_name}".
    Return JSON with:
    {{
        "title": "movie name",
        "rating": 8.5,
        "summary": "one sentence",
        "recommendation": "watch" or "skip"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response
    response_text = response.choices[0].message.content
    
    # Extract JSON from response
    import re
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group()
        data = json.loads(json_str)
        return MovieReview(**data)
    
    raise ValueError("Could not parse response")

# Test it
review = get_movie_review("Inception")
print(f"Title: {review.title}")
print(f"Rating: {review.rating}/10")
print(f"Recommendation: {review.recommendation}")
```

---

## 7. Using Claude (Anthropic Alternative)

### 7.1 Claude API Call

```python
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
```

---

## 8. FastAPI Endpoint for LLM

### 8.1 Simple LLM API Endpoint

```python
# llm_api.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    message: str
    tokens_used: int

# Store conversations (in production, use database)
conversations = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with LLM"""
    
    if not request.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    try:
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}]
        )
        
        return ChatResponse(
            message=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM error: {str(e)}"
        )

@app.get("/health")
async def health():
    return {"status": "ok"}

# Run: uvicorn llm_api:app --reload
```

**Test it**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AI?"}'
```

---

## 9. Cost Management & Best Practices

### 9.1 Cost Monitoring

```python
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track costs
total_tokens = 0
total_cost = 0

def log_api_call(tokens: int, model: str = "gpt-3.5-turbo"):
    """Log and track API usage"""
    global total_tokens, total_cost
    
    costs = {
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},  # per 1M tokens
        "gpt-4": {"input": 30, "output": 60}
    }
    
    cost = (tokens / 1_000_000) * costs[model]["input"]
    total_tokens += tokens
    total_cost += cost
    
    logger.info(f"Used {tokens} tokens (~${cost:.6f}). Total: ${total_cost:.6f}")

# Optimization tips
"""
1. Use cheaper models (gpt-3.5-turbo vs gpt-4)
2. Keep prompts concise
3. Use caching for repeated questions
4. Set max_tokens limit
5. Monitor usage in OpenAI dashboard
6. Use batch API for non-urgent requests
"""
```

### 9.2 Prompt Best Practices

```python
# ❌ Bad prompt (vague)
"Tell me about AI"

# ✅ Good prompt (specific)
"""
Explain machine learning in simple terms:
- Use 3 paragraphs max
- Target audience: high school students
- Include one real-world example
"""

# ❌ Bad prompt (expensive)
"Generate a full book about Python"

# ✅ Good prompt (efficient)
"Summarize Python best practices in 5 bullet points"
```

---

## 10. Common Pitfalls & Solutions

### 10.1 Issues You'll Face

| Issue | Cause | Solution |
|-------|-------|----------|
| `APIError 401` | Invalid API key | Check .env file, regenerate key |
| `RateLimitError` | Too many requests | Add retry logic with backoff |
| `Timeout` | Request too slow | Increase timeout, use GPT-3.5 |
| `Context too long` | Message history too big | Summarize old messages |
| `High costs` | Too many calls | Optimize prompts, use cheaper model |
| `Token limit exceeded` | Response too long | Set `max_tokens` parameter |

---

## 11. Practice Tasks

### Task 1: Basic Chatbot
```python
# Build a chatbot that remembers conversation history
# Requirements:
# - Multi-turn conversation
# - Error handling
# - Cost tracking
# - Type hints
```

### Task 2: Movie Review API
```python
# Build FastAPI endpoint that:
# - Takes movie name as input
# - Returns structured review (rating, summary)
# - Validates input
# - Handles errors
```

### Task 3: Cost Calculator
```python
# Create function that:
# - Estimates cost before making API call
# - Warns if > $1
# - Tracks total monthly spend
```

---

## 12. Testing Your Code

### 12.1 Unit Tests

```python
# test_llm.py
from unittest.mock import patch, MagicMock
import pytest

def test_chat_response():
    """Test LLM call"""
    with patch('openai.OpenAI.chat.completions.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello!"))],
            usage=MagicMock(total_tokens=10)
        )
        
        # Your test code here
        assert True

# Run: pytest test_llm.py
```

---

## 13. Next Steps

After Phase 1:
- ✅ Move to Phase 2: Embeddings & Vector Databases
- ✅ Learn RAG (Retrieval Augmented Generation)
- ✅ Build production-grade AI backend

---

## 14. Quick Reference

### OpenAI API Call Template
```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.7,  # 0 = deterministic, 1 = creative
    max_tokens=100    # Limit response length
)

print(response.choices[0].message.content)
```

### Error Handling Template
```python
try:
    response = client.chat.completions.create(...)
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Too many requests")
except Exception as e:
    print(f"Error: {e}")
```

---

## Troubleshooting

**Q: "ModuleNotFoundError: No module named 'openai'"**  
A: Run `pip install openai`

**Q: "APIError: 401 Unauthorized"**  
A: Check your API key in .env file

**Q: "Timeout error"**  
A: Add `timeout=60` to create() call

**Q: "Context length exceeded"**  
A: Summarize old messages or use GPT-4-turbo

---

**You're ready to start coding with LLMs! 🚀**

Complete all 4 tasks above before moving to Phase 2.
