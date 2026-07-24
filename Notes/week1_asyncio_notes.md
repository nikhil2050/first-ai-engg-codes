# Async I/O in Python - Interview-Ready Notes

## 1. Core Concepts & Theory

### Concurrency vs Parallelism (Common Interview Question ⭐)
**Interviewer might ask**: "Explain the difference between concurrency and parallelism"

- **Concurrency**: Multiple tasks *appear* to run simultaneously by context switching
  - Example: 1 chef making multiple dishes (switches between them)
  - Single CPU core, but looks like parallel execution
  - **Used by**: Threading, Async I/O

- **Parallelism**: Multiple tasks *actually* execute at the same time
  - Example: 4 chefs cooking 4 dishes simultaneously
  - Multiple CPU cores needed
  - **Used by**: Multiprocessing

- **Async I/O**: Single-threaded cooperative multitasking
  - Tasks voluntarily yield control (`await`) when blocking
  - No context switching overhead (unlike threading)
  - Only 1 core used, but very efficient for I/O

### Why Async I/O Over Threading? (Common Follow-up)
```
Threading issues:
- Thread overhead (memory, context switching)
- GIL (Global Interpreter Lock) limits Python threads
- Max ~1000-5000 concurrent threads
- Race conditions & deadlocks possible

Async I/O benefits:
- No thread overhead (10,000+ concurrent tasks possible)
- No GIL issues (single-threaded)
- Predictable execution (explicit await points)
- Lighter weight & faster
```

### When to Use What? (Interview Decision Tree)
```
Question: Is the task CPU-bound or I/O-bound?

├─ CPU-BOUND → Use Multiprocessing
│  (math calculations, data processing)
│
└─ I/O-BOUND
   ├─ Few concurrent tasks (< 100) → Threading is OK
   ├─ Many concurrent tasks (> 100) → Async I/O ✨
   └─ Need high throughput servers → Async I/O ✨
```

**Real-world examples**:
- ✅ **Async I/O**: Web scraper (1000s of URLs), chat server (1000s of users), microservice (concurrent API calls)
- ✅ **Threading**: Download manager (5-10 files), simple API wrapper
- ✅ **Multiprocessing**: Image processing, data science calculations, ML training

---

## 2. How Async I/O Actually Works (Interview Explanation)

### The Chess Master Analogy ♟️ (Great to mention!)
Imagine a chess master playing 24 opponents simultaneously:
- **Synchronous**: Play one opponent completely (30 mins), then next opponent (30 mins) = 12 hours total
- **Asynchronous**: Make a move on table 1 (5 sec), move to table 2 (5 sec), etc. While opponent 1 thinks, play others. After 24 moves, come back to opponent 1 = 1 hour total!

**How Async I/O mirrors this**:
```
Event Loop = Chess Master (one thread)
Coroutines = Tables/Opponents (tasks)
await = "I'm waiting, go help someone else"

When task says "await asyncio.sleep(5)", event loop switches to another task
After 5 seconds, comes back to first task
Result: All tasks make progress during wait time!
```

### Event Loop Under the Hood
```python
# Simplified event loop pseudocode:
while True:
    # 1. Check if any tasks are ready to run
    ready_tasks = [t for t in tasks if t.is_ready()]
    
    # 2. Run each task until it hits await
    for task in ready_tasks:
        result = task.send(None)  # Resume execution
        # Task hits await, pauses, returns control
    
    # 3. Sleep until next I/O event completes
    # (no CPU wasted spinning!)
    
    # 4. Repeat
```

### Key Difference: Blocking vs Non-Blocking
```python
# BLOCKING: Task holds entire thread
time.sleep(1)  # CPU wasted, other tasks CANNOT run
               # Event loop is stuck

# NON-BLOCKING: Task yields, tells when it'll be ready
await asyncio.sleep(1)  # Task returns, event loop continues
                        # Other tasks CAN run
                        # After 1s, task resumes
```

---

## 3. Basic Syntax

### Synchronous (Blocking) vs Async
```python
# SYNC - Takes 6+ seconds
import time
def count():
    print("One")
    time.sleep(1)  # BLOCKS everything
    print("Two")
    time.sleep(1)

def main():
    for _ in range(3):
        count()  # Runs 3x sequentially

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(f"Time: {time.perf_counter() - start:.2f}s")
```

