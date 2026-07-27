# FastAPI REST APIs - Handwritten Interview Notes
## AI Backend Engineering Module 2a

---

## 1. FastAPI FUNDAMENTALS

### 1.1 What is FastAPI? ⭐

**FastAPI** = Modern Python web framework for building APIs
- Built on **Starlette** (web) + **Pydantic** (validation)
- Async-first (uses async/await natively)
- Auto-documentation (Swagger UI, ReDoc)
- Type hints for validation
- Lightning fast (comparable to Node.js)

### 1.2 FastAPI vs Flask vs Django

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| **Speed** | Ultra-fast ⚡ | Moderate | Moderate |
| **Async** | Native ✅ | Limited | Limited |
| **Validation** | Automatic (Pydantic) | Manual | Built-in but heavy |
| **Docs** | Auto (Swagger) | Manual setup | Manual setup |
| **Learning curve** | Easy | Very easy | Steep |
| **Production ready** | ✅ Yes | ✅ Yes | ✅ Yes (overkill) |
| **Best for** | APIs, microservices | Simple apps | Full-stack apps |

**Interview line**: "FastAPI is built for modern async Python with automatic validation and docs—perfect for microservices and AI backends."

### 1.3 Why Use FastAPI for AI Backends?

✅ **Async I/O** → Handle 1000s of concurrent API calls  
✅ **Type safety** → Pydantic catches bad data early  
✅ **Auto-docs** → Swagger UI out of the box  
✅ **Speed** → Fast JSON serialization (crucial for ML models)  
✅ **Validation** → Request/response validation built-in  
✅ **Testing** → Easy to test (same async support)  

---

## 2. ASYNC/AWAIT IN FASTAPI

### 2.1 Synchronous vs Asynchronous Routes

```python
# SYNC - Blocks thread
@app.get("/sync")
def sync_endpoint():
    time.sleep(2)  # Blocks!
    return {"status": "done"}

# ASYNC - Non-blocking
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(2)  # Doesn't block!
    return {"status": "done"}
```

**Key difference**: 
- Sync blocks the thread → Can handle ~10-100 concurrent requests
- Async yields control → Can handle 1000s of concurrent requests

### 2.2 When to Use Async

✅ **Use async when**:
- Waiting for I/O (database, API calls, file operations)
- Handling many concurrent users
- ML inference (often I/O bound)

❌ **Don't need async for**:
- CPU-bound operations (pure computation)
- Quick operations (just return cached data)

```python
# ✅ Good async use cases
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.query(f"SELECT * FROM users WHERE id = {user_id}")
    return user

# ❌ CPU-bound (doesn't benefit from async)
@app.post("/predict")
async def predict(data: InputData):
    result = ml_model.predict(data.values)  # CPU-bound
    return {"prediction": result}
    # Note: Still async for concurrency, but computation is bottleneck
```

### 2.3 Async Database Operations

```python
# Pattern: Use async database drivers
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# SQLAlchemy Async
async def get_user(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# Or use httpx for async API calls
import httpx

@app.get("/fetch-data")
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
```

**Memory trick**: "Async = waiting without blocking. Use `await` whenever you're waiting for I/O."

---

## 3. PYDANTIC MODELS (Validation Superpower!)

### 3.1 What is Pydantic?

**Pydantic** = Library that validates data types & converts JSON → Python objects

```python
from pydantic import BaseModel, Field, validator

# Define schema
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = Field(gt=0, lt=150)  # age > 0 and < 150
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# Automatic validation
user = User(id=1, name="Alice", email="alice@example.com", age=25)
# ✅ Works

user = User(id=1, name="Alice", email="alice", age=25)
# ❌ ValidationError: email must contain @

user = User(id=1, name="Alice", email="alice@example.com", age=200)
# ❌ ValidationError: age must be < 150
```

### 3.2 Common Pydantic Field Constraints

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class Product(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)  # price > 0
    description: Optional[str] = None  # Can be null
    tags: List[str] = []  # Default empty list
    url: HttpUrl  # Validates URL format
    quantity: int = Field(default=0, ge=0)  # >= 0
