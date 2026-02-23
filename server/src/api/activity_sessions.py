import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.database import get_postgres_session
from src.models.postgres.users import UserModel
from src.repositories.activity_sessions import ActivitySessionRepository
from src.schemas.activity_sessions import (
    ActivitySessionListResponse,
    ActivitySessionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/activity/sessions", tags=["activity-sessions"])


def get_session_repo(
    session: AsyncSession = Depends(get_postgres_session),
) -> ActivitySessionRepository:
    return ActivitySessionRepository(session)


@router.get("", response_model=ActivitySessionListResponse)
async def list_sessions(
    date: date = Query(description="Start date (YYYY-MM-DD)"),
    range: str = Query(default="day", pattern="^(day|week)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    session_repo: ActivitySessionRepository = Depends(get_session_repo),
):
    start_date = date
    if range == "week":
        end_date = date + timedelta(days=6)
    else:
        end_date = date

    sessions = await session_repo.get_by_date_range(
        current_user.id, start_date, end_date, limit, offset,
    )
    total_count = await session_repo.count_by_date_range(
        current_user.id, start_date, end_date,
    )

    return ActivitySessionListResponse(
        sessions=[ActivitySessionResponse.model_validate(s) for s in sessions],
        total_count=total_count,
        limit=limit,
        offset=offset,
    )
