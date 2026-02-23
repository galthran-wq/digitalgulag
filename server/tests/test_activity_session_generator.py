import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.postgres.users import UserModel
from src.repositories.activity_events import ActivityEventRepository
from src.repositories.activity_sessions import ActivitySessionRepository
from src.schemas.activity_events import ActivityEventCreate, ActivityEventType
from src.services.activity_session_generator import ActivitySessionGenerator


def _event(
    event_type: str,
    timestamp: datetime,
    app_name: str = "Firefox",
    window_title: str = "Home",
    url: str | None = None,
) -> ActivityEventCreate:
    return ActivityEventCreate(
        client_event_id=uuid.uuid4(),
        timestamp=timestamp,
        event_type=event_type,
        app_name=app_name,
        window_title=window_title,
        url=url,
    )


async def _seed_events(
    repo: ActivityEventRepository, user_id: uuid.UUID, events: list[ActivityEventCreate],
) -> None:
    await repo.bulk_create(user_id, events)


class TestActivitySessionGenerator:
    async def test_consecutive_windows_create_sessions(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="GitHub"),
            _event("active_window", base + timedelta(minutes=15), app_name="VSCode", window_title="main.py"),
            _event("active_window", base + timedelta(minutes=45), app_name="Chrome", window_title="Docs"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        count = await generator.generate_for_date(test_user.id, date(2026, 2, 23))
        assert count == 3

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        assert len(sessions) == 3

        assert sessions[0].app_name == "Firefox"
        assert sessions[0].start_time == base
        assert sessions[0].end_time == base + timedelta(minutes=15)

        assert sessions[1].app_name == "VSCode"
        assert sessions[1].start_time == base + timedelta(minutes=15)
        assert sessions[1].end_time == base + timedelta(minutes=45)

        assert sessions[2].app_name == "Chrome"

    async def test_idle_gap_ends_session(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="VSCode", window_title="main.py"),
            _event("idle_start", base + timedelta(minutes=30)),
            _event("idle_end", base + timedelta(minutes=45)),
            _event("active_window", base + timedelta(minutes=45), app_name="Chrome", window_title="Search"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        count = await generator.generate_for_date(test_user.id, date(2026, 2, 23))
        assert count == 2

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        assert sessions[0].app_name == "VSCode"
        assert sessions[0].end_time == base + timedelta(minutes=30)

        assert sessions[1].app_name == "Chrome"
        assert sessions[1].start_time == base + timedelta(minutes=45)

    async def test_same_app_heartbeats_merge(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="VSCode", window_title="main.py"),
            _event("active_window", base + timedelta(minutes=5), app_name="VSCode", window_title="utils.py"),
            _event("active_window", base + timedelta(minutes=10), app_name="VSCode", window_title="test.py"),
            _event("active_window", base + timedelta(minutes=15), app_name="Firefox", window_title="Docs"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        count = await generator.generate_for_date(test_user.id, date(2026, 2, 23))
        assert count == 2

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        assert sessions[0].app_name == "VSCode"
        assert sessions[0].start_time == base
        assert sessions[0].end_time == base + timedelta(minutes=15)
        assert set(sessions[0].window_titles) == {"main.py", "utils.py", "test.py"}

    async def test_short_sessions_dropped(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="Home"),
            # 2-second alt-tab to Terminal
            _event("active_window", base + timedelta(seconds=2), app_name="Terminal", window_title="bash"),
            # Back to Firefox
            _event("active_window", base + timedelta(seconds=4), app_name="Firefox", window_title="Home"),
            _event("active_window", base + timedelta(minutes=10), app_name="Chrome", window_title="Search"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        count = await generator.generate_for_date(test_user.id, date(2026, 2, 23))

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        # Terminal session (2s) dropped; the two Firefox segments merge
        app_names = [s.app_name for s in sessions]
        assert "Terminal" not in app_names
        assert sessions[0].app_name == "Firefox"

    async def test_regeneration_replaces_old_sessions(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="Home"),
            _event("active_window", base + timedelta(minutes=10), app_name="Chrome", window_title="Search"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        count1 = await generator.generate_for_date(test_user.id, date(2026, 2, 23))
        assert count1 == 2

        # Re-generate should replace, not duplicate
        count2 = await generator.generate_for_date(test_user.id, date(2026, 2, 23))
        assert count2 == 2

        total = await session_repo.count_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23),
        )
        assert total == 2

    async def test_empty_day_returns_zero(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        count = await generator.generate_for_date(test_user.id, date(2026, 2, 23))
        assert count == 0

    async def test_single_event_capped_at_end_of_day(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        # Use a recent past date to ensure day_end < now(), so cap = day_end
        target = date(2026, 2, 22)
        base = datetime(2026, 2, 22, 22, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="Home"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        count = await generator.generate_for_date(test_user.id, target)
        assert count == 1

        sessions = await session_repo.get_by_date_range(
            test_user.id, target, target, limit=100, offset=0,
        )
        assert len(sessions) == 1
        # end_time should be capped at end of day (not equal to start_time)
        assert sessions[0].end_time > sessions[0].start_time
        day_end = datetime(2026, 2, 22, 23, 59, 59, 999999, tzinfo=timezone.utc)
        assert sessions[0].end_time <= day_end

    async def test_window_titles_collected(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="Tab 1", url="https://example.com"),
            _event("active_window", base + timedelta(minutes=5), app_name="Firefox", window_title="Tab 2"),
            _event("active_window", base + timedelta(minutes=10), app_name="Firefox", window_title="Tab 1"),
            _event("active_window", base + timedelta(minutes=15), app_name="Chrome", window_title="Docs"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        await generator.generate_for_date(test_user.id, date(2026, 2, 23))

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        firefox = sessions[0]
        assert firefox.window_title == "Tab 1"
        assert set(firefox.window_titles) == {"Tab 1", "Tab 2"}
        assert firefox.url == "https://example.com"


class TestIncrementalGeneration:
    async def test_first_batch_creates_sessions(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="GitHub"),
            _event("active_window", base + timedelta(minutes=15), app_name="VSCode", window_title="main.py"),
            _event("active_window", base + timedelta(minutes=45), app_name="Chrome", window_title="Docs"),
        ]
        await _seed_events(activity_repo, test_user.id, events)

        timestamps = [e.timestamp for e in events]
        count = await generator.generate_incremental(test_user.id, timestamps)
        assert count == 3

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        assert len(sessions) == 3
        assert sessions[0].app_name == "Firefox"
        assert sessions[1].app_name == "VSCode"
        assert sessions[2].app_name == "Chrome"

    async def test_second_batch_extends_sessions(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)

        # First batch
        batch1 = [
            _event("active_window", base, app_name="Firefox", window_title="GitHub"),
            _event("active_window", base + timedelta(minutes=15), app_name="VSCode", window_title="main.py"),
        ]
        await _seed_events(activity_repo, test_user.id, batch1)
        await generator.generate_incremental(test_user.id, [e.timestamp for e in batch1])

        # Second batch — continues from where we left off
        batch2 = [
            _event("active_window", base + timedelta(minutes=30), app_name="VSCode", window_title="utils.py"),
            _event("active_window", base + timedelta(minutes=45), app_name="Chrome", window_title="Docs"),
        ]
        await _seed_events(activity_repo, test_user.id, batch2)
        await generator.generate_incremental(test_user.id, [e.timestamp for e in batch2])

        sessions = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        assert len(sessions) == 3
        assert sessions[0].app_name == "Firefox"
        assert sessions[1].app_name == "VSCode"
        assert sessions[1].end_time == base + timedelta(minutes=45)
        assert sessions[2].app_name == "Chrome"

    async def test_late_arriving_old_events_trigger_rebuild(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)

        # First batch: events from 14:30 onward
        batch1 = [
            _event("active_window", base + timedelta(minutes=30), app_name="VSCode", window_title="main.py"),
            _event("active_window", base + timedelta(minutes=45), app_name="Chrome", window_title="Docs"),
        ]
        await _seed_events(activity_repo, test_user.id, batch1)
        await generator.generate_incremental(test_user.id, [e.timestamp for e in batch1])

        sessions_before = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        assert len(sessions_before) == 2

        # Late-arriving batch: events from 14:00 (earlier than existing sessions)
        batch2 = [
            _event("active_window", base, app_name="Firefox", window_title="GitHub"),
            _event("active_window", base + timedelta(minutes=15), app_name="Firefox", window_title="PR Review"),
        ]
        await _seed_events(activity_repo, test_user.id, batch2)
        await generator.generate_incremental(test_user.id, [e.timestamp for e in batch2])

        sessions_after = await session_repo.get_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23), limit=100, offset=0,
        )
        # Should rebuild from 14:00 onward: Firefox(14:00-14:30), VSCode(14:30-14:45), Chrome(14:45+)
        assert len(sessions_after) == 3
        assert sessions_after[0].app_name == "Firefox"
        assert sessions_after[0].start_time == base
        assert sessions_after[1].app_name == "VSCode"
        assert sessions_after[2].app_name == "Chrome"

    async def test_idempotent_same_batch_twice(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        base = datetime(2026, 2, 23, 14, 0, tzinfo=timezone.utc)
        events = [
            _event("active_window", base, app_name="Firefox", window_title="GitHub"),
            _event("active_window", base + timedelta(minutes=15), app_name="VSCode", window_title="main.py"),
        ]
        await _seed_events(activity_repo, test_user.id, events)
        timestamps = [e.timestamp for e in events]

        count1 = await generator.generate_incremental(test_user.id, timestamps)
        count2 = await generator.generate_incremental(test_user.id, timestamps)

        # Both calls should produce same result
        assert count1 == count2

        total = await session_repo.count_by_date_range(
            test_user.id, date(2026, 2, 23), date(2026, 2, 23),
        )
        assert total == count1

    async def test_empty_timestamps_returns_zero(
        self, db_session: AsyncSession, test_user: UserModel,
    ):
        activity_repo = ActivityEventRepository(db_session)
        session_repo = ActivitySessionRepository(db_session)
        generator = ActivitySessionGenerator(activity_repo, session_repo)

        count = await generator.generate_incremental(test_user.id, [])
        assert count == 0
