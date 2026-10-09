from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    brand: Optional[str]
    age_limit: int
    image_url: Optional[str]
    interest_tags: List[str]
    occasion_tags: List[str]
    relationship_tags: List[str]

    model_config = ConfigDict(from_attributes=True)


class ProductImportResult(BaseModel):
    imported: int