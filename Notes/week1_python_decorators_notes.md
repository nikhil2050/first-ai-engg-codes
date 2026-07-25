# Python Decorators - Interview-Ready Notes

## 1. What is a Decorator? (Common Interview Question ⭐)

**Simple Answer**: A decorator is a function that takes another function as input, wraps it with additional functionality, and returns the modified function.

**How it works**:
```python
def decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@decorator  # Same as: say_hi = decorator(say_hi)
def say_hi():
    print("Hello!")

say_hi()
# Output:
# Before
# Hello!
# After
```

**Key insight**: `@decorator` is syntactic sugar for `say_hi = decorator(say_hi)`

---

## 2. Function Foundations (Must Know)

### 2.1 First-Class Objects
Functions are objects in Python—you can pass them around like any variable:

```python
def greet_bob(greeter_func):
    return greeter_func("Bob")

def say_hello(name):
    return f"Hello {name}"

# Pass function WITHOUT parentheses (reference)
result = greet_bob(say_hello)  # ✅
result = greet_bob(say_hello())  # ❌ Calls say_hello first
```

### 2.2 Inner Functions
Functions defined inside functions are locally scoped:

```python
def parent():
    def child():
        print("I'm inside parent")
    child()  # Works here
    return child  # Returns reference

child()  # ❌ NameError - not defined outside parent()
```

### 2.3 Functions Returning Functions
This is the core building block of decorators:

```python
def create_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier  # Return reference, not call

times_three = create_multiplier(3)
print(times_three(5))  # 15
```

---

## 3. Simple Decorator Pattern

### 3.1 Basic Template (Memorize This!)
```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # Preserves func's name/docstring
    def wrapper(*args, **kwargs):
        # Do something before
        result = func(*args, **kwargs)
        # Do something after
        return result
    return wrapper

@my_decorator
def my_function(x):
    return x * 2
```

**Key points**:
- `*args, **kwargs` → decorator works with any arguments
- `@functools.wraps(func)` → preserves original function metadata
- Must `return func(*args, **kwargs)` to get return value

### 3.2 Decorating Functions With Arguments

**Problem**: Basic decorator doesn't handle function arguments
```python
@do_twice
def greet(name):
    print(f"Hello {name}")

greet("Bob")  # ❌ TypeError: wrapper() takes 0 arguments but 1 was given
```

**Solution**: Use `*args, **kwargs` in wrapper
```python
def do_twice(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return func(*args, **kwargs)  # Must return on 2nd call
    return wrapper

@do_twice
def greet(name):
    print(f"Hello {name}")

greet("Bob")  # ✅ Prints "Hello Bob" twice
```

---

## 4. Real-World Examples (Interview Favorites)

### 4.1 Timer Decorator (Execution Time)
```python
import functools
import time

def timer(func):
    """Measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function(n):
    sum([i**2 for i in range(n)])
    return "done"

slow_function(1_000_000)
# Output: slow_function took 0.0234s
```

**Interview angle**: "Timing is important for performance optimization."

### 4.2 Debug Decorator (Print Arguments & Return)
```python
def debug(func):
    """Print function signature and return value"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"{func.__name__}() returned {repr(result)}")
        return result
    return wrapper

@debug
def make_greeting(name, age=None):
    if age is None:
        return f"Hi {name}!"
    return f"Hi {name}! You're {age}?"

make_greeting("Alice", age=30)
# Calling make_greeting('Alice', age=30)
# make_greeting() returned 'Hi Alice! You\'re 30?'
```

### 4.3 Rate Limiter (Slow Down)
```python
def slow_down(func):
    """Sleep 1 second before calling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)
    return wrapper

@slow_down
def api_call():
    print("Fetching data...")

# Each call waits 1 second first (rate limiting)
```

### 4.4 Plugin Registration (No Wrapping)
```python
PLUGINS = {}

def register(func):
    """Register function as a plugin (don't wrap it)"""
    PLUGINS[func.__name__] = func
    return func  # Return unchanged

@register
def plugin_1():
    return "I'm plugin 1"

@register
def plugin_2():
    return "I'm plugin 2"

# PLUGINS = {'plugin_1': <func>, 'plugin_2': <func>}
```

**Interview angle**: "Decorators don't always modify behavior—they can just manage metadata."

---

## 5. Advanced Decorator Patterns

### 5.1 Decorators With Arguments

#### 5.1.1 Problem & Solution (3 Levels Deep)
When you want `@repeat(num_times=3)` instead of just `@repeat`

```python
def repeat(num_times):  # Level 1: Takes decorator arguments
    def decorator_repeat(func):  # Level 2: Takes function to decorate
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # Level 3: Actual wrapper
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat  # Return level 2

@repeat(num_times=3)
def greet(name):
    print(f"Hello {name}")

greet("Bob")
# Hello Bob
# Hello Bob
# Hello Bob
```

**Mental model**: Each layer handles one responsibility
- Outer: decorator arguments
- Middle: receives function to decorate
- Inner: actual wrapping logic

#### 5.1.2 Optional Arguments (Best Practice)
Allow decorator to work with or without arguments:

