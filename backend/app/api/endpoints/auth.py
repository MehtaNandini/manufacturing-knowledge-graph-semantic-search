from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from ...database.session import get_db
from ...models.domain import User, RoleEnum
from ...security.auth import get_password_hash, verify_password, create_access_token, get_current_user, timedelta, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "viewer"

class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
        
    try:
        role = RoleEnum(user.role)
    except ValueError:
        role = RoleEnum.VIEWER

    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
