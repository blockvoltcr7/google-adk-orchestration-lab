# Google ADK: DatabaseSessionService Masterclass

This guide teaches how to use **`DatabaseSessionService`** in Google's Agent Development Kit (ADK) to build durable, scalable, and multi-turn stateful AI applications.

---

## 1. Overview & Conceptual Architecture

In Google ADK, agents are stateless decision engines; conversation history, variable memory, and user state are managed externally by a **Session Service**.

While ADK defaults to `InMemorySessionService` for rapid local testing, production systems require persistent storage that survives server restarts, enables horizontal scaling across container replicas, and maintains state integrity.

### Comparison of ADK Session Services

| Feature | `InMemorySessionService` | `DatabaseSessionService` | `VertexAiSessionService` |
|---|---|---|---|
| **Storage Backend** | RAM (In-process dict) | Relational SQL (SQLAlchemy 2.x) | Managed Google Cloud Vertex AI |
| **Persistence** | Volatile (Lost on restart) | Permanent (Disk / Managed DB) | Permanent (Managed GCP service) |
| **Scaling** | Single process only | Multi-instance / Distributed pool | Serverless / Cloud managed |
| **Supported DBs** | N/A | SQLite, PostgreSQL, MySQL, MariaDB, Spanner | GCP Cloud Vertex AI |
| **Best For** | Unit testing, local prototypes | Custom backends, Cloud SQL, self-hosted DBs | Fully managed GCP cloud deployments |

---

## 2. ADK Relational Database Schema (V1 Schema)

`DatabaseSessionService` automatically manages relational tables via SQLAlchemy ORM models. When initialized, ADK creates the following schema:

```mermaid
erDiagram
    STORAGE_SESSIONS ||--o{ STORAGE_EVENTS : "contains"
    STORAGE_APP_STATES ||--o{ STORAGE_USER_STATES : "scoped under app"
    STORAGE_USER_STATES ||--o{ STORAGE_SESSIONS : "owns"

    STORAGE_SESSIONS {
        string app_name PK
        string user_id PK
        string id PK
        json state "Session-scoped state"
        datetime create_time
        datetime update_time
    }

    STORAGE_APP_STATES {
        string app_name PK
        json state "Global app state"
    }

    STORAGE_USER_STATES {
        string app_name PK
        string user_id PK
        json state "Per-user state across sessions"
    }

    STORAGE_EVENTS {
        integer id PK
        string app_name
        string user_id
        string session_id
        string invocation_id
        string author "user | model | system"
        json content "Gemini Content payload"
        json actions "State deltas & side effects"
        datetime timestamp
        string isolation_scope
    }

    STORAGE_METADATA {
        string key PK
        string value "Schema version ('v1')"
    }
```

### State Key Namespaces & Merging Logic

ADK implements a 3-tier state scope:

1. **Session State**: Keys stored directly in `storage_sessions.state` (e.g., `current_topic`).
2. **User State**: Keys prefixed with `user:` stored in `storage_user_states.state` (e.g., `user:preferred_language`). Persistent across all sessions belonging to the same user.
3. **App State**: Keys prefixed with `app:` stored in `storage_app_states.state` (e.g., `app:system_maintenance`). Shared globally across all users of the application.

When `get_session()` is called, ADK executes `_merge_state()` to present a unified dictionary to the agent:

$$\text{Merged State} = \text{Session State} \cup \{ \text{"app:"} + k \mid k \in \text{App State} \} \cup \{ \text{"user:"} + k \mid k \in \text{User State} \}$$

---

## 3. Initialization & Engine Configuration

`DatabaseSessionService` can be instantiated in two primary ways:

### Method A: Connection URL String (`db_url`)

ADK creates and manages the underlying SQLAlchemy `AsyncEngine` internally:

```python
from google.adk.sessions import DatabaseSessionService

# 1. SQLite (File-based async database)
session_service = DatabaseSessionService(
    db_url="sqlite+aiosqlite:///./adk_sessions.db"
)

# 2. PostgreSQL (Cloud SQL / Self-hosted)
pg_session_service = DatabaseSessionService(
    db_url="postgresql+asyncpg://dbuser:secret@localhost:5432/agent_db"
)
```

### Method B: Existing SQLAlchemy `AsyncEngine` (`db_engine`)

Inject a custom pre-configured `AsyncEngine` (ideal for enterprise web frameworks like FastAPI, Cloud Run, or custom connection pooling):

```python
from sqlalchemy.ext.asyncio import create_async_engine
from google.adk.sessions import DatabaseSessionService

# Create custom engine with tuned pool parameters
engine = create_async_engine(
    "postgresql+asyncpg://dbuser:secret@localhost:5432/agent_db",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

session_service = DatabaseSessionService(db_engine=engine)
```

### Eager Table Initialization

By default, tables are created lazily on the first session operation. For production workloads, call `prepare_tables()` eagerly during application startup:

```python
await session_service.prepare_tables()
```

---