```python
# ASYNC - Takes ~2 seconds (3x faster!)
import asyncio

async def count():  # async def = coroutine function
    print("One")
    await asyncio.sleep(1)  # Non-blocking wait
    print("Two")
    await asyncio.sleep(1)

async def main():
    # Run 3 coroutines concurrently
    await asyncio.gather(count(), count(), count())

if __name__ == "__main__":
    asyncio.run(main())  # Launch event loop
```

### Key Differences
- `time.sleep()` → blocks entire event loop ❌
- `asyncio.sleep()` → yields control, allows other tasks to run ✅
- `asyncio.run()` → starts event loop, runs coroutine, closes loop

---

## 4. Coroutines & Event Loop (Interview Deep Dive)

### "What is a Coroutine?" (Interview Question ⭐)
**Definition**: A function that can pause execution and resume later, yielding control to other coroutines.

```python
# Regular function: Runs start to finish, no pausing
def regular():
    x = 1
    y = 2
    return x + y

# Coroutine: Can PAUSE at await points
async def coro():
    x = 1
    y = await get_value()  # PAUSE here (blocking)
    return x + y            # RESUME here when get_value() done
```

**Key differences**:
- Regular function: Caller waits for complete execution
- Coroutine: Returns immediately, caller must `await` or schedule on event loop

### Coroutine Function vs Coroutine Object
```python
async def my_coro():
    await asyncio.sleep(1)
    return "done"

# Calling returns COROUTINE OBJECT, not result
coro = my_coro()
print(type(coro))  # <class 'coroutine'>

# Must run with event loop
result = asyncio.run(coro)  # Now it executes
```

**Interview explanation**: Calling `async def` function doesn't run it immediately like regular functions. It returns a coroutine object that's dormant. You need the event loop (via `asyncio.run()`) to actually execute it.

### What is "Awaitable"? (Follow-up Question)
An **awaitable** is any object that can be awaited (used with `await`). Includes:
1. Coroutines (from `async def`)
2. Tasks (wrapper around coroutines)
3. Futures (placeholder for result)
4. Any object implementing `__await__()` method

```python
# Awaitable examples:
await coroutine()           # ✅ Coroutine object
await asyncio.sleep(1)      # ✅ Builtin coroutine
await task                  # ✅ Task object
await future                # ✅ Future object

# NOT awaitable:
await regular_function()    # ❌ Returns int, not awaitable
await 5                     # ❌ Not awaitable
```

### Rules for `async` & `await` (Interview Checklist)
✅ CAN do:
- Use `await` inside `async def` function
- `await` another coroutine → pauses, resumes when result ready
- Use `return`, `yield` in `async def`

❌ CANNOT do:
- Use `await` outside `async def` → SyntaxError
- Use `yield from` in `async def` → SyntaxError
- Only `await` awaitable objects (coroutines, futures)

### Event Loop Fundamentals (Important for Interviews!)

**Q: "Explain what an event loop does?"**

An event loop is an infinite loop that:
1. Collects ready-to-run coroutines
2. Runs each until it hits `await` (pauses)
3. Checks for I/O completion
4. Resumes paused coroutines when their I/O is done
5. Repeats until all tasks complete

```python
# Simplified event loop flow:
while tasks_exist:
    # Find tasks ready to run
    ready = get_ready_tasks()
    
    for task in ready:
        try:
            task.send(None)  # Resume execution
        except StopIteration:
            tasks.remove(task)  # Task done
    
    # Wait for I/O events (non-blocking wait)
    # Don't waste CPU spinning!
    wait_for_io_completion()
```

**Multiple Event Loops?**
- Only 1 event loop per thread (typically)
- Can't call `asyncio.run()` twice (it closes the loop)
- To run async code in existing loop: use `asyncio.create_task()`

```python
# Get running loop (inside async context)
loop = asyncio.get_running_loop()

# Default implementations:
# - Unix: SelectorEventLoop (uses select())
# - Windows: ProactorEventLoop (better I/O)
# - Third-party: uvloop (faster C implementation)

# Key properties:
loop.is_running()  # Returns True if loop actively running
loop.is_closed()   # Returns True if loop shut down
```

**Interview tip**: Mention that asyncio.run() handles creating/closing the loop for you, so you rarely need to manage it manually.

---

## 5. Common Patterns & Real Scenarios

### Interview Question: "How would you fetch multiple users and their posts asynchronously?"

