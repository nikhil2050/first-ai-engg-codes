from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="User Management API")

# ============================================================================
# DATA MODEL - Used Throughout
# ============================================================================

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int


# Simulated database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30}
}


# ============================================================================
# CUSTOM EXCEPTIONS - Define Once
# ============================================================================

class UserNotFoundError(Exception):
    """User does not exist"""
    pass


class EmailAlreadyExistsError(Exception):
    """Email already registered"""
    pass


class InvalidAgeError(Exception):
    """Age is out of valid range"""
    pass


# ============================================================================
# CUSTOM EXCEPTION HANDLERS - Define Once
# ============================================================================

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "UserNotFoundError", "detail": "User does not exist"}
    )


@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "EmailAlreadyExistsError", "detail": "Email already registered"}
    )


@app.exception_handler(InvalidAgeError)
async def invalid_age_handler(request: Request, exc: InvalidAgeError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "InvalidAgeError", "detail": "Age must be between 18 and 120"}
    )


# ============================================================================
# 5.2 SETTING STATUS CODES + 5.3 HTTPException + 5.4 Custom Exceptions
# ============================================================================

# GET - Returns 200 OK (default)
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Get user by ID
    
    Status Codes:
    - 200 OK (default) - User found
    - 404 NOT FOUND (custom exception) - User doesn't exist
    """
    if user_id not in users_db:
        raise UserNotFoundError()  # → 404 response
    
    return users_db[user_id]


# POST - Explicitly set to 201 CREATED
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """
    Create new user
    
    Status Codes:
    - 201 CREATED (explicit) - User created successfully
    - 400 BAD REQUEST (custom exception) - Age invalid
    - 409 CONFLICT (custom exception) - Email already exists
    """
    # Validation 1: Check age
    if user.age < 18 or user.age > 120:
        raise InvalidAgeError()  # → 400 response
    
    # Validation 2: Check email uniqueness
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise EmailAlreadyExistsError()  # → 409 response
    
    # Add to database
    users_db[user.id] = user.dict()
    return user  # Returns 201 with user data


# PUT - Update user (no explicit status code = 200)
@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    """
    Update existing user
    
    Status Codes:
    - 200 OK (default) - User updated
    - 400 BAD REQUEST (custom exception) - Age invalid
    - 404 NOT FOUND (custom exception) - User doesn't exist
    """
    # Check if user exists
    if user_id not in users_db:
        raise UserNotFoundError()  # → 404 response
    
    # Validate age
    if user.age < 18 or user.age > 120:
        raise InvalidAgeError()  # → 400 response
    
    # Update database
    users_db[user_id] = user.dict()
    return user  # Returns 200 with updated data


# DELETE - Explicitly set to 204 NO CONTENT
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """
    Delete user
    
    Status Codes:
    - 204 NO CONTENT (explicit) - User deleted successfully
    - 404 NOT FOUND (custom exception) - User doesn't exist
    """
    if user_id not in users_db:
        raise UserNotFoundError()  # → 404 response
    
    del users_db[user_id]
    return None  # 204 returns nothing


# GET all users - 200 OK (default)
@app.get("/users", response_model=list[User])
async def list_users():
    """
    List all users
    
    Status Codes:
    - 200 OK (default) - Returns list of users
    """
    return list(users_db.values())


# ============================================================================
# USING HTTPException (Alternative to Custom Exceptions)
# ============================================================================

@app.get("/users/{user_id}/details")
async def get_user_details(user_id: int):
    """
    Alternative: Using HTTPException directly (instead of custom exception)
    
    Both approaches work - this shows HTTPException method
    """
    if user_id not in users_db:
        # Direct HTTPException (simpler for standard errors)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return users_db[user_id]


# ============================================================================
# CONCEPT COMPARISON
# ============================================================================

"""
THREE WAYS TO HANDLE ERRORS:

1. DEFAULT STATUS CODE (5.2)
   @app.get("/users")
   async def list_users():
       return users  # Automatically returns 200 OK

2. HTTPException (5.3)
   @app.get("/users/{id}")
   async def get(id: int):
       if not found:
           raise HTTPException(404, "Not found")  # Returns error response

3. CUSTOM EXCEPTIONS (5.4)
   raise UserNotFoundError()  # Triggers @app.exception_handler → custom response

WHEN TO USE:
- Default: GET requests that always succeed
- HTTPException: Standard HTTP errors (404, 401, 400)
- Custom Exceptions: Business logic errors (OutOfStock, InvalidAge, etc.)
"""


# ============================================================================
# RUN IT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# TEST IT (Copy & Paste in Terminal)
# ============================================================================

"""
# 1. LIST USERS (200 OK - default)
curl http://localhost:8000/users

# 2. CREATE USER (201 CREATED - explicit)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"id":3,"name":"Charlie","email":"charlie@example.com","age":28}'

# 3. CREATE USER - INVALID AGE (400 - custom exception)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"id":4,"name":"Diana","email":"diana@example.com","age":15}'

# 4. CREATE USER - DUPLICATE EMAIL (409 - custom exception)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"id":5,"name":"Eve","email":"alice@example.com","age":25}'

# 5. GET USER (200 OK - default)
curl http://localhost:8000/users/1

# 6. GET USER - NOT FOUND (404 - custom exception)
curl http://localhost:8000/users/999

# 7. UPDATE USER (200 OK - default)
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"id":1,"name":"Alice Updated","email":"alice_new@example.com","age":26}'

# 8. UPDATE USER - INVALID AGE (400 - custom exception)
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"id":1,"name":"Alice","email":"alice@example.com","age":150}'

# 9. DELETE USER (204 NO CONTENT - explicit)
curl -X DELETE http://localhost:8000/users/1

# 10. DELETE USER - NOT FOUND (404 - custom exception)
curl -X DELETE http://localhost:8000/users/999
"""