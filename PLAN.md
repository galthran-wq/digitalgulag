# TimeOracle — High-Level Architecture & Task Breakdown

## Context

TimeOracle is an AI-powered personal time tracker. A Rust daemon running on the user's machine captures activity data (active windows, URLs, app usage) and streams it to a server. On the server, an AI agent analyzes the raw data and produces a human-readable timeline — automatically labeling what you were doing without manual input. External sources (Oura ring, etc.) fill in offline/physical activity gaps. The frontend is a calendar-like view of your AI-generated day.

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐
│  Oura API   │     │ Future APIs │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────┐
│          FastAPI Server          │
│                                  │
│  ┌────────────┐ ┌─────────────┐  │
│  │ Ingestion  │ │ Integrations│  │
│  │ API        │ │ (Oura etc.) │  │
│  └─────┬──────┘ └──────┬──────┘  │
│        │               │         │
│        ▼               ▼         │
│  ┌───────────────────────────┐   │
│  │     PostgreSQL (raw       │   │
│  │     activity events)      │   │
│  └────────────┬──────────────┘   │
│               │                  │
│               ▼                  │
│  ┌───────────────────────────┐   │
│  │     AI Agent              │   │
│  │  (LLM-based analysis &    │   │
│  │   timeline generation)    │   │
│  └────────────┬──────────────┘   │
│               │                  │
│               ▼                  │
│  ┌───────────────────────────┐   │
│  │   Timeline API            │   │
│  │   (calendar entries)      │   │
│  └───────────────────────────┘   │
└──────────────┬───────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌────────┐         ┌───────────┐
│ Vue 3  │         │ Rust      │
│ Calendar│        │ Daemon    │
│ UI     │         │ (Linux/   │
│        │         │  macOS)   │
└────────┘         └───────────┘
```

## Data Model (core tables beyond existing `users`)

- **activity_events** — raw stream from daemon: `(user_id, timestamp, event_type, app_name, window_title, url, metadata_json)`
- **integration_events** — data from external APIs: `(user_id, source, timestamp, event_type, data_json)`
- **timeline_entries** — AI-generated calendar blocks: `(user_id, start_time, end_time, label, category, source_summary, confidence, edited_by_user)`

---

## Task 1: Rust Daemon — Activity Capture

### Goal
A lightweight background process that silently captures what the user is doing on their computer and reliably delivers that data to the TimeOracle server.

### Requirements
- Runs on Linux (X11 + Wayland) and macOS
- Captures: active window title, application name, and (where possible) browser URL
- Detects idle periods (no keyboard/mouse input for configurable threshold)
- Authenticates with the server using the user's JWT token
- Buffers events locally when the server is unreachable, flushes when connection resumes
- Minimal CPU/memory footprint — must not noticeably impact the user's machine
- Configurable polling interval (default ~5 seconds)
- Configurable ignore list (skip certain apps from tracking)

### High-Level Implementation Plan
1. **Project setup**: Create a new Rust crate (`daemon/`) with a workspace layout. Dependencies: `tokio` (async runtime), `reqwest` (HTTP client), `serde`/`serde_json` (serialization), `dirs` (config paths), platform-specific crates.
2. **Platform abstraction layer**: Define a trait `ActivitySource` with `fn get_active_window() -> WindowInfo`. Implement separately:
   - **Linux**: Use `xcb` crate for X11, `wayland-client` or D-Bus (`org.freedesktop.portal`) for Wayland.
   - **macOS**: Use `core-graphics` crate (`CGWindowListCopyWindowInfo`) and accessibility APIs.
3. **Idle detection**: Monitor last input time. Linux: read from `/proc/interrupts` or X11 screensaver extension. macOS: `CGEventSourceSecondsSinceLastEventType`.
4. **Event loop**: Tokio-based loop — poll every N seconds, diff against last state, emit `ActivityEvent` structs when the active window changes or periodically.
5. **Local buffer**: SQLite file in `~/.timeoracle/buffer.db`. Write events there first. A separate flush task sends batches to `POST /api/activity/events` and deletes on success.
6. **Auth**: Read JWT from `~/.timeoracle/config.toml`. Provide a `timeoracle-daemon login` CLI command that hits the server's login endpoint and stores the token.
7. **Service installation**: Provide `timeoracle-daemon install` command that writes a systemd unit file (Linux) or LaunchAgent plist (macOS).
8. **Config**: TOML file at `~/.timeoracle/config.toml` — server URL, token, poll interval, ignore list.

---

## Task 2: Activity Ingestion API

### Goal
Server-side endpoints that receive raw activity data from daemons, validate it, and store it efficiently for later AI processing.

### Requirements
- Accept batches of activity events from authenticated users
- Validate event schema (required fields, timestamp sanity)
- Store events in PostgreSQL with proper indexing for time-range queries
- Allow users to query their own raw events (for debugging and transparency)
- Handle high write throughput (a user generates ~1 event every 5 seconds)

### High-Level Implementation Plan
1. **Database model**: Create SQLAlchemy model `ActivityEvent` in `server/src/models/postgres/activity_events.py`. Columns: `id (UUID)`, `user_id (FK)`, `timestamp (DateTime, indexed)`, `event_type (String)`, `app_name`, `window_title`, `url (nullable)`, `metadata (JSONB)`. Add composite index on `(user_id, timestamp)`.
2. **Alembic migration**: Generate migration for the `activity_events` table.
3. **Repository**: `ActivityEventRepository` in `server/src/repositories/activity_events.py` — methods: `bulk_create(events)`, `get_by_time_range(user_id, start, end)`, `get_latest(user_id, limit)`.
4. **Schemas**: Pydantic models in `server/src/schemas/` — `ActivityEventCreate`, `ActivityEventResponse`, `ActivityEventBatch`.
5. **API endpoints** in `server/src/api/activity.py`:
   - `POST /api/activity/events` — accepts a list of events, bulk inserts. Returns count of inserted events.
   - `GET /api/activity/events?start=...&end=...` — returns user's events in a time range, paginated.
6. **Wire into FastAPI**: Register the router in `main.py`.

---

## Task 3: External Integrations Framework + Oura

### Goal
A pluggable system for connecting third-party data sources that provide context about what the user was doing when they weren't at their computer (sleep, exercise, location, etc.).

### Requirements
- Generic integration interface so adding new sources is straightforward
- Store integration credentials securely per user
- Periodic background sync to pull new data
- Normalize external data into `integration_events` table
- Oura Ring as the first integration: pull sleep, activity, and readiness scores
- User can connect/disconnect integrations via API

### High-Level Implementation Plan
1. **Integration base class**: `server/src/integrations/base.py` — abstract class `Integration` with methods: `authorize(credentials) -> bool`, `sync(user_id, since_date) -> list[IntegrationEvent]`, `get_source_name() -> str`.
2. **Database models**:
   - `UserIntegration` table: `(user_id, source, credentials_encrypted, last_synced_at, enabled)` — stores per-user connection state.
   - `IntegrationEvent` table: `(user_id, source, timestamp, event_type, data_json)`.
3. **Alembic migrations** for both tables.
4. **Integration registry**: A dict mapping source names to integration classes. New integrations just register themselves.
5. **API endpoints** in `server/src/api/integrations.py`:
   - `GET /api/integrations` — list available integrations and user's connection status.
   - `POST /api/integrations/{source}/connect` — save credentials / initiate OAuth.
   - `DELETE /api/integrations/{source}/disconnect` — remove connection.
   - `POST /api/integrations/{source}/sync` — manually trigger a sync.
6. **Background sync**: Use `APScheduler` (already easy to add to FastAPI). Run every N hours: for each user with active integrations, call `integration.sync()` and store new events.
7. **Oura implementation** in `server/src/integrations/oura.py`:
   - Oura API v2 (`https://cloud.ouraring.com/v2/usercollection/...`).
   - Pull daily sleep periods, activity sessions, readiness scores.
   - Map to `IntegrationEvent` records with `source="oura"`, `event_type` in `{"sleep", "activity", "readiness"}`.

