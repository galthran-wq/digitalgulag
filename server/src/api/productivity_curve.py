import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.database import get_postgres_session
from src.models.postgres.users import UserModel
from src.repositories.productivity_points import ProductivityPointRepository
from src.schemas.productivity_points import (
    ProductivityCurveResponse,
    ProductivityPointResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/productivity-curve", tags=["productivity-curve"])

MAX_RANGE_DAYS = 90


def get_productivity_point_repository(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> ProductivityPointRepository:
    return ProductivityPointRepository(postgres_session)


@router.get("/{target_date}", response_model=ProductivityCurveResponse)
async def get_productivity_curve(
    target_date: date,
    current_user: UserModel = Depends(get_current_user),
    repo: ProductivityPointRepository = Depends(get_productivity_point_repository),
):
    points = await repo.get_by_date(current_user.id, target_date)

    work_scores = []
    work_count = 0
    for p in points:
        if p.is_work:
            work_count += 1
            if p.productivity_score is not None:
                work_scores.append(p.productivity_score)

    day_score = round(sum(work_scores) / len(work_scores), 1) if work_scores else None
    work_minutes = work_count * 10.0

    return ProductivityCurveResponse(
        date=target_date,
        points=[ProductivityPointResponse.model_validate(p) for p in points],
        day_score=day_score,
        work_minutes=work_minutes,
    )


@router.get("", response_model=list[ProductivityCurveResponse])
async def get_productivity_curve_range(
    start: date = Query(...),
    end: date = Query(...),
    current_user: UserModel = Depends(get_current_user),
    repo: ProductivityPointRepository = Depends(get_productivity_point_repository),
):
    if (end - start).days > MAX_RANGE_DAYS:
        raise HTTPException(status_code=400, detail=f"Date range must not exceed {MAX_RANGE_DAYS} days")
    if end < start:
        raise HTTPException(status_code=400, detail="end must be after start")

    all_points = await repo.get_by_date_range(current_user.id, start, end)

    by_date: dict[date, list] = {}
    for p in all_points:
        by_date.setdefault(p.date, []).append(p)

    results = []
    for d in sorted(by_date.keys()):
        points = by_date[d]
        work_scores = []
        work_count = 0
        for p in points:
            if p.is_work:
                work_count += 1
                if p.productivity_score is not None:
                    work_scores.append(p.productivity_score)

        day_score = round(sum(work_scores) / len(work_scores), 1) if work_scores else None
        work_minutes = work_count * 10.0

        results.append(ProductivityCurveResponse(
            date=d,
            points=[ProductivityPointResponse.model_validate(p) for p in points],
            day_score=day_score,
            work_minutes=work_minutes,
        ))

    return results
