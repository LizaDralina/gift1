from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    recipient_id: int
    budget_min: float = Field(ge=0)
    budget_max: float = Field(gt=0)
    categories: List[str] = []
    top_k: int = Field(default=10, ge=1, le=20)


class RecommendationItem(BaseModel):
    product_id: int
    name: str
    description: str
    price: float
    category: str
    brand: Optional[str]
    image_url: Optional[str]
    score: float
    reasons: List[str]