```python
def repeat(_func=None, *, num_times=2):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    
    # Check if called with or without arguments
    if _func is None:
        return decorator_repeat  # Called with args: @repeat(num_times=3)
    else:
        return decorator_repeat(_func)  # Called without args: @repeat

@repeat  # Works without arguments (uses default num_times=2)
def say_hello():
    print("Hello")

@repeat(num_times=3)  # Works with arguments
def say_goodbye():
    print("Goodbye")
```

### 5.2 Multiple Decorators (Order Matters!)

```python
def decorator_a(func):
    def wrapper():
        print("A before")
        func()
        print("A after")
    return wrapper

def decorator_b(func):
    def wrapper():
        print("B before")
        func()
        print("B after")
    return wrapper

# Decorators applied BOTTOM to TOP
@decorator_a
@decorator_b
def say_hi():
    print("Hi!")

say_hi()
# Output:
# A before
# B before
# Hi!
# B after
# A after
```

**Execution order**: `decorator_a(decorator_b(say_hi))`

**Interview tip**: "Order matters because each decorator wraps the output of the next one."

### 5.3 Stateful Decorators (Track State)

#### 5.3.1 Using Function Attributes
```python
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.num_calls += 1
        print(f"Call #{wrapper.num_calls}")
        return func(*args, **kwargs)
    wrapper.num_calls = 0  # Store state on function
    return wrapper

@count_calls
def say_hello():
    print("Hello!")

say_hello()  # Call #1
say_hello()  # Call #2
print(say_hello.num_calls)  # 2
```

#### 5.3.2 Using Classes (More Powerful)
```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.num_calls = 0
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"Call #{self.num_calls}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()  # Call #1
say_hello.num_calls  # 2
```

---

## 6. Working With Classes

### 6.1 Decorating Methods
```python
class TimeWaster:
    @timer  # Decorates method, not class
    def waste_time(self, n):
        sum([i**2 for i in range(n)])

tw = TimeWaster()
tw.waste_time(1000)  # Method is timed
```

### 6.2 Built-in Class Decorators

#### 6.2.1 @property and @property.setter
```python
class Circle:
    @property  # Custom getter
    def radius(self):
        return self._radius
    
    @radius.setter  # Custom setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
```

#### 6.2.2 @classmethod and @staticmethod
```python
class Circle:
    @classmethod  # Factory method
    def unit_circle(cls):
        return cls(1)
    
    @staticmethod  # Utility method
    def pi():
        return 3.14159

c = Circle.unit_circle()  # Create using class method
radius = Circle.pi()  # Call static method
```

