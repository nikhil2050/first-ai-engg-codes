# Full Stack Agentic AI Engineering Roadmap
## From Python Basics to Production AI Systems (3–6 Months to Interview-Ready)

**Target Role:** AI Backend Engineer (e.g., Patsnap Singapore)  
**Focus:** Full Stack Agentic AI aligned with Durga Soft curriculum  
**Free Tier Deployment:** Vercel, Railway, Replit, Hugging Face Spaces, n8n Cloud Free  
**Start Date:** Immediate

---

## Executive Summary

You have 10+ years of backend engineering—your biggest asset. 

You need **Python production skills**, **LLM application architecture**, and **hands-on agentic AI projects** to land interviews at AI-native startups and enterprises.

This roadmap bypasses the Java-to-Python bridge entirely. It focuses on:
1. **Python fundamentals** you're missing (async, OOP, decorators)
2. **LLM application patterns** (RAG, prompt engineering, tool use)
3. **Agentic AI frameworks** (LangChain, LangGraph)
4. **Production safety** (guardrails, monitoring, evaluation)
5. **5 portfolio projects** deployable to free tiers

**Timeline:** 3 months for "interview-ready" (basic competence), 6 months for "strong hire" (depth + polish).

---

## Phase 0: Python Bootcamp (Weeks 1–2)
**Goal:** Stop Python basics; begin writing production Python.

### What You're Missing
- Async/await + concurrent.futures
- OOP (classes, inheritance, `__init__`, `self`)
- Decorators + context managers
- List/dict comprehensions
- Memory profiling (find leaks)

### Free Resources