### Pattern 1: Coroutine Chaining (Sequential Dependencies)
```python
async def get_user_with_posts(user_id):
    user = await fetch_user(user_id)  # Wait for result
    await fetch_posts(user)             # Chain next operation

async def fetch_user(user_id):
    await asyncio.sleep(1)  # Simulate network call
    return {"id": user_id, "name": f"User{user_id}"}

async def fetch_posts(user):
    await asyncio.sleep(1)
    return [f"Post {i}" for i in range(3)]

async def main():
    await asyncio.gather(
        get_user_with_posts(1),
        get_user_with_posts(2),
        get_user_with_posts(3),
    )

# Result: 3 * 2 seconds = ~6s sequential → ~2s concurrent

# When to use: Task B depends on result from Task A
# Example: Get user ID → Fetch user → Fetch user's posts
```

**Interview explanation**: Use chaining when tasks have dependencies. Each coroutine waits for the previous one's result before proceeding.

### Pattern 2: Producer-Consumer with Queue (Independent Tasks)
```python
async def producer(queue, items):
    for item in items:
        await asyncio.sleep(0.5)
        await queue.put(item)
    
    # Signal consumers to stop
    for _ in range(3):  # 3 consumers
        await queue.put(None)  # Sentinel value

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Processing: {item}")
        await asyncio.sleep(1)

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(
        producer(queue, [1, 2, 3, 4, 5]),
        consumer(queue),
        consumer(queue),
        consumer(queue),
    )

asyncio.run(main())
```

**When to use**: Producer and consumers are independent. Decoupled communication via queue.
Example: Web scraper (producer) → multiple workers (consumers) processing URLs

**Interview tip**: Mention that queues ensure thread-safe communication without explicit locking.

**Why queues over chaining?**
```
Chaining:     A → B → C (sequential, strict order)
Queue:        Producer → [Queue] → Multiple Consumers (flexible, scalable)

Queue benefits:
- Producers and consumers don't know each other
- Easy to add more consumers without changing code
- Producers can produce faster/slower than consumers
- Natural for producer-consumer pattern
```

---

## 7. Advanced Features

### Async Iterators & For Loops
```python
async def powers_of_two(n):
    for i in range(n):
        yield 2 ** i
        await asyncio.sleep(0.2)

async def main():
    # Async for loop
    async for power in powers_of_two(5):
        print(power)  # 1, 2, 4, 8, 16
    
    # Async comprehension
    powers = [x async for x in powers_of_two(5) if x > 2]
```

### Async Context Managers (`async with`)
```python
import aiohttp

async def check_website(url):
    # Ensures proper resource cleanup (async)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"{url}: {response.status}")

async def main():
    urls = ["https://python.org", "https://github.com"]
    await asyncio.gather(
        *(check_website(url) for url in urls)
    )
```

### Task vs Coroutine (Interview Question ⭐)
**Q: "What's the difference between awaiting a coroutine and creating a task?"**

```python
async def my_work():
    await asyncio.sleep(1)
    return "done"

# Option 1: Await coroutine (blocks until done)
result = await my_work()  # Main task waits here

# Option 2: Create task (runs in background)
task = asyncio.create_task(my_work())  # Starts immediately
# Main continues, task runs in parallel
result = await task  # Wait for task later
```

**Difference**:
- `await coro()`: Runs immediately, caller waits
- `create_task(coro())`: Schedules to run, returns immediately

**When to use**:
- `await`: Simple dependency (need result before proceeding)
- `create_task()`: Need to run in parallel (fire-and-forget, then await later)

```python
# Real example: Download multiple files in parallel
async def download_files():
    # Create tasks for all downloads (start immediately)
    task1 = asyncio.create_task(download("file1.zip"))
    task2 = asyncio.create_task(download("file2.zip"))
    task3 = asyncio.create_task(download("file3.zip"))
    
    # Do other work while downloading
    print("Downloads started!")
    
    # Wait for all to complete
    results = await asyncio.gather(task1, task2, task3)
    return results
```