**Use cases**:
- **@classmethod**: Factory methods, class-level operations
- **@staticmethod**: Utility functions (don't need instance or class)
- **@property**: Custom getters/setters for attributes

### 6.3 Class Decorators (Decorating the Whole Class)

#### 6.3.1 Singleton Pattern
```python
def singleton(cls):
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if wrapper.instance is None:
            wrapper.instance = cls(*args, **kwargs)
        return wrapper.instance
    wrapper.instance = None
    return wrapper

@singleton
class Database:
    def __init__(self):
        self.connection = "Connected"

db1 = Database()
db2 = Database()
print(db1 is db2)  # True (same instance!)
```

---

## 7. Production-Ready Patterns

### 7.1 Caching & Memoization

#### 7.1.1 Custom Cache
```python
def cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = args + tuple(kwargs.items())
        if key not in wrapper.cache:
            wrapper.cache[key] = func(*args, **kwargs)
        return wrapper.cache[key]
    wrapper.cache = {}
    return wrapper

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(10)  # Calculates & caches results
fibonacci(10)  # Instant (cached)
```

#### 7.1.2 Built-in @functools.lru_cache (Recommended!)
```python
@functools.lru_cache(maxsize=128)  # Better! Use this
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(10)
fibonacci.cache_info()  # See cache statistics
fibonacci.cache_clear()  # Clear cache if needed
```

**Interview angle**: "Caching is crucial for recursive functions and expensive computations. Use `@functools.lru_cache` for production."

### 7.2 Retry Logic (Error Handling)
```python
def retry(max_attempts=3, delay=1):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator_retry

@retry(max_attempts=3, delay=2)
def unstable_api_call():
    # Might fail, will retry 3 times with 2s delay
    pass
```

### 7.3 Validation Decorator
```python
def validate_json(func):
    """Validate JSON input before function call"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        json_data = kwargs.get('json_data') or args[0]
        required_keys = {'student_id', 'grade'}
        if not required_keys.issubset(json_data.keys()):
            raise ValueError(f"Missing required keys: {required_keys}")
        return func(*args, **kwargs)
    return wrapper

@validate_json
def update_grade(json_data):
    # json_data is guaranteed to have 'student_id' and 'grade'
    return "Updated successfully"
```

---

## 8. Interview Questions & Answers

### Q1: What's the difference between `@decorator` and `decorator(func)`?
**A**: They're equivalent. `@decorator` is syntactic sugar. `@decorator` above a function is same as `func = decorator(func)` below it.

### Q2: Why use `@functools.wraps`?
**A**: Preserves the original function's `__name__`, `__doc__`, and other metadata. Without it, decorated functions lose their identity.

### Q3: Can you decorate a class?
**A**: Yes. `@decorator` on a class is `ClassName = decorator(ClassName)`. You can decorate class methods or the entire class.

### Q4: What's a common mistake?
**A**: Forgetting to return the function or not using `*args, **kwargs` in the wrapper. Then the decorator either doesn't return anything or doesn't work with decorated function's arguments.

### Q5: How do decorators with arguments work?
**A**: Three nested functions. Outermost takes arguments, middle takes the function, inner is the actual wrapper.

### Q6: When should I use class decorators vs function decorators?
**A**: Use functions for simple wrapping. Use classes when you need to maintain state or have more complex logic.

### Q7: What's the execution order with multiple decorators?
**A**: Applied from bottom to top. `@decorator_a @decorator_b def f()` = `decorator_a(decorator_b(f))`

### Q8: When would I use a decorator instead of just modifying the function?
**A**: Decorators promote code reusability, separation of concerns, and readability. They let you add behavior to multiple functions without changing their source code.

---

## 9. Common Pitfalls & How to Avoid Them ❌

1. **Forgetting `return` statement**
   ```python
   def bad_decorator(func):
       def wrapper(*args, **kwargs):
           func(*args, **kwargs)  # ❌ No return!
       return wrapper
   
   # Decorated function always returns None
   ```

2. **Not using `@functools.wraps`**
   ```python
   # Decorated function loses its identity
   @my_decorator
   def my_function():
       pass
   
   print(my_function.__name__)  # 'wrapper' (wrong!)
   ```

3. **Not using `*args, **kwargs`**
   ```python
   def my_decorator(func):
       def wrapper():  # ❌ Only works with no-arg functions
           return func()
       return wrapper
   ```

4. **Executing instead of passing function reference**
   ```python
   @my_decorator()  # ❌ Calls decorator immediately!
   def my_function():
       pass
   ```

5. **Modifying function behavior unexpectedly**
   ```python
   @repeat(num_times=2)
   def return_value():
       return "result"
   
   result = return_value()  # Returns "result" twice? No!
   # Must return on last call only
   ```

---

## 10. Interview Preparation Checklist

### Must Know ⭐⭐⭐
- [ ] What a decorator is (function that wraps another function)
- [ ] Basic decorator pattern (def decorator, def wrapper, return wrapper)
- [ ] `@functools.wraps` usage and why
- [ ] `*args, **kwargs` in decorators
- [ ] `@` syntax vs manual assignment
- [ ] Real examples: timer, debug, caching

### Should Know ⭐⭐
- [ ] Decorators with arguments (3 levels)
- [ ] Multiple decorators (order matters)
- [ ] Stateful decorators (function attributes or classes)
- [ ] Class decorators (@property, @classmethod, @staticmethod)
- [ ] Plugin registration pattern
- [ ] @functools.lru_cache for caching

### Nice to Know ⭐
- [ ] Singleton pattern
- [ ] Retry logic with exponential backoff
- [ ] Async decorators
- [ ] Validation decorators
- [ ] Class as decorators vs function decorators

---

## 11. Practice Problem (Interview Ready)

**Question**: Write a decorator that:
1. Measures execution time
2. Logs function name and arguments
3. Catches exceptions and logs them
4. Can be used with or without arguments for rate limiting

**Solution**:
```python
import functools
import time
from datetime import datetime

def advanced_decorator(_func=None, *, rate_limit=0):
    def decorator_advanced(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Rate limiting
            if rate_limit > 0:
                time.sleep(rate_limit)
            
            # Logging
            timestamp = datetime.now().isoformat()
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            print(f"[{timestamp}] Calling {func.__name__}({signature})")
            
            # Timing & error handling
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                print(f"✅ {func.__name__} succeeded in {elapsed:.4f}s")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                print(f"❌ {func.__name__} failed after {elapsed:.4f}s: {e}")
                raise
        
        return wrapper
    
    if _func is None:
        return decorator_advanced
    else:
        return decorator_advanced(_func)

# Usage
@advanced_decorator
def simple_function(x):
    return x * 2

@advanced_decorator(rate_limit=1)
def api_call(endpoint):
    return f"Data from {endpoint}"

simple_function(5)
api_call("/users")  # Waits 1 second before calling
```

**Interview explanation**: "This decorator handles common production requirements: timing, logging, error handling, and rate limiting. It's flexible with optional arguments for different use cases."

---

## 12. TL;DR: Quick Reference

```python
# Basic template - MEMORIZE THIS
import functools

def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper

# With arguments
def decorator_with_args(arg):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Class decorator
class ClassDecorator:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
```

**Key facts**:
- Decorators modify function behavior without changing source
- `@decorator` is shorthand for `func = decorator(func)`
- Always use `@functools.wraps` to preserve metadata
- Always use `*args, **kwargs` for flexibility
- Return value must be returned from wrapper
