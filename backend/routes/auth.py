from fastapi import APIRouter, Depends , HTTPException, Header
from sqlalchemy.orm import Session
from backend.models.user import User
from jose import JWTError
from backend.database import get_db
from backend.schemas.user import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from backend.services.auth_service import register_user, login_user,decode_access_token
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(data, db)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(data.email, data.password, db)
    return result


@router.get("/me")
def get_current_user_data(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Remove Bearer
        token = authorization.replace("Bearer ", "")

        payload = decode_access_token(token)

        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "name": user.full_name,
            "full_name": user.full_name,
            "email": user.email
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        print("AUTH ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))