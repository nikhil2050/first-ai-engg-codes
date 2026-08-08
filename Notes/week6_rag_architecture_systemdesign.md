# RAG System Architecture - Interview Guide

## Visual Overview (ASCII)

```
                            👤 CLIENT
                               |
                               | User Query
                               ↓
                    ⚖️  LOAD BALANCER (nginx)
                    /           |           \
                   /            |            \
          🖥️ API SERVER 1   🖥️ API SERVER 2   🖥️ API SERVER N
          Query validation  Query validation  Query validation
          Caching           Caching           Caching
          Hybrid search     Hybrid search     Hybrid search
          LLM calls         LLM calls         LLM calls
                   \            |            /
                    \           |           /
                        🔄 RESPONSE SYNC
                               |
                    ┌──────────┼──────────┐
                    ↓          ↓          ↓
            ┌─────────────┐ ┌──────────┐ ┌──────────────┐
            │ 🔎 HYBRID   │ │ 🧠 LLM   │ │ ⚡ REDIS    │
            │   SEARCH    │ │  API     │ │  CACHE      │
            ├─────────────┤ ├──────────┤ ├──────────────┤
            │ • Semantic  │ │ • Claude │ │ • Queries   │
            │ • Keyword   │ │ • OpenAI │ │ • Embeddings│
            │   (BM25)    │ │          │ │ • Sessions  │
            └─────────────┘ └──────────┘ └──────────────┘
                    ↓              ↓
        ┌───────────────────────────────────────┐
        │      DATA RETRIEVAL LAYER (Dashed)    │
        └───────────────────────────────────────┘
                    ↓              ↓              ↓
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ 🗂️ VECTOR DB │  │ 🔍 SEARCH    │  │ 📊 METADATA │
        │              │  │  INDEX       │  │ (PostgreSQL) │
        ├──────────────┤  ├──────────────┤  ├──────────────┤
        │ Pinecone/    │  │ Elasticsearch│  │ • Tenant ID  │
        │ Qdrant/      │  │ or BM25      │  │ • User ID    │
        │ Chroma       │  │              │  │ • Filters    │
        │              │  │              │  │ • Timestamps │
        │ Semantic     │  │ Keyword      │  │              │
        │ search       │  │ search       │  │              │
        └──────────────┘  └──────────────┘  └──────────────┘
                    │              │              │
                    └──────────────┼──────────────┘
                                   ↑
                    (Retrieved documents + rankings)
                                   |
                                   ↓
                        ✅ FORMATTED RESPONSE
                        (Answer + citations)
                                   |
                                   ↓
                    📈 MONITORING & LOGGING
                    (Datadog/ELK/Prometheus)
                    Track: latency, quality,
                    user satisfaction, errors
```

---

## Layer Breakdown

### Layer 1: Client
- User sends query ("What's in our Q3 sales report?")
- Single entry point

### Layer 2: Load Balancer + API Servers
- **nginx**: Distributes requests across N API server replicas
- **API Servers** (each instance):
  - Validate query (length, format, auth)
  - Check Redis cache (avoid redundant work)
  - Call hybrid search if not cached
  - Orchestrate LLM call with context
  - Format response

**Why N replicas?**
- Handle concurrent requests (horizontal scaling)
- Fault tolerance (if one dies, others handle load)
- Cost efficiency (scale down during low traffic)

### Layer 3: Processing Layer (Core Logic)

#### 🔎 Hybrid Search
Combines two approaches:

| Method | How | Pros | Cons |
|--------|-----|------|------|
| **Semantic** | Query → embedding → vector similarity | Understands meaning, catches synonyms ("car" = "automobile") | Slower, costs API calls |
| **Keyword** (BM25) | Query → exact term lookup in index | Fast, precise, exact matches | Misses synonyms, requires exact terms |

**Best practice:** Combine both. Use `EnsembleRetriever` (LangChain) to merge results.

#### 🧠 LLM API
- Takes top-k retrieved documents + user query
- Generates grounded answer (constrained: "only use provided docs")
- Supports streaming (show response word-by-word)
- Models: Claude 3.5 Sonnet, GPT-4, open-source Llama

