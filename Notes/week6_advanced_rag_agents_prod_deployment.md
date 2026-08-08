# Phase 3: Advanced RAG, Agents & Production Deployment
## AI Backend Engineering Roadmap

---

## Overview: What You'll Build in Phase 3

- ✅ Advanced RAG: Hybrid search (keyword + semantic)
- ✅ Re-ranking: Better relevance scoring
- ✅ Agents: AI systems that take actions
- ✅ Function calling: Tools for agents
- ✅ Production deployment: Docker, monitoring, scaling
- ✅ Error handling & guardrails

**Time**: 6-7 hours  
**Prerequisites**: Phase 1-2 completed  
**Goal**: Production-ready AI backend system

---

# Part 1: Advanced RAG Techniques

## 1. Hybrid Search Architecture

### 1.1 Concepts ✅

#### 1.1.1 What is Hybrid Search?

**Hybrid Search** = Combine keyword search + semantic search

```
Traditional Semantic Search:
  Query → Embedding → Vector DB → Similar documents
  ✅ Good for: "What is AI?"
  ❌ Poor for: Exact phrases, recent dates, specific IDs

Keyword Search (BM25):
  Query → Tokenize → Inverted index → Exact matches
  ✅ Good for: "gpt-4 2024 release"
  ❌ Poor for: Concept matching, synonyms

Hybrid = Best of Both!
  ✅ Exact matches (keyword)
  ✅ Semantic understanding (vector)
```

#### 1.1.2 When to Use Hybrid

```python
# Use keyword search for:
- Specific dates, versions, IDs
- Technical terms, acronyms
- Exact phrase matching

# Use semantic search for:
- Conceptual questions
- Synonym matching
- Long-form queries

# Use hybrid for:
- Everything (safe default)
- Mix of technical + conceptual content
```

### 1.2 Implementation Strategy ✅

#### 1.2.1 Hybrid Search Architecture Diagram

```
User Query
    ↓
    ├─ Path 1: Keyword Search (BM25)
    │  ├─ Tokenize query
    │  ├─ Search inverted index
    │  └─ Get keyword matches (scores 0-100)
    │
    ├─ Path 2: Semantic Search (Vectors)
    │  ├─ Generate embedding
    │  ├─ Search vector DB
    │  └─ Get semantic matches (scores 0-1)
    │
    └─ Combine & Rank (Fusion Algorithm)
       ├─ Normalize scores
       ├─ Weight keyword: semantic (e.g., 0.3:0.7)
       ├─ Re-rank results
       └─ Return top-k combined results
```

---

## 2. Re-ranking & Relevance Scoring

### 2.1 Ranking Algorithms

#### 2.1.1 Basic Ranking Approach

```python
# Simple fusion strategy
def hybrid_search(query: str, top_k: int = 5):
    # Get results from both searches
    keyword_results = bm25_search(query, top_k=20)  # Get more, re-rank later
    semantic_results = vector_search(query, top_k=20)
    
    # Normalize scores to 0-1
    keyword_norm = normalize_scores(keyword_results)  # Already 0-100, divide by 100
    semantic_norm = semantic_results  # Already 0-1
    
    # Combine with weights
    combined = {}
    for doc_id, score in keyword_norm.items():
        combined[doc_id] = combined.get(doc_id, 0) + (score * 0.3)  # 30% weight
    
    for doc_id, score in semantic_norm.items():
        combined[doc_id] = combined.get(doc_id, 0) + (score * 0.7)  # 70% weight
    
    # Sort and return top-k
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
```

#### 2.1.2 Advanced: Cross-Encoder Re-ranking

```python
# Cross-Encoder: Specialized model for relevance scoring
# Takes (query, document) pair → relevance score

from sentence_transformers import CrossEncoder

# Initialize cross-encoder (trained specifically for ranking)
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

def advanced_rerank(query: str, documents: list[str], top_k: int = 5):
    """Re-rank documents using cross-encoder"""
    
    # Score each (query, doc) pair
    pairs = [[query, doc] for doc in documents]
    scores = reranker.predict(pairs)
    
    # Re-rank by cross-encoder scores
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    
    return [doc for doc, score in ranked[:top_k]]
```

