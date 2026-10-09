from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.product import Product
from app.models.recipient import Recipient
from app.models.user import User
from app.schemas.recommendation import RecommendationRequest, RecommendationItem
from app.services.recommendation_service import generate_recommendations


router = APIRouter()


def get_owned_recipient(db: Session, recipient_id: int, user_id: int) -> Recipient:
    recipient = db.get(Recipient, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")
    if recipient.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return recipient


@router.post("/generate", response_model=list[RecommendationItem])
def recommend(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.budget_min > payload.budget_max:
        raise HTTPException(status_code=400, detail="budget_min не может быть больше budget_max")

    recipient = get_owned_recipient(db, payload.recipient_id, current_user.id)
    products = db.scalars(select(Product)).all()

    return generate_recommendations(
        recipient=recipient,
        products=products,
        budget_min=payload.budget_min,
        budget_max=payload.budget_max,
        categories=payload.categories,
        top_k=payload.top_k,
    )