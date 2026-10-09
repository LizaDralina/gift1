# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.core.security import get_current_user
# from app.models.recipient import Recipient
# from app.models.user import User
# from app.services.vk_service import (
#     get_vk_user_info,
#     get_vk_groups,
#     extract_vk_raw_interests,
#     map_vk_interests_to_internal,
# )
# from app.utils.text import normalize_list


# router = APIRouter()


# class VkImportTokenRequest(BaseModel):
#     recipient_id: int
#     access_token: str


# def get_owned_recipient(db: Session, recipient_id: int, user_id: int) -> Recipient:
#     recipient = db.get(Recipient, recipient_id)
#     if not recipient:
#         raise HTTPException(status_code=404, detail="Получатель не найден")
#     if recipient.user_id != user_id:
#         raise HTTPException(status_code=403, detail="Нет доступа")
#     return recipient


# @router.post("/import-token")
# def import_vk_token(
#     payload: VkImportTokenRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     recipient = get_owned_recipient(db, payload.recipient_id, current_user.id)

#     user_info = get_vk_user_info(payload.access_token)
#     groups_info = get_vk_groups(payload.access_token)

#     raw_interests = extract_vk_raw_interests(user_info, groups_info)
#     mapped_interests = map_vk_interests_to_internal(raw_interests)

#     merged = list(set(normalize_list(recipient.interests) + mapped_interests))
#     recipient.interests = merged

#     db.commit()
#     db.refresh(recipient)

#     return {
#         "recipient_id": recipient.id,
#         "imported_interests": mapped_interests,
#         "all_interests": recipient.interests,
#     }

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.recipient import Recipient
from app.models.user import User
from app.services.vk_service import (
    get_vk_user_public_info,
    try_get_vk_groups,
    extract_vk_raw_interests_from_public_profile,
    map_vk_interests_to_internal,
)
from app.utils.text import normalize_list


router = APIRouter()


class VkPublicImportRequest(BaseModel):
    recipient_id: int
    profile_input: str


def get_owned_recipient(db: Session, recipient_id: int, user_id: int) -> Recipient:
    recipient = db.get(Recipient, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")
    if recipient.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return recipient


@router.post("/import-public-profile")
def import_vk_public_profile(
    payload: VkPublicImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipient = get_owned_recipient(db, payload.recipient_id, current_user.id)

    try:
        user_info = get_vk_user_public_info(payload.profile_input)
        groups = try_get_vk_groups(user_info["id"])
        raw_interests = extract_vk_raw_interests_from_public_profile(user_info, groups)
        mapped_interests = map_vk_interests_to_internal(raw_interests)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка импорта VK: {str(e)}")

    merged = list(set(normalize_list(recipient.interests) + mapped_interests))
    recipient.interests = merged

    db.commit()
    db.refresh(recipient)

    return {
        "recipient_id": recipient.id,
        "vk_user_id": user_info["id"],
        "vk_screen_name": user_info.get("screen_name"),
        "imported_interests": mapped_interests,
        "all_interests": recipient.interests,
    }