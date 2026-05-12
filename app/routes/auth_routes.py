from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import hash_password, verify_password, get_current_user
from ..schemas import UserLogin, UserRegister
from ..database import get_db
from .. import models, auth

router = APIRouter()

@router.post("/register")
def register(user:UserRegister, db:Session= Depends(get_db)):
    db_existing = db.query(models.User).filter(models.User.username == user.username).first()

    if db_existing:
        raise HTTPException(status_code=400, detail="User already exist")
    
    hashed = auth.hash_password(user.password)

    new_user = models.User(
        username = user.username,
        password = hashed
    )
    db.add(new_user)
    db.commit()

    return {"message":"User created successfully"}


@router.post("/login")
def login(user:UserLogin, db:Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not auth.verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(status_code=401, detail="Wrong Password")
    
    token = auth.create_access_token({
        "sub": db_user.username
    })

    return {"access_token": token}