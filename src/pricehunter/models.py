from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Currency(str, Enum):
    LKR = "LKR"
    USD = "USD"


class ResearchItem(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class PriceCandidate(BaseModel):
    item_name: str
    vendor: str
    title: str
    price: Decimal = Field(ge=0)
    currency: Currency = Currency.LKR
    url: str | None = None
    availability: str | None = None
    confidence: float = Field(default=0, ge=0, le=1)
    notes: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ItemRecommendation(BaseModel):
    item: ResearchItem
    candidates: list[PriceCandidate] = Field(default_factory=list)
    recommended: PriceCandidate | None = None
    estimated_total: Decimal = Decimal("0")
    confidence: float = Field(default=0, ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    items: list[ItemRecommendation]
    grand_total: Decimal = Decimal("0")
    currency: Currency = Currency.LKR
    warnings: list[str] = Field(default_factory=list)


class ResearchRequest(BaseModel):
    items: list[ResearchItem] = Field(min_length=1)
    max_candidates_per_item: int = Field(default=5, ge=1, le=20)


class ResearchResponse(BaseModel):
    report: ResearchReport
