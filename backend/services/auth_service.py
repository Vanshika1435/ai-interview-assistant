from sqlalchemy.orm import Session
from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from backend.models.user import User
from backend.schemas.user import RegisterRequest
from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PASSWORD FUNCTIONS

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# JWT TOKEN FUNCTIONS

def create_token(user: User) -> str:
    expiry = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user.email,
        "user_id": user.id,
        "exp": expiry
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# REGISTER

def register_user(data: RegisterRequest, db: Session) -> User:

    existing = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# LOGIN

def login_user(email: str, password: str, db: Session) -> dict:

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email
        }
    }


# GET CURRENT USER

def get_current_user(token: str, db: Session) -> User:

    payload = decode_access_token(token)

    email = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user