### 2.2 Quality Metrics

#### 2.2.1 Measuring Relevance Quality

```python
def evaluate_ranking(results: list, ground_truth: list) -> dict:
    """Evaluate ranking quality"""
    
    # Precision@K
    k = 5
    precision_at_k = len(set(results[:k]) & set(ground_truth)) / k
    
    # Mean Reciprocal Rank (MRR)
    mrr = 0
    for i, result in enumerate(results, 1):
        if result in ground_truth:
            mrr = 1 / i
            break
    
    # Normalized Discounted Cumulative Gain (NDCG)
    # Higher for relevant results placed earlier
    dcg = sum(
        (2**rel - 1) / np.log2(i + 2)
        for i, rel in enumerate([1 if r in ground_truth else 0 for r in results])
    )
    
    return {
        "precision@5": precision_at_k,
        "mrr": mrr,
        "dcg": dcg
    }
```

---

## 3. Consolidated: Hybrid Search + Re-ranking Implementation

### 3.1 Complete Working Example

```python
# hybrid_rag.py
import chromadb
from openai import OpenAI
from rank_bm25 import BM25Okapi
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class HybridRAG:
    def __init__(self):
        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection("hybrid_search")
        self.documents = []
        self.tokenized_docs = []
        self.bm25 = None
    
    def add_documents(self, documents: list[str]):
        """Add documents to hybrid search system"""
        self.documents = documents
        
        # Generate embeddings for semantic search
        embeddings_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=documents
        )
        embeddings = [item.embedding for item in embeddings_response.data]
        
        # Store in Chroma
        self.collection.add(
            ids=[str(i) for i in range(len(documents))],
            embeddings=embeddings,
            documents=documents
        )
        
        # Prepare for BM25 (keyword search)
        self.tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        
        print(f"✅ Added {len(documents)} documents to hybrid search")
    
    def keyword_search(self, query: str, top_k: int = 5) -> list:
        """BM25 keyword search"""
        query_tokens = query.split()
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        return [
            (self.documents[i], float(scores[i]))
            for i in top_indices
        ]
    
    def semantic_search(self, query: str, top_k: int = 5) -> list:
        """Vector semantic search"""
        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return [
            (doc, 1 - distance)  # Convert distance to similarity
            for doc, distance in zip(results["documents"][0], results["distances"][0])
        ]
    
    def hybrid_search(self, query: str, top_k: int = 5, 
                     keyword_weight: float = 0.3, 
                     semantic_weight: float = 0.7) -> list:
        """Combine keyword + semantic search"""
        
        # Get results from both
        keyword_results = self.keyword_search(query, top_k=20)
        semantic_results = self.semantic_search(query, top_k=20)
        
        # Combine scores
        combined_scores = {}
        
        # Add keyword scores (normalize 0-1)
        max_keyword_score = max([score for _, score in keyword_results])
        for doc, score in keyword_results:
            normalized_score = score / (max_keyword_score or 1)
            combined_scores[doc] = combined_scores.get(doc, 0) + (normalized_score * keyword_weight)
        
        # Add semantic scores (already 0-1)
        for doc, score in semantic_results:
            combined_scores[doc] = combined_scores.get(doc, 0) + (score * semantic_weight)
        
        # Sort and return
        ranked = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [(doc, score) for doc, score in ranked[:top_k]]
    
    def rag_query(self, query: str, use_hybrid: bool = True) -> str:
        """Full RAG pipeline with optional hybrid search"""
        
        # Retrieve
        if use_hybrid:
            retrieved = self.hybrid_search(query, top_k=3)
            context = "\n".join([doc for doc, _ in retrieved])
        else:
            retrieved = self.semantic_search(query, top_k=3)
            context = "\n".join([doc for doc, _ in retrieved])
        
        print(f"\n🔍 Retrieved documents:")
        for doc, score in retrieved:
            print(f"  • {doc[:60]}... (score: {score:.4f})")
        
        # Generate answer
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Answer based on the provided context only."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}"
                }
            ],
            temperature=0.2
        )
        
        answer = response.choices[0].message.content
        print(f"\n💡 Answer: {answer}")
        return answer

# Usage
if __name__ == "__main__":
    hybrid_rag = HybridRAG()
    
    docs = [
        "Python 3.11 was released on October 24, 2022",
        "FastAPI is a modern web framework for building APIs",
        "Vector databases enable semantic search capabilities",
        "Machine learning requires large datasets for training",
        "RAG combines retrieval and generation for better answers"
    ]
    
    hybrid_rag.add_documents(docs)
    
    # Test queries
    print("\n" + "="*70)
    print("SEMANTIC SEARCH (good for concepts)")
    hybrid_rag.rag_query("What are embeddings used for?", use_hybrid=False)
    
    print("\n" + "="*70)
    print("HYBRID SEARCH (best of both)")
    hybrid_rag.rag_query("When was Python 3.11 released?", use_hybrid=True)
```