```

### 3.3 Request & Response Models

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# REQUEST model
class CreateUserRequest(BaseModel):
    name: str
    email: str
    age: int

# RESPONSE model
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True  # SQLAlchemy compatibility

@app.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    # user is already validated!
    db_user = await db.create_user(user.name, user.email, user.age)
    return db_user  # FastAPI converts to UserResponse
```

**Interview tip**: "Pydantic gives you automatic validation + type checking + API documentation."

---

## 4. PATH, QUERY, BODY PARAMETERS

### 4.1 Path Parameters (`:id` in URL)

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):  # Type hint = validation
    return {"user_id": user_id}

# GET /users/123 → user_id = 123 (int)
# GET /users/abc → ❌ ValidationError (not an int)
```

**Rules**:
- Part of URL path
- Required always
- Type-validated by FastAPI

### 4.2 Query Parameters (?key=value in URL)

```python
@app.get("/users")
async def list_users(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# GET /users?skip=20&limit=5 → skip=20, limit=5
# GET /users → skip=0, limit=10 (defaults)

# Optional query parameter
@app.get("/search")
async def search(q: str = None):  # or Optional[str]
    if q:
        return {"query": q}
    return {"message": "No query"}

# GET /search → q=None
# GET /search?q=hello → q="hello"
```

### 4.3 Request Body (POST data)

```python
class Item(BaseModel):
    name: str
    price: float
    description: str = None

@app.post("/items")
async def create_item(item: Item):  # Auto-validated from request JSON
    return item

# POST /items
# Body: {"name": "Laptop", "price": 999.99}
# → item is Item object with all fields validated
```

### 4.4 Combining All Three

```python
class UpdateRequest(BaseModel):
    name: str
    price: float

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,  # Path parameter
    item: UpdateRequest,  # Body
    include_tax: bool = False  # Query parameter
):
    return {
        "item_id": item_id,
        "item": item,
        "include_tax": include_tax
    }

# PUT /items/5?include_tax=true
# Body: {"name": "Updated", "price": 100}
```

**Memory trick**: "PATH is part of URL, QUERY is ?after, BODY is the JSON."

---

## 5. STATUS CODES & ERROR HANDLING

### 5.1 Common HTTP Status Codes

```
2xx - Success
├─ 200 OK           → Request successful
├─ 201 Created      → Resource created
├─ 204 No Content   → Success, no response body

4xx - Client Error
├─ 400 Bad Request      → Invalid data
├─ 401 Unauthorized     → Need auth
├─ 403 Forbidden        → Auth failed
├─ 404 Not Found        → Resource doesn't exist

5xx - Server Error
├─ 500 Internal Server Error → Code crashed
├─ 503 Service Unavailable   → Server overloaded
```

### 5.2 Setting Status Codes

```python
from fastapi import FastAPI, status

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item  # Returns 201 instead of 200

# Explicit status code
from fastapi.responses import JSONResponse

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if not found:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Item not found"}
        )
    return item
```

### 5.3 HTTPException (Proper Error Handling)

```python
from fastapi import HTTPException, status

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.post("/login")
async def login(credentials: Credentials):
    if not verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"access_token": token}
```

### 5.4 Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# Usage
@app.get("/risky")
async def risky_operation():
    if something_wrong:
        raise CustomException("Something went wrong!", 400)
    return {"status": "ok"}
```

---

## 6. PRODUCTION API PATTERNS

### 6.1 API Request Lifecycle

```
1. Request arrives
   ↓
2. FastAPI parses path/query/body
   ↓
3. Pydantic validates (raises 422 if invalid)
   ↓
4. Route handler executes
   ↓
5. Handler returns data
   ↓
6. FastAPI serializes to JSON
   ↓
7. Response sent to client
```

### 6.2 Error Handling Strategy (Production)

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)