### Task Management
```python
async def coro(x):
    await asyncio.sleep(x)
    return x * 2

async def main():
    # Create task (runs in background)
    task = asyncio.create_task(coro(5))
    print(task.done())  # False initially
    
    # Wait for result
    result = await task
    print(task.done())  # True
    
    # Use gather() to wait for multiple
    results = await asyncio.gather(
        asyncio.create_task(coro(1)),
        asyncio.create_task(coro(2)),
        asyncio.create_task(coro(3)),
    )
    
    # as_completed() - process tasks as they finish (not in order)
    tasks = [asyncio.create_task(coro(x)) for x in [3, 1, 2]]
    for task in asyncio.as_completed(tasks):
        result = await task
        print(f"Done: {result}")  # First: 2, then: 6, then: 4 (completion order)

# gather() vs as_completed() - Interview comparison
```
**Interview explanation**:
- `gather()`: Waits for ALL tasks, returns results in ORIGINAL order
- `as_completed()`: Processes tasks as they COMPLETE, returns in completion order

**When to use**:
- `gather()`: Need all results together, order matters (e.g., 3 API calls returning list)
- `as_completed()`: Process results as they arrive, order doesn't matter (e.g., scraper processing URLs)
```

### Task Cancellation
```python
task = asyncio.create_task(long_running_task())
# ... later ...
task.cancel()  # Request cancellation

# Handle cancellation
try:
    await task
except asyncio.CancelledError:
    print("Task was cancelled")
    # Cleanup if needed
```
```

### Exception Handling (Python 3.11+)
```python
async def failing_coro():
    raise ValueError("Error!")

async def main():
    try:
        results = await asyncio.gather(
            failing_coro(),
            another_coro(),
            return_exceptions=True  # Don't raise, return exceptions
        )
        exceptions = [e for e in results if isinstance(e, Exception)]
        if exceptions:
            raise ExceptionGroup("Multiple errors", exceptions)
    except* ValueError as ve_group:
        print(f"Caught ValueError: {ve_group.exceptions}")
```

---

## 8. Common Interview Scenarios & Real Solutions

### Scenario 1: "Build an API that fetches data from 3 external APIs concurrently"
```python
import aiohttp

async def fetch_from_api(api_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            return await response.json()

async def get_all_data():
    urls = ["https://api1.com/data", "https://api2.com/data", "https://api3.com/data"]
    
    # Run all 3 requests concurrently
    results = await asyncio.gather(
        *(fetch_from_api(url) for url in urls)
    )
    return results  # [data1, data2, data3]

# Usage
data = asyncio.run(get_all_data())
```

**Interview talking points**:
- Use `gather()` when you need all results
- Use `aiohttp` (async HTTP client) instead of `requests` (blocking)
- This scales to 100s of APIs without thread overhead

### Scenario 2: "Process 1000 URLs with only 10 concurrent requests"
```python
async def process_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def limited_concurrency(urls, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_fetch(url):
        async with semaphore:
            return await process_url(url)
    
    tasks = [bounded_fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

# Run with 1000 URLs but max 10 concurrent
urls = [f"https://example.com/{i}" for i in range(1000)]
results = asyncio.run(limited_concurrency(urls, max_concurrent=10))
```

**Interview talking points**:
- Use `Semaphore` to limit concurrent tasks
- Prevents overwhelming servers or hitting rate limits
- Scales from 10 to 1000 concurrent tasks easily

### Scenario 3: "Chat server handling 1000s of concurrent connections"
```python
connected_clients = set()

async def handle_client(reader, writer):
    connected_clients.add(writer)
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            
            # Broadcast to all clients
            for client in connected_clients:
                if client != writer:
                    client.write(data)
                    await client.drain()
    finally:
        connected_clients.remove(writer)
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

# Run
asyncio.run(main())
```

**Interview talking points**:
- Each connected client runs `handle_client()` concurrently
- Can handle 1000s of concurrent clients without threads
- Threading would need 1000 threads = massive memory overhead

### Scenario 4: "Implement timeout for async operation"
```python
async def fetch_with_timeout(url, timeout=5):
    try:
        async with asyncio.timeout(timeout):  # Python 3.11+
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
    except asyncio.TimeoutError:
        print(f"Request timed out after {timeout}s")
        return None

# For older Python:
async def fetch_with_timeout_old(url, timeout=5):
    try:
        return await asyncio.wait_for(
            fetch_from_api(url),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return None
```

**Interview talking points**:
- Use `asyncio.timeout()` or `asyncio.wait_for()` for timeouts
- Important for preventing hanging requests
- Shows you think about robustness and error handling

---

## 10. Key Functions Reference

