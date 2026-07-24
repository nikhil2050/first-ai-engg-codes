# Quick Start Guide: AI Engineering Roadmap
## 30-Day Action Plan (Get Started Now!)

---

## Week 1: Python Fundamentals Foundation

### Day 1: Setup (2 hours)
- [ ] Create GitHub repo: `nikhil-ai-engineering`
- [ ] Create Python venv: `python3 -m venv venv && source venv/bin/activate`
- [ ] Install basics: `pip install anthropic langchain fastapi uvicorn pytest`
- [ ] Set up `.env` file with ANTHROPIC_API_KEY

### Days 2–3: OOP Bootcamp (4 hours)
**Goal:** Write 3 classes from scratch

```python
# example.py
class APIClient:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def call(self, prompt):
        # Implementation
        pass

class Retriever:
    def __init__(self, documents):
        self.docs = documents
    
    def search(self, query):
        return [d for d in self.docs if query in d]

class RAGPipeline(APIClient, Retriever):
    def __init__(self, api_key, documents):
        APIClient.__init__(self, api_key)
        Retriever.__init__(self, documents)
    
    def generate(self, query):
        docs = self.search(query)
        return self.call(f"Context: {docs}\nQ: {query}")
```

**Commit:** `/week1/classes.py`

### Days 4–5: Async Python (3 hours)
**Goal:** Fetch 10 URLs concurrently, measure speedup

```python
# async_example.py
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Run
urls = ["https://api.github.com/users/github", ...] * 10
results = asyncio.run(fetch_all(urls))
print(f"Fetched {len(results)} URLs in parallel")
```

**Commit:** `/week1/async_fetch.py`

### Days 6–7: Decorators (2 hours)
**Goal:** Write 3 reusable decorators

```python
# decorators.py
import functools
import time

def retry(max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)
        return wrapper
    return decorator

def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

def cache(func):
    cache_dict = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args in cache_dict:
            return cache_dict[args]
        result = func(*args)
        cache_dict[args] = result
        return result
    return wrapper

# Usage
@retry(max_attempts=3)
@log_time
def call_api(prompt):
    # Simulated API call
    return f"Response to {prompt}"

@cache
def expensive_computation(n):
    time.sleep(1)
    return n * n
```

**Commit:** `/week1/decorators.py`

**Week 1 Checkpoint:**
- [ ] All 3 files committed to GitHub
- [ ] Verify venv + imports work
- [ ] Push to GitHub with message "Week 1: Python fundamentals"

---

## Week 2: First LLM Integration

### Day 1: Make Your First API Call (1 hour)
**Goal:** Call Claude API successfully

```python
# projects/01_first_call/main.py
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain embeddings in 1 sentence."}
    ]
)

print(response.content[0].text)
```

**Run:** `python main.py`  
**Commit:** `/projects/01_first_call/`

### Days 2–3: Multi-Turn Conversation (2 hours)

```python
# projects/01_first_call/conversation.py
from anthropic import Anthropic

client = Anthropic()
conversation = []

def chat(user_message):
    conversation.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation
    )
    assistant_message = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_message})
    return assistant_message

# Test
print(chat("What are embeddings?"))
print(chat("Why use them for search?"))
print(chat("Can they replace keyword search?"))
```

**Commit:** Add to `/projects/01_first_call/`

### Days 4–7: Simple RAG (4 hours)

```python
# projects/02_simple_rag/main.py
from anthropic import Anthropic
import json

client = Anthropic()

# Mock document database
DOCUMENTS = [
    "Embeddings convert text to high-dimensional vectors.",
    "RAG retrieves relevant documents before generation.",
    "LLMs can hallucinate without grounding.",
    "Prompt engineering improves model outputs."
]

def simple_retrieval(query, top_k=2):
    """Simple keyword-based retrieval."""
    scores = []
    for doc in DOCUMENTS:
        score = sum(1 for word in query.split() if word in doc.lower())
        scores.append((doc, score))
    return [doc for doc, _ in sorted(scores, key=lambda x: -x[1])[:top_k]]

def rag_pipeline(user_query):
    # Step 1: Retrieve
    relevant_docs = simple_retrieval(user_query)
    context = "\n".join(relevant_docs)
    
    # Step 2: Generate
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=f"Use this context to answer: {context}",
        messages=[{"role": "user", "content": user_query}]
    )
    
    return {
        "query": user_query,
        "context": relevant_docs,
        "answer": response.content[0].text
    }

# Test
result = rag_pipeline("What are embeddings used for?")
print(f"Q: {result['query']}")
print(f"Context: {result['context']}")
print(f"A: {result['answer']}")
```

**Deploy to Replit:**
1. Push to GitHub
2. Go to replit.com → Import from GitHub
3. Click "Run"
4. Share public link

**Commit:** `/projects/02_simple_rag/` + live Replit link in README

---

## Week 3: Production Readiness

### Days 1–3: FastAPI REST Endpoint (3 hours)

```python
# projects/03_rag_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
client = Anthropic()

class QueryRequest(BaseModel):
    question: str
    context: str = ""

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(request: QueryRequest):
    logger.info(f"Query: {request.question}")
    try:
        system_prompt = f"Context: {request.context}" if request.context else "You are helpful."
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": request.question}]
        )
        return {"answer": response.content[0].text}
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Test locally:**

```bash
pip install fastapi uvicorn anthropic
python main.py