#### ⚡ Redis Cache
- Stores embeddings of frequent queries (avoid re-computing)
- Caches popular Q&A pairs (skip LLM entirely)
- Session data (conversation history)
- **Hit rate impact:** 40% cache hit = 40% fewer API calls

### Layer 4: Data Stores (Independent)

#### 🗂️ Vector Database
**Purpose:** Store + retrieve embeddings (semantic search)

**Options:**
- **Pinecone** (SaaS, easiest, paid)
- **Qdrant** (self-hosted, supports filtering, open-source)
- **Milvus** (self-hosted, distributed, complex)
- **Chroma** (local, free, prototyping)

**Key feature:** Metadata filtering
```
Search with filter: {
  "embedding": [0.2, 0.8, ...],
  "filter": {"tenant_id": "user123"}  ← multi-tenancy
}
```

#### 🔍 Search Index
**Purpose:** Keyword/BM25 search for exact matches

**Options:**
- **Elasticsearch** (industry standard, complex)
- **PostgreSQL + BM25** (simple, if using Postgres)
- **Typesense** (simpler Elasticsearch alternative)

**When to use:**
- User searches for "invoice #12345" (exact match)
- Company name, product SKU, ID lookups

#### 📊 Metadata Database
**Purpose:** Store document metadata + enable filtering

**Options:**
- **PostgreSQL** (most common)
- **Supabase** (PostgreSQL + vector extension)
- **DynamoDB** (if AWS-native)

**Stores:**
- tenant_id (SaaS multi-tenancy isolation)
- user_id
- document_source (which file/URL)
- timestamps (created_at, updated_at)
- access_level (public, private, restricted)

**Example filtering:**
```sql
SELECT doc_id FROM metadata
WHERE tenant_id = 'customer_abc'
AND created_at > '2024-01-01'
AND access_level IN ('public', 'user_private')
```

---

## Data Flow (Request → Response)

### Step 1: Query Arrives
```
User: "What's the ROI on Project X?"
     ↓ (via HTTPS)
Load Balancer routes to API Server #3
```

### Step 2: Check Cache
```
API Server #3:
├─ Query hash = "ROI_Project_X"
├─ Check Redis: FOUND (cached answer from 2 hours ago)
└─ Return cached response immediately ✅
   (90% latency improvement, 0 API calls)
```

### Step 3a: Cache Miss → Hybrid Search
```
If cache miss:
├─ Embed query: "What's the ROI on Project X?" 
│  → [0.23, 0.81, 0.12, ..., 0.45] (embedding model)
│
├─ Semantic search (vector DB):
│  Vector DB: "ROI_Project_X" embedding nearest to query
│  ↓
│  Returns: [doc_1 (similarity: 0.89), 
│            doc_5 (similarity: 0.82),
│            doc_12 (similarity: 0.71)]
│
└─ Keyword search (search index):
   Search Index: "ROI" AND "Project" AND "X"
   ↓
   Returns: [doc_1, doc_3, doc_5, doc_8]

   Merge & rank results:
   1. doc_1  (appears in both, highest score)
   2. doc_5  (appears in both)
   3. doc_12 (semantic match, high similarity)
   4. doc_3  (keyword match only)
   5. doc_8  (keyword match only)
```

### Step 3b: Metadata Filtering
```
Before returning docs, check metadata:
├─ Tenant filter: tenant_id = "customer_123" ✅
├─ Time filter: created_at >= "2024-01-01" ✅
├─ Access filter: user has "read" permission ✅
└─ Return only docs matching ALL filters
```

### Step 4: Re-ranking (Optional)
```
If confidence low:
├─ Pass top-10 retrieved docs through re-ranker
│  (cross-encoder model, more expensive but accurate)
└─ Reorder by true relevance (not just vector similarity)
```

