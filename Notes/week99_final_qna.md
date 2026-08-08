# RAG:

## Basic

### Q. What is re-ranking and why is it important? ✅

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

### Q: "Compare different re-ranking strategies"

**A**: 

| Strategy | Speed | Accuracy | Cost | When to Use |
|----------|-------|----------|------|-------------|
| **Fusion** | ⭐⭐⭐ | ⭐⭐ | Free | Fast API |
| **Cross-Encoder** | ⭐⭐ | ⭐⭐⭐ | $$ | Production search |
| **LLM Judge** | ⭐ | ⭐⭐⭐⭐ | $$$ | High value queries |

**Recommendation**: Start with fusion, move to cross-encoder if metrics decline.

---
## Debugging

### Q. What would you do if retrieval doesn't find the right documents? (Intermediate)

Diagnosis first: Is it a retrieval or generation issue?

Retrieval debugging:

1. Check embeddings
- Embed your query, manually inspect top-5 retrieved chunks
- Are they actually relevant? If no → embedding model issue

2. Experiment with chunk size
- If chunks are too large (1500+ tokens) → try 512
- If too small (50 tokens) → try 256 or 512

3. Try a different embedding model
- Swap to a stronger model (text-embedding-3-large, BAAI/bge-large)
- Domain-specific models: e.g., sciBERT for scientific papers

4. Add re-ranking
- Run Flashrank or cross-encoder to filter noise

5. Hybrid search
- Add BM25 keyword search to catch exact-match queries

6. Metadata pre-filtering
- If docs have categories/tags, narrow search space first

### Q. Your RAG system is producing hallucinations. How do you fix it? (Intermediate)

Root causes: Retrieval isn't returning relevant docs, or LLM is adding info not in context.

Fixes (in order of impact):

1. Constrain the prompt
- "Only answer using the provided documents. If the answer is not in the documents, say 'I cannot answer this based on available information.'"
- This is often 50% of the win

2. Improve retrieval
- Better embedding model
- Increase top-k from 3 to 5 (more context)
- Add re-ranking

3. Use a less capable model
- Smaller models (Llama-2, Mistral) hallucinate less than GPT-4
- Trade accuracy for reliability

4. Add citations
- Prompt LLM to cite sources: "Answer with [source: doc_name]"
- Makes hallucinations obvious (no source to cite)

5. Reduce context length
- Too much context confuses models; try top-3 instead of top-10

Measure: Build a test set of 50 Q&As, manually score hallucinations, then track improvement.

---

## Architecture & Implementation

### Q. How do you handle multi-tenant RAG applications? (Advanced)

Challenge: Prevent tenant A's documents from being retrieved for tenant B's queries.

Solutions:

1. Metadata filtering (Recommended)
- Store tenant_id in vector DB metadata
- Add metadata filter at retrieval time: {"tenant_id": "user123"}
- Requires DB support: Qdrant, Milvus, Weaviate (support filters)
- Fastest, cleanest approach

2. Separate namespaces/indices
- Pinecone: Use separate indices per tenant
- Elasticsearch: Separate indices per tenant
- Higher operational overhead, strong isolation

3. Post-retrieval filtering
- Retrieve all results, filter in application code
- Inefficient, security risk (data could leak in logs)

Best practice: Use metadata filtering with a vector DB that supports it (Qdrant, Milvus).

### Q. How do you update embeddings when source documents change? (Advanced)

Challenge: Documents are dynamic. Updating millions of embeddings is expensive.

Strategies:

1. Re-index on schedule
- Run daily/weekly batch job to re-process all docs
- Simple, predictable, but slow for large corpora

2. Incremental updates
- Track which docs changed (timestamps, change logs)
- Re-embed only changed documents
- Delete old embeddings, insert new ones

3. Event-driven indexing
- Listen to doc update events (webhook, Kafka, webhooks)
- Immediately re-embed and update DB
- Near-real-time, but complex

4. Hybrid TTL + versioning
- Store doc version in metadata
- Query filters out stale versions
- Clean up old versions in background