---

# Part 2: Agents & Function Calling

## 4. Understanding Agents

### 4.1 Agent Concepts

#### 4.1.1 What is an Agent?

**Agent** = AI system that can perceive, reason, and take actions

```
Agent Loop:
  1. Perceive: Read user query
  2. Think: Decide what to do (which tool to use)
  3. Plan: Break down into steps
  4. Act: Call tools/functions
  5. Observe: Get results
  6. Loop: Repeat until done
```

#### 4.1.2 Agent vs Simple API Call

```python
# Simple API Call
User: "What's the weather in London?"
→ Call weather_api("London")
→ Return result
(No reasoning, just direct call)

# Agent
User: "Should I bring an umbrella to London tomorrow?"
→ Agent thinks: "Need weather forecast for London"
→ Agent calls: get_weather_forecast("London", "tomorrow")
→ Agent receives: "Rainy, 60% chance"
→ Agent reasons: "Rain likely → recommend umbrella"
→ Agent generates: "Yes, bring an umbrella"
(Reasoning + multiple steps + tool use)
```

### 4.2 Function Calling

#### 4.2.1 What is Function Calling?

**Function Calling** = LLM tells you which function to call with what parameters

```python
# Setup: Define tools available to LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Query LLM with tools
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "What's the weather in London?"}
    ],
    tools=tools,
    tool_choice="auto"  # Let LLM decide to use tools
)

# LLM responds with function call
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Function: {tool_call.function.name}")
    print(f"Args: {tool_call.function.arguments}")
    # Output: Function: get_weather, Args: {"location": "London"}
```

### 4.3 Building Complete Agent with Function Calling

#### 4.3.1 Travel Agent Implementation ✅
Refer week6/multistep_agent.py

#### 4.3.2 Trip weather planner Implementation