# In another terminal:
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "context": "AI is artificial intelligence"}'
```

**Create requirements.txt:**

```
fastapi==0.104.1
uvicorn==0.24.0
anthropic==0.21.0
python-dotenv==1.0.0
```

**Deploy to Railway:**
1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
2. Push to GitHub
3. Connect GitHub to Railway.app
4. Railway auto-deploys

**Commit:** `/projects/03_rag_api/` + live API link

### Days 4–7: Testing & Monitoring (2 hours)

```python
# projects/03_rag_api/test_main.py
import pytest
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ask():
    response = client.post("/ask", json={
        "question": "What is 2+2?",
        "context": "Simple math"
    })
    assert response.status_code == 200
    assert "answer" in response.json()
    assert len(response.json()["answer"]) > 0

def test_error_handling():
    response = client.post("/ask", json={
        "question": "",
        "context": ""
    })
    assert response.status_code in [200, 400]
```

**Run tests:**

```bash
pip install pytest
pytest test_main.py -v
```

---

## Immediate Next Steps (This Week)

### Priority 1: Set Up Environment (Today - 2 hours)

```bash
# Create project
mkdir ai-learning && cd ai-learning
git init
python3 -m venv venv
source venv/bin/activate
pip install anthropic langchain fastapi uvicorn pytest

# Create .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# First commit
git add . && git commit -m "Initial setup"
git push -u origin main
```

### Priority 2: Run Week 1 Tasks (Days 1–7)
- [ ] OOP + async + decorators
- [ ] Commit all 3 Python files
- [ ] Verify imports work

### Priority 3: First LLM Call (Week 2 Day 1)
- [ ] Make API call to Claude
- [ ] Deploy to Replit
- [ ] Get live URL

### Priority 4: REST API (Week 3)
- [ ] Build FastAPI endpoint
- [ ] Deploy to Railway
- [ ] Test with curl

---

## GitHub Structure (Copy This)

```
nikhil-ai-engineering/
├── README.md (links to all projects + progress)
├── .gitignore
├── .env (ANTHROPIC_API_KEY)
├── requirements.txt (shared dependencies)
│
├── week1-python-fundamentals/
│   ├── classes.py
│   ├── async_fetch.py
│   ├── decorators.py
│   └── test_*.py
│
├── projects/
│   ├── 01-first-llm-call/
│   │   ├── main.py
│   │   ├── conversation.py
│   │   ├── requirements.txt
│   │   └── README.md (Live: replit link)
│   │
│   ├── 02-simple-rag/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── README.md (Live: replit link)
│   │
│   └── 03-rag-api/
│       ├── main.py
│       ├── test_main.py
│       ├── Procfile
│       ├── requirements.txt
│       └── README.md (Live: railway.app link)
│
└── notes/
    ├── week1-takeaways.md
    ├── week2-learnings.md
    └── interview-prep.md
```

---

## Daily Commit Checklist

**Every day, commit your progress:**

```bash
git add .
git commit -m "Day X: [Task completed]"
git push
```

**Example messages:**
- Day 1: "Setup venv + installed dependencies"
- Day 3: "OOP bootcamp: APIClient, Retriever, RAGPipeline classes"
- Day 5: "Async Python: concurrent URL fetcher"
- Day 8: "First LLM call working"
- Day 14: "RAG API deployed to Railway"

---

## Success Metrics (First Month)

✅ **Week 1:**
- [ ] Python venv setup
- [ ] 3 OOP classes written
- [ ] Async function fetching URLs
- [ ] 3 decorators working

✅ **Week 2:**
- [ ] First Claude API call
- [ ] Multi-turn conversation
- [ ] Simple RAG on Replit

✅ **Week 3:**
- [ ] FastAPI REST endpoint
- [ ] Deployed to Railway
- [ ] Tests passing

✅ **Week 4:**
- [ ] 3 projects live with URLs
- [ ] README + architecture diagrams
- [ ] 20+ GitHub commits

---

## Resources (Bookmarks for This Week)

- **Anthropic Docs:** https://docs.anthropic.com
- **Real Python - OOP:** https://realpython.com/python3-object-oriented-programming/
- **Real Python - Async:** https://realpython.com/async-io-python/
- **FastAPI Tutorial:** https://fastapi.tiangolo.com/tutorial/
- **Railway Deploy Guide:** https://docs.railway.app/getting-started
- **Replit Deploy:** https://replit.com/
- **LangChain Docs:** https://python.langchain.com

---

## If You Get Stuck

**"venv not activating?"**

```bash
# Try Windows:
venv\Scripts\activate

# Or create fresh:
python3 -m venv venv2 && source venv2/bin/activate
```

**"API key not working?"**
- Check: `cat .env` (key is there?)
- Check: `echo $ANTHROPIC_API_KEY` (is it exported?)
- Verify at: https://console.anthropic.com/account/api-keys

**"Deploy failing?"**
- Check: `requirements.txt` has all imports
- Check: `Procfile` is in repo root
- Check: Railway logs (dashboard → deployments)

**"Rate limited?"**
- Add exponential backoff (see decorators.py)
- Check: https://console.anthropic.com/account/usage
- Free tier is generous; apply for credits if needed

---

## Next Phase (After Day 30)

Once you've completed the first month:
1. Move to **Phase 2: LLM Foundations** (Weeks 5–8 in full roadmap)
2. Add LangChain integrations
3. Build multi-step RAG pipeline
4. Start portfolio project #4 (LangGraph agent)

---

## Final Checklist (Show This to Interviewers)

By the end of Month 1, you can say:

✅ "I can write async Python and production-ready OOP code"  
✅ "I've integrated Claude API and built a functioning RAG system"  
✅ "I've deployed real APIs to production (Railway, Replit)"  
✅ "I understand retrieval, generation, and prompt engineering"  
✅ "I write tests and monitor production errors"  

**GitHub to show:** nikhil-ai-engineering (public repo, 3 live projects)

---

## Start Today. Don't Wait.

Day 1 tasks:
1. Create GitHub repo
2. Set up venv
3. Make first API call
4. Commit everything

**You've got this! 🚀**
