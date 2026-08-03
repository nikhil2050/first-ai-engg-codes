# Phase 2: Embeddings & Vector Databases - Practical Coding Tutorial
## AI Backend Engineering Roadmap

---

## Overview: What You'll Build in Phase 2

- ✅ Understand embeddings and why they matter
- ✅ Generate embeddings using OpenAI API
- ✅ Store embeddings in a vector database (Pinecone, Supabase)
- ✅ Perform semantic search on documents
- ✅ Build RAG (Retrieval Augmented Generation) pipeline
- ✅ Create production-grade AI backend

**Time**: 5-6 hours  
**Prerequisites**: Phase 1 completed, Python, API concepts  
**Goal**: Build RAG system that retrieves + generates intelligent responses

---

# Part 1: Foundations - Embeddings & Vectors

## 1. Understanding Embeddings

### 1.1 Fundamentals

#### 1.1.1 What are Embeddings?

**Embeddings** = Convert text into numbers (vectors) that capture meaning

```
Text: "The cat sat on the mat"
       ↓ (embedding model)
Vector: [0.234, -0.891, 0.456, ..., 0.123]  (1536 dimensions for OpenAI)
```

#### 1.1.2 Why Embeddings Matter

- Enable semantic search (find similar documents)
- Enable RAG (retrieve relevant context for LLM)
- Enable clustering (group similar texts)

### 1.2 Vector Space Visualization

#### 1.2.1 Spatial Relationships

```
"dog" embedding     ← close to each other (similar meaning)
  ↓
"cat" embedding     ← close to each other (similar meaning)
  ↓
"pizza" embedding   ← far from dog/cat (different meaning)
```

**Key insight**: Similar texts have similar embeddings (small distance)

### 1.3 Distance & Similarity Metrics

#### 1.3.1 Cosine Similarity (Most Common)

```python
# Cosine Similarity (most common)
# Range: -1 to 1 (higher = more similar)
# 1.0 = identical, 0.0 = unrelated, -1.0 = opposite

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embedding1 = np.array([0.1, 0.2, 0.3])
embedding2 = np.array([0.1, 0.2, 0.31])

similarity = cosine_similarity([embedding1], [embedding2])[0][0]
print(f"Similarity: {similarity:.4f}")  # ~0.9999 (very similar)
```

---

# Part 2: Generating Embeddings

## 2. Working with OpenAI Embeddings API

### 2.1 Getting Started

#### 2.1.1 Create Your First Embedding

```python
# embedding_example.py
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Generate embedding
response = client.embeddings.create(
    model="text-embedding-3-small",  # Cheap option
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")  # 1536
print(f"First 10 values: {embedding[:10]}")
print(f"Cost: $0.02 per 1M tokens")
```

### 2.2 Processing Multiple Documents

#### 2.2.1 Batch Embeddings (Multiple Texts)

```python
def embed_documents(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple documents"""
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    
    # Sort by index to maintain order
    embeddings = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in embeddings]

# Example
docs = [
    "Python is a programming language",
    "Dogs are loyal pets",
    "Machine learning is powerful"
]

embeddings = embed_documents(docs)
print(f"Generated {len(embeddings)} embeddings")
```

### 2.3 Model Selection & Pricing

#### 2.3.1 Embedding Models Comparison

```python
# OpenAI Embedding Models (2024)

models = {
    "text-embedding-3-small": {
        "dimension": 512,  # Can reduce dimensions
        "cost": 0.02,      # per 1M tokens (CHEAPEST)
        "use": "Learning, testing"
    },
    "text-embedding-3-large": {
        "dimension": 3072,
        "cost": 0.13,      # per 1M tokens
        "use": "Production, high quality"
    },
    "text-embedding-ada-002": {
        "dimension": 1536,
        "cost": 0.10,      # per 1M tokens (deprecated)
        "use": "Legacy, avoid"
    }
}

print("✅ Recommendation: Use text-embedding-3-small for learning")
```

---

# Part 3: Vector Database Foundations

## 3. Introduction to Vector Databases

### 3.1 Core Concepts

#### 3.1.1 Why Vector Databases?

```
Regular Database (SQL):
  SELECT * FROM users WHERE age > 25  ← keyword matching

Vector Database:
  Find documents similar to this query  ← semantic matching!
```

### 3.2 Available Solutions

#### 3.2.1 Vector Database Options

