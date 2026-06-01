from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid, secrets

from ..database import get_db
from ..models.api_key import APIKey

router = APIRouter()

class CreateKeyRequest(BaseModel):
    name: str

@router.post("/")
def create_api_key(req: CreateKeyRequest, request: Request, db: Session = Depends(get_db)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(401, "Authentication required")

    raw_key = f"gw_{secrets.token_urlsafe(32)}"
    key = APIKey(
        id=str(uuid.uuid4()),
        name=req.name,
        key_hash=APIKey.hash_key(raw_key),
        key_prefix=raw_key[:10],
        owner_id=user_id
    )
    db.add(key)
    db.commit()
    return {
        "id": key.id,
        "name": key.name,
        "key": raw_key,           # only returned once
        "prefix": key.key_prefix,
        "message": "Store this key securely — it won't be shown again."
    }

@router.get("/")
def list_api_keys(request: Request, db: Session = Depends(get_db)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(401, "Authentication required")
    keys = db.query(APIKey).filter(APIKey.owner_id == user_id, APIKey.is_active == True).all()
    return [{"id": k.id, "name": k.name, "prefix": k.key_prefix, "created_at": str(k.created_at)} for k in keys]

@router.delete("/{key_id}")
def revoke_api_key(key_id: str, request: Request, db: Session = Depends(get_db)):
    user_id = getattr(request.state, "user_id", None)
    key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.owner_id == user_id).first()
    if not key:
        raise HTTPException(404, "Key not found")
    key.is_active = False
    db.commit()
    return {"message": "Key revoked"}
