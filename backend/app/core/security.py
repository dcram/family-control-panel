from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(password=plain.encode(), hashed_password=hashed.encode())


def create_access_token(subject: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return str(jwt.encode(claims=payload, key=settings.secret_key, algorithm=ALGORITHM))


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token=token, key=settings.secret_key, algorithms=[ALGORITHM]
        )
        sub: str | None = payload.get("sub")
        return sub
    except JWTError:
        return None