| Database | Free Tier | Ease | Best For |
|----------|-----------|------|----------|
| **Pinecone** | ❌ (paid) | ⭐⭐⭐ Easy | Quickest setup |
| **Supabase** | ✅ Yes | ⭐⭐⭐ Easy | Self-hosted option |
| **Chroma** | ✅ Yes | ⭐⭐⭐ Easy | Local/in-memory |
| **Milvus** | ✅ Yes | ⭐⭐ Medium | Complex queries |
| **Weaviate** | ✅ Yes | ⭐⭐ Medium | Enterprise |

**For learning: Use Chroma (no setup needed!)**

---

# Part 4: Chroma - Local Vector Database

## 4. Getting Started with Chroma

### 4.1 Setup & Installation

#### 4.1.1 Install & Setup Chroma

```bash
pip install chromadb openai
```

### 4.2 Core Operations

#### 4.2.1 Store & Search Embeddings

```python
# chroma_example.py
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Chroma (local, in-memory)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="documents")

# Sample documents
documents = [
    "Python is a great programming language for AI",
    "Machine learning models need training data",
    "Vector databases enable semantic search",
    "Embeddings capture text meaning as numbers"
]

# Generate embeddings
print("🔄 Generating embeddings...")
embeddings_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents
)

embeddings = [item.embedding for item in embeddings_response.data]

# Store in Chroma
print("💾 Storing in vector database...")
collection.add(
    ids=[str(i) for i in range(len(documents))],
    embeddings=embeddings,
    metadatas=[{"source": f"doc_{i}"} for i in range(len(documents))],
    documents=documents
)

print(f"✅ Stored {len(documents)} documents")

# Search (semantic)
print("\n🔍 SEMANTIC SEARCH:")
print("-" * 70)

query = "What are embeddings used for?"
query_embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
).data[0].embedding

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2
)

for i, (doc, distance) in enumerate(zip(results["documents"][0], results["distances"][0])):
    similarity = 1 - distance  # Convert distance to similarity
    print(f"{i+1}. {doc}")
    print(f"   Similarity: {similarity:.4f}\n")
```

**Output**:
```
✅ Stored 4 documents

🔍 SEMANTIC SEARCH:
1. Embeddings capture text meaning as numbers
   Similarity: 0.8234

2. Vector databases enable semantic search
   Similarity: 0.7891
```

### 4.3 Data Management

#### 4.3.1 Update & Delete Operations

```python
# Update document
collection.update(
    ids=["0"],
    documents=["Updated: Python is excellent for AI and ML"],
    embeddings=[new_embedding]
)

# Delete document
collection.delete(ids=["3"])

# Persist to disk
chroma_client = chromadb.PersistentClient(path="./chroma_data")
```

---

# Part 5: RAG - Retrieval Augmented Generation

## 5. RAG Fundamentals

### 5.1 Architecture & Concepts

#### 5.1.1 RAG Architecture

```
User Question
    ↓
[1] Retrieve relevant documents from vector database
    ↓
[2] Combine retrieved docs + question as context
    ↓
[3] Send to LLM for intelligent response
    ↓
Answer grounded in actual documents
```

### 5.2 Implementation

#### 5.2.1 Simple RAG Pipeline

```python
# rag_pipeline.py
from openai import OpenAI
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.Client()

# Sample knowledge base
knowledge_base = [
    "Python 3.11 was released in October 2022",
    "FastAPI is a modern web framework for Python",
    "Vector databases store embeddings for semantic search",
    "RAG combines retrieval and generation for better answers"
]

def build_rag_system():
    """Initialize RAG with knowledge base"""
    
    # Create collection
    collection = chroma_client.create_collection(name="knowledge_base")
    
    # Generate embeddings
    print("📚 Building RAG system...")
    embeddings_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=knowledge_base
    )
    embeddings = [item.embedding for item in embeddings_response.data]
    
    # Store in vector DB
    collection.add(
        ids=[str(i) for i in range(len(knowledge_base))],
        embeddings=embeddings,
        documents=knowledge_base
    )
    
    return collection

def rag_query(collection, question: str) -> str:
    """
    RAG Pipeline:
    1. Retrieve relevant docs
    2. Send to LLM with context
    """
    
    # Step 1: Retrieve
    print(f"\n🔍 Question: {question}")
    print("-" * 70)
    
    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    retrieved_docs = results["documents"][0]
    print("📖 Retrieved documents:")
    for doc in retrieved_docs:
        print(f"  • {doc}")
    
    # Step 2: Generate answer using LLM
    context = "\n".join(retrieved_docs)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Answer based on the provided context. If not in context, say 'Not in knowledge base'."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ],
        temperature=0.2  # More factual
    )
    
    answer = response.choices[0].message.content
    print(f"\n💡 Answer: {answer}")
    return answer

# Run RAG
if __name__ == "__main__":
    collection = build_rag_system()
    
    # Test queries
    rag_query(collection, "When was Python 3.11 released?")
    rag_query(collection, "What is FastAPI?")
    rag_query(collection, "How does blockchain work?")  # Not in KB
```

