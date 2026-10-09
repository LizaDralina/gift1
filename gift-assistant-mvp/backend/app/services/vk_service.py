# from typing import List
# import requests

# from app.utils.text import normalize_list

# VK_API_VERSION = "5.199"

# INTEREST_MAPPING = {
#     "астрономия": "космос",
#     "космос": "космос",
#     "наука": "наука",
#     "книги": "книги",
#     "литература": "книги",
#     "музыка": "музыка",
#     "техника": "техника",
#     "гаджеты": "техника",
#     "спорт": "спорт",
#     "кино": "кино",
#     "фильмы": "кино",
#     "игры": "настольные игры",
#     "настольные игры": "настольные игры",
#     "путешествия": "путешествия",
#     "программирование": "техника",
# }


# def get_vk_user_info(access_token: str) -> dict:
#     response = requests.get(
#         "https://api.vk.com/method/users.get",
#         params={
#             "fields": "interests,music,movies,books,games,activities",
#             "access_token": access_token,
#             "v": VK_API_VERSION,
#         },
#         timeout=10,
#     )
#     response.raise_for_status()
#     return response.json()


# def get_vk_groups(access_token: str) -> dict:
#     response = requests.get(
#         "https://api.vk.com/method/groups.get",
#         params={
#             "extended": 1,
#             "access_token": access_token,
#             "v": VK_API_VERSION,
#         },
#         timeout=10,
#     )
#     response.raise_for_status()
#     return response.json()


# def extract_vk_raw_interests(user_info: dict, groups_info: dict) -> List[str]:
#     raw = []

#     users = user_info.get("response", [])
#     if users:
#         user = users[0]
#         for field in ["interests", "music", "movies", "books", "games", "activities"]:
#             value = user.get(field)
#             if value:
#                 raw.extend(
#                     [x.strip().lower() for x in str(value).replace(";", ",").split(",") if x.strip()]
#                 )

#     groups = groups_info.get("response", {}).get("items", [])
#     for group in groups:
#         name = group.get("name")
#         if name:
#             raw.append(name.strip().lower())

#     return raw


# def map_vk_interests_to_internal(raw_interests: List[str]) -> List[str]:
#     mapped = set()

#     for item in raw_interests:
#         item_lower = item.lower()
#         for vk_key, internal_value in INTEREST_MAPPING.items():
#             if vk_key in item_lower:
#                 mapped.add(internal_value)

#     return normalize_list(list(mapped))

import re
from typing import List, Optional
from urllib.parse import urlparse

import requests

from app.core.config import settings
from app.utils.text import normalize_list


INTEREST_MAPPING = {
    "астрономия": "космос",
    "космос": "космос",
    "наука": "наука",
    "книги": "книги",
    "литература": "книги",
    "музыка": "музыка",
    "техника": "техника",
    "гаджеты": "техника",
    "спорт": "спорт",
    "кино": "кино",
    "фильмы": "кино",
    "игры": "настольные игры",
    "настольные игры": "настольные игры",
    "путешествия": "путешествия",
    "программирование": "техника",
    "it": "техника",
}


def build_vk_api_params(params: dict) -> dict:
    result = params.copy()
    result["v"] = settings.VK_API_VERSION

    if settings.VK_SERVICE_TOKEN:
        result["access_token"] = settings.VK_SERVICE_TOKEN

    return result


def vk_api_get(method: str, params: dict) -> dict:
    response = requests.get(
        f"https://api.vk.com/method/{method}",
        params=build_vk_api_params(params),
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(str(data["error"]))

    return data


def extract_vk_identifier(profile_input: str) -> str:
    value = (profile_input or "").strip()

    if not value:
        raise ValueError("Пустой VK профиль")

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        path = parsed.path.strip("/")
        if not path:
            raise ValueError("Не удалось извлечь путь из VK URL")
        return path.split("/")[0]

    return value


def get_vk_user_public_info(profile_input: str) -> dict:
    identifier = extract_vk_identifier(profile_input)

    data = vk_api_get(
        "users.get",
        {
            "user_ids": identifier,
            "fields": "about,activities,books,games,interests,movies,music,screen_name",
        },
    )

    users = data.get("response", [])
    if not users:
        raise RuntimeError("Пользователь VK не найден")

    return users[0]


def try_get_vk_groups(user_id: int) -> List[dict]:
    try:
        data = vk_api_get(
            "groups.get",
            {
                "user_id": user_id,
                "extended": 1,
                "count": 100,
            },
        )
        return data.get("response", {}).get("items", [])
    except Exception:
        # если группы скрыты или недоступны — просто вернем пустой список
        return []


def extract_vk_raw_interests_from_public_profile(user_info: dict, groups: List[dict]) -> List[str]:
    raw = []

    for field in ["about", "activities", "books", "games", "interests", "movies", "music"]:
        value = user_info.get(field)
        if value:
            raw.extend([x.strip().lower() for x in str(value).replace(";", ",").split(",") if x.strip()])

    for group in groups:
        name = group.get("name")
        description = group.get("description")

        if name:
            raw.append(str(name).strip().lower())

        if description:
            raw.extend(
                [x.strip().lower() for x in re.split(r"[,.!?:;]", str(description)) if x.strip()]
            )

    return raw


def map_vk_interests_to_internal(raw_interests: List[str]) -> List[str]:
    mapped = set()

    for item in raw_interests:
        item_lower = item.lower()
        for vk_key, internal_value in INTEREST_MAPPING.items():
            if vk_key in item_lower:
                mapped.add(internal_value)

    return normalize_list(list(mapped))