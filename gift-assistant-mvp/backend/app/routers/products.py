from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductOut, ProductImportResult
from app.services.product_import_service import import_products_from_csv
from app.utils.text import normalize_text


router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(
    min_price: Optional[float] = Query(default=None),
    max_price: Optional[float] = Query(default=None),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    products = db.scalars(select(Product)).all()
    result = []

    for product in products:
        if min_price is not None and product.price < min_price:
            continue
        if max_price is not None and product.price > max_price:
            continue
        if category and normalize_text(product.category) != normalize_text(category):
            continue
        result.append(product)

    return result


@router.post("/import-csv", response_model=ProductImportResult)
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    imported = import_products_from_csv(content, db)
    return ProductImportResult(imported=imported)