### Step 5: Generate Response
```
LLM prompt construction:
┌──────────────────────────────┐
│ System:                      │
│ "You are a financial analyst.│
│  Only answer using provided  │
│  documents. Cite sources."   │
├──────────────────────────────┤
│ Documents:                   │
│ [doc_1]: Project X ROI is 42%│
│ [doc_5]: Budget was $2.5M    │
│ [doc_12]: Timeline: Q3 2024  │
├──────────────────────────────┤
│ User Query:                  │
│ "What's the ROI on Project X?│
└──────────────────────────────┘
        ↓ (via API)
      Claude
        ↓
Answer: "Project X achieved a 42% 
ROI on a $2.5M budget in Q3 2024.
[Citation: doc_1, doc_5]"
```

### Step 6: Cache Response
```
Before returning:
├─ Store in Redis: key="ROI_Project_X", 
│                  value="Project X achieved...",
│                  ttl=3600 (1 hour)
└─ Return to user ✅
```

### Step 7: Log & Monitor
```
Datadog/ELK captures:
├─ latency: 342ms (cache miss) or 45ms (cache hit)
├─ retrieval_quality: top-1 relevant? yes ✅
├─ user_satisfaction: thumbs_up / thumbs_down
├─ model_version: claude-3.5-sonnet
├─ tokens_used: 450 input, 120 output
└─ cost: $0.003
```

---

## Multi-Tenancy Isolation (Critical for SaaS)

**Problem:** Customer A's docs must NOT appear in Customer B's queries

**Solution:** Metadata filtering at every layer

```
Customer A Query:
├─ Embed query
├─ Search Vector DB:
│  search(embedding, filter={"tenant_id": "A"})
│  ↓ Only returns embeddings where tenant_id=A
├─ Search Index:
│  BM25(query, filter={"tenant_id": "A"})
│  ↓ Only returns docs where tenant_id=A
└─ Metadata DB:
   SELECT * FROM docs
   WHERE tenant_id = "A"
   ↓ Enforced at DB level

Result: Customer A can NEVER see Customer B's data
```

---

## Scaling Considerations

| Component | Bottleneck | Solution |
|-----------|-----------|----------|
| **API Servers** | CPU-bound (LLM calls) | Async/batch LLM requests, add replicas |
| **Vector DB** | Latency (semantic search slow) | Use ANN (approximate NN), ~95% accuracy, 10x faster |
| **Search Index** | Disk I/O (large corpus) | Sharding, Elasticsearch clusters |
| **Cache Hit Rate** | Memory (Redis full) | LRU eviction, increase Redis size |
| **LLM Latency** | Token generation speed | Smaller model, streaming responses |

---

## Interview Q&A

**Q: Your vector DB goes down. What happens?**
- Fallback to keyword-only search (slower, less accurate)
- Or fail gracefully: return error, don't crash

**Q: How do you update embeddings when source docs change?**
- Option 1: Re-embed nightly (simple, slow for large corpus)
- Option 2: Event-driven (Kafka, listen to doc updates, re-embed immediately)
- Option 3: Versioning (store doc version in metadata, filter stale versions)

**Q: Cost optimization — how do you reduce LLM API spend?**
- Increase Redis cache hit rate (popular queries)
- Batch requests (10 queries → 1 API call)
- Use cheaper model for low-complexity queries
- Limit retrieved context (top-3 docs instead of top-10)

**Q: How do you measure RAG quality?**
- Recall@k: Did relevant docs appear in top-k? (0-100%)
- Precision@k: Of top-k, how many are relevant?
- User feedback: Thumbs up/down after each answer
- Latency: P50, P95, P99 response times

---

## Key Takeaways

✅ **Scale horizontally:** Load balancer + N API servers
✅ **Cache aggressively:** Redis for embeddings + popular Q&As
✅ **Hybrid search:** Semantic + keyword, not just vectors
✅ **Metadata filtering:** Critical for multi-tenancy
✅ **Separate data stores:** Don't couple vector DB + keyword index
✅ **Monitor quality:** Track retrieval accuracy + latency
✅ **Graceful degradation:** Work without one component (e.g., vector DB down → keyword only)