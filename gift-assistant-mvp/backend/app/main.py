from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.routers.auth import router as auth_router
from app.routers.recipients import router as recipients_router
from app.routers.products import router as products_router
from app.routers.recommendations import router as recommendations_router
from app.ml.model_loader import load_model
from app.routers.vk import router as vk_router

app = FastAPI(title="Gift Assistant MVP")


# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    load_model()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(recipients_router, prefix="/recipients", tags=["recipients"])
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
app.include_router(vk_router, prefix="/vk", tags=["vk"])

@app.get("/health")
def health():
    return {"status": "ok"}