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
#Commit: /week1/d