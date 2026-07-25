# Python List Comprehensions - Interview-Ready Notes

## 1. Fundamentals & Overview

### 1.1 What is a List Comprehension? (Common Question ⭐)

**Definition**: A list comprehension is a concise, declarative way to create a new list by applying an expression to each item in an iterable, optionally with filtering.

**Simple Answer**: It's a one-liner alternative to for-loops for creating/transforming lists.

**Core Formula**:
```python
new_list = [expression for member in iterable]
```

**Example**:
```python
# Traditional loop (3 lines)
squares = []
for number in range(10):
    squares.append(number * number)

# List comprehension (1 line)
squares = [number * number for number in range(10)]
# Result: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### 1.2 Three Essential Components

1. **Expression**: The operation to perform on each member
   - Can be: calculation, method call, or any valid Python expression
   - Example: `number * number`, `char.upper()`, `func(x)`

2. **Member**: The current item from the iterable
   - Example: `number`, `char`, `item`

3. **Iterable**: The source data (must be iterable)
   - Examples: `range(10)`, `list`, `string`, `set`, `generator`

**Visual Breakdown**:
```
[    number * number    for    number    in    range(10)   ]
      └─ expression ─┘        └─ member ─┘    └─ iterable ─┘
```

---

## 2. Syntax Variations & Patterns

### 2.1 Basic Transformation

```python
# Square all numbers
squares = [x**2 for x in range(5)]
# [0, 1, 4, 9, 16]

# Apply function to each element
prices = [1.09, 23.56, 57.84]
TAX_RATE = 0.08
final_prices = [price * (1 + TAX_RATE) for price in prices]
# [1.1772, 25.4448, 62.4672]

# String transformation
words = ["hello", "world"]
uppercase = [word.upper() for word in words]
# ["HELLO", "WORLD"]
```

### 2.2 Conditional Filtering (if clause at end)

**Formula**:
```python
new_list = [expression for member in iterable if condition]
```

**Use**: When you want to **exclude** certain elements

```python
# Filter even numbers
numbers = [1, 2, 3, 4, 5, 6]
evens = [n for n in numbers if n % 2 == 0]
# [2, 4, 6]

# Extract vowels from string
sentence = "hello world"
vowels = [char for char in sentence if char in "aeiou"]
# ['e', 'o', 'o']

# Filter with complex condition
original_prices = [1.25, -9.45, 10.22, 3.78, -5.92]
valid_prices = [p for p in original_prices if p > 0]
# [1.25, 10.22, 3.78]
```

**Interview tip**: "The conditional at the end FILTERS—it only keeps elements that match the condition."

### 2.3 Conditional Expression (if-else in expression)

**Formula**:
```python
new_list = [true_expr if condition else false_expr for member in iterable]
```

**Use**: When you want to **transform** elements based on condition

```python
# Replace negative with 0
original_prices = [1.25, -9.45, 10.22, -5.92]
corrected = [price if price > 0 else 0 for price in original_prices]
# [1.25, 0, 10.22, 0]

# Apply different transformation based on value
numbers = [1, 2, 3, 4, 5]
result = ["even" if n % 2 == 0 else "odd" for n in numbers]
# ["odd", "even", "odd", "even", "odd"]

# Ternary operator (another name for conditional expression)
status = [("pass" if score >= 60 else "fail") for score in [45, 78, 92, 55]]
# ["fail", "pass", "pass", "fail"]
```

**Interview tip**: "Conditional EXPRESSION (if-else) TRANSFORMS; conditional at END (if) FILTERS."

### 2.4 Combining Filter & Transform

```python
# Filter and transform together
numbers = [1, 2, 3, 4, 5, 6]
doubled_evens = [n * 2 for n in numbers if n % 2 == 0]
# [4, 8, 12]

