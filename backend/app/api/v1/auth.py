import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from app.models.kiosk_pin import KioskPin
from app.models.parent import Parent
from app.schemas.auth import LoginRequest, ParentOut, VerifyPinOut, VerifyPinRequest
from app.schemas.pin import PinOut, PinSet
from app.services.pins import get_pin, upsert_pin

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "access_token"


def get_optional_parent(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> Parent | None:
    if not access_token:
        return None
    parent_id = decode_access_token(token=access_token)
    if not parent_id:
        return None
    return db.get(entity=Parent, ident=uuid.UUID(parent_id))


def get_current_parent(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> Parent:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    parent_id = decode_access_token(token=access_token)
    if not parent_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    parent = db.get(entity=Parent, ident=uuid.UUID(parent_id))
    if not parent:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return parent


@router.post("/login")
def login(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> ParentOut:
    parent = db.scalar(select(Parent).where(Parent.login == body.login))
    if not parent or not verify_password(plain=body.password, hashed=parent.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        )
    token = create_access_token(subject=str(parent.id))
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return ParentOut.model_validate(obj=parent)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key=COOKIE_NAME)
    return {"detail": "Déconnecté"}


@router.get("/me")
def me(current_parent: Parent = Depends(get_current_parent)) -> ParentOut:
    return ParentOut.model_validate(obj=current_parent)


@router.get("/pin")
def get_parent_pin(
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent),
) -> PinOut:
    pin = get_pin(db=db, holder_type="parent", holder_id=current_parent.id)
    return PinOut(pin=pin.pin if pin else None)


@router.post("/pin")
def set_parent_pin(
    body: PinSet,
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent),
) -> PinOut:
    pin = upsert_pin(
        db=db, holder_type="parent", holder_id=current_parent.id, new_pin=body.pin
    )
    return PinOut(pin=pin.pin)


@router.post("/verify-pin")
def verify_pin(
    body: VerifyPinRequest,
    db: Session = Depends(get_db),
) -> VerifyPinOut:
    kiosk_pin = db.get(entity=KioskPin, ident=body.pin)
    if not kiosk_pin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN inconnu")
    return VerifyPinOut(
        holder_type=kiosk_pin.holder_type,
        holder_id=kiosk_pin.holder_id,
    )