## 4. End-to-End Code Example with ADK `Runner`

Below is a complete, runnable example demonstrating multi-turn conversation persistence across script executions using SQLite:

```python
import asyncio
import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai.types import Content

async def run_agent_turn(user_message: str, user_id: str, session_id: str):
    # 1. Initialize DatabaseSessionService with an async SQLite DB
    session_service = DatabaseSessionService(
        db_url="sqlite+aiosqlite:///./fitness_app.db"
    )

    # 2. Eagerly prepare tables
    await session_service.prepare_tables()

    # 3. Create Root Agent
    agent = LlmAgent(
        name="fitness_coach",
        model="gemini-2.5-flash",
        instruction="You are a personal fitness coach. Remember the user's goals and preferences."
    )

    # 4. Pass session_service to Runner
    runner = Runner(
        app_name="fitness-onboarding",
        agent=agent,
        session_service=session_service,
        auto_create_session=True,  # Auto-create session if it doesn't exist yet
    )

    # 5. Run turn asynchronously
    print(f"\nUser > {user_message}")
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=Content.from_text(user_message),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Coach > {part.text}")

async def main():
    user_id = "student_01"
    session_id = "session_workout_plan"

    # Turn 1: Provide preference
    await run_agent_turn(
        "Hi! My name is Jordan and I prefer 30-minute bodyweight workouts.",
        user_id,
        session_id
    )

    # Turn 2: Follow-up question relying on persisted memory
    await run_agent_turn(
        "Can you recommend a Monday routine based on my preferences?",
        user_id,
        session_id
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Direct Session API Reference (CRUD Operations)

Beyond agent runs, `DatabaseSessionService` provides direct programmatic methods for managing sessions and states:

### 1. `create_session()`
Initializes a new session row and sets initial app, user, and session states:
```python
session = await session_service.create_session(
    app_name="fitness-onboarding",
    user_id="student_01",
    session_id="session_001",
    state={
        "user:preferred_name": "Jordan",
        "user:experience": "intermediate",
        "app:maintenance_mode": False,
        "current_step": "intake_complete"
    }
)
```

### 2. `get_session()`
Retrieves a session by primary key `(app_name, user_id, session_id)` along with event history:
```python
from google.adk.sessions import GetSessionConfig

session = await session_service.get_session(
    app_name="fitness-onboarding",
    user_id="student_01",
    session_id="session_001",
    config=GetSessionConfig(num_recent_events=5) # Limit to 5 most recent events
)

if session:
    print("Merged State:", session.state)
    print("Recent Events Count:", len(session.events))
```

### 3. `list_sessions()`
Queries all active sessions for a given application and optional user:
```python
response = await session_service.list_sessions(
    app_name="fitness-onboarding",
    user_id="student_01"
)
for s in response.sessions:
    print(f"ID: {s.id} | Created: {s.create_time} | Updated: {s.update_time}")
```

### 4. `get_user_state()`
Fetches accumulated user state across sessions:
```python
user_state = await session_service.get_user_state(
    app_name="fitness-onboarding",
    user_id="student_01"
)
print("User Preferences:", user_state)
```

### 5. `delete_session()`
Removes a session and its associated event rows:
```python
await session_service.delete_session(
    app_name="fitness-onboarding",
    user_id="student_01",
    session_id="session_001"
)
```

---

## 6. Concurrency & Production Safety

When running multi-tenant AI agents in production, concurrent requests for the same session could cause race conditions. `DatabaseSessionService` protects data integrity through two mechanisms:

1. **In-Process Per-Session Locking**:
   Uses an `asyncio.Lock` keyed by `(app_name, user_id, session_id)` so parallel tasks within the same process append events sequentially.
2. **Database Row-Level Locking**:
   On supported dialects (PostgreSQL, MySQL, MariaDB), state fetches and updates use `SELECT ... FOR UPDATE` row locks during transactions.
3. **Savepoints for Concurrent Inserts**:
   User state and App state initialization use nested savepoints (`begin_nested()`) to catch `IntegrityError` from racing concurrent inserts cleanly.

---

## 7. Student Practice Exercises

### Exercise 1: Build a Multi-Turn Persisted Assistant
Write a CLI Python script that uses `DatabaseSessionService` with SQLite. Run the script twice, verifying that the second execution recalls user details supplied in the first execution.

### Exercise 2: Inspect the Relational Database
Run your script from Exercise 1, then open the generated SQLite database using `sqlite3` CLI or Python `sqlite3` module:
```sql
SELECT id, author, timestamp FROM storage_events;
SELECT app_name, user_id, state FROM storage_user_states;
```
Verify how `storage_events` records input text, model output, and invocation IDs.

### Exercise 3: Connection Pool Optimization for PostgreSQL
Configure a `DatabaseSessionService` connected to a local PostgreSQL instance. Tune `pool_size`, `max_overflow`, and enable `pool_pre_ping`. Measure connection behavior under concurrent `asyncio.gather()` simulated requests.