class CreateUserRequest(BaseModel):
    name: str
    email: str
    age: int
    
    @validator('age')
    def age_valid(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be 0-150')
        return v

@app.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    try:
        # Validation already done by Pydantic ✅
        
        # Check business logic
        existing = await db.get_user_by_email(user.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create in database
        db_user = await db.create_user(
            name=user.name,
            email=user.email,
            age=user.age
        )
        logger.info(f"User created: {db_user.id}")
        return db_user
        
    except HTTPException:
        raise  # Re-raise HTTP errors
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
```

### 6.3 Logging Setup (Production)

```python
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# File handler for production
file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
logger.addHandler(file_handler)

# Structured logging
class LogEntry:
    def __init__(self, event: str, **kwargs):
        self.data = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **kwargs
        }
    
    def log(self):
        logger.info(json.dumps(self.data))

# Usage
LogEntry("user_created", user_id=123, email="alice@example.com").log()
# Output: {"timestamp": "2024-01-15T10:30:45", "event": "user_created", ...}
```

### 6.4 Response Models & Schemas

```python
from pydantic import BaseModel
from typing import List, Optional

# Nested models
class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address
    
    class Config:
        from_attributes = True  # SQLAlchemy ORM

class UserListResponse(BaseModel):
    total: int
    users: List[User]

@app.get("/users", response_model=UserListResponse)
async def list_users():
    users = await db.get_all_users()
    return UserListResponse(total=len(users), users=users)
```

---

## 7. HELLO WORLD FASTAPI APP

### 7.1 Minimal App

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Backend API", version="1.0.0")

# Models
class PredictionRequest(BaseModel):
    text: str
    
class PredictionResponse(BaseModel):
    text: str
    prediction: str
    confidence: float

# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(req: PredictionRequest):
    # Placeholder ML inference
    return PredictionResponse(
        text=req.text,
        prediction="positive",
        confidence=0.95
    )

# Run: uvicorn main:app --reload
```

### 7.2 With Logging & Error Handling

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class Item(BaseModel):
    name: str
    price: float

# Simulated database
db = {}
item_id_counter = 0

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    logger.info(f"Getting item {item_id}")
    
    if item_id not in db:
        logger.warning(f"Item {item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return db[item_id]

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    global item_id_counter
    
    try:
        item_id_counter += 1
        db[item_id_counter] = item
        logger.info(f"Item created: {item_id_counter}")
        return {"id": item_id_counter, **item.dict()}
    except Exception as e:
        logger.error(f"Failed to create item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create item"
        )

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    del db[item_id]
    logger.info(f"Item deleted: {item_id}")
    return {"detail": "Item deleted"}
```

---

## 8. ENVIRONMENT VARIABLES & CONFIG

### 8.1 .env File Setup

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
API_KEY=secret_key_123
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 8.2 Loading Environment Variables

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    api_key: str
    log_level: str = "INFO"
    environment: str = "development"
    
    class Config:
        env_file = ".env"

# Singleton pattern
@lru_cache
def get_settings():
    return Settings()

# Usage
@app.get("/config")
async def get_config():
    settings = get_settings()
    return {"environment": settings.environment}
```

---

## 9. TESTING REST ENDPOINTS

### 9.1 Using curl (Quick Manual Testing)

```bash
# GET request
curl http://localhost:8000/users/123

# POST with JSON
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":999.99}'

# With query parameters
curl "http://localhost:8000/items?skip=0&limit=10"

# With headers
curl http://localhost:8000/protected \
  -H "Authorization: Bearer token123"
```

### 9.2 Testing with pytest

```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_item():
    response = client.post(
        "/items",
        json={"name": "Laptop", "price": 999.99}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Laptop"

def test_item_not_found():
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_invalid_data():
    response = client.post(
        "/items",
        json={"name": "Laptop"}  # Missing price
    )
    assert response.status_code == 422  # Validation error

# Run: pytest test_main.py
```

---

## 10. DOCKER & DEPLOYMENT

### 10.1 Dockerfile for FastAPI

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
```

### 10.2 requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
httpx==0.25.2
pytest==7.4.3
gunicorn==21.2.0
```

### 10.3 Docker Compose (with PostgreSQL)

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/apidb
    depends_on:
      - db
  
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: apidb
    ports:
      - "5432:5432"
```

### 10.4 Deploy to Free Tier Services

**Railway** (Best for FastAPI):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Init project
railway init

# Deploy
railway up
```

**Render**:
- Connect GitHub repo
- Auto-deploys on push
- Free tier: 0.5GB RAM, 100GB/month bandwidth

**Vercel** (Serverless):
- Not ideal for FastAPI (limited function runtime)
- Use Railway or Render instead

---

## 11. INTERVIEW Q&A

### Q1: "Explain the difference between FastAPI and Flask"

**A**: 
- **FastAPI** = Async-first, auto-validation, auto-docs
- **Flask** = Minimal, synchronous, flexible
- FastAPI is faster, has type hints + Pydantic validation, generates Swagger docs automatically
- Use FastAPI for modern APIs/microservices, Flask for simple apps or learning
- **Interview line**: "FastAPI is built for production APIs with async support, automatic validation, and zero-config documentation."

### Q2: "How do you handle validation in FastAPI?"

**A**:
```python
from pydantic import BaseModel, Field, validator

class User(BaseModel):
    email: str  # Type hint = validation
    age: int = Field(gt=0, lt=150)  # Constraints
    
    @validator('email')
    def email_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# FastAPI automatically validates request JSON against schema
# Returns 422 if validation fails
```
**Key point**: "Pydantic validates automatically—bad data returns 422 before your code runs."

### Q3: "Path vs Query parameters?"

**A**:
- **Path** (`/users/{id}`) = Part of URL, always required
- **Query** (`?skip=0&limit=10`) = After `?`, optional with defaults

```python
@app.get("/users/{user_id}")  # Path
async def get_user(
    user_id: int,  # Required
    skip: int = 0  # Query, optional
):
    pass
```

### Q4: "How do you structure error handling in production?"

**A**:
1. Pydantic validates automatically (422)
2. Business logic checks → HTTPException (400/409)
3. Try-catch for unexpected errors → 500
4. Always log errors with context
5. Never expose stack traces to client

```python
try:
    # validation already done ✓
    if resource_not_found:
        raise HTTPException(404, "Not found")
    result = await db.operation()
    logger.info("Success")
    return result
except HTTPException:
    raise  # Re-raise
except Exception as e:
    logger.error(f"Unexpected: {e}")
    raise HTTPException(500, "Internal error")
```

### Q5: "Walk me through building a REST API from scratch"

**A**:
1. **Setup**: `pip install fastapi uvicorn pydantic`
2. **Models**: Define Pydantic request/response models
3. **Routes**: Create @app.get/@app.post handlers
4. **Validation**: Type hints + Pydantic models (auto)
5. **Errors**: Use HTTPException for known errors
6. **Logging**: Add logger for debugging
7. **Testing**: pytest with TestClient
8. **Deploy**: Docker + Railway/Render

```python
# Complete minimal example
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
async def create(item: Item):
    if item.price < 0:
        raise HTTPException(400, "Price must be positive")
    return {"id": 1, **item.dict()}

# Run: uvicorn main:app --reload
```

### Q6: "How would you deploy a FastAPI app?"

**A**:
1. **Build Docker image**: `docker build -t myapp .`
2. **Test locally**: `docker run -p 8000:8000 myapp`
3. **Push to registry**: DockerHub, GitHub Container Registry
4. **Deploy**: 
   - Railway (easiest): `railway up`
   - Render: Connect GitHub, auto-deploy
   - AWS/GCP: ECS/Cloud Run
5. **Monitor**: CloudWatch, Sentry for errors

**Quick wins**:
- Use environment variables for secrets
- Set proper log levels
- Add health check endpoint
- Use gunicorn + uvicorn workers

---

## 12. PRODUCTION CHECKLIST ✅

### Before Shipping to Production

```
□ Validation
  └─ Pydantic models for all inputs
  └─ Custom validators for business logic

□ Error Handling
  └─ HTTPException for known errors
  └─ Try-catch for unexpected errors
  └─ All errors logged

□ Logging
  └─ INFO for normal operations
  └─ ERROR for failures
  └─ Structured logging (JSON format)

□ Testing
  └─ pytest for all routes
  └─ Test happy path + error cases
  └─ Coverage > 80%

□ Performance
  └─ Use async for I/O operations
  └─ Connection pooling for databases
  └─ Response caching where applicable

□ Security
  └─ Secrets in .env (never in code)
  └─ CORS configured
  └─ Rate limiting if needed
  └─ Input sanitization

□ Deployment
  └─ Docker image tested
  └─ Environment variables configured
  └─ Health check endpoint
  └─ Monitoring set up
```

---

## 13. QUICK CODE PATTERNS

### Pattern 1: CRUD API

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()
db = {}  # Simulated

class Item(BaseModel):
    name: str
    price: float

# CREATE
@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create(item: Item):
    item_id = len(db) + 1
    db[item_id] = item
    return {"id": item_id, **item.dict()}

# READ
@app.get("/items/{item_id}")
async def read(item_id: int):
    if item_id not in db:
        raise HTTPException(404, "Not found")
    return {"id": item_id, **db[item_id].dict()}

# UPDATE
@app.put("/items/{item_id}")
async def update(item_id: int, item: Item):
    if item_id not in db:
        raise HTTPException(404, "Not found")
    db[item_id] = item
    return {"id": item_id, **item.dict()}

# DELETE
@app.delete("/items/{item_id}")
async def delete(item_id: int):
    if item_id not in db:
        raise HTTPException(404, "Not found")
    del db[item_id]
    return {"message": "Deleted"}
```

### Pattern 2: Async Database Queries

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, name: str, email: str):
    user = User(name=name, email=email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@app.get("/users/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

### Pattern 3: Middleware for Logging

```python
from fastapi import Request
import logging
import time

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} "
        f"- {process_time:.2f}s"
    )
    
    return response