```python
# agent_system.py
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simulated tool implementations
def get_weather(location: str) -> dict:
    """Simulated weather API"""
    weather_data = {
        "London": "Rainy, 15°C",
        "Paris": "Sunny, 22°C",
        "Tokyo": "Cloudy, 18°C"
    }
    return {
        "location": location,
        "weather": weather_data.get(location, "Unknown")
    }

def calculate_trip_cost(destination: str, days: int) -> dict:
    """Simulated trip cost calculator"""
    costs = {
        "London": 100,  # per day
        "Paris": 120,
        "Tokyo": 150
    }
    daily_cost = costs.get(destination, 0)
    return {
        "destination": destination,
        "days": days,
        "total_cost": daily_cost * days
    }

def search_flights(departure: str, destination: str, date: str) -> dict:
    """Simulated flight search"""
    return {
        "departure": departure,
        "destination": destination,
        "date": date,
        "flights": [
            {"airline": "United", "price": 250, "duration": "7h"},
            {"airline": "British Airways", "price": 280, "duration": "6.5h"}
        ]
    }

# Define tools for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_trip_cost",
            "description": "Calculate total trip cost",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Destination city"},
                    "days": {"type": "integer", "description": "Number of days"}
                },
                "required": ["destination", "days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search available flights",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure": {"type": "string", "description": "Departure city"},
                    "destination": {"type": "string", "description": "Destination city"},
                    "date": {"type": "string", "description": "Travel date (YYYY-MM-DD)"}
                },
                "required": ["departure", "destination", "date"]
            }
        }
    }
]

# Tool dispatcher
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate_trip_cost": calculate_trip_cost,
    "search_flights": search_flights
}

class Agent:
    def __init__(self):
        self.messages = []
    
    def process_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Execute tool and return result"""
        if tool_name not in TOOL_FUNCTIONS:
            return f"Unknown tool: {tool_name}"
        
        tool_function = TOOL_FUNCTIONS[tool_name]
        result = tool_function(**tool_input)
        return json.dumps(result)
    
    def run(self, user_query: str) -> str:
        """Run agent loop"""
        print(f"\n👤 User: {user_query}")
        print("-" * 70)
        
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_query
        })
        
        # Agent loop
        iteration = 0
        max_iterations = 10
        
        while iteration < max_iterations:
            iteration += 1
            
            # Get LLM response
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            # Check if LLM wants to use tools
            if response.choices[0].message.tool_calls:
                # Add assistant's response
                self.messages.append({
                    "role": "assistant",
                    "content": response.choices[0].message.content or "",
                    "tool_calls": response.choices[0].message.tool_calls
                })
                
                # Process each tool call
                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Calling {tool_name}({tool_input})")
                    
                    # Execute tool
                    tool_result = self.process_tool_call(tool_name, tool_input)
                    print(f"✅ Result: {tool_result[:100]}...")
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "user",
                        "content": f"Tool result: {tool_result}"
                    })
            else:
                # No more tool calls, get final answer
                final_answer = response.choices[0].message.content
                print(f"\n🤖 Agent: {final_answer}")
                return final_answer
        
        return "Max iterations reached"

# Usage
if __name__ == "__main__":
    agent = Agent()
    
    # Complex query requiring multiple tool calls
    agent.run(
        "I want to plan a trip to Paris for 5 days from London on 2024-03-15. "
        "Can you check the weather, find flights, and calculate costs?"
    )
```

---

# Part 3: Production Deployment

## 5. Containerization & Docker

### 5.1 Docker Basics

#### 5.1.1 Dockerfile Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Environment
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 5.1.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DATABASE_URL: postgresql://user:pass@db:5432/rag_db
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: rag_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 5.2 Production Deployment

#### 5.2.1 Deployment to Production Platforms

```bash
# Railway Deployment
railway login
railway init
railway up

# Render Deployment
# 1. Connect GitHub
# 2. Set environment variables
# 3. Auto-deploy on push

# AWS ECS
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin
docker build -t rag-app:latest .
docker tag rag-app:latest <account>.dkr.ecr.us-east-1.amazonaws.com/rag-app
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/rag-app
```

---

## 6. Monitoring & Logging

### 6.1 Production Logging

#### 6.1.1 Structured Logging Setup

```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Output logs in JSON format for ELK/Datadog"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "service": "rag-api",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Setup logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

#### 6.1.2 Performance Monitoring

```python
# monitoring.py
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        
        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            
            logger.info({
                "function": func.__name__,
                "duration_ms": elapsed * 1000,
                "status": "success"
            })
            
            return result
        
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error({
                "function": func.__name__,
                "duration_ms": elapsed * 1000,
                "status": "error",
                "error": str(e)
            })
            raise
    
    return wrapper

# Usage
@monitor_performance
async def hybrid_search_endpoint(query: str):
    # Implementation
    pass
```

---

## 7. Consolidated: Production RAG API

### 7.1 Complete Production Application

```python
# production_rag_app.py
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import chromadb
from rank_bm25 import BM25Okapi
import logging
import json
from datetime import datetime
from functools import wraps
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.Client()
app = FastAPI(title="Production RAG API", version="1.0.0")

# Logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Models
class Document(BaseModel):
    content: str
    metadata: dict = {}

class QueryRequest(BaseModel):
    query: str
    use_hybrid: bool = True
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float
    latency_ms: float

