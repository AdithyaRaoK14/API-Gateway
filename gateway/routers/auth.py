from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import uuid, os

from ..database import get_db
from ..models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

def make_token(user: User):
    exp = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": user.id, "role": user.role, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Username taken")
    user = User(id=str(uuid.uuid4()), username=req.username,
                hashed_password=pwd_context.hash(req.password), role=req.role)
    db.add(user)
    db.commit()
    return {"message": "Registered", "token": make_token(user)}

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"token": make_token(user), "role": user.role}