Practical choice: Start with incremental updates; graduate to event-driven if latency matters.

---

## Evaluation & Optimization

### Q. How do you evaluate RAG quality? (Advanced)

Key metrics:

1. Retrieval Metrics
- Recall@k: Did relevant docs appear in top-k? (0–100%)
- Precision@k: Of top-k retrieved, how many are relevant?
- MRR (Mean Reciprocal Rank): Position of first relevant result

2. Generation Metrics
- BLEU/ROUGE: Text similarity to reference answers (limited)
- Semantic similarity: Embedding similarity to gold answer
- Human evaluation: Accuracy, hallucination, relevance (best)

3. End-to-End Metrics
- User satisfaction: Did user accept the answer? (thumbs up/down)
- Task success rate: Did the answer solve the user's problem?

**Practical approach**: Build a small test set (50–100 Q&A pairs). Score retrieval and generation separately. Iterate.

### Q. What common RAG failure modes do you know? (Advanced)

1. Retrieval Failures
- Missing relevant docs: Embedding model can't capture intent (wrong model, poor chunk size)
- Retrieved garbage: Low-quality or outdated documents in index
- Fix: Use better embedding models, re-evaluate chunk size, add quality filters

2. Generation Failures
- Hallucination: LLM invents info not in retrieved docs
- Context overload: Too much context confuses the model
- Fix: Use prompt engineering ("Only answer from provided context"), reduce retrieved chunks

3. Ranking Issues
- Top-k doesn't contain best answer: Retrieval score doesn't match relevance
- Fix: Add re-ranking, improve embedding model

4. Latency/Cost
- Expensive embeddings: Too many API calls
- Slow retrieval: Vector DB query slow
- Fix: Cache embeddings, optimize DB indexes, use cheaper models

### Q. How would you optimize a RAG system for latency? (Advanced)

Latency culprits: Embedding calculation, vector DB query, LLM generation

Optimizations:

1. Embedding Layer
- Cache embeddings for frequent queries
- Use faster embedding models (all-MiniLM-L6 vs GPT-4 embed)
- Batch embedding calls

2. Vector DB Layer
- Use approximate nearest neighbor (ANN) search (fast, ~95% accuracy)
- Index tuning: Qdrant HNSW parameters, Milvus IVF tuning
- Pre-filter by metadata (reduces search space)

3. Generation Layer
- Use faster LLM (Grok, Llama vs GPT-4)
- Limit retrieved chunks (top-3 instead of top-10)
- Streaming responses (show first token quickly)

4. Caching
- Cache query embeddings (popular queries)
- Cache frequently asked Q&A pairs
- Redis/Memcached layer

Benchmark order: Measure first! Profile which component is slow before optimizing.

---

## System Design

### Q. Design a RAG system for a customer support chatbot at scale. (Hard)

Architecture outline:

Data Ingestion:
- Source: Confluence docs, help center articles, FAQs
- Process: PDFLoader/DocumentLoader → RecursiveCharacterTextSplitter (512 tokens, 50 overlap)
- Embed: Batch with text-embedding-3-small (OpenAI) or open-source alternative
- Store: Qdrant (production) or Milvus (self-hosted)

Query/Retrieval:
- Embed user query with same model
- Hybrid search: BM25 (keywords) + semantic (vector)
- Metadata filter by product/category
- Top-5 retrieval + re-rank with cross-encoder

Generation:
- Prompt: System prompt + retrieved chunks + user query
- Model: GPT-4 (quality) or open-source (cost)
- Constraint: "If not in docs, say 'I don't have that info'"

Multi-tenancy:
- Each tenant gets isolated namespace in vector DB
- Metadata filter: {tenant_id, product_id}
- Separate LLM context per tenant (system prompts)

Monitoring/Optimization:
- Track retrieval → generation quality (thumbs up/down)
- Identify retrieval failures → re-train embedding model or adjust chunks
- Cache popular queries to reduce latency

---
