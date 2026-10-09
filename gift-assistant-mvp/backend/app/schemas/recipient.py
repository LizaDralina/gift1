from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class RecipientCreate(BaseModel):
    age: int = Field(ge=0, le=120)
    gender: Optional[str] = None
    relationship_type: Optional[str] = None
    occasion: str
    interests: List[str] = []
    exclusions: List[str] = []


class RecipientUpdate(BaseModel):
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    relationship_type: Optional[str] = None
    occasion: Optional[str] = None
    interests: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None


class RecipientOut(BaseModel):
    id: int
    age: int
    gender: Optional[str]
    relationship_type: Optional[str]
    occasion: str
    interests: List[str]
    exclusions: List[str]

    model_config = ConfigDict(from_attributes=True)