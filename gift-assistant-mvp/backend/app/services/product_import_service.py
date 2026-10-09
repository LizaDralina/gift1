import csv
import io

from sqlalchemy.orm import Session

from app.models.product import Product
from app.utils.text import normalize_text, parse_tags


def import_products_from_csv(file_bytes: bytes, db: Session) -> int:
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    imported = 0

    for row in reader:
        try:
            name = (row.get("name") or "").strip()
            if not name:
                continue

            price = float(row.get("price") or 0)
            if price < 0:
                continue

            product = Product(
                name=name,
                description=(row.get("description") or "").strip(),
                price=price,
                category=normalize_text(row.get("category") or "other"),
                brand=(row.get("brand") or "").strip() or None,
                age_limit=int(row.get("age_limit") or 0),
                image_url=(row.get("image_url") or "").strip() or None,
                interest_tags=parse_tags(row.get("interest_tags")),
                occasion_tags=parse_tags(row.get("occasion_tags")),
                relationship_tags=parse_tags(row.get("relationship_tags")),
            )

            db.add(product)
            imported += 1
        except Exception:
            continue

    db.commit()
    return imported