# Performance monitoring
def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            logger.info(f"{func.__name__} completed in {elapsed:.2f}ms")
            return result, elapsed
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper

# Hybrid RAG
class ProductionRAG:
    def __init__(self):
        self.collection = chroma_client.create_collection("documents")
        self.documents = []
        self.bm25 = None
    
    def add_documents(self, documents: list[str]):
        """Add docs with embeddings"""
        self.documents = documents
        
        # Embeddings
        embeddings_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=documents
        )
        embeddings = [item.embedding for item in embeddings_response.data]
        
        # Store
        self.collection.add(
            ids=[str(i) for i in range(len(documents))],
            embeddings=embeddings,
            documents=documents
        )
        
        # BM25
        self.bm25 = BM25Okapi([doc.split() for doc in documents])
        logger.info(f"Added {len(documents)} documents")
    
    def hybrid_search(self, query: str, top_k: int = 3):
        """Hybrid search with keyword + semantic"""
        # Keyword
        keyword_scores = self.bm25.get_scores(query.split())
        keyword_results = sorted(
            enumerate(keyword_scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Semantic
        query_emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        
        semantic_results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )
        
        # Combine
        combined = {}
        max_keyword = keyword_results[0][1] if keyword_results else 1
        
        for idx, score in keyword_results:
            combined[idx] = combined.get(idx, 0) + (score / max_keyword) * 0.3
        
        for doc_idx, (doc, dist) in enumerate(
            zip(semantic_results["documents"][0], semantic_results["distances"][0])
        ):
            for orig_idx, orig_doc in enumerate(self.documents):
                if orig_doc == doc:
                    combined[orig_idx] = combined.get(orig_idx, 0) + (1 - dist) * 0.7
        
        # Return ranked
        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return [self.documents[idx] for idx, _ in ranked[:top_k]]

# Global RAG instance
rag = None

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    global rag
    rag = ProductionRAG()
    
    # Load sample docs
    sample_docs = [
        "Python 3.11 released October 2022",
        "FastAPI is a modern web framework",
        "RAG combines retrieval and generation"
    ]
    rag.add_documents(sample_docs)
    logger.info("✅ Application started")

# Endpoints
@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query RAG system"""
    start = time.perf_counter()
    
    try:
        if not rag:
            raise HTTPException(500, "RAG not initialized")
        
        # Retrieve
        retrieved = rag.hybrid_search(request.query, request.top_k)
        context = "\n".join(retrieved)
        
        # Generate
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Answer based on context"},
                {"role": "user", "content": f"Context:\n{context}\n\nQ: {request.query}"}
            ],
            temperature=0.2
        )
        
        answer = response.choices[0].message.content
        elapsed = (time.perf_counter() - start) * 1000
        
        logger.info(f"Query processed in {elapsed:.2f}ms")
        
        return QueryResponse(
            answer=answer,
            sources=retrieved,
            confidence=0.85,
            latency_ms=elapsed
        )
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(500, str(e))

@app.post("/add-documents")
async def add_documents(docs: list[Document]):
    """Add documents to system"""
    try:
        contents = [doc.content for doc in docs]
        rag.add_documents(contents)
        return {"status": "Added", "count": len(docs)}
    except Exception as e:
        logger.error(f"Add failed: {str(e)}")
        raise HTTPException(500, str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Run: uvicorn production_rag_app:app --reload
```

---

# Part 4: Interview Questions & Answers

## 8. Advanced RAG Interview Q&A

### 8.1 Hybrid Search Questions

#### 8.1.1 Q: "Explain hybrid search. When would you use it?" ✅

**A**: Hybrid search combines keyword-based search (BM25) with semantic/vector search.

**Explanation**:
- **Keyword search**: Finds exact matches, good for specific terms, numbers, dates
- **Semantic search**: Understands meaning, good for conceptual queries, synonyms
- **Hybrid**: Takes best of both

**When to use**:
```
- Technical documentation (mix of terms + concepts)
- Product catalogs (SKUs + descriptions)
- News articles (dates/names + topics)
- Scientific papers (citations + concepts)

Default: Always use hybrid if unsure. The weighting can be tuned later.
```

**Interview tip**: "Hybrid search reduces false negatives from pure semantic search while improving semantic understanding over pure keyword search."

#### 8.1.2 Q: "How do you weight keyword vs semantic scores in hybrid search?" ✅

**A**: Depends on your data and use case. Common approaches:

```python
# Tuning strategy:
1. Start with equal weights (0.5 / 0.5)
2. Evaluate performance
3. Adjust based on metrics:
   - More technical content → increase keyword weight
   - More conceptual queries → increase semantic weight
   - Mixed → use 0.3/0.7 or 0.4/0.6

# A/B testing:
Score semantic=0.7, keyword=0.3  (default)
vs
semantic=0.6, keyword=0.4
vs
semantic=0.5, keyword=0.5

# Measure: NDCG, Precision@K, User satisfaction
```

**Interview tip**: "The optimal weights depend on your domain. Always A/B test rather than guessing."

### 8.2 Re-ranking Questions

#### 8.2.1 Q: "What is re-ranking and why is it important?" ✅

**A**: Re-ranking means scoring document pairs (query, doc) to improve relevance.

**Why it matters**:
```
Scenario: Query returns 10 documents
- Initial retrieval: Fast but coarse (top-100)
- Re-ranking: Slower but precise (top-10)

Benefits:
1. Improves relevance of top-k results
2. Catch relevant docs missed by initial retrieval
3. Better user experience
4. Can use expensive but accurate models (cross-encoders)
```

**Implementation approaches**:
```python
# Approach 1: Simple fusion (fast)
# Combine multiple rankings → Sort

# Approach 2: Cross-encoder (accurate)
# Pass (query, doc) pairs to specialized model
# Returns relevance score
# Slower but more accurate

# Approach 3: LLM as judge (expensive)
# Ask LLM to rate relevance
# Very accurate but costly
```

**Interview tip**: "Re-ranking is a two-stage retrieval pattern: fast retrieval (recall) → accurate re-ranking (precision)."

#### 8.2.2 Q: "Compare different re-ranking strategies" ✅

**A**: 

| Strategy | Speed | Accuracy | Cost | When to Use |
|----------|-------|----------|------|-------------|
| **Fusion** | ⭐⭐⭐ | ⭐⭐ | Free | Fast API |
| **Cross-Encoder** | ⭐⭐ | ⭐⭐⭐ | $$ | Production search |
| **LLM Judge** | ⭐ | ⭐⭐⭐⭐ | $$$ | High value queries |

**Recommendation**: Start with fusion, move to cross-encoder if metrics decline.

### 8.3 Agent & Function Calling Questions

#### 8.3.1 Q: "Explain agents. How are they different from chatbots?" ❌

**A**: 

**Chatbot**:
```
User → LLM → Generate text → Return
(Single turn, no reasoning about actions)
```

**Agent**:
```
User → LLM (thinks what to do)
    → Selects tool/function
    → Executes tool
    → Observes result
    → Reasons about next step
    → Repeat until done
    → Generate final answer

(Multi-turn, tool usage, planning)
```

**Key difference**: Agents can take actions, chatbots just talk.

**Interview tip**: "Agents are goal-oriented systems that can break down complex tasks into steps and use tools."

#### 8.3.2 Q: "What is function calling? How does it work?" ✅

**A**: Function calling = LLM decides which function to call with which parameters.

**How it works**:
```
1. Define tools (functions with descriptions)
2. Send to LLM along with message
3. LLM analyzes and decides:
   - Should I use a tool? Yes/No
   - Which tool? (tool name)
   - With what params? (arguments)
4. Return structured tool call
5. Your code executes the function
6. Send result back to LLM
7. LLM generates final answer
```

**Key advantage**: LLM never directly accesses tools. You control execution.

**Interview tip**: "Function calling is structured tool use. The LLM tells you what to do, you execute it safely."

#### 8.3.3 Q: "How do you prevent agent loops? What's max iterations?" ✅

**A**: 

**Issues**:
- Agent keeps calling same tool repeatedly
- Calls tool with invalid arguments
- Never reaches conclusion

**Solutions**:
```python
# 1. Set max iterations
for iteration in range(MAX_ITERATIONS):  # e.g., 10
    if done:
        break

# 2. Track tool calls
called_tools = set()
if tool_name in called_tools and not new_args:
    # Same tool, same args → likely loop
    return "Unable to complete"
called_tools.add(tool_name)

# 3. Timeout
import time
start = time.time()
while time.time() - start < TIMEOUT_SECONDS:  # e.g., 30
    ...

# 4. Cost limits
total_tokens = 0
if total_tokens > MAX_TOKENS:
    return "Cost limit reached"
```

**Best practice**: Max iterations (5-10) + timeout (30-60s) + cost limit

**Interview tip**: "Always set guardrails. Agents are powerful but need boundaries."

---

## 9. Production Deployment Interview Q&A

### 9.1 Docker & Containerization Questions

#### 9.1.1 Q: "Why containerize your application? Benefits of Docker?" ⚠️

**A**: 

**Benefits**:
```
1. Consistency: Works same on dev, staging, production
2. Isolation: Dependencies don't conflict
3. Scalability: Easy to run multiple containers
4. Reproducibility: Same image everywhere
5. Deployment: Simple deployment process
```

**Without Docker**:
```
"Works on my machine" problem
Different OS → different behavior
Manual dependency management
Hard to replicate production locally
```

**With Docker**:
```
Same image everywhere
Dependencies locked in Dockerfile
Easy scaling (spin up more containers)
Infrastructure-agnostic
```

**Interview tip**: "Docker solves the 'works on my machine' problem and enables easy scaling."

#### 9.1.2 Q: "What's the difference between image and container?" ⚠️

**A**:

```python
# Image = Blueprint (static)
# Container = Running instance (dynamic)

# Analogy:
Image = Recipe
Container = Food prepared from recipe

# Docker:
docker build -t my-app:1.0 .    # Create image
docker run my-app:1.0           # Run container

# Key difference:
- Image: Read-only, versioned (1.0, 1.1, 2.0)
- Container: Running, stateful, ephemeral
```

**Interview tip**: "Image is the artifact, container is the execution. You ship images, run containers."

### 9.2 Monitoring & Observability Questions

#### 9.2.1 Q: "What metrics should you monitor in production?" ✅

**A**: 

**Key metrics** (4 Golden Signals):
```
1. Latency: How long requests take (p50, p95, p99)
2. Traffic: Requests per second
3. Errors: Error rate (4xx, 5xx)
4. Saturation: Resource utilization (CPU, Memory)
```

**RAG-specific metrics**:
```
- Retrieval quality: Precision@K, NDCG
- Answer quality: User satisfaction, feedback
- Cost: Tokens used per query
- Speed: Query latency, retrieval + generation time
- LLM accuracy: Hallucination rate
```

**Alerting**:
```
Alert if:
- Latency > 5s (slow)
- Error rate > 5% (broken)
- Cost > $X/hour (expensive)
- Memory > 80% (close to OOM)
```

**Interview tip**: "Monitor business metrics (cost, quality) + system metrics (latency, errors)."

#### 9.2.2 Q: "How do you track costs in production?"

**A**:

```python
# Track at each API call
def log_api_usage(model, prompt_tokens, completion_tokens):
    pricing = {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06}
    }
    
    prices = pricing[model]
    cost = (prompt_tokens / 1000 * prices["input"] + 
            completion_tokens / 1000 * prices["output"])
    
    logger.info({
        "event": "api_call",
        "model": model,
        "tokens": prompt_tokens + completion_tokens,
        "cost": cost
    })
    
    return cost

# Alert on cost anomalies
if daily_cost > BUDGET:
    send_alert(f"Daily cost ${daily_cost} exceeds budget ${BUDGET}")
```

**Best practices**:
1. Log every API call
2. Use structured logging (JSON)
3. Aggregate by model, user, feature
4. Set budgets and alerts
5. Review weekly/monthly

**Interview tip**: "In production, cost is as important as correctness. Track every API call."

---

## 10. System Design Interview Questions

### 10.1 Complete RAG System Design

#### 10.1.1 Q: "Design a production RAG system handling 1000 QPS" (Also refer [link](week6_rag_architecture_systemdesign.md))

**A**: (Interview-style answer)

**Requirements**:
```
- 1000 queries per second
- < 2 second latency (p99)
- < 5% error rate
- Cost-effective
- Scalable, maintainable
```

**Architecture**:
```
Client
  ↓
Load Balancer (nginx)
  ↓
[API Server] × N (replicas)
  ├─ Query validation
  ├─ Hybrid search cache
  ├─ Async LLM calls
  └─ Response formatting
  ↓
  ├─ Redis (cache layer)
  │  ├─ Popular queries
  │  ├─ Embeddings cache
  │  └─ Session data
  ├─ Vector DB (Pinecone)
  │  └─ Semantic search (indexed)
  ├─ Search Index (Elasticsearch)
  │  └─ Keyword search (BM25)
  └─ LLM API (OpenAI/Claude)
     └─ Batch requests
  ↓
Monitoring & Logging (Datadog/ELK)
```

**Scaling strategies**:
```
1. Caching layer (Redis)
   - Cache popular queries (80/20 rule)
   - Cache embeddings (avoid recomputing)
   - Save 40-60% of API calls

2. Async processing
   - Queue long queries
   - Process in background
   - Return immediately

3. Batch processing
   - Batch embeddings requests
   - Batch LLM calls
   - Save 30% on costs

4. Database indexing
   - Vector DB indexing
   - Full-text search indexing
   - Query optimization

5. Multiple replicas
   - Horizontal scaling
   - Load balancing
   - Graceful degradation
```

**Cost optimization**:
```
- Cache hits reduce embedding costs
- Batching reduces LLM costs  
- Async processing spreads load
- Cheaper models for re-ranking
- Budget limits per query
```

**Interview tip**: "Start with basic architecture, then add caching, async, batching as you scale. Always profile before optimizing."

---

# Part 5: Quick Start & Setup

## 11. Installation & Setup

### 11.1 Complete Setup

```bash
# 1. Create project
mkdir phase3-rag && cd phase3-rag

# 2. Virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install \
  openai \
  chromadb \
  rank-bm25 \
  fastapi \
  uvicorn \
  pydantic \
  python-dotenv \
  sentence-transformers \
  numpy

# 4. Setup environment
echo "OPENAI_API_KEY=sk-..." > .env

# 5. Run examples
python hybrid_rag.py
python agent_system.py
uvicorn production_rag_app:app --reload
```

---

## 12. Comprehensive Testing

### 12.1 Test Suite

```python
# test_phase3.py
import pytest
from hybrid_rag import HybridRAG
from agent_system import Agent, get_weather

def test_hybrid_search():
    rag = HybridRAG()
    rag.add_documents([
        "Python released 2022",
        "FastAPI framework"
    ])
    
    results = rag.hybrid_search("Python release date", top_k=1)
    assert len(results) == 1
    assert "Python" in results[0][0]

def test_agent_function_calling():
    agent = Agent()
    result = agent.run("What's weather in London?")
    assert "London" in result or "weather" in result

def test_production_api():
    from production_rag_app import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

# Run: pytest test_phase3.py -v
```

---

## 13. Deployment Checklist

```
☐ Code review completed
☐ All tests pass (>80% coverage)
☐ Logging configured
☐ Monitoring alerts set up
☐ Error handling complete
☐ Cost limits implemented
☐ Rate limiting configured
☐ Docker image built & tested
☐ Environment variables secured (.env not committed)
☐ Documentation updated
☐ Graceful degradation working
☐ Backup strategy in place
☐ Rollback plan documented
☐ Performance tested (load test)
☐ Security audit passed
```

---

**Phase 3 Complete! You now have a production-ready RAG system. 🚀**

Continue to Phase 4: Multi-agent systems and advanced agentic patterns.