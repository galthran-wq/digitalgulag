from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ProductivityPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interval_start: datetime
    focus_score: float | None
    depth: str | None
    category: str | None
    color: str | None
    is_work: bool
    productivity_score: float | None


class ProductivityCurveResponse(BaseModel):
    date: date
    points: list[ProductivityPointResponse]
    day_score: float | None
    work_minutes: float
