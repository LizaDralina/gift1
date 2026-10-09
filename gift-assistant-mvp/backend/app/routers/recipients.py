from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.recipient import Recipient
from app.models.user import User
from app.schemas.recipient import RecipientCreate, RecipientUpdate, RecipientOut
from app.utils.text import normalize_list, normalize_text


router = APIRouter()


def get_owned_recipient(db: Session, recipient_id: int, user_id: int) -> Recipient:
    recipient = db.get(Recipient, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")
    if recipient.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return recipient


@router.post("", response_model=RecipientOut)
def create_recipient(
    payload: RecipientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipient = Recipient(
        user_id=current_user.id,
        age=payload.age,
        gender=payload.gender,
        relationship_type=normalize_text(payload.relationship_type) or None,
        occasion=normalize_text(payload.occasion),
        interests=normalize_list(payload.interests),
        exclusions=normalize_list(payload.exclusions),
    )
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    return recipient


@router.get("", response_model=list[RecipientOut])
def list_recipients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.scalars(select(Recipient).where(Recipient.user_id == current_user.id)).all()
    return items


@router.get("/{recipient_id}", response_model=RecipientOut)
def get_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_recipient(db, recipient_id, current_user.id)


@router.patch("/{recipient_id}", response_model=RecipientOut)
def update_recipient(
    recipient_id: int,
    payload: RecipientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipient = get_owned_recipient(db, recipient_id, current_user.id)

    if payload.age is not None:
        recipient.age = payload.age
    if payload.gender is not None:
        recipient.gender = payload.gender
    if payload.relationship_type is not None:
        recipient.relationship_type = normalize_text(payload.relationship_type) or None
    if payload.occasion is not None:
        recipient.occasion = normalize_text(payload.occasion)
    if payload.interests is not None:
        recipient.interests = normalize_list(payload.interests)
    if payload.exclusions is not None:
        recipient.exclusions = normalize_list(payload.exclusions)

    db.commit()
    db.refresh(recipient)
    return recipient


@router.delete("/{recipient_id}")
def delete_recipient(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipient = get_owned_recipient(db, recipient_id, current_user.id)
    db.delete(recipient)
    db.commit()
    return {"ok": True}