| Function | Purpose |
|----------|---------|
| `asyncio.run(coro)` | Start event loop, run coroutine, close loop |
| `asyncio.gather(*coros)` | Run multiple coroutines concurrently, wait all |
| `asyncio.create_task(coro)` | Schedule coroutine as Task, run in background |
| `asyncio.as_completed(tasks)` | Iterator yielding tasks as they complete |
| `asyncio.sleep(delay)` | Non-blocking sleep |
| `asyncio.Queue()` | Thread-safe queue for passing data |
| `asyncio.get_running_loop()` | Get current event loop |
| `task.done()` | Check if task finished |
| `await task.cancel()` | Cancel task |
| `asyncio.Semaphore(n)` | Limit concurrent tasks to n |
| `asyncio.wait_for(coro, timeout)` | Set timeout for operation |
| `asyncio.timeout(timeout)` | Context manager timeout (Python 3.11+) |

---

## 11. Quick Comparison: Threading vs Async I/O

| Aspect | Threading | Async I/O |
|--------|-----------|-----------|
| CPU cores | 1 (can multithread) | 1 (cooperative) |
| Complexity | Complex (race conditions, locks) | Simpler (no locks needed) |
| Scalability | ~1000s threads | 10,000s+ tasks |
| GIL Impact | Blocked by GIL | No GIL issues |
| Best for | I/O with limited tasks | High concurrency I/O |
| Learning curve | Moderate | Steep (new paradigm) |

---

## 12. Real-World Libraries Using asyncio

- **Web**: FastAPI, Starlette, Sanic, Quart, Tornado
- **HTTP**: aiohttp, HTTPX
- **Database**: Databases, Tortoise ORM, Motor (MongoDB)
- **Utils**: aiofiles, aiocache, APScheduler
- **Testing**: pytest-asyncio

---

## 13. Common Pitfalls & How to Avoid Them ⚠️ (Interview Red Flags)

1. **Using `time.sleep()` in async code** → Blocks entire loop ❌
   ```python
   async def bad():
       time.sleep(1)  # WRONG! Stops all tasks
   
   async def good():
       await asyncio.sleep(1)  # Correct
   ```

2. **Forgetting to `await`** → Coroutine never runs
   ```python
   async def coro():
       return "result"
   
   await coro()   # ✅ Runs
   coro()         # ❌ Returns coroutine object, doesn't run
   ```

3. **Mixing sync and async** → Need async wrapper library
   ```python
   # Can't directly use sync DB driver in async code
   # Solution: Use async-compatible library (Motor, Tortoise ORM, etc.)
   ```

4. **Tasks not awaited** → Cancelled when loop closes
   ```python
   async def main():
       task = asyncio.create_task(coro())
       # If main() ends before awaiting task, it gets cancelled
       return await task  # ✅ Must wait for it
   ```

---

## 14. Learning Path & Interview Preparation

1. **Basics**: async/await, sleep, gather
2. **Patterns**: Chaining, queues
3. **Real I/O**: aiohttp, aiofiles
4. **Advanced**: Custom event loops, exception groups
5. **Integration**: FastAPI, databases

**Mindset**: Think of `await` as "pause here, let others run" not "wait for this to finish"

---

## 15. Common Interview Questions & Answers

### Q1: "Explain async/await in simple terms"
**Good Answer**:
"Async/await allows one thread to manage multiple I/O operations efficiently. When a coroutine hits `await`, it pauses and yields control to the event loop. The event loop then runs other waiting coroutines. When the I/O completes, the loop resumes the paused coroutine. This way, thousands of I/O tasks can be handled by a single thread without thread overhead."

**Better**: Give the chess master example!

### Q2: "Why can't you use `time.sleep()` in async code?"
**Good Answer**:
"`time.sleep()` is blocking. It pauses the entire thread for the specified duration. In async code, blocking the thread means ALL tasks pause, not just the current one. Use `asyncio.sleep()` instead, which is non-blocking and allows other tasks to run."

### Q3: "What's the difference between `await` and `create_task()`?"
**Good Answer**:
"`await coroutine()` runs the coroutine immediately and pauses the caller until it completes. `create_task()` schedules the coroutine to run in the background and returns immediately. Use `await` for dependencies, `create_task()` for parallel work."

### Q4: "How would you handle errors in async code?"
**Good Answer**:
"Wrap `gather()` calls in try-except. Use `return_exceptions=True` to collect exceptions without stopping other tasks. For multiple exception types, use ExceptionGroup (Python 3.11+) with `except*` syntax for granular handling."