---

## Task 4: AI Agent — Timeline Generation

### Goal
Analyze raw activity data and external integration data to produce a clean, human-readable timeline of the user's day — labeled and categorized without manual effort.

### Requirements
- Group raw activity events into coherent sessions (e.g., "45 min coding in VS Code")
- Merge integration data (sleep, exercise) into the timeline
- Use an LLM (Claude API) to interpret and label the sessions
- Produce structured timeline entries with: time range, label, category, confidence
- Allow on-demand generation (user requests it) and scheduled generation
- Support user corrections that persist and improve future results
- Handle a full day of data (potentially thousands of raw events) within reasonable token limits

### High-Level Implementation Plan
1. **Pre-processing / clustering** in `server/src/services/activity_clusterer.py`:
   - Query all `activity_events` for a user + date.
   - Group consecutive events with the same app into sessions. Merge sessions separated by <2 min gaps.
   - Output: list of `ActivitySession(app, window_titles[], start, end, duration_minutes)`.
2. **Context builder** in `server/src/services/timeline_context.py`:
   - Take clustered sessions + integration events for the day.
   - Build a compact text summary: "9:00-9:45 — VS Code (files: auth.py, users.py), 9:45-10:00 — Chrome (GitHub, Stack Overflow), ... Oura: slept 11pm-7am".
   - This is what gets sent to the LLM. Keep it under token limits by summarizing window titles, deduplicating, etc.
3. **LLM integration** in `server/src/services/timeline_generator.py`:
   - Call Claude API with a system prompt: "You are a time-tracking assistant. Given the following computer activity and health data, produce a timeline..."
   - Structured output: list of `{start, end, label, category, confidence}`.
   - Parse the LLM response into `TimelineEntry` objects.