---

# Part 6: Production - Supabase & FastAPI

## 6. Production RAG with Supabase

### 6.1 Setup & Configuration

#### 6.1.1 Setup Supabase Vector Storage

```bash
# Install Supabase Python client
pip install supabase
```

### 6.2 Implementation

#### 6.2.1 Supabase RAG Implementation

```python
# supabase_rag.py
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def store_document(text: str, metadata: dict = None):
    """Store document in Supabase with embedding"""
    
    # Generate embedding
    embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding
    
    # Store in Supabase
    data = supabase.table("documents").insert({
        "content": text,
        "embedding": embedding,
        "metadata": metadata or {}
    }).execute()
    
    print(f"✅ Stored: {text[:50]}...")
    return data

def search_documents(query: str, limit: int = 3):
    """Search documents by semantic similarity"""
    
    # Generate query embedding
    query_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    
    # Search in Supabase
    results = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": limit
        }
    ).execute()
    
    return results.data

# Setup in Supabase SQL:
"""
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_count int
) RETURNS TABLE (
  id bigint,
  content text,
  similarity float
) LANGUAGE SQL STABLE AS $$
  SELECT
    documents.id,
    documents.content,
    1 - (documents.embedding <=> query_embedding) as similarity
  FROM documents
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
$$;
"""
```

### 6.3 Configuration

#### 6.3.1 .env Configuration for Supabase

```bash
# .env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## 7. FastAPI RAG Endpoint

### 7.1 Building the API

#### 7.1.1 Production RAG API

```python
# rag_api.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="RAG API")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.Client()
collection = None

# Models
class Document(BaseModel):
    content: str
    metadata: dict = {}

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float

# Initialize
@app.on_event("startup")
async def startup():
    """Initialize RAG system on startup"""
    global collection
    
    # Create collection
    collection = chroma_client.create_collection(name="documents")
    
    # Load sample documents
    sample_docs = [
        "FastAPI is a modern Python web framework",
        "RAG combines retrieval and generation",
        "Vector databases enable semantic search"
    ]
    
    embeddings_resp = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=sample_docs
    )
    embeddings = [item.embedding for item in embeddings_resp.data]
    
    collection.add(
        ids=[str(i) for i in range(len(sample_docs))],
        embeddings=embeddings,
        documents=sample_docs
    )

# Endpoints
@app.post("/add-document")
async def add_document(doc: Document):
    """Add document to RAG system"""
    
    try:
        # Generate embedding
        embedding = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=doc.content
        ).data[0].embedding
        
        # Add to collection
        collection.add(
            ids=[str(hash(doc.content))],
            embeddings=[embedding],
            documents=[doc.content],
            metadatas=[doc.metadata]
        )
        
        return {"status": "Document added", "content": doc.content[:50]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag(req: QueryRequest):
    """Query RAG system"""
    
    try:
        # Generate query embedding
        query_embedding = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=req.question
        ).data[0].embedding
        
        # Retrieve documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=req.top_k
        )
        
        retrieved_docs = results["documents"][0]
        context = "\n".join(retrieved_docs)
        
        # Generate answer
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Answer based on context only"},
                {"role": "user", "content": f"Context:\n{context}\n\nQ: {req.question}"}
            ],
            temperature=0.2
        )
        
        answer = response.choices[0].message.content
        
        return QueryResponse(
            answer=answer,
            sources=retrieved_docs,
            confidence=0.85
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "RAG API healthy"}

# Run: uvicorn rag_api:app --reload
```

#### 7.1.2 Testing the RAG API
```bash
# Add document
curl -X POST http://localhost:8000/add-document \
  -H "Content-Type: application/json" \
  -d '{"content":"Python was created by Guido van Rossum"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Who created Python?"}'