| Topic | Resource | Duration | Hands-On |
|-------|----------|----------|----------|
| **OOP fundamentals** | [Real Python – Classes & Objects](https://realpython.com/python3-object-oriented-programming/) | 2 hrs | Code 3 classes from scratch |
| **Async Python** | [Real Python – Async IO](https://realpython.com/async-io-python/) + [David Beazley talk](https://www.youtube.com/watch?v=MCs5OvIHa9I) | 3 hrs | Write async scraper (fetch 10 URLs concurrently) |
| **Decorators** | [Real Python – Decorators](https://realpython.com/primer-on-python-decorators/) | 1.5 hrs | Build `@retry`, `@cache`, `@log_time` decorators |
| **Comprehensions** | [Real Python – List Comprehensions - New](https://realpython.com/list-comprehension-python/)<br/>~~[Real Python – List Comprehensions](https://realpython.com/list-comprehensions-and-generator-expressions/)~~ | 1 hr | Refactor loops → comprehensions |
| **Memory debugging** | [PySpy + Memory Profiler](https://docs.python.org/3/library/profile.html) | 2 hrs | Profile a slow script, find bottleneck |

### Week 1 Tasks
- [ ] Rewrite 1 old script using async (fetch data from 5+ URLs, measure speedup)
- [ ] Write 3 reusable decorators (`@retry`, `@cache`, `@validate_input`)
- [ ] Convert 20 loops → comprehensions
- [ ] Create a class-based config system (inherit, override, use `__init__`)

### Week 2 Tasks
- [ ] Build a concurrent API client (async requests to 3+ endpoints)
- [ ] Profile it with memory_profiler; fix one leak
- [ ] Write unit tests using `unittest` or `pytest`
- [ ] Deploy to Replit (free Python hosting)

**GitHub Checkpoint:** Commit a `/fundamentals/` folder with OOP + async examples.

---

## Phase 1: LLM Foundations (Weeks 3–5)
**Goal:** Understand LLMs, embeddings, and why RAG works.

### Conceptual Foundations (no coding yet)

| Concept | Video | Duration | Notes |
|---------|-------|----------|-------|
| **Transformers** | [3Blue1Brown – Attention](https://www.youtube.com/watch?v=oapKHEGK7qk) | 30 min | Why attention matters |
| **Token & context window** | [Andrej Karpathy – Let's build GPT](https://www.youtube.com/watch?v=kCc8Fmoe10s) (first 45 min) | 45 min | How tokens work, why context matters |
| **Embeddings** | [Real Python – Embeddings](https://realpython.com/what-are-embeddings/) | 30 min | Vector similarity, semantic search |
| **RAG vs Fine-tuning** | [LLamaIndex blog – RAG advantages](https://blog.llamaindex.com/retrieval-augmented-generation/) | 20 min | Why RAG is production-grade |
| **Prompt engineering** | [OpenAI – Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) | 30 min | Few-shot, CoT, role-play |
| **Hallucinations & grounding** | [Anthropic – Factuality](https://www.anthropic.com/research/fact-checking) | 15 min | Why evidence matters |

### Hands-On: Week 3

**Project 1: First LLM Call**
```python
# pip install anthropic
from anthropic import Anthropic

client = Anthropic()

# Single message
msg = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain embeddings in 1 sentence."}
    ]
)
print(msg.content[0].text)

# Multi-turn conversation
conversation_history = []
for user_input in ["What are embeddings?", "Why use them for RAG?"]:
    conversation_history.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    assistant_msg = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_msg})
    print(f"Q: {user_input}\nA: {assistant_msg}\n")
```

**Deliverable:** Save to `/projects/01_first_llm_call/main.py`

### Hands-On: Week 4–5

**Project 2: Simple RAG (Vector DB + Retrieval)**

```python
# pip install anthropic faiss-cpu
import faiss
import json
from anthropic import Anthropic

# 1. Create fake documents + embeddings
documents = [
    "Machine learning requires large datasets to train models.",
    "Embeddings convert text to high-dimensional vectors.",
    "RAG retrieves relevant documents before generation.",
    "LLMs can hallucinate when they lack grounding."
]

# Mock embeddings (in reality, use sentence-transformers or OpenAI embeddings)
# For now, use deterministic numbers
import numpy as np
embeddings = np.random.rand(len(documents), 384).astype('float32')

# 2. Index with FAISS
index = faiss.IndexFlatL2(384)
index.add(embeddings)

# 3. Query function
def retrieve(query_text, k=2):
    # Mock query embedding
    query_embedding = np.random.rand(1, 384).astype('float32')
    distances, indices = index.search(query_embedding, k)
    return [documents[i] for i in indices[0]]

# 4. RAG pipeline
client = Anthropic()

def rag_query(user_query):
    # Retrieve
    context = retrieve(user_query, k=2)
    
    # Augment
    system_prompt = f"""You are a helpful assistant. Answer based on this context:
{chr(10).join(context)}

If context doesn't help, say "I don't have relevant information."""
    
    # Generate
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_query}
        ]
    )
    return response.content[0].text, context

# Test
answer, sources = rag_query("What are embeddings used for?")
print(f"Answer: {answer}\nSources: {sources}")
```

**Deliverable:** `/projects/02_simple_rag/main.py` + `requirements.txt`

### Week 5 Checkpoint
- [ ] Run both projects locally
- [ ] Deploy Project 2 to Replit (free tier)
- [ ] Commit to GitHub with README explaining RAG flow

---

## Phase 2: Production Python + Frameworks (Weeks 6–9)
**Goal:** Write REST APIs, learn LangChain basics, handle errors in production.

### Module 2a: REST APIs with FastAPI

**Install:** `pip install fastapi uvicorn python-dotenv`

**Quick Start:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
import os

app = FastAPI()
client = Anthropic()

class QueryRequest(BaseModel):
    question: str
    context: str = None

@app.post("/ask")
def ask_question(req: QueryRequest):
    """Simple RAG endpoint."""
    try:
        system = f"Context: {req.context}" if req.context else "You are helpful."
        resp = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": req.question}]
        )
        return {"answer": resp.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Deploy to Railway (free tier):** Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Module 2b: LangChain Intro

**Install:** `pip install langchain anthropic langchain-community`

```python
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Simple chain
prompt = ChatPromptTemplate.from_template("Explain {topic} in 1 sentence.")
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.run(topic="embeddings")
print(result)

# Multi-step chain
template = """Given this context: {context}
Question: {question}
Answer:"""

prompt = ChatPromptTemplate.from_template(template)
chain = LLMChain(llm=llm, prompt=prompt)

answer = chain.run(
    context="Embeddings are vectors representing text.",
    question="What are embeddings?"
)
print(answer)
```

### Module 2c: Error Handling & Observability

**Retry logic:**
```python
import time
from anthropic import RateLimitError

def call_llm_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("Failed after retries")
```

**Basic logging:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Calling LLM with prompt: {prompt}")
logger.error(f"API error: {e}", exc_info=True)
```

### Weeks 6–9 Projects

**Project 3: LangChain-Based Q&A API**

```python
# main.py
from fastapi import FastAPI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

class DocumentQA(BaseModel):
    document: str
    question: str

@app.post("/qa")
def answer_question(req: DocumentQA):
    """Answer questions about a document."""
    logger.info(f"Processing question: {req.question}")
    
    prompt = ChatPromptTemplate.from_template(
        "Document: {doc}\n\nQuestion: {q}\n\nAnswer:"
    )
    
    try:
        chain = prompt | llm
        result = chain.invoke({"doc": req.document, "q": req.question})
        return {"answer": result.content}
    except Exception as e:
        logger.error(f"Error in QA: {e}", exc_info=True)
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Deploy:**
1. Create GitHub repo
2. Add `requirements.txt`:
   ```
   fastapi==0.104.1
   uvicorn==0.24.0
   langchain==0.0.352
   langchain-anthropic==0.1.0
   python-dotenv==1.0.0
   ```
3. Deploy to Railway or Vercel Functions

**Deliverable:** GitHub + live API endpoint

---

## Phase 3: Agentic AI Essentials (Weeks 10–12)
**Goal:** Master LangGraph, tool use, and autonomous workflows.

### Module 3a: Tool Use & Function Calling

**Concept:** LLMs call functions you define; the LLM decides *when* and *with what params*.

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string", "enum": ["C", "F"]}
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform arithmetic",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression like '2+2'"}
            },
            "required": ["expression"]
        }
    }
]

# Tool implementations
def get_weather(city, unit="C"):
    # Mock weather service
    return {"city": city, "temp": 22, "unit": unit, "condition": "Clear"}

def calculate(expression):
    try:
        return {"result": eval(expression)}
    except:
        return {"error": "Invalid expression"}

tool_map = {
    "get_weather": get_weather,
    "calculate": calculate
}

# Agentic loop
def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        # Check if LLM wants to use a tool
        if response.stop_reason == "tool_use":
            # Find tool use blocks
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    print(f"LLM calling {tool_name} with {tool_input}")
                    
                    # Execute tool
                    result = tool_map[tool_name](**tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            
            # Add assistant response + tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        
        else:
            # LLM stopped (end_turn), extract final answer
            final_answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_answer += block.text
            return final_answer

# Test
answer = run_agent("What's the weather in London and calculate 15 * 3?")
print(f"Final answer: {answer}")
```

**Key insight:** The LLM orchestrates; you provide tools. This is the foundation of agentic AI.

### Module 3b: LangGraph (State Management)

**Install:** `pip install langgraph langchain-core`

LangGraph is for multi-step workflows with explicit state.

```python
from langgraph.graph import StateGraph
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, Annotated
import operator

# 1. Define state
class AgentState(TypedDict):
    messages: list
    context: str

# 2. Define nodes (steps in workflow)
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

def retrieval_node(state: AgentState):
    """Simulated retrieval."""
    # In reality, query vector DB
    relevant_docs = ["Embeddings are vectors.", "RAG uses retrieval."]
    return {
        "context": " ".join(relevant_docs),
        "messages": state["messages"]
    }

def generation_node(state: AgentState):
    """Generate answer from context."""
    prompt = f"Context: {state['context']}\n\nAnswer the user's question."
    response = llm.invoke(prompt)
    messages = state["messages"] + [{"role": "assistant", "content": response.content}]
    return {
        "messages": messages,
        "context": state["context"]
    }

# 3. Build graph
graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieval_node)
graph.add_node("generate", generation_node)

graph.add_edge("retrieve", "generate")
graph.set_entry_point("retrieve")
graph.set_finish_point("generate")

# 4. Compile and run
runnable = graph.compile()

result = runnable.invoke({
    "messages": [{"role": "user", "content": "What are embeddings?"}],
    "context": ""
})

print(result["messages"][-1])
```

### Weeks 10–12 Projects

**Project 4: Multi-Agent System (LangGraph + Tool Use)**

Architecture:
- **Supervisor node:** Routes queries to specialists
- **Researcher node:** Uses tools to fetch data
- **Writer node:** Generates summaries
- **Human approval gate:** Pauses for review

```python
# agent_system.py
from langgraph.graph import StateGraph
from langchain_anthropic import ChatAnthropic
from typing import TypedDict
import json

class WorkflowState(TypedDict):
    query: str
    research_results: str
    draft: str
    approved: bool

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Mock tools
def search_web(topic):
    return f"[Web search results for '{topic}': Found 5 relevant articles.]"

def summarize(text):
    return f"Summary of {len(text)} chars: [condensed version]"

# Nodes
def supervisor_node(state):
    """Route query to appropriate specialist."""
    prompt = f"Route this query to research or writing: {state['query']}"
    decision = llm.invoke(prompt)
    return {"query": state["query"]}

def research_node(state):
    """Research phase with tool use."""
    results = search_web(state["query"])
    return {
        "query": state["query"],
        "research_results": results
    }

def writing_node(state):
    """Generate output."""
    draft = f"Based on research: {state['research_results']}\n\nDraft summary..."
    return {
        "query": state["query"],
        "research_results": state["research_results"],
        "draft": draft,
        "approved": False
    }

def approval_node(state):
    """Human approval gate."""
    print(f"Review draft: {state['draft']}")
    approved = input("Approve? (y/n): ").lower() == "y"
    return {
        "query": state["query"],
        "research_results": state["research_results"],
        "draft": state["draft"],
        "approved": approved
    }

# Build graph
graph = StateGraph(WorkflowState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("research", research_node)
graph.add_node("writing", writing_node)
graph.add_node("approval", approval_node)

graph.set_entry_point("supervisor")
graph.add_edge("supervisor", "research")
graph.add_edge("research", "writing")
graph.add_edge("writing", "approval")
graph.set_finish_point("approval")

runnable = graph.compile()

result = runnable.invoke({
    "query": "Explain agentic AI",
    "research_results": "",
    "draft": "",
    "approved": False
})

print("Workflow complete:", result)
```

**Deliverable:** GitHub + live LangGraph workflow demo

---

## Phase 4: Production RAG & Enterprise Patterns (Weeks 13–16)
**Goal:** Build Patsnap-level RAG with citations, guardrails, and evaluation.

### Module 4a: Agentic RAG (Evidence-First)

**Problem:** Basic RAG hallucinates. Fix it:
1. Always retrieve first
2. Cite sources
3. Validate answers against evidence

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

# 1. Setup vector DB
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
docs = [
    Document(page_content="RAG is retrieval-augmented generation.", metadata={"source": "doc1"}),
    Document(page_content="Embeddings map text to vectors.", metadata={"source": "doc2"}),
]
vectorstore = Chroma.from_documents(docs, embeddings)

# 2. Retriever + LLM
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# 3. RAG prompt with citations
prompt = ChatPromptTemplate.from_template("""
You MUST answer ONLY using the provided documents. 
For each claim, cite the source like [source: doc1].

Documents:
{context}

Question: {question}

Answer (with citations):""")

# 4. Agentic RAG chain
from langchain.schema.runnable import RunnablePassthrough

rag_chain = (
    {"context": retriever | (lambda docs: "\n".join([d.page_content for d in docs])),
     "question": RunnablePassthrough()}
    | prompt
    | llm
)

# 5. Run
answer = rag_chain.invoke("What are embeddings?")
print(answer.content)
# Expected: "Embeddings map text to vectors [source: doc2]. RAG uses these..."
```

### Module 4b: Guardrails & Safety

**Problem:** LLM might execute malicious tool calls. Fix it:

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Allowlist of safe tools
SAFE_TOOLS = {
    "search_docs": {"input_schema": {"type": "string"}},
    "get_current_date": {},
}

BLOCKED_TOOLS = {"delete_database", "send_email", "execute_code"}

def validate_tool_call(tool_name, tool_input):
    """Ensure tool is safe."""
    if tool_name in BLOCKED_TOOLS:
        return False, f"Tool '{tool_name}' is not allowed."
    if tool_name not in SAFE_TOOLS:
        return False, f"Unknown tool '{tool_name}'."
    return True, None

def safe_agent_loop(user_query):
    messages = [{"role": "user", "content": user_query}]
    
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=[...],  # Define tools
            messages=messages
        )
        
        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    # VALIDATE before executing
                    safe, error = validate_tool_call(block.name, block.input)
                    if not safe:
                        print(f"BLOCKED: {error}")
                        # Inform LLM it can't use this tool
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user",
                            "content": [{"type": "tool_result", "tool_use_id": block.id,
                                       "content": f"Error: {error}"}]
                        })
                        break
                    
                    # SAFE: execute
                    result = execute_tool(block.name, block.input)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": [
                        {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
                    ]})
        else:
            return response.content[0].text
```

### Module 4c: Evaluation & Monitoring

**Track what matters:**
- Retrieval quality (are we fetching relevant docs?)
- Generation quality (is the answer correct?)
- Hallucination rate (does it make things up?)

```python
def evaluate_rag(query, generated_answer, retrieved_docs, reference_answer):
    """Simple evaluation metrics."""
    
    # 1. Groundedness: is answer supported by docs?
    prompt = f"""Rate if this answer is grounded in the docs (0-10):
    Answer: {generated_answer}
    Docs: {retrieved_docs}"""
    
    grounding = llm.invoke(prompt)
    
    # 2. Citation coverage: does it cite sources?
    citation_count = generated_answer.count("[source:")
    citation_rate = citation_count / max(1, len(retrieved_docs))
    
    # 3. Semantic similarity to reference
    from sklearn.metrics.pairwise import cosine_similarity
    embeddings_obj = HuggingFaceEmbeddings()
    sim = cosine_similarity(
        embeddings_obj.embed_query(generated_answer).reshape(1, -1),
        embeddings_obj.embed_query(reference_answer).reshape(1, -1)
    )[0][0]
    
    return {
        "groundedness": grounding,
        "citation_rate": citation_rate,
        "semantic_similarity": sim
    }

# Log metrics
metrics = evaluate_rag(
    query="What is RAG?",
    generated_answer="RAG is retrieval-augmented generation [source: doc1].",
    retrieved_docs=["RAG is retrieval-augmented generation."],
    reference_answer="RAG retrieves documents before generation."
)
print(metrics)
```

### Weeks 13–16 Projects

**Project 5: Enterprise Knowledge Base (GraphRAG + Neo4j)**

Architecture:
1. **Ingest documents** → extract entities (Person, Company, Concept)
2. **Build knowledge graph** → relationships (Person works at Company)
3. **Hybrid retrieval** → vector search + graph traversal
4. **Explainable answers** → show reasoning path through graph

```python
# knowledge_graph_rag.py
from langchain_community.graphs import Neo4jGraph
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.chains import GraphCypherQAChain

# Connect to Neo4j (use free Aura sandbox)
graph = Neo4jGraph(
    url="neo4j+s://your-sandbox.neo4j.io",
    username="neo4j",
    password="your-password"
)

# Create schema
graph.query("""
CREATE CONSTRAINT unique_person IF NOT EXISTS ON (p:Person) ASSERT p.name IS UNIQUE;
CREATE CONSTRAINT unique_company IF NOT EXISTS ON (c:Company) ASSERT c.name IS UNIQUE;
""")

# Ingest sample data
graph.query("""
CREATE (p:Person {name: "Alice", role: "AI Engineer"})
CREATE (c:Company {name: "Patsnap", industry: "AI"})
CREATE (p)-[:WORKS_AT]->(c)
""")

# Cypher QA chain
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
chain = GraphCypherQAChain.from_llm(llm, graph=graph, verbose=True)

# Query with reasoning
answer = chain.run("Who works at Patsnap and what's their role?")
print(answer)

# Expected: Traverses graph → returns path → generates explanation
```

**Deliverable:** Graph visualization + live API

---

## Phase 5: Deployment & Interview Prep (Weeks 17–20)
**Goal:** Polish portfolio, practice interviews, deploy everything.

### Module 5a: Observability (Langfuse)

Track every LLM call:

```python
from langfuse.decorators import observe

@observe()
def my_rag_function(query: str) -> str:
    # This call is automatically logged to Langfuse
    docs = retrieve(query)
    answer = generate(docs, query)
    return answer

# View traces at dashboard.langfuse.com
```

### Module 5b: Portfolio Polish

| Project | Status | Demo Link | GitHub |
|---------|--------|-----------|--------|
| Project 1: First LLM | ✅ | Replit | repo/01 |
| Project 2: Simple RAG | ✅ | Hugging Face Spaces | repo/02 |
| Project 3: Q&A API | ✅ | Railway | repo/03 |
| Project 4: Multi-Agent | 🚀 | Docker on Render | repo/04 |
| Project 5: GraphRAG | 🚀 | Neo4j + Flask | repo/05 |

### Module 5c: Interview Preparation

**Typical questions at AI startups:**

1. **"Walk me through your RAG system. How do you prevent hallucinations?"**
   - Answer: Retrieval-first, evidence citations, guardrails, evaluation metrics
   - Demo: Show project 5, explain grounding score

2. **"You need to build an agent that can query a database safely. How?"**
   - Answer: Tool allowlisting, input validation, SQL injection checks, approval gates
   - Code: Show safe_agent_loop from Module 4b

3. **"What's your biggest challenge with LLM apps in production?"**
   - Answer: Latency vs. quality trade-off; token optimization; hallucination rates
   - Reference: Your monitoring setup (Langfuse)

4. **"Design a knowledge infrastructure for 1M+ documents."**
   - Answer: Chunking strategy, embedding model selection, vector DB (Pinecone/Weaviate), BM25 hybrid search, caching
   - Sketch: Architecture diagram

**Mock interview checklist:**
- [ ] 1 system design question (60 min)
- [ ] 1 coding question (60 min, build a tool-use agent from scratch)
- [ ] 1 domain question (30 min, your portfolio project deep dive)

---

## Free Tier Deployment Guides

### Project 1–2: Replit
- Sign up: replit.com
- Import GitHub repo → Run
- Live URL auto-generated
- Limits: One-click deployment, 0.5 CPU

### Project 3: Railway
- Sign up: railway.app
- Connect GitHub
- Deploy via Procfile or Dockerfile
- First 100 hours/month free

### Project 4: Render
- Sign up: render.com
- Deploy FastAPI + Docker
- Free tier: 15-min idle shutdown

### Project 5: Neo4j Aura
- Free sandbox: aura.neo4j.io
- 3-day expiry (renewable)
- For production: Vercel + Railway backend

### LLM API Costs
- **Claude API:** $0.003 per 1K input tokens, $0.015 per 1K output tokens
  - Estimate: $1–5/month for prototyping, $50–200/month for production
  - Apply for free credits: https://console.anthropic.com/account/billing/overview
- **HuggingFace:** Free embeddings (self-hosted model)
- **Pinecone/Weaviate:** Free tier (1M vectors)

---

## Week-by-Week Timeline

| Week | Phase | Focus | Deliverable |
|------|-------|-------|-------------|
| 1–2 | Python bootcamp | OOP, async, decorators | `/fundamentals/` commit |
| 3–5 | LLM foundations | Embeddings, RAG concept, first calls | Project 2: Simple RAG on Replit |
| 6–9 | Production Python | FastAPI, LangChain, error handling | Project 3: Q&A API on Railway |
| 10–12 | Agentic AI | Tool use, LangGraph, multi-step workflows | Project 4: Multi-Agent System |
| 13–16 | Enterprise RAG | Guardrails, evaluation, knowledge graphs | Project 5: GraphRAG + Neo4j |
| 17–20 | Polish & interviews | Observability, portfolio cleanup, mock interviews | Interview-ready |

---

## Resources Summary

### YouTube Channels (Free)
- **Durga Soft:** Full Stack Agentic AI (see course syllabus)
- **3Blue1Brown:** Transformers & attention
- **Andrej Karpathy:** Building GPT
- **Jeremy Howard / Fast.ai:** Deep learning (optional depth)

### Documentation
- **Anthropic:** https://docs.anthropic.com (Claude API)
- **LangChain:** https://python.langchain.com
- **LangGraph:** https://langchain-ai.github.io/langgraph
- **FastAPI:** https://fastapi.tiangolo.com
- **Pydantic:** https://docs.pydantic.dev (data validation)

### Blogs & Papers
- **LlamaIndex blog:** RAG best practices
- **Anthropic research:** Factuality, constitutional AI
- **LangChain blog:** Production patterns
- **Papers:** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)

### Communities
- **LangChain Discord:** https://discord.gg/6adMQxSpJS
- **LlamaIndex Discord:** https://discord.gg/dXtQ81gezh
- **Anthropic forum:** https://github.com/anthropics/anthropic-sdk-python/discussions

---

## Success Metrics

You're interview-ready when:

✅ **Technical depth:**
- Write async Python without help
- Build a complete RAG system from scratch
- Explain tool use vs. function calling
- Design a multi-agent system on whiteboard

✅ **Portfolio:**
- 5 projects deployed to live URLs
- Each project has GitHub + README + architecture diagram
- At least 1 project uses LangGraph, 1 uses Neo4j

✅ **Interview performance:**
- Mock system design: score 7/10+
- Coding challenge: tool-use agent from scratch in 45 min
- Domain deep-dive: articulate trade-offs (latency vs. quality, hallucination handling)

---

## If You Get Stuck

**Python async too confusing?**
- Pair it with a real use case (fetch 10 URLs concurrently)
- Use `asyncio.run()` to test locally
- Reference: https://realpython.com/async-io-python/

**RAG evaluations unclear?**
- Start with simple metrics (citation rate, grounding score)
- Build evaluation dashboard (plot metrics over time)
- Reference: Durga Soft Module 10 (Langfuse)

**LangGraph too abstract?**
- Draw state transitions on whiteboard first
- Code one node at a time
- Reference: https://langchain-ai.github.io/langgraph/tutorials/

**Free tier limits hitting you?**
- Replit → Railway → Render (escalating resources)
- Use `.env` files to manage API keys securely
- Monitor token usage weekly (Langfuse dashboards)

---

## Next Steps (Starting Tomorrow)

1. **Week 1:** Clone this roadmap, set up GitHub repo structure
2. **Day 1:** Commit to Weeks 1–2 async/OOP deep dive
3. **Day 3:** First LLM call to Claude (Project 1)
4. **Day 7:** Deploy to Replit
5. **Weekly:** Commit progress to GitHub; track metrics

**Month 3:** Interview calls start  
**Month 6:** Strong hire for AI Backend roles (Patsnap, equivalent)

---

## Appendix: Quick Command Reference

**Python setup:**
```bash
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Deploy to Replit:**
```bash
# From GitHub: Click "Import" → Paste repo URL → Run
```

**Deploy to Railway:**
```bash
# Create Procfile:
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# Push to GitHub, Railway auto-deploys
```

**Test locally:**
```bash
# FastAPI
uvicorn main:app --reload

# LangGraph
python graph.py

# LLM call
python -m pytest tests/test_llm.py -v
```

**Monitor costs:**
```bash
# Check Claude usage at: https://console.anthropic.com/account/usage
# Langfuse dashboard: https://dashboard.langfuse.com
```

---

**Version:** 1.0  
**Last updated:** July 2026  
**Feedback:** GitHub Issues
