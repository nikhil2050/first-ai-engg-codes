import functools

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