# Complex example: vowels to uppercase, keep only if uppercase
sentence = "hello world"
loud_vowels = [char.upper() for char in sentence if char in "aeiou"]
# ['E', 'O', 'O']
```

---

## 3. Comprehension Types

### 3.1 List Comprehensions (Most Common)

```python
result = [x for x in range(5)]
# Creates: [0, 1, 2, 3, 4]
# Type: <class 'list'>
```

**Characteristics**:
- Returns a **list** (evaluated eagerly, entire list in memory)
- Uses **square brackets** `[ ]`
- Fastest for small-to-medium lists
- Subscriptable: `result[0]`

### 3.2 Set Comprehensions

**Formula**:
```python
new_set = {expression for member in iterable}
```

**Use**: Create set with unique elements automatically

```python
# Remove duplicate vowels
quote = "life, uh, finds a way"
vowels = {char for char in quote if char in "aeiou"}
# {'a', 'e', 'u', 'i'} — order not guaranteed, no duplicates

# Unique squares
numbers = [1, 2, 2, 3, 3, 3]
squares = {n**2 for n in numbers}
# {1, 4, 9}
```

**Key difference from list**:
- Automatically **removes duplicates**
- Uses **curly braces** `{ }`
- Unordered collection
- Faster lookup: O(1) average

### 3.3 Dictionary Comprehensions

**Formula**:
```python
new_dict = {key: value for member in iterable}
```

**Use**: Create dictionaries from iterables

```python
# Map numbers to their squares
squares_dict = {n: n**2 for n in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Create lookup from list
words = ["apple", "banana", "cherry"]
word_lengths = {word: len(word) for word in words}
# {"apple": 5, "banana": 6, "cherry": 6}

# Transform dictionary
prices = {"apple": 1.20, "banana": 0.50, "cherry": 2.00}
discounted = {item: price * 0.9 for item, price in prices.items()}
# {"apple": 1.08, "banana": 0.45, "cherry": 1.8}

# Conditional dictionary
numbers = [1, 2, 3, 4, 5, 6]
even_squares = {n: n**2 for n in numbers if n % 2 == 0}
# {2: 4, 4: 16, 6: 36}
```

**Interview tip**: "Dictionary comprehensions need both key and value separated by colon."

### 3.4 Generator Expressions

**Formula**:
```python
generator = (expression for member in iterable)
```

**Use**: Lazy evaluation for memory efficiency with large datasets

```python
# List comprehension (eager, all in memory)
squares_list = [n**2 for n in range(1_000_000)]  # ⚠️ Uses lots of memory

# Generator (lazy, on-demand)
squares_gen = (n**2 for n in range(1_000_000))   # ✅ Minimal memory
next_square = next(squares_gen)  # Get one value at a time

# Useful for large datasets
sum_of_squares = sum(n**2 for n in range(1_000_000_000))  # Doesn't crash
```

**Key differences**:
- Uses **parentheses** `( )` (or can be bare in function calls)
- **Lazy evaluation** (values computed on-demand)
- Returns **generator object** (not a list)
- Memory efficient for large/infinite sequences
- Can only iterate once

---

## 4. Advanced Patterns

### 4.1 Nested List Comprehensions (Creating Matrices)

```python
# Create 3x3 matrix of zeros
matrix = [[0 for _ in range(3)] for _ in range(3)]
# [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

# Multiplication table
table = [[i * j for j in range(1, 4)] for i in range(1, 4)]
# [[1, 2, 3], [2, 4, 6], [3, 6, 9]]

# With transformation
matrix = [[row**2 for row in range(3)] for _ in range(3)]
# [[0, 1, 4], [0, 1, 4], [0, 1, 4]]
```

**Order matters**: Inner loop first, then outer

### 4.2 Flattening Nested Lists

```python
# Using nested comprehension (advanced)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Equivalent to:
flat_alt = []
for row in matrix:
    for num in row:
        flat_alt.append(num)
```

**Interview note**: "Multiple for clauses execute in order, reading left to right."

### 4.3 Walrus Operator `:=` (Python 3.8+)

**Use**: Assign value while evaluating in comprehension

```python
import random

def get_weather():
    return random.randrange(90, 110)

# Get temperatures >= 100 degrees
hot_days = [temp for _ in range(20) if (temp := get_weather()) >= 100]
# Walrus operator lets us use temp in condition AND expression

# Without walrus (would need two function calls)
temps = [get_weather() for _ in range(20)]
hot = [t for t in temps if t >= 100]  # Inefficient, called function twice
```

**When to use**: When you need the computed value in both condition and expression

---

## 5. Comparison: Different Approaches

### 5.1 For Loop vs List Comprehension

```python
# FOR LOOP (3 lines, verbose)
prices = [1.09, 23.56, 57.84, 4.56, 6.78]
TAX_RATE = 0.08
final = []
for price in prices:
    final.append(price * (1 + TAX_RATE))

# LIST COMPREHENSION (1 line, concise)
final = [price * (1 + TAX_RATE) for price in prices]

# MAP FUNCTION (functional style)
final = list(map(lambda p: p * (1 + TAX_RATE), prices))
```

**When to use each**:
- **For loop**: Complex multi-step logic, multiple statements
- **List comprehension**: Single transformation/filter, readable one-liner
- **map()**: Functional programming style, with existing function

### 5.2 List Comprehension vs filter()

```python
numbers = [1, 2, 3, 4, 5, 6]

# LIST COMPREHENSION
evens = [n for n in numbers if n % 2 == 0]

# FILTER FUNCTION
evens = list(filter(lambda n: n % 2 == 0, numbers))

# FILTER + MAP (multiple operations)
even_squares = [n**2 for n in numbers if n % 2 == 0]
even_squares = list(map(lambda n: n**2, filter(lambda n: n % 2 == 0, numbers)))
```

**Verdict**: List comprehension is more readable, especially with conditionals

### 5.3 List Comprehension vs map()

```python
prices = [1.09, 23.56, 57.84, 4.56, 6.78]

# MAP (lazy, returns map object)
result_map = map(lambda p: p * 1.08, prices)  # Lazy
print(result_map)  # <map object at 0x...>

# LIST COMPREHENSION (eager, returns list)
result_list = [p * 1.08 for p in prices]  # Eager
print(result_list)  # [1.1772, 25.4448, ...]

# Key difference: eval timing
list(map(...))  # Fully evaluated now
(... for ...)   # Evaluated on demand
```

**Tradeoff**:
- `map()`: Lazy (memory efficient for huge data)
- `list comprehension`: Eager (simpler, more Pythonic)

---

## 6. Performance & Optimization

### 6.1 Performance Comparison (Real Measurements)

```python
import timeit

# Test data
PRICES = [random.randrange(100) for _ in range(100_000)]
TAX_RATE = 0.08

# Approach 1: For Loop
def loop_approach():
    prices = []
    for price in PRICES:
        prices.append(price * (1 + TAX_RATE))
    return prices

# Approach 2: List Comprehension
def comprehension_approach():
    return [price * (1 + TAX_RATE) for price in PRICES]

# Approach 3: Map
def map_approach():
    return list(map(lambda p: p * (1 + TAX_RATE), PRICES))

# Results (100 iterations each):
# Loop: 3.05 seconds
# Comprehension: 2.40 seconds  ← Faster!
# Map: 2.05 seconds           ← Even faster!
```

**Key insight**: List comprehension faster than loop, but `map()` can be faster for simple operations.

### 6.2 Memory Considerations

```python
# List comprehension (eager, all in memory)
squares_list = [n**2 for n in range(1_000_000)]  # ~40MB in memory

# Generator expression (lazy, minimal memory)
squares_gen = (n**2 for n in range(1_000_000))   # ~1KB in memory

# For huge datasets:
sum_billion = sum(n**2 for n in range(1_000_000_000))  # ✅ Works fine
# vs
list_billion = [n**2 for n in range(1_000_000_000)]    # ❌ Crashes (out of memory)
```

**Rule**: Use generator for large datasets, list comprehension for normal sizes

### 6.3 Profiling Best Practices

```python
import timeit

# Profile snippet 1
t1 = timeit.timeit('sum([n**2 for n in range(1000)])', number=10000)

# Profile snippet 2
t2 = timeit.timeit('sum(n**2 for n in range(1000))', number=10000)

print(f"List: {t1:.4f}s, Generator: {t2:.4f}s")

# Always measure YOUR specific code, don't rely on intuition!
```

**Interview tip**: "Always profile before optimizing. Use `timeit` for accurate measurements."

---

## 7. When NOT to Use List Comprehensions

### 7.1 Nested Comprehensions (Readability Issues)

```python
# ❌ Hard to read
result = [[n**2 if n % 2 == 0 else n for n in row if len(row) > 2] for row in matrix]

# ✅ Better: Use explicit loop
result = []
for row in matrix:
    if len(row) > 2:
        for n in row:
            if n % 2 == 0:
                result.append(n**2)
            else:
                result.append(n)
```

**Rule**: If comprehension takes >2 lines to understand mentally, use a loop

### 7.2 Large Datasets (Memory Issues)

```python
# ❌ List comprehension: Loads all 1 billion numbers into memory
sum_million = sum([n**2 for n in range(1_000_000_000)])  # Crashes!

# ✅ Generator: On-demand, minimal memory
sum_million = sum(n**2 for n in range(1_000_000_000))   # Works!
```

**Rule**: For large/infinite sequences, use generators

### 7.3 Complex Logic (Maintainability)

```python
# ❌ Comprehension too complex
results = [calculate_complex_value(item) if item.status == 'active' 
           and item.value > 100 and is_valid(item) 
           else default_value(item) for item in items]

# ✅ Use loop for clarity
results = []
for item in items:
    if item.status == 'active' and item.value > 100 and is_valid(item):
        results.append(calculate_complex_value(item))
    else:
        results.append(default_value(item))
```

**Rule**: Prioritize readability over cleverness

---

## 8. Interview Questions & Answers

### Q1: What are the three components of a list comprehension?
**A**: Expression (what to create), member (current item), and iterable (where items come from). Formula: `[expression for member in iterable]`

### Q2: What's the difference between `[x if x > 0 else 0 for x in list]` and `[x for x in list if x > 0]`?
**A**: First TRANSFORMS (conditional expression), keeps all items but modifies some. Second FILTERS (conditional clause), only keeps items matching condition.

### Q3: When should I use a list comprehension instead of a loop?
**A**: When transforming/filtering a list into a new list in a single, readable operation. Use loops for complex multi-step logic.

### Q4: Is a list comprehension faster than a for loop?
**A**: Generally yes, 15-50% faster, but `map()` can be even faster. Always profile your specific use case.

### Q5: What's a set comprehension?
**A**: Like list comprehension but with curly braces `{}` and automatically removes duplicates. Example: `{x**2 for x in range(5)}`

### Q6: What's a dictionary comprehension?
**A**: Creates dict with `{key: value for x in iterable}`. Example: `{x: x**2 for x in range(5)}`

### Q7: When should I use a generator instead of list comprehension?
**A**: For large datasets where you don't need all values at once. Generators use `()` and evaluate lazily, saving memory.

### Q8: Can you nest list comprehensions?
**A**: Yes, but only for simple operations. Complex nesting hurts readability—use loops instead.

---

## 9. Common Mistakes & Gotchas

### 9.1 Confusing Conditional Filter vs Transform

```python
# ❌ Wrong: Trying to filter with if-else (doesn't work as expected)
result = [x if x > 0 for x in [-1, 0, 1, 2]]  # SyntaxError

# ✅ Correct: Use filter (end) or transform (start)
filtered = [x for x in [-1, 0, 1, 2] if x > 0]  # [1, 2]
transformed = [x if x > 0 else 0 for x in [-1, 0, 1, 2]]  # [0, 0, 1, 2]
```

### 9.2 Forgetting Parentheses for Generators

```python
# ❌ This is a list comprehension (eager)
result = [n**2 for n in range(1_000_000)]  # Uses memory

# ✅ This is a generator (lazy)
result = (n**2 for n in range(1_000_000))  # Minimal memory

# Bare generator in function call (parentheses optional)
total = sum(n**2 for n in range(1_000_000))  # ✅ Works
```

### 9.3 Variable Scope Issues

```python
# ❌ Expecting `x` to exist outside comprehension
squares = [x**2 for x in range(5)]
print(x)  # NameError in Python 3

# ✅ Comprehension variables are local in Python 3
# (In Python 2, they leaked to outer scope)
```

### 9.4 Multiple Iterations

```python
# ❌ Generator can only iterate once
gen = (x**2 for x in range(5))
print(list(gen))  # [0, 1, 4, 9, 16]
print(list(gen))  # []  — Empty! Generator exhausted

# ✅ List can iterate multiple times
lst = [x**2 for x in range(5)]
print(lst)  # [0, 1, 4, 9, 16]
print(lst)  # [0, 1, 4, 9, 16]  — Still works
```

---

## 10. Interview Preparation Checklist

### Must Know ⭐⭐⭐
- [ ] Basic syntax: `[expr for x in iterable]`
- [ ] Three components: expression, member, iterable
- [ ] Conditional filtering: `if` at end
- [ ] Conditional transform: `if-else` in expression
- [ ] List vs set vs dict comprehensions
- [ ] Performance: Faster than loops, slower than map()
- [ ] Real examples: squares, filtering, transformation

### Should Know ⭐⭐
- [ ] Generator expressions vs list comprehensions
- [ ] Nested comprehensions (matrices, flattening)
- [ ] Dictionary comprehensions (key: value)
- [ ] Walrus operator `:=`
- [ ] When NOT to use (readability, large data)
- [ ] Memory implications

### Nice to Know ⭐
- [ ] Micro-optimizations with `map()`
- [ ] Set comprehensions for uniqueness
- [ ] Profiling with `timeit`
- [ ] Lazy vs eager evaluation

---

## 11. Practice Problems (Interview Ready)

### Problem 1: Filter and Transform
```python
# Given: numbers = [1, 2, 3, 4, 5, 6]
# Create list of doubled even numbers

# Solution
numbers = [1, 2, 3, 4, 5, 6]
result = [n * 2 for n in numbers if n % 2 == 0]
# [4, 8, 12]
```

### Problem 2: Dictionary Lookup
```python
# Given: words = ["apple", "banana", "cherry", "date"]
# Create dict mapping word to its length

# Solution
words = ["apple", "banana", "cherry", "date"]
word_dict = {word: len(word) for word in words}
# {"apple": 5, "banana": 6, "cherry": 6, "date": 4}
```

### Problem 3: Nested Comprehension (Matrix)
```python
# Create 4x4 matrix where element (i,j) = i*j

# Solution
matrix = [[i*j for j in range(1, 5)] for i in range(1, 5)]
# [[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12], [4, 8, 12, 16]]
```

### Problem 4: Flatten List
```python
# Given: nested = [[1, 2], [3, 4], [5, 6]]
# Flatten to single list

# Solution
nested = [[1, 2], [3, 4], [5, 6]]
flat = [n for row in nested for n in row]
# [1, 2, 3, 4, 5, 6]
```

### Problem 5: Conditional Transform
```python
# Given: prices = [1.25, -9.45, 10.22, -5.92]
# Replace negative prices with 0

# Solution
prices = [1.25, -9.45, 10.22, -5.92]
corrected = [p if p > 0 else 0 for p in prices]
# [1.25, 0, 10.22, 0]
```

---

## 12. TL;DR Quick Reference

### Basic Formulas
```python
# Standard list comprehension
[expr for x in iterable]

# With filter
[expr for x in iterable if condition]

# With transform condition
[expr_true if condition else expr_false for x in iterable]

# Set comprehension (unique, unordered)
{expr for x in iterable}

# Dictionary comprehension
{key: value for x in iterable}

# Generator (lazy, memory efficient)
(expr for x in iterable)

# Nested comprehension
[expr for x in iterable for y in another]
```

### When to Use
| Use Case | Tool | Example |
|----------|------|---------|
| Simple transform | List comp | `[x*2 for x in lst]` |
| Filter values | List comp | `[x for x in lst if x > 0]` |
| Unique values | Set comp | `{x for x in lst}` |
| Key-value pairs | Dict comp | `{x: x**2 for x in range(5)}` |
| Large data | Generator | `(x**2 for x in huge_range)` |
| Functional style | map() | `list(map(lambda x: x*2, lst))` |
| Complex logic | For loop | Multi-step operations |

### Performance Summary
```
Speed:        map() > list comp > for loop
Memory:       generator > map/comp > list
Readability:  list comp > map > generator
Flexibility:  for loop > list comp > map
```

### Red Flags
- ❌ Comprehension that doesn't fit on one line
- ❌ Nested comprehension with multiple conditions
- ❌ Using list comp for billions of items
- ❌ Can't understand it after reading once

**Pythonic Principle**: "Readability counts. If you have to explain your comprehension, use a loop."