4. **Database model**: `TimelineEntry` in `server/src/models/postgres/timeline_entries.py`. Columns: `id`, `user_id`, `date`, `start_time`, `end_time`, `label`, `category`, `source_summary`, `confidence`, `edited_by_user (bool)`, `created_at`.
5. **API endpoints** in `server/src/api/timeline.py`:
   - `POST /api/timeline/generate` — trigger generation for a date. Returns the generated entries.
   - `GET /api/timeline?date=...&range=day|week` — fetch timeline entries.
   - `PATCH /api/timeline/{id}` — user edits (change label, adjust times). Sets `edited_by_user=true`.
   - `DELETE /api/timeline/{id}` — remove an entry.
6. **Scheduled generation**: Optional APScheduler job that runs at end-of-day (e.g., 23:00 user's local time) to auto-generate if not already done.

---

## Task 5: Frontend — Calendar UI

### Goal
A clean calendar interface where users see their AI-generated timeline and can interact with it — review what they did, correct mistakes, and trigger new analyses.

### Requirements
- Day view: 24-hour vertical timeline with colored blocks for each activity
- Week view: condensed daily summaries
- Activity blocks show label, category, and time range
- Click a block to see details: AI reasoning, raw source events, confidence score
- Inline editing: rename, recategorize, adjust start/end times
- "Generate" button to trigger AI analysis for a date
- Authentication: login/register pages using existing JWT backend
- Integration settings page: connect/disconnect external sources
- Responsive layout (desktop-first, functional on mobile)

### High-Level Implementation Plan
1. **API client layer**: `client/src/api/` — Axios (or fetch wrapper) configured with JWT auth header from Pinia store. Modules: `auth.ts`, `activity.ts`, `timeline.ts`, `integrations.ts`.
2. **Auth store + pages**:
   - Pinia store `client/src/stores/auth.ts`: holds JWT, user info, login/logout/register actions.
   - Pages: `LoginView.vue`, `RegisterView.vue`. Redirect to calendar after auth.
3. **Router setup**: `/login`, `/register`, `/` (day view), `/week` (week view), `/settings` (integrations). Auth guard on protected routes.
4. **Day view** (`client/src/views/DayView.vue`):
   - Vertical axis: hours 0-24. Each `TimelineEntry` rendered as a positioned block (`top` = start time, `height` = duration).
   - Color-coded by category (work, communication, browsing, rest, etc.).
   - Date picker to navigate between days.
   - "Generate Timeline" button → calls `POST /api/timeline/generate`, refreshes view.
5. **Week view** (`client/src/views/WeekView.vue`):
   - 7 columns, each showing stacked category totals for the day. Click a day → navigate to day view.
6. **Detail panel** (`client/src/components/EntryDetail.vue`):
   - Slide-out or modal when clicking a block. Shows: label, category, time range, confidence, source summary.
   - Edit form: inline-editable label and category, draggable time handles.
   - Save → `PATCH /api/timeline/{id}`.
7. **Settings page** (`client/src/views/SettingsView.vue`):
   - List of available integrations. Connect/disconnect buttons. Shows last sync time.
8. **Styling**: Use a lightweight CSS framework or utility classes. Keep it minimal and clean — the timeline blocks themselves are the main UI element.

---

## Task 6: Polish & Ops

### Goal
Make the product installable, reliable, and ready for real daily use.

### Requirements
- Easy daemon installation on Linux and macOS
- Production deployment is stable and monitored
- New users can go from zero to seeing their first timeline with minimal friction

### High-Level Implementation Plan
1. **Daemon packaging**:
   - Linux: `.deb` package via `cargo-deb`, plus a shell install script. Systemd service included.
   - macOS: Homebrew formula or downloadable binary + install script. LaunchAgent plist included.
   - Both: `timeoracle-daemon setup` wizard — prompts for server URL, authenticates, installs service.
2. **Production hardening**:
   - Rate limiting on ingestion endpoint (per-user, token bucket).
   - CORS config for the frontend domain.
   - Input sanitization on all endpoints.
   - Graceful error responses (no stack traces in prod).
3. **Monitoring**:
   - Add Prometheus metrics: events ingested/sec, timeline generations/day, integration sync success/failure.
   - Grafana dashboard for operational visibility.
4. **Onboarding flow**:
   - After first login, frontend shows a setup wizard: "Install the daemon" (platform-specific instructions) → "Connect integrations" (optional) → "Generate your first timeline".

---

## Execution Order

```
1 (Daemon) ──────┐
                  ├──→ 4 (AI Agent) ──→ 6 (Polish)
2 (Ingest API) ──┤
                  │
3 (Integrations)─┘

5 (Frontend) ─── starts early with mocks, integrates with 4 later
```

Tasks 1 and 2 can start in parallel. Task 3 is independent. Task 4 depends on 2+3. Task 5 starts early with mock data. Task 6 is last.