### Q5: "When would you use asyncio.Semaphore()?"
**Good Answer**:
"When you have many tasks but want to limit concurrency. For example, 1000 API requests but only 10 at a time to avoid overloading the server. Semaphore acts as a gate that only allows N tasks to proceed simultaneously."

### Q6: "Can you run multiple event loops?"
**Good Answer**:
"No, you can only have one event loop per thread. `asyncio.run()` creates, runs, and closes the loop. You can't call it twice. If you need to run async code while a loop is already running, use `create_task()` instead."

### Q7: "How is async I/O different from threading?"
**Good Answer**:
"Threading uses OS-level threads with context switching (expensive). Async uses cooperative multitasking with explicit `await` points (cheap). Async scales to 10,000+ concurrent tasks. Threading maxes out around 1000 threads before memory/performance issues."

### Q8: "Explain `gather()` vs `as_completed()`"
**Good Answer**:
"`gather()` waits for all tasks and returns results in original order. `as_completed()` processes tasks as they finish and returns them in completion order. Use `gather()` when order matters, `as_completed()` when you want to process results immediately."

---

## Quick Reference: Execution Timeline

```
SYNC (6 seconds):
task1: [======]
task2:        [======]
task3:               [======]

ASYNC (2 seconds):
task1: [==]           [==]
task2:     [==]       [==]
task3:         [==]   [==]
       ↑ Everyone runs in gaps
```

When `await asyncio.sleep(1)` hits → control returns to event loop → other tasks run
→ 1 second elapses for ALL tasks simultaneously → control returns to each task

---

## 16. Interview Checklist: What You Should Know

Before the interview, make sure you can explain/code:

### Must Know ⭐⭐⭐
- [ ] Async/await syntax (`async def`, `await`, `return`)
- [ ] `asyncio.run()` - entry point
- [ ] `asyncio.gather()` - run multiple tasks
- [ ] `asyncio.create_task()` - schedule background task
- [ ] Difference between `await coro()` and `create_task(coro())`
- [ ] Event loop basics - what it does
- [ ] Why `time.sleep()` is bad in async code
- [ ] Concurrency vs Parallelism

### Should Know ⭐⭐
- [ ] Coroutine chaining (dependencies)
- [ ] `asyncio.Queue` - producer-consumer
- [ ] `asyncio.Semaphore` - limit concurrency
- [ ] `asyncio.as_completed()` - process as they finish
- [ ] Timeout handling (`wait_for`, `asyncio.timeout`)
- [ ] Exception handling in async code
- [ ] Task cancellation (`task.cancel()`)

### Nice to Know ⭐
- [ ] Async context managers (`async with`)
- [ ] Async iterators (`async for`)
- [ ] ExceptionGroup (Python 3.11+)
- [ ] Different event loop implementations
- [ ] Third-party libraries (FastAPI, aiohttp, etc.)

### Red Flags to Avoid ❌
- [ ] Using `time.sleep()` in async code
- [ ] Forgetting to `await` a coroutine
- [ ] Creating tasks and not awaiting them
- [ ] Mixing sync and async without adapters
- [ ] Not handling timeouts
- [ ] Not understanding when to use async vs threading

---

## 17. Final Tips for Interview Success

1. **Start with fundamentals**: Be able to explain async/await simply
2. **Use analogies**: Chess master, chef examples make concepts stick
3. **Give code examples**: Show you can code, not just explain
4. **Discuss trade-offs**: When to use async vs threading vs multiprocessing
5. **Think about scale**: How would this work with 10,000 users?
6. **Mention real libraries**: FastAPI, aiohttp, asyncpg (PostgreSQL), Motor (MongoDB)
7. **Ask clarifying questions**: "What's the scale? What's the latency requirement?"
8. **Discuss error handling**: Show you think about robustness
9. **Mention testing**: How would you test async code? (pytest-asyncio)
10. **Be honest**: If you don't know, say "I haven't used that, but here's how I'd learn"

---

## Practice Problem
**Interview question**: "Design a web scraper that fetches data from 100 URLs, but with max 10 concurrent requests, 5-second timeout per request, and proper error handling."

Try coding this before your interview! Use:
- `aiohttp.ClientSession` for HTTP
- `asyncio.Semaphore` for rate limiting
- `asyncio.timeout()` or `wait_for()` for timeout
- Try-except for error handling
- `asyncio.gather()` to run all with `return_exceptions=True`