```

---

# Part 7: Advanced Techniques

## 8. Document Processing

### 8.1 Chunking Strategies

#### 8.1.1 Document Chunking Strategy

```python
def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split large document into overlapping chunks"""
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap  # Overlap for context
    
    return chunks

# Example
long_doc = "Python is... [very long document]"
chunks = chunk_document(long_doc, chunk_size=500)
print(f"Split into {len(chunks)} chunks")
```

#### 8.1.2 Smart Chunking with Langchain

```bash
pip install langchain
```

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def smart_chunk(text: str):
    """Use sentence-aware chunking"""
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    
    chunks = splitter.split_text(text)
    return chunks
```

## 9. Quality Assurance

### 9.1 Evaluation Methods

#### 9.1.1 Retrieval Quality Assessment

```python
def evaluate_rag(question: str, ground_truth: str, retrieved_docs: list[str]):
    """Evaluate RAG system quality"""
    
    # Retrieval metrics
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    # 1. Is ground truth in retrieved docs?
    hit = any(ground_truth.lower() in doc.lower() for doc in retrieved_docs)
    print(f"✅ Retrieval Hit: {hit}")
    
    # 2. Similarity score
    gt_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=ground_truth
    ).data[0].embedding
    
    for doc in retrieved_docs:
        doc_embedding = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=doc
        ).data[0].embedding
        
        sim = cosine_similarity([gt_embedding], [doc_embedding])[0][0]
        print(f"  Similarity: {sim:.4f}")
```

---

# Part 8: Deployment & Best Practices

## 10. Pre-Deployment Checklist

### 10.1 Validation Requirements

```
☐ Documents loaded into vector DB
☐ Embeddings generated and stored
☐ Semantic search tested
☐ Retrieved docs are relevant
☐ LLM generates good answers
☐ Error handling for edge cases
☐ Cost tracking (embeddings + LLM)
☐ API endpoints secured
☐ Logging for debugging
☐ Performance optimized
```

## 11. Practice & Learning

### 11.1 Hands-On Projects

#### 11.1.1 Task 1: Simple RAG
```python
# Build RAG system for:
# - 5 documents about Python
# - Query: "What version of Python was released in 2022?"
# - Return answer with sources
```

#### 11.1.2 Task 2: PDF Document RAG
```python
# Extract text from PDF
# Chunk into 500-token pieces
# Generate embeddings
# Build RAG API endpoint
```

#### 11.1.3 Task 3: Multi-Source RAG
```python
# Combine multiple document types:
# - Website articles
# - PDFs
# - Database records
# Build unified search
```

---

## 12. Cost Management & Optimization

### 12.1 Cost Analysis

#### 12.1.1 Cost Breakdown per 1000 Queries

```python
# Phase 2 costs (per 1000 queries)

embeddings_cost = (1000 * 100 / 1_000_000) * 0.02  # $0.002
retrieval_cost = 0  # Free (vector DB)
llm_cost = (1000 * 200 / 1_000_000) * 0.75  # $0.15

total = embeddings_cost + retrieval_cost + llm_cost
print(f"Total cost per 1000 queries: ${total:.3f}")
# ≈ $0.15 per 1000 queries (very cheap!)
```

---

## 13. Reference & Tools

### 13.1 Code Templates

#### 13.1.1 Chroma Quick Start
```python
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.Client()
collection = chroma.create_collection("docs")

# Add
embeddings = [client.embeddings.create(model="text-embedding-3-small", input=doc).data[0].embedding for doc in docs]
collection.add(ids=[str(i) for i in range(len(docs))], embeddings=embeddings, documents=docs)

# Search
query_emb = client.embeddings.create(model="text-embedding-3-small", input="query").data[0].embedding
results = collection.query(query_embeddings=[query_emb], n_results=3)
```

#### 13.1.2 RAG Query Template
```python
# Retrieve
retrieved = vector_db.search(query, top_k=3)

# Generate
context = "\n".join(retrieved)
answer = llm.chat([{"role": "user", "content": f"Context:\n{context}\n\nQ: {query}"}])
```

---

## 14. Troubleshooting & Common Issues

### 14.1 Problem Resolution

| Issue | Cause | Solution |
|-------|-------|----------|
| Poor retrieval | Bad embeddings | Use better embedding model |
| Irrelevant answers | Wrong context | Improve chunking strategy |
| Slow queries | Large dataset | Add indexing, batch queries |
| High costs | Too many embeddings | Cache embeddings, batch process |
| Hallucinations | LLM ignoring context | Use lower temperature, better prompt |

---

## 15. Progression Path

### 15.1 What's Next

#### 15.1.1 Phase 3 Learning Path

After Phase 2:
- ✅ Move to Phase 3: Advanced RAG (Hybrid Search, Re-ranking)
- ✅ Learn agents and function calling
- ✅ Deploy to production

---

## 16. Quick Start & Execution

### 16.1 Getting Started

#### 16.1.1 Run Phase 2 Locally

```bash
# 1. Install
pip install chromadb openai python-dotenv

# 2. Add .env
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Run examples
python chroma_example.py
python rag_pipeline.py
python rag_api.py
```

---

**You're now building RAG systems! 🚀**

Complete all 3 practice tasks before moving to Phase 3.