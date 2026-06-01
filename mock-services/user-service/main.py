from fastapi import FastAPI
app = FastAPI()

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]

@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}

@app.get("/users/")
def list_users():
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "Not found")
    return user
