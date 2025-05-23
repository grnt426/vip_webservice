# Backend Documentation - VIP Guild Dashboard

This document provides an overview of the backend architecture, key components, and its interaction with the frontend for the VIP Guild Dashboard.

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database (SQLite)](#database-sqlite)
  - [Schema Overview](#schema-overview)
  - [Database Location](#database-location)
- [API (FastAPI)](#api-fastapi)
  - [Key Endpoints](#key-endpoints)
  - [API Router](#api-router)
- [Guild Wars 2 API Integration](#guild-wars-2-api-integration)
  - [GW2Client](#gw2client)
  - [Rate Limiting](#rate-limiting)
  - [Data Fetching and Caching Logic](#data-fetching-and-caching-logic)
- [Models (SQLAlchemy)](#models-sqlalchemy)
  - [Guild Data Models](#guild-data-models)
  - [Guild Log Models](#guild-log-models)
- [Frontend Interaction](#frontend-interaction)
  - [Serving Static Assets](#serving-static-assets)
  - [API for Frontend](#api-for-frontend)
- [Configuration](#configuration)
  - [`.secrets` File](#secrets-file)
- [Running the Backend](#running-the-backend)

## Technology Stack

- **Python 3.11+**
- **FastAPI:** Modern, fast (high-performance) web framework for building APIs with Python based on standard Python type hints.
- **SQLAlchemy:** SQL toolkit and Object-Relational Mapper (ORM) for Python.
- **SQLite:** Self-contained, serverless, zero-configuration, transactional SQL database engine used for local development and data storage.
- **Uvicorn:** ASGI server for running FastAPI applications.
- **httpx:** Asynchronous HTTP client for making requests to the Guild Wars 2 API.

## Project Structure

The `backend/` directory is structured as follows:

```
backend/
├── app/                    # Main application package
│   ├── api/                # API endpoint definitions (routers)
│   │   ├── guilds.py       # Endpoints related to guild data and logs
│   │   ├── items.py        # Endpoints for item data (if any)
│   │   └── health.py       # Health check endpoint
│   │   └── __init__.py     # Combines API routers
│   ├── database.py         # Database setup, engine, session management
│   ├── gw2_client.py       # Client for interacting with the GW2 API
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── guild.py        # Guild, GuildEmblem models
│   │   ├── guild_member.py # GuildMember, GuildMembership models
│   │   ├── guild_rank.py   # GuildRank model
│   │   ├── item.py         # Item model (if any)
│   │   └── guild_logs/     # Directory for specific guild log type models
│   │       ├── base.py     # Base class for all log types
│   │       ├── kick.py     # KickLog model
│   │       └── ...         # Other log type models (invite, stash, etc.)
│   │       └── __init__.py # Exports log models and LOG_TYPE_MAP
│   ├── utils/              # Utility functions
│   │   └── name_utils.py   # Utilities for GW2 names
│   ├── server.py           # FastAPI application instance, middleware, static files, startup logic
│   └── rate_limiter.py   # Token bucket rate limiter for GW2 API calls
├── alembic/                # Alembic database migration scripts (if using migrations)
│   └── versions/
├── tests/                  # Automated tests (currently placeholders)
├── .secrets                # (Gitignored) Stores the GW2 API Key
├── Dockerfile              # Defines the Docker image for the backend
└── requirements.txt        # Python dependencies
```

## Database (SQLite)

The backend uses SQLite as its database. SQLite is a file-based database, which is simple to set up and use for development.

### Schema Overview

The database schema is defined by SQLAlchemy models in `app/models/`. Key tables include:

-   `guilds`: Stores core data for each tracked guild (ID, name, tag, level, MOTD, resources, last update timestamp, last log ID seen).
-   `guild_emblems`: Stores guild emblem details, linked to the `guilds` table.
-   `guild_members`: Stores unique Guild Wars 2 account names.
-   `guild_memberships`: An association table linking `guild_members` and `guilds`, storing rank, join date, and WvW representation status for each member within a specific guild.
-   `guild_ranks`: Stores rank details for each guild (ID, order, permissions, icon).
-   `guild_logs_*`: A set of tables, one for each type of guild log (e.g., `guild_logs_kick`, `guild_logs_stash`). Each log table inherits common fields from `BaseGuildLog` and has its own specific columns.
    -   Common fields: `id` (API log ID), `guild_id`, `time`, `type` (log type string), `user` (acting user, if any), `fetched_at`.

SQLAlchemy ORM handles the mapping between Python model classes and these database tables.

### Database Location

-   When running in Docker (as recommended), the SQLite database file (`guild.db`) is created inside the container at `/app/data/guild.db`.
-   This path is configured in `app/database.py`.
-   The database is ephemeral by default if you just run `docker-compose up`; it will be recreated if the container is removed and rebuilt. For persistent data across container runs (not typically needed for this dev setup but good to know), a named volume could be configured in `docker-compose.yml` for the `/app/data` directory.

## API (FastAPI)

The backend API is built using FastAPI. FastAPI provides automatic data validation, serialization, and interactive API documentation (Swagger UI and ReDoc).

### Key Endpoints

Defined in `app/api/guilds.py` (and other files in `app/api/`):

-   `GET /api/guilds`: Fetches data for all tracked guilds. Supports a `force_refresh` query parameter.
-   `GET /api/guilds/{guild_id}/logs`: Fetches paginated logs for a specific guild. Supports filtering by `type` and `user`.
-   `GET /api/logs`: Fetches paginated logs from *all* tracked guilds combined. Supports filtering by `type` and `user`.
-   `GET /api/health`: A simple health check endpoint.

### API Router

-   The main API router is initialized in `app/api/__init__.py` with a prefix of `/api`.
-   Individual routers (like `guilds_router`) are included in this main router.
-   The FastAPI application in `app/server.py` includes this main API router.

## Guild Wars 2 API Integration

Interaction with the official Guild Wars 2 API is handled by the `GW2Client` class in `app/gw2_client.py`.

### GW2Client

-   Manages the GW2 API base URL and authentication (using the API key from `.secrets`).
-   Provides asynchronous methods to fetch various guild-related data points: core guild data, members, ranks, and logs.
-   The `get_guild_data()` method orchestrates fetching all necessary data for a single guild concurrently using `asyncio.gather()`.

### Rate Limiting

-   The GW2 API has rate limits (e.g., 300 requests per 5 minutes per endpoint, or 600 requests per minute per IP).
-   A simple token bucket rate limiter (`TokenBucketRateLimiter` in `app/rate_limiter.py`) is *initialized* in `GW2Client` but is **not currently actively used** to throttle outgoing requests. This is a potential area for improvement if API rate limit errors become an issue during heavy data fetching.
-   Currently, the application relies on fetching data only when stale or explicitly refreshed to avoid hitting limits too frequently.

### Data Fetching and Caching Logic

-   The `GET /api/guilds` endpoint in `app/api/guilds.py` implements a basic caching strategy.
-   It checks the `last_updated` timestamp of a guild in the database.
-   If data is considered stale (older than a defined `stale_after` period in `GW2Client`, e.g., 5 minutes) or if `force_refresh=true` is passed, it fetches fresh data from the GW2 API.
-   Otherwise, it serves data from the local database.
-   When fetching logs, it uses the `last_log_id` stored for the guild to fetch only new logs since the last update (unless `force_refresh` is true or no previous logs exist).

## Models (SQLAlchemy)

SQLAlchemy ORM models define the structure of our database tables and provide an object-oriented way to interact with the database.

### Guild Data Models

Located in `app/models/`:

-   `Guild`: Represents a guild.
-   `GuildEmblem`: Guild emblem details.
-   `GuildMember`: Represents a GW2 account.
-   `GuildMembership`: Association between `Guild` and `GuildMember`, including rank.
-   `GuildRank`: Represents a guild rank.

Each model has a `to_dict()` method to serialize its data, often mimicking the GW2 API response structure where appropriate.

### Guild Log Models

Located in `app/models/guild_logs/`:

-   `BaseGuildLog`: An abstract base class defining common fields for all log types (`id`, `guild_id`, `time`, `type`, `user`, `fetched_at`). It also defines a `guild` relationship.
-   Specific log models (e.g., `KickLog`, `StashLog`, `InviteDeclineLog`, `InfluenceLog`, `MissionLog`) inherit from `BaseGuildLog` and add their own specific columns (e.g., `kicked_by` for `KickLog`, `item_id` and `count` for `StashLog`).
-   Each specific log model has its own table (e.g., `guild_logs_kick`).
-   `app/models/guild_logs/__init__.py` contains:
    -   `LOG_TYPE_MAP`: A dictionary mapping log type strings (from the GW2 API, e.g., "kick", "joined") to their corresponding SQLAlchemy model classes (e.g., `KickLog`, `JoinLog`).
    -   `create_log_entry()`: A factory function that uses `LOG_TYPE_MAP` to instantiate the correct log model object based on the `type` field in an API log entry.

## Frontend Interaction

### Serving Static Assets

-   The FastAPI application in `app/server.py` is configured to serve static files for the frontend.
-   During the Docker build process (see `backend/Dockerfile`):
    1.  The frontend is built (e.g., `npm run build` in the `frontend` directory).
    2.  The resulting static assets (typically `index.html` and files in an `assets/` directory) are copied from the frontend build output (`frontend/dist/`) into the backend's `/app/static/` directory within the Docker image.
-   FastAPI then serves:
    -   `index.html` from `/app/static/index.html` when the root path (`/`) is requested.
    -   Other assets (CSS, JS, images) from `/app/static/assets/` under the `/assets` path.

### API for Frontend

-   The frontend application makes HTTP requests to the API endpoints provided by this backend (e.g., `/api/guilds`, `/api/logs`) to fetch and display data.
-   CORS (Cross-Origin Resource Sharing) is configured in `app/server.py` to allow requests from the frontend development server (e.g., `http://localhost:5173`) and the served application itself (`http://localhost:8080`).

## Configuration

### `.secrets` File

-   A crucial configuration file is `.secrets`, located in the `backend/` directory.
-   It **must** contain the Guild Wars 2 API key:
    ```
    API_KEY=YOUR_GW2_API_KEY_HERE
    ```
-   This file is gitignored and should never be committed to version control.

## Running the Backend

-   The recommended way to run the backend (along with the frontend) for development is using Docker and `docker-compose up --build` as described in the main project `README.md`.
-   The `backend/Dockerfile` defines how the backend service is built and run.
-   The `app/server.py` script is the entry point for the Uvicorn ASGI server when run via Docker.
-   On startup, `app/server.py` initializes the database (creates tables if they don't exist) and then calls `warm_database()` to pre-fetch guild data.
