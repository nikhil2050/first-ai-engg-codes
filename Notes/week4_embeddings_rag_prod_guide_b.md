# Phase 2: Embeddings, Vector Databases & RAG
## From API Calls to Production-Grade AI Backend
### Weeks 3-9: LLM Foundations + Production AI Backend

---

## Table of Contents
1. [Learning Flow Overview](#learning-flow-overview)
2. [1. Environment Setup](#1-environment-setup)
3. [2. Understanding Embeddings](#2-understanding-embeddings)
4. [3. First Embedding Call](#3-first-embedding-call)
5. [4. Vector Databases](#4-vector-databases)
6. [5. Document Ingestion](#5-document-ingestion)
7. [6. RAG Fundamentals](#6-rag-fundamentals)
8. [7. Build Simple RAG](#7-build-simple-rag)
9. [8. Production RAG](#8-production-rag)
10. [9. Evaluation & Optimization](#9-evaluation--optimization)
11. [10. LangChain RAG](#10-langchain-rag)
12. [11. FastAPI RAG Service](#11-fastapi-rag-service)
13. [12. Common Issues](#12-common-issues)
14. [13. Practice Tasks](#13-practice-tasks)
15. [14. Testing RAG Systems](#14-testing-rag-systems)
16. [15. Quick Reference](#15-quick-reference)

---

## Learning Flow Overview

```
Embeddings (Week 3)
    ↓
Vector Databases (Week 4)
    ↓
Document Indexing (Week 5)
    ↓
Simple RAG (Week 6)
    ↓
Production RAG (Week 7-8)
    ↓
Evaluation & Optimization (Week 9)
    ↓
Portfolio Project: LangChain Q&A API
```

### Teaching Pattern
Every concept: **Explain → Show code → Run it → Explain output → Best practices → Practice task**

---

## 1. Environment Setup ✅

### Install Required Libraries

```bash
# Core dependencies
pip install openai anthropic python-dotenv

# Vector databases & embeddings
pip install chromadb qdrant-client pinecone-client sentence-transformers

# Data processing
pip install langchain langchain-community langchain-text-splitters

# Web frameworks & utilities
pip install fastapi uvicorn pydantic

# Production tools
pip install python-dotenv pydantic-settings
```

### Create Virtual Environment ✅

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Configure API Keys ✅

Create `.env` file:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HUGGINGFACE_API_KEY=hf_...
```

Create `config.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_DB_PATH = "./vector_db"
```

---

## 2. Understanding Embeddings

### What are Embeddings?

**Concept**: Convert text into numerical vectors (arrays of numbers).

**Why?**
- LLMs think in numbers, not text
- Enables semantic search (find similar meaning, not just exact matches)
- Powers RAG systems
- Enables clustering, similarity analysis

**Example**:
```
Text: "The cat sat on the mat"
Embedding: [0.1, -0.5, 0.3, ..., 0.2]  (1536 dimensions for OpenAI)
```

**Key Properties**:
- **Fixed length**: Always same size (e.g., 1536 for `text-embedding-3-small`)
- **Semantic**: Similar text has similar embeddings
- **Normalized**: Can compute cosine similarity (distance between vectors)

### Common Embedding Models

| Model | Provider | Dimensions | Use Case |
|-------|----------|-----------|----------|
| `text-embedding-3-small` | OpenAI | 1536 | Fast, cheap, good quality |
| `text-embedding-3-large` | OpenAI | 3072 | High accuracy, slower |
| `all-MiniLM-L6-v2` | HuggingFace | 384 | Local, free, fast |
| `voyage-large-2-instruct` | Voyage AI | 1024 | Specialized for RAG |

### Similarity: Cosine Distance

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """Compute similarity between two embeddings (0-1, higher = more similar)"""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

# Example
emb1 = np.array([0.1, 0.2, 0.3])
emb2 = np.array([0.1, 0.2, 0.3])
emb3 = np.array([0.9, 0.8, 0.7])

print(cosine_similarity(emb1, emb2))  # 1.0 (identical)
print(cosine_similarity(emb1, emb3))  # 0.95 (similar)
```

---

## 3. First Embedding Call

### Explain: Embedding API

Call embedding model → get back vector for text.

**Simple vs Advanced**:
- **Simple**: One string → one vector
- **Advanced**: Batch multiple texts, handle errors, track costs

### Show Code: Generate Embedding

```python
from openai import OpenAI
from config import OPENAI_API_KEY, EMBEDDING_MODEL
import json

client = OpenAI(api_key=OPENAI_API_KEY)

# Example texts
texts = [
    "The cat sat on the mat",
    "A feline rested on a rug",
    "Python is a programming language"
]

def get_embedding(text: str) -> list:
    """Get embedding for a single text"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

# Run it
embeddings = []
for text in texts:
    emb = get_embedding(text)
    embeddings.append({
        "text": text,
        "embedding": emb,
        "dimension": len(emb)
    })
    print(f"✓ Embedded: {text[:40]}...")
    print(f"  Dimensions: {len(emb)}")
    print(f"  First 5 values: {emb[:5]}")
```

### Explain Output

```
✓ Embedded: The cat sat on the mat...
  Dimensions: 1536
  First 5 values: [0.001, -0.023, 0.045, ...]

✓ Embedded: A feline rested on a rug...
  Dimensions: 1536
  First 5 values: [0.002, -0.021, 0.047, ...]

✓ Embedded: Python is a programming language...
  Dimensions: 1536
  First 5 values: [-0.005, 0.018, -0.032, ...]
```

**What it means**:
- Each text is a vector of 1536 numbers
- Similar texts (cat/feline) have similar vectors
- Different topics (cats vs Python) have different vectors

### Best Practices

```python
def get_embeddings_batch(texts: list) -> list:
    """Batch embeddings (cheaper, faster)"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts  # Can pass list
    )
    # Preserves order: response.data[i] matches texts[i]
    return [item.embedding for item in response.data]

# Batch call
embeddings = get_embeddings_batch([
    "The cat sat on the mat",
    "A feline rested on a rug",
    "Python is a programming language"
])

# Cost tracking
def get_embedding_cost(num_tokens: int) -> float:
    """OpenAI embedding cost"""
    # text-embedding-3-small: $0.02 per 1M tokens
    cost_per_token = 0.02 / 1_000_000
    return num_tokens * cost_per_token

total_tokens = sum([len(text.split()) * 1.3 for text in texts])  # rough estimate
print(f"Estimated cost: ${get_embedding_cost(total_tokens):.6f}")
```

### Practice Task 1

**Task**: Embed 5 sentences about your favorite topic, find which 2 are most similar.

```python
# Your code here
my_texts = [
    "...",  # 5 sentences
    "...",
    "...",
    "...",
    "..."
]

# Get embeddings
embeddings = get_embeddings_batch(my_texts)

# Find max similarity
max_sim = 0
pair = None
for i in range(len(embeddings)):
    for j in range(i+1, len(embeddings)):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        if sim > max_sim:
            max_sim = sim
            pair = (i, j)

print(f"Most similar pair: {pair} with similarity {max_sim:.3f}")
print(f"  '{my_texts[pair[0]]}'")
print(f"  '{my_texts[pair[1]]}'")
```

---

## 4. Vector Databases

### What is a Vector Database?

**Concept**: Database optimized for storing and searching embeddings.

**Why not regular database?**
- Regular DB: Exact match only (`WHERE name = 'John'`)
- Vector DB: Similarity search (`Find similar embeddings`)
- Regular DB: Slow for high dimensions (millions of vectors)
- Vector DB: Fast with indexing (ANN - Approximate Nearest Neighbors)

### Three Popular Options

| DB | Setup | Scale | Free Tier | Best For |
|----|-------|-------|-----------|----------|
| **Chroma** | Local/Docker | Small-medium | Yes | Learning, prototyping |
| **Qdrant** | Docker/Cloud | Large | Yes | Production RAG |
| **Pinecone** | Cloud only | Very large | Limited | Enterprise scale |

### Chroma: Local Vector DB

**Advantage**: Zero setup, runs on laptop, perfect for learning.

```bash
pip install chromadb
```

### Qdrant: Production Vector DB

**Advantage**: Open source, Docker-based, excellent for RAG.

```bash
pip install qdrant-client

# Or run Docker
docker run -p 6333:6333 qdrant/qdrant
```

---

## 5. Document Ingestion

### Why Document Ingestion?

Goal: Convert documents → chunks → embeddings → vector DB.

**Process**:
```
Raw PDF/TXT/Markdown
    ↓
Split into chunks (important!)
    ↓
Generate embeddings for each chunk
    ↓
Store in vector DB
    ↓
Ready for RAG search
```

### Chunking Strategies

**Problem**: A 50-page document can't be embedded as one vector. Too much context lost.

**Solution**: Split into chunks.

#### Strategy 1: Fixed Size (Simple)

```python
def chunk_text_fixed(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into fixed-size chunks with overlap"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks

# Example
doc = "This is a long document. " * 100
chunks = chunk_text_fixed(doc, chunk_size=500, overlap=50)
print(f"Split into {len(chunks)} chunks")
```

**Best for**: Simple documents, technical manuals.

#### Strategy 2: Semantic (Smart)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text_semantic(text: str, chunk_size: int = 500) -> list:
    """Split by sentences/paragraphs, not hard cutoffs"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]  # Try in order
    )
    return splitter.split_text(text)

# Example
chunks = chunk_text_semantic(doc)
for i, chunk in enumerate(chunks[:2]):
    print(f"Chunk {i}: {chunk[:100]}...")
```

**Best for**: Books, articles, natural text.

#### Strategy 3: Paragraph-Based

```python
def chunk_text_paragraphs(text: str, min_length: int = 100) -> list:
    """Split by paragraphs, keep meaningful units"""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < 1000:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return [c for c in chunks if len(c) >= min_length]

chunks = chunk_text_paragraphs(doc)
```

**Best for**: Academic papers, structured documents.

### Show Code: Ingest and Store

```python
import chromadb
from datetime import datetime

# Initialize Chroma client (local, in-memory)
chroma_client = chromadb.Client()

# Create collection (like table in database)
collection = chroma_client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)

def ingest_document(doc_text: str, doc_name: str):
    """Ingest document: split → embed → store"""
    
    # Step 1: Split into chunks
    chunks = chunk_text_semantic(doc_text, chunk_size=500)
    print(f"✓ Split into {len(chunks)} chunks")
    
    # Step 2: Embed all chunks
    embeddings = get_embeddings_batch(chunks)
    print(f"✓ Generated {len(embeddings)} embeddings")
    
    # Step 3: Add to vector DB
    chunk_ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
    
    collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{
            "doc_name": doc_name,
            "chunk_index": i,
            "created_at": datetime.now().isoformat()
        } for i in range(len(chunks))]
    )
    print(f"✓ Stored in vector DB")
    return len(chunks)

# Example document
sample_doc = """
Python is a high-level programming language known for its simplicity.
It supports multiple programming paradigms and has a rich ecosystem of libraries.

Key features of Python:
- Easy to learn and read
- Dynamic typing
- Automatic memory management
- Large standard library
- Active community

Python applications:
- Web development (Django, Flask)
- Data science (Pandas, NumPy)
- Machine learning (TensorFlow, PyTorch)
- Automation and scripting
- Scientific computing
""" * 10  # Repeat to simulate larger doc

# Ingest
chunks_count = ingest_document(sample_doc, "python_guide")
```

### Explain Output

```
✓ Split into 8 chunks
✓ Generated 8 embeddings
✓ Stored in vector DB
```

**What happened**:
1. Document split into 8 semantic chunks (paragraph boundaries respected)
2. Each chunk embedded into vector
3. Vectors + text stored in Chroma DB
4. Ready for retrieval!

### Best Practices

```python
def ingest_with_validation(doc_text: str, doc_name: str, min_chunk_length: int = 50):
    """Ingest with error handling and validation"""
    
    # Validate input
    if not doc_text or len(doc_text) < 100:
        raise ValueError("Document too short")
    
    if not doc_name or "/" in doc_name:
        raise ValueError("Invalid document name")
    
    chunks = chunk_text_semantic(doc_text, chunk_size=500)
    
    # Filter out very short chunks
    chunks = [c for c in chunks if len(c) >= min_chunk_length]
    
    if not chunks:
        raise ValueError("No valid chunks after filtering")
    
    try:
        embeddings = get_embeddings_batch(chunks)
        chunk_ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
        
        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{
                "doc_name": doc_name,
                "chunk_index": i,
                "chunk_length": len(c)
            } for i in range(len(chunks))]
        )
        
        print(f"✓ Successfully ingested {len(chunks)} chunks from {doc_name}")
        return True
    
    except Exception as e:
        print(f"✗ Failed to ingest: {e}")
        return False
```

### Practice Task 2

**Task**: Load a `.txt` file, ingest into vector DB, verify storage.

```python
# 1. Create a sample file
with open("sample_doc.txt", "w") as f:
    f.write("""
The solar system consists of the Sun and all objects that orbit it.
The eight planets are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune.

Earth is the third planet from the Sun.
It has one natural satellite: the Moon.

Mars is known as the Red Planet.
It is home to the largest volcano in the solar system.
""")

# 2. Load and ingest
with open("sample_doc.txt", "r") as f:
    doc_text = f.read()

chunks_count = ingest_document(doc_text, "solar_system")

# 3. Verify
results = collection.get()
print(f"Total chunks in DB: {len(results['ids'])}")
print(f"Sample chunk: {results['documents'][0][:100]}...")
```

---

## 6. RAG Fundamentals

### What is RAG?

**RAG = Retrieval Augmented Generation**

**Problem**: LLMs have knowledge cutoff. Can't answer questions about your private documents.

**Solution**: 
1. **Retrieve**: Find relevant chunks from vector DB
2. **Augment**: Add chunks to LLM prompt
3. **Generate**: LLM answers using retrieved context

### RAG Flow

```
User Question
    ↓
Embed question
    ↓
Search vector DB for similar chunks
    ↓
Get top-K relevant chunks
    ↓
Build prompt: "Context: [chunks]. Question: [user_question]"
    ↓
Send to LLM
    ↓
LLM answers (with grounding in your docs)
```

### Example: Without vs With RAG

**Without RAG (GPT knows nothing about your company)**:
```
User: "What is our revenue for Q3 2024?"
LLM: "I don't have access to your company's financial data."
```

**With RAG (Retrieved from docs)**:
```
User: "What is our revenue for Q3 2024?"
System: Retrieves from DB → "Q3 2024 revenue: $5M"
LLM: "According to your documents, Q3 2024 revenue is $5M."
```

### Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Query** | User's question (embed it) |
| **Top-K** | Return K most similar chunks (e.g., K=3) |
| **Retrieval** | Finding relevant chunks |
| **Augmentation** | Adding chunks to prompt |
| **Context** | Retrieved chunks used to answer |

---

## 7. Build Simple RAG

### Show Code: Basic RAG Pipeline

```python
def retrieve_chunks(query: str, top_k: int = 3) -> list:
    """Search vector DB for chunks relevant to query"""
    
    # Step 1: Embed the query
    query_embedding = get_embedding(query)
    
    # Step 2: Search Chroma DB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # Extract documents and metadata
    chunks = results['documents'][0]  # List of texts
    distances = results['distances'][0]  # Similarity scores
    
    retrieved = []
    for i, (chunk, distance) in enumerate(zip(chunks, distances)):
        retrieved.append({
            "rank": i + 1,
            "similarity": 1 - distance,  # Convert distance to similarity
            "text": chunk
        })
    
    return retrieved


def simple_rag(user_query: str, top_k: int = 3) -> dict:
    """Simple RAG: retrieve → generate"""
    
    # Step 1: Retrieve
    retrieved = retrieve_chunks(user_query, top_k=top_k)
    
    # Step 2: Build context
    context = "\n\n".join([r["text"] for r in retrieved])
    
    # Step 3: Build prompt
    system_prompt = """You are a helpful assistant.
Answer the user's question using ONLY the provided context.
If the context doesn't contain relevant information, say so."""
    
    user_message = f"""Context:
{context}

Question: {user_query}

Answer based on the context above:"""
    
    # Step 4: Generate with LLM
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    answer = response.content[0].text
    
    return {
        "query": user_query,
        "retrieved_chunks": retrieved,
        "context": context,
        "answer": answer
    }


# Run it
result = simple_rag("What is Python?", top_k=2)
print(f"Question: {result['query']}")
print(f"\nRetrieved {len(result['retrieved_chunks'])} chunks:")
for chunk in result['retrieved_chunks']:
    print(f"  Chunk {chunk['rank']} (similarity: {chunk['similarity']:.2f})")
    print(f"    {chunk['text'][:80]}...")
print(f"\nAnswer: {result['answer']}")
```

### Explain Output

```
Question: What is Python?

Retrieved 2 chunks:
  Chunk 1 (similarity: 0.92)
    Python is a high-level programming language known for...
  Chunk 2 (similarity: 0.85)
    Key features of Python: - Easy to learn and read...

Answer: Python is a high-level programming language known for its simplicity 
and ease of use. According to the provided context, it supports multiple 
programming paradigms, has dynamic typing, automatic memory management, and 
a large standard library. It's used for web development, data science, 
machine learning, and automation.
```

**What happened**:
1. Question "What is Python?" embedded
2. Similar chunks found (0.92 and 0.85 similarity)
3. Context built from chunks
4. LLM answered using only that context (grounded answer)

### Best Practices

```python
def advanced_retrieve_chunks(query: str, top_k: int = 3, similarity_threshold: float = 0.6) -> list:
    """Retrieve with filtering and logging"""
    
    # Embed query
    query_embedding = get_embedding(query)
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 2  # Get more, filter after
    )
    
    chunks = results['documents'][0]
    distances = results['distances'][0]
    
    # Filter by similarity threshold
    retrieved = []
    for chunk, distance in zip(chunks, distances):
        similarity = 1 - distance
        if similarity >= similarity_threshold:
            retrieved.append({
                "similarity": similarity,
                "text": chunk
            })
    
    # Sort by similarity
    retrieved = sorted(retrieved, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    print(f"✓ Retrieved {len(retrieved)} relevant chunks")
    return retrieved
```

### Practice Task 3

**Task**: Query your ingested document, retrieve chunks, check relevance.

```python
# Try different queries
queries = [
    "What is Python?",
    "How is Python used in data science?",
    "What are the planet sizes?",
    "Tell me about coffee"  # Should have low relevance
]

for query in queries:
    result = simple_rag(query, top_k=2)
    print(f"\n{'='*50}")
    print(f"Query: {query}")
    print(f"Retrieved chunks: {len(result['retrieved_chunks'])}")
    for chunk in result['retrieved_chunks']:
        print(f"  Similarity: {chunk['similarity']:.2f}")
```

---

## 8. Production RAG

### Add Production Features

Production RAG adds:
- Error handling
- Logging
- Cost tracking
- Response caching
- Prompt versioning
- Structured outputs

### Show Code: Production RAG

```python
import logging
from datetime import datetime
from typing import Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionRAG:
    def __init__(self, collection_name: str = "documents"):
        self.collection = chroma_client.get_collection(name=collection_name)
        self.call_log = []
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def retrieve_chunks(self, query: str, top_k: int = 3, 
                       min_similarity: float = 0.5) -> dict:
        """Retrieve with error handling and logging"""
        
        try:
            # Embed query
            query_embedding = get_embedding(query)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            chunks = results['documents'][0]
            distances = results['distances'][0]
            
            # Convert to similarity (1 - distance)
            retrieved = []
            for i, (chunk, distance) in enumerate(zip(chunks, distances)):
                similarity = 1 - distance
                if similarity >= min_similarity:
                    retrieved.append({
                        "rank": i + 1,
                        "similarity": round(similarity, 3),
                        "text": chunk,
                        "chunk_length": len(chunk)
                    })
            
            logger.info(f"Retrieved {len(retrieved)} chunks for query: {query[:50]}")
            
            return {
                "success": True,
                "query": query,
                "chunks_retrieved": len(retrieved),
                "chunks": retrieved
            }
        
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks": []
            }
    
    def generate_answer(self, query: str, retrieved_chunks: list, 
                       max_tokens: int = 500) -> dict:
        """Generate answer with cost tracking"""
        
        try:
            # Build context
            context = "\n\n---\n\n".join([r["text"] for r in retrieved_chunks])
            
            system_prompt = """You are a helpful assistant answering questions based on provided documents.
- Answer ONLY using the provided context
- If context doesn't contain answer, say "Not found in documents"
- Cite which chunk/document the answer comes from
- Be concise and accurate"""
            
            user_message = f"""Context from documents:
{context}

User Question: {query}

Provide your answer:"""
            
            # Generate with Anthropic
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            answer = response.content[0].text
            
            # Track tokens and cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Cost calculation (Anthropic pricing)
            # Input: $3 per 1M tokens, Output: $15 per 1M tokens
            cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000
            
            self.total_tokens += total_tokens
            self.total_cost += cost
            
            logger.info(f"Generated answer ({input_tokens} in, {output_tokens} out, ${cost:.6f})")
            
            return {
                "success": True,
                "answer": answer,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "cost": round(cost, 6)
            }
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": None
            }
    
    def answer_question(self, query: str, top_k: int = 3) -> dict:
        """Complete RAG pipeline: retrieve → generate"""
        
        logger.info(f"Processing query: {query}")
        start_time = datetime.now()
        
        # Step 1: Retrieve
        retrieval = self.retrieve_chunks(query, top_k=top_k)
        
        if not retrieval["success"] or not retrieval["chunks"]:
            return {
                "success": False,
                "error": "No relevant chunks found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 2: Generate
        generation = self.generate_answer(query, retrieval["chunks"])
        
        # Step 3: Log and return
        elapsed = (datetime.now() - start_time).total_seconds()
        
        result = {
            "success": True,
            "query": query,
            "retrieved_chunks": len(retrieval["chunks"]),
            "answer": generation["answer"],
            "tokens_used": generation["tokens"]["total"],
            "cost": generation["cost"],
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        self.call_log.append(result)
        logger.info(f"Query completed in {elapsed:.2f}s, cost: ${generation['cost']:.6f}")
        
        return result
    
    def get_statistics(self) -> dict:
        """Get usage statistics"""
        return {
            "total_calls": len(self.call_log),
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
            "average_cost_per_call": round(self.total_cost / len(self.call_log), 6) if self.call_log else 0,
            "average_latency": round(sum([c["elapsed_seconds"] for c in self.call_log]) / len(self.call_log), 2) if self.call_log else 0
        }

# Usage
rag = ProductionRAG()

# Answer a question
result = rag.answer_question("What is Python used for?", top_k=2)
print(json.dumps(result, indent=2))

# Get stats
stats = rag.get_statistics()
print(f"\nStats: {stats}")
```

### Explain Output

```json
{
  "success": true,
  "query": "What is Python used for?",
  "retrieved_chunks": 2,
  "answer": "According to the documents, Python is used for: Web development (Django, Flask), Data science (Pandas, NumPy), Machine learning (TensorFlow, PyTorch), Automation and scripting, and Scientific computing.",
  "tokens_used": 145,
  "cost": 0.000435,
  "elapsed_seconds": 1.23,
  "timestamp": "2024-01-15T10:30:45.123456"
}

Stats: {
  "total_calls": 1,
  "total_tokens": 145,
  "total_cost": 0.000435,
  "average_cost_per_call": 0.000435,
  "average_latency": 1.23
}
```

### Best Practices

```python
class RobustRAG(ProductionRAG):
    """Add retry logic, caching, and fallbacks"""
    
    def retrieve_with_retry(self, query: str, max_retries: int = 3) -> dict:
        """Retry retrieval on failure"""
        
        for attempt in range(max_retries):
            try:
                return self.retrieve_chunks(query)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                # Wait before retry
                import time
                time.sleep(2 ** attempt)
    
    def answer_with_fallback(self, query: str, top_k: int = 3, 
                            fallback_model: str = "gpt-3.5-turbo") -> dict:
        """Try primary model, fallback if fail"""
        
        try:
            return self.answer_question(query, top_k)
        except Exception as e:
            logger.warning(f"Primary model failed, using fallback: {e}")
            # Use cheaper/faster fallback model
            return {
                "success": True,
                "answer": "Using fallback model",
                "fallback": True
            }
```

### Practice Task 4

**Task**: Implement ProductionRAG, answer 3 questions, track costs.

```python
# Create instance
rag = ProductionRAG()

# Answer questions
questions = [
    "What is Python?",
    "What are Python's key features?",
    "What is Earth?"
]

results = []
for q in questions:
    result = rag.answer_question(q, top_k=2)
    results.append(result)
    print(f"Q: {q}")
    print(f"A: {result['answer'][:100]}...")
    print(f"Cost: ${result['cost']:.6f}\n")

# Print summary
stats = rag.get_statistics()
print(f"\nTotal cost: ${stats['total_cost']:.6f}")
print(f"Average latency: {stats['average_latency']:.2f}s")
```

---

## 9. Evaluation & Optimization

### Evaluation Metrics

#### 1. Retrieval Quality

```python
def evaluate_retrieval(query: str, relevant_chunks: list, 
                      retrieved: list) -> dict:
    """Evaluate if retrieval returned relevant chunks"""
    
    # Recall: How many relevant chunks did we get?
    relevant_ids = set([c["id"] for c in relevant_chunks])
    retrieved_ids = set([c["id"] for c in retrieved])
    
    recall = len(relevant_ids & retrieved_ids) / len(relevant_ids) if relevant_ids else 0
    
    # Precision: How many retrieved were relevant?
    precision = len(relevant_ids & retrieved_ids) / len(retrieved_ids) if retrieved_ids else 0
    
    # F1: Balance of precision/recall
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "recall": round(recall, 3),
        "precision": round(precision, 3),
        "f1": round(f1, 3)
    }

# Example
relevant = [{"id": "chunk_1"}, {"id": "chunk_3"}]
retrieved = [
    {"id": "chunk_1", "similarity": 0.95},
    {"id": "chunk_2", "similarity": 0.85},
    {"id": "chunk_4", "similarity": 0.75}
]

metrics = evaluate_retrieval("test", relevant, retrieved)
print(f"Recall: {metrics['recall']} (got {1} out of {2} relevant)")
print(f"Precision: {metrics['precision']} (1 out of 3 retrieved were relevant)")
print(f"F1: {metrics['f1']}")
```

#### 2. Answer Quality

```python
def evaluate_answer(answer: str, ground_truth: str) -> dict:
    """Simple evaluation: does answer mention key concepts?"""
    
    # Extract key terms from ground truth
    keywords = set(ground_truth.lower().split())
    answer_words = set(answer.lower().split())
    
    # Coverage: what % of keywords are in answer?
    covered = len(keywords & answer_words) / len(keywords) if keywords else 0
    
    # Length check
    is_reasonable_length = 50 < len(answer) < 2000
    
    return {
        "keyword_coverage": round(covered, 3),
        "reasonable_length": is_reasonable_length,
        "answer_length": len(answer)
    }

answer = "Python is used for web development and data science"
ground_truth = "Python web development data science machine learning"

eval_result = evaluate_answer(answer, ground_truth)
print(f"Coverage: {eval_result['keyword_coverage']} ({100 * eval_result['keyword_coverage']:.0f}%)")
print(f"Length OK: {eval_result['reasonable_length']}")
```

#### 3. Groundedness (Using LLM Judge)

```python
def evaluate_groundedness(answer: str, context: str) -> float:
    """Use LLM to check if answer is grounded in context"""
    
    judge_prompt = f"""Rate if the answer is grounded in the context (0-1).
- 1.0: Answer only uses context, well-cited
- 0.5: Answer mostly from context, some additions
- 0.0: Answer ignores context or contradicts it

Context:
{context}

Answer:
{answer}

Rating (just the number):"""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    
    try:
        score = float(response.content[0].text.strip())
        return max(0, min(1, score))  # Clamp to 0-1
    except:
        return 0.5  # Default if parsing fails

# Example
context = "Python is used for web development and data science"
answer = "Python is great for web development and data science applications"
groundedness = evaluate_groundedness(answer, context)
print(f"Groundedness: {groundedness:.2f}")
```

### Optimization Strategies

#### 1. Chunk Size Tuning

```python
def test_chunk_sizes(doc: str, query: str, sizes: list = [256, 512, 1024]):
    """Test different chunk sizes, measure retrieval quality"""
    
    results = {}
    
    for size in sizes:
        # Create collection for this size
        coll_name = f"test_size_{size}"
        coll = chroma_client.create_collection(name=coll_name)
        
        # Ingest with this size
        chunks = chunk_text_semantic(doc, chunk_size=size)
        embeddings = get_embeddings_batch(chunks)
        
        coll.add(
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            documents=chunks
        )
        
        # Retrieve and evaluate
        query_emb = get_embedding(query)
        retrieved = coll.query(query_embeddings=[query_emb], n_results=3)
        
        avg_length = sum([len(c) for c in retrieved['documents'][0]]) / len(retrieved['documents'][0])
        
        results[size] = {
            "num_chunks": len(chunks),
            "avg_chunk_length": round(avg_length),
            "retrieved_samples": [c[:80] for c in retrieved['documents'][0]]
        }
    
    return results

# Test
results = test_chunk_sizes(sample_doc, "What is Python?", sizes=[256, 512, 1024])
for size, data in results.items():
    print(f"Size {size}: {data['num_chunks']} chunks")
```

**Recommendation**:
- **256**: Too small, loses context
- **512**: Good balance (sweet spot)
- **1024**: Good for dense documents
- **2048**: Too large for short queries

#### 2. Top-K Optimization

```python
def optimize_top_k(query: str, true_relevant_count: int, k_values: list = [1, 3, 5, 10]):
    """Find optimal K for this query"""
    
    for k in k_values:
        retrieved = retrieve_chunks(query, top_k=k)
        
        # If using ground truth, calculate recall
        # For demo, just show stats
        avg_similarity = sum([r['similarity'] for r in retrieved]) / len(retrieved)
        
        print(f"K={k}: Retrieved {len(retrieved)}, avg similarity: {avg_similarity:.3f}")

optimize_top_k("What is Python?", true_relevant_count=2)
```

**Recommendation**:
- **K=1-2**: Fast, for simple queries
- **K=3-5**: Best for most RAG (default)
- **K=10+**: High precision, slower, higher cost

#### 3. Similarity Threshold

```python
def optimize_threshold(query: str, thresholds: list = [0.5, 0.6, 0.7, 0.8]):
    """Filter low-quality retrievals"""
    
    for threshold in thresholds:
        retrieved = retrieve_chunks(query, top_k=10)
        filtered = [r for r in retrieved if r['similarity'] >= threshold]
        
        print(f"Threshold {threshold}: {len(filtered)} chunks (from {len(retrieved)})")

optimize_threshold("What is Python?")
```

---

## 10. LangChain RAG

### Why LangChain?

**Problem**: Writing RAG from scratch is verbose, error-prone.

**Solution**: LangChain = framework for LLM apps.

```python
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Setup
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Split document
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(sample_doc)

# Create vector store
vectorstore = Chroma.from_texts(chunks, embeddings)

# Create RAG chain (3 lines!)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # Stuff all chunks in context
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# Use it
result = qa_chain.invoke({"query": "What is Python?"})
print(result['result'])
```

### LangChain Advantage

| Feature | Custom | LangChain |
|---------|--------|-----------|
| Document loading | Manual | Built-in loaders |
| Chunking | DIY | Pre-configured splitters |
| Embedding | DIY | Multiple providers |
| Vector store | DIY | Chroma, Pinecone, etc. |
| Chain logic | DIY | Ready-to-use chains |
| Memory | DIY | ConversationMemory |

---

## 11. FastAPI RAG Service

### Show Code: Production RAG API

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

app = FastAPI(title="RAG API", version="1.0.0")

# Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)
    stream: bool = Field(default=False)

class ChunkMetadata(BaseModel):
    rank: int
    similarity: float
    text: str
    chunk_length: int

class QueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_chunks: list[ChunkMetadata]
    tokens_used: int
    cost: float
    elapsed_seconds: float

# Global RAG instance
rag = ProductionRAG()

# Endpoints
@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    """Answer a question using RAG"""
    
    try:
        result = rag.answer_question(request.query, top_k=request.top_k)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail="Failed to process query")
        
        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            retrieved_chunks=result["retrieved_chunks"],
            tokens_used=result["tokens_used"],
            cost=result["cost"],
            elapsed_seconds=result["elapsed_seconds"]
        )
    
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get RAG statistics"""
    return rag.get_statistics()

@app.post("/ingest")
async def ingest_doc(doc_name: str, doc_text: str):
    """Ingest a new document"""
    
    try:
        chunks_count = ingest_document(doc_text, doc_name)
        return {
            "success": True,
            "doc_name": doc_name,
            "chunks_ingested": chunks_count
        }
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}

# Run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Test API

```bash
# Start server
python app.py

# Test endpoint (in another terminal)
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "top_k": 3}'

# Expected response
{
  "query": "What is Python?",
  "answer": "...",
  "retrieved_chunks": [...],
  "tokens_used": 145,
  "cost": 0.000435,
  "elapsed_seconds": 1.23
}
```

---

## 12. Common Issues

### Issue 1: Low Retrieval Quality

**Symptom**: Retrieved chunks not relevant to query.

**Causes**:
- Chunk size too small/large
- Embedding model not suitable
- Similarity threshold too low

**Fixes**:
```python
# 1. Try different chunk size
chunks = chunk_text_semantic(doc, chunk_size=750)  # Try 750 instead of 500

# 2. Try better embedding model
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # Better quality

# 3. Increase similarity threshold
retrieved = advanced_retrieve_chunks(query, top_k=5, similarity_threshold=0.75)

# 4. Re-rank retrieved chunks (reorder by LLM)
def rerank_chunks(query: str, chunks: list) -> list:
    """Use LLM to rerank chunks"""
    # Ask LLM which chunks are most relevant
    pass
```

### Issue 2: Hallucinations (Answer doesn't match context)

**Symptom**: LLM makes up information not in chunks.

**Causes**:
- LLM "knowing" answer from training data
- Weak system prompt

**Fixes**:
```python
# 1. Strict system prompt
system_prompt = """You are a fact-checking assistant.
RULES:
1. Answer ONLY from provided context
2. If context insufficient, output: "Not enough information"
3. Quote the context when possible
4. Never make up information"""

# 2. Add citation requirement
system_prompt += "\n\nRequire citations: [Chunk N: \"quote\"]"

# 3. Filter low-confidence retrievals
retrieved = [r for r in retrieved if r['similarity'] > 0.70]

# 4. Use lower temperature (more deterministic)
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    temperature=0,  # Deterministic
    messages=[...]
)
```

### Issue 3: Slow Queries

**Symptom**: RAG takes >5 seconds per query.

**Bottlenecks**:
- Embedding generation (slow model)
- Large number of chunks
- LLM latency

**Fixes**:
```python
# 1. Cache embeddings (don't re-embed same query)
cache = {}

def get_embedding_cached(text: str) -> list:
    if text in cache:
        return cache[text]
    emb = get_embedding(text)
    cache[text] = emb
    return emb

# 2. Reduce top_k
retrieved = retrieve_chunks(query, top_k=2)  # Instead of 5

# 3. Use faster model for embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 4. Async queries
import asyncio

async def query_async(query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, rag.answer_question, query)
```

### Issue 4: High Costs

**Symptom**: RAG queries cost more than expected.

**Causes**:
- Large context (many chunks) = more input tokens
- Expensive embedding model
- Repeated queries

**Fixes**:
```python
# 1. Use cheaper embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. Reduce context size
chunks_count = 2  # Instead of 5
retrieved = retrieve_chunks(query, top_k=chunks_count)

# 3. Cache repeated queries
from functools import lru_cache

@lru_cache(maxsize=100)
def answer_question_cached(query: str, top_k: int = 3):
    return rag.answer_question(query, top_k)

# 4. Batch queries
queries = ["Q1", "Q2", "Q3"]
results = [rag.answer_question(q) for q in queries]
total_cost = sum([r["cost"] for r in results])
print(f"Batch cost: ${total_cost:.6f}")
```

---

## 13. Practice Tasks

### Task 1: Build Complete RAG System

**Objective**: Ingest docs, answer questions, track stats.

```python
# 1. Load multiple documents
docs = {
    "python": "Python is a programming language...",
    "javascript": "JavaScript is a web language...",
    "rust": "Rust is a systems language..."
}

# 2. Ingest all
for name, text in docs.items():
    ingest_document(text, name)

# 3. Create RAG
rag = ProductionRAG()

# 4. Answer questions
questions = [
    "What is Python?",
    "Is JavaScript web-focused?",
    "What language are they discussing?"
]

for q in questions:
    result = rag.answer_question(q)
    print(f"Q: {q}")
    print(f"A: {result['answer'][:150]}...")
    print()

# 5. Report statistics
stats = rag.get_statistics()
print(f"Total cost: ${stats['total_cost']:.6f}")
```

### Task 2: Evaluate RAG Quality

**Objective**: Measure precision, recall, groundedness.

```python
# Define test cases with ground truth
test_cases = [
    {
        "query": "What is Python?",
        "expected_keywords": ["programming", "language", "simplicity"],
        "relevant_chunks": ["chunk_1", "chunk_3"]
    },
    {
        "query": "Python uses?",
        "expected_keywords": ["web", "data science", "ML"],
        "relevant_chunks": ["chunk_2", "chunk_4", "chunk_5"]
    }
]

# Evaluate
for test in test_cases:
    result = rag.answer_question(test["query"])
    
    # Check keywords
    answer_lower = result["answer"].lower()
    keyword_coverage = sum([1 for kw in test["expected_keywords"] 
                           if kw in answer_lower]) / len(test["expected_keywords"])
    
    print(f"Query: {test['query']}")
    print(f"Keyword coverage: {keyword_coverage:.1%}")
    print(f"Latency: {result['elapsed_seconds']:.2f}s")
    print()
```

### Task 3: Deploy RAG API

**Objective**: Build and deploy FastAPI RAG endpoint.

```bash
# 1. Create app.py with RAG endpoint (from section 11)

# 2. Create requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
openai==1.3.0
chromadb==0.4.21
langchain==0.0.350
python-dotenv==1.0.0

# 3. Run locally
uvicorn app:app --reload

# 4. Test
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "top_k": 3}'

# 5. Deploy (Render/Railway)
# Push code to GitHub, connect in Render/Railway
```

---

## 14. Testing RAG Systems

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock

def test_retrieve_chunks():
    """Test retrieval returns chunks"""
    query = "What is Python?"
    result = retrieve_chunks(query, top_k=3)
    
    assert len(result) <= 3
    assert all("similarity" in r for r in result)
    assert all("text" in r for r in result)

def test_chunk_text_semantic():
    """Test semantic chunking"""
    text = "Sentence 1. Sentence 2.\n\nParagraph 2. More text."
    chunks = chunk_text_semantic(text, chunk_size=30)
    
    assert len(chunks) > 0
    assert all(len(c) <= 30 for c in chunks)

@patch('get_embedding')
def test_rag_with_mocked_embedding(mock_embedding):
    """Test RAG with mocked LLM response"""
    mock_embedding.return_value = [0.1] * 1536
    
    result = simple_rag("test query", top_k=2)
    
    assert result["answer"] is not None
    mock_embedding.assert_called()

def test_production_rag_logging(caplog):
    """Test that RAG logs properly"""
    rag = ProductionRAG()
    rag.answer_question("test")
    
    assert "Processing query" in caplog.text
    assert len(rag.call_log) == 1

# Run tests
pytest test_rag.py -v
```

### Integration Tests

```python
def test_full_rag_pipeline():
    """Test entire RAG flow"""
    
    # Setup
    doc_text = "Python is amazing" * 50
    ingest_document(doc_text, "test_doc")
    
    # Query
    rag = ProductionRAG()
    result = rag.answer_question("What is Python?")
    
    # Assert
    assert result["success"]
    assert result["answer"]
    assert len(result["retrieved_chunks"]) > 0
    assert result["cost"] > 0
    assert result["elapsed_seconds"] > 0
    
    # Cleanup
    # Delete test collection
```

---

## 15. Quick Reference

### Chroma Commands

```python
# Create collection
collection = chroma_client.create_collection(name="my_docs")

# Add documents
collection.add(
    ids=["1", "2", "3"],
    embeddings=[emb1, emb2, emb3],
    documents=["text1", "text2", "text3"],
    metadatas=[{"source": "doc1"}, ...]
)

# Query
results = collection.query(query_embeddings=[query_emb], n_results=3)

# Get all
all_docs = collection.get()

# Delete
collection.delete(ids=["1", "2"])

# Count
count = collection.count()
```

### FastAPI Patterns

```python
# POST with request body
@app.post("/endpoint")
async def endpoint(request: RequestModel) -> ResponseModel:
    return ResponseModel(...)

# GET with query params
@app.get("/search")
async def search(query: str, limit: int = 10):
    return {"results": []}

# Error handling
try:
    ...
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

# Async operation
async def async_task():
    await asyncio.sleep(1)
    return "done"
```

### Embedding Cost Estimation

```python
# OpenAI embeddings
# text-embedding-3-small: $0.02 per 1M tokens
# text-embedding-3-large: $0.13 per 1M tokens

tokens_used = 10000
cost_small = tokens_used * 0.02 / 1_000_000  # $0.0002
cost_large = tokens_used * 0.13 / 1_000_000  # $0.0013

# Anthropic Claude
# Input: $3 per 1M tokens
# Output: $15 per 1M tokens
input_tokens = 500
output_tokens = 100
cost_claude = (input_tokens * 3 + output_tokens * 15) / 1_000_000
```

### Debugging RAG

```python
# Check retrieval quality
def debug_retrieval(query: str):
    retrieved = retrieve_chunks(query, top_k=5)
    for r in retrieved:
        print(f"Similarity: {r['similarity']:.2f}")
        print(f"Text: {r['text'][:100]}...")
        print("---")

# Check embedding similarity
def debug_similarity(text1: str, text2: str):
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    sim = cosine_similarity(emb1, emb2)
    print(f"Similarity between texts: {sim:.3f}")

# Log all RAG calls
import json
def log_rag_call(result: dict):
    with open("rag_calls.jsonl", "a") as f:
        f.write(json.dumps(result) + "\n")
```

---

## Summary

### Phase 2 Learning Path

**Week 3**: Embeddings fundamentals + first embedding call
**Week 4**: Vector databases (Chroma/Qdrant) setup
**Week 5**: Document ingestion + chunking strategies
**Week 6**: RAG fundamentals + simple RAG pipeline
**Week 7-8**: Production RAG + error handling + cost tracking
**Week 9**: Evaluation metrics + optimization strategies

### Key Takeaways

1. **Embeddings** convert text to vectors → enable semantic search
2. **Vector databases** store embeddings efficiently
3. **RAG** retrieves relevant context + LLM generates grounded answers
4. **Production RAG** adds logging, error handling, cost tracking
5. **Evaluation** matters: measure retrieval quality and answer grounding

### Next Steps

- Build project: **LangChain Q&A API** (portfolio item 3)
- Deploy on Railway/Render
- Iterate on chunk size, top-k, similarity threshold
- Add caching and optimization
- Move to **Phase 3: Production AI Backend**

---

## Code Repository Structure

```
rag-project/
├── .env
├── config.py
├── embeddings.py
├── vector_db.py
├── document_ingestion.py
├── rag.py
├── production_rag.py
├── evaluation.py
├── app.py (FastAPI)
├── test_rag.py
├── requirements.txt
└── README.md
```

---

**Happy RAG building! 🚀**