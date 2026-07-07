from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.auth.hashing import hash_password
from app.auth.hashing import verify_password
from app.database.mysql import SessionLocal
from app.models.user_model import User
from app.auth.jwt_handler import create_access_token

router = APIRouter()


@router.post("/signup")
def signup(name: str, email: str, password: str):

    db: Session = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:

        db.close()

        # Was previously allowed to fall through to an IntegrityError
        # (unique email constraint) which would have returned an ugly
        # unhandled 500. Fail clearly instead.
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists"
        )

    new_user = User(
        name=name,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(new_user)

    db.commit()

    db.close()

    return {
        "message": "User created successfully"
    }

@router.post("/login")
def login(email: str, password: str):

    db: Session = SessionLocal()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        db.close()

        # NOTE: this previously returned a plain 200 OK with a
        # "User not found" message body. The frontend only treats a
        # login as failed when the request raises an HTTP error status,
        # so a 200 response was silently treated as a *successful*
        # login with an undefined token. Returning a proper 401 makes
        # the frontend's existing error handling actually trigger.
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    password_correct = verify_password(
        password,
        user.password_hash
    )

    if not password_correct:

        db.close()

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    token = create_access_token(
        data={
            "email": user.email
        }
    )

    db.close()

    return {
        "message": "Login successful",
        "access_token": token
    }
