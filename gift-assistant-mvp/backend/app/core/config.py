# import os


# class Settings:
#     APP_TITLE = os.getenv("APP_TITLE", "Gift Assistant MVP")
#     DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gift_mvp.db")
#     SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
#     ALGORITHM = os.getenv("ALGORITHM", "HS256")
#     ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

#     VK_CLIENT_ID = os.getenv("VK_CLIENT_ID", "")
#     VK_CLIENT_SECRET = os.getenv("VK_CLIENT_SECRET", "")
#     VK_REDIRECT_URI = os.getenv("VK_REDIRECT_URI", "http://localhost:5173/vk/callback")


# settings = Settings() 

import os


class Settings:
    APP_TITLE = os.getenv("APP_TITLE", "Gift Assistant MVP")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gift_mvp.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    VK_SERVICE_TOKEN = os.getenv("VK_SERVICE_TOKEN", "")
    VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")


settings = Settings()