```

---

## 14. MEMORY TRICKS & KEYWORDS ⭐

**FAST API** = **F**ast, **A**sync, **S**imple, **T**ype-safe API

**FAT** = **F**rame, **A**ync, **T**ypes (Pydantic)

**Validation happens in order**:
1. Path parameters validated
2. Query parameters validated
3. Body validated by Pydantic
4. Handler executes
5. Response validated
6. JSON returned

**Status codes**:
- 2xx = Good ✅
- 4xx = Your fault ❌
- 5xx = Server's fault 💣

**Error handling priority**:
1. Pydantic validation (automatic)
2. Business logic checks
3. Unexpected errors
4. Log everything

**Async when**:
- ✅ Waiting for I/O (database, API, file)
- ❌ Pure computation
- ✅ Handling many users
- ❌ Quick in-memory operations

---

## 15. RESOURCES & NEXT STEPS

### Must-Know Commands

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install
pip install fastapi uvicorn[standard] pydantic

# Run dev server
uvicorn main:app --reload

# Run production (4 workers)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Test
pytest test_main.py -v

# Docker
docker build -t myapi .
docker run -p 8000:8000 myapi
```

### Study Plan

**Week 1**: Basics
- [ ] Hello World FastAPI
- [ ] Path/Query/Body parameters
- [ ] Pydantic models
- [ ] Status codes & HTTPException

**Week 2**: Production
- [ ] Async database patterns
- [ ] Logging setup
- [ ] Error handling strategies
- [ ] Testing with pytest

**Week 3**: Deployment
- [ ] Docker & docker-compose
- [ ] Environment variables
- [ ] Railway/Render deployment
- [ ] Monitoring & logs

**Week 4**: Projects
- [ ] Build AI inference API
- [ ] Connect to database
- [ ] Add authentication (JWT)
- [ ] Deploy to production

---

**Interview Confidence**: After mastering this, you should be able to:
✅ Explain FastAPI advantages  
✅ Build a complete REST API  
✅ Handle errors properly  
✅ Write async code  
✅ Deploy to production  
✅ Answer technical questions  

**Good luck! 🚀**
