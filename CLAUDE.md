# Claude Context

## Project Overview

**Voogle** is a fork of [Voilib](https://github.com/unmonoqueteclea/voilib), an open-source podcast search engine with semantic search capabilities. This project enables users to search through thousands of minutes of high-quality podcast transcriptions using natural language queries, and also allows indexing of custom audio files.

### What is Voogle?

Voogle performs four main tasks:
1. **Collecting** - Fetches podcast metadata and audio files from RSS feeds
2. **Transcribing** - Uses OpenAI's Whisper model (via faster-whisper) to transcribe episodes
3. **Indexing** - Divides transcripts into ~40-word fragments and calculates embeddings (384-dimensional vectors) using Sentence Transformers
4. **Querying** - Performs semantic search by comparing query embeddings to indexed fragments in Qdrant vector database

### Architecture

**Backend** (Python/FastAPI):
- REST API with JWT authentication for admin endpoints
- SQLite for metadata (podcasts, episodes, transcriptions)
- Qdrant vector database for embeddings storage
- Redis + RQ for asynchronous task queuing (transcription, embedding calculation)
- Streamlit-based management interface

**Frontend** (Svelte/Vite):
- Client-side routing with page.js
- Tailwind CSS + DaisyUI for styling
- Consumes backend REST API

**Infrastructure**:
- Docker Compose orchestration
- Services: backend, frontend, management, redis, worker, qdrant
- All data stored in `./data/` volume mount

### Tech Stack

- **Backend**: Python 3.x, FastAPI, Ormar ORM, faster-whisper, sentence-transformers
- **Frontend**: Svelte 3, Vite, Tailwind CSS, DaisyUI
- **Databases**: SQLite (metadata), Qdrant (vector embeddings), Redis (job queue)
- **ML Models**: Whisper (transcription), SBERT (embeddings)

## Quick Commands

### Development Workflows

Voogle supports two development approaches:

---

### 1. Native Dev (Recommended for Claude Code)

**Best IDE experience** - Run infrastructure in Docker, app services natively with hot reload.

```bash
# Terminal 1: Start infrastructure only
docker compose up redis qdrant -d

# Terminal 2: Backend with hot reload
cd backend
pip install -e .[dev]           # Install in editable mode (first time)
make migrate                     # Run migrations (first time)
make start                       # Starts uvicorn with --reload flag

# Terminal 3: Frontend with hot reload
cd frontend
npm install                      # First time only
npm run dev                      # Vite dev server with HMR

# Changes to Python/Svelte reload instantly!
```

**Ports**:
- Backend API: http://localhost:8080/docs (Swagger)
- Frontend: http://localhost:5173
- Redis: localhost:6379 (internal)
- Qdrant: localhost:6333 (internal)

**Pros**: Full IDE integration (intellisense, debugging), no Docker extension needed
**Cons**: Requires Python/Node setup on host
**Reload speed**: Same as Docker dev (both have hot reload)

---

### 2. Docker Dev with Hot Reload (Full Stack)

**Complete dev environment** - All services in Docker with bind mounts for hot reload.

```bash
# First time setup
cd infra/development
cp .env.example .env              # Create your env file

# Build images (first time or after dependency changes)
cd infra && make dev-build

# Run all services with hot reload
make dev-run

# Services auto-reload when you edit files!
```

**Ports**:
- Frontend: http://localhost:80
- Backend API: http://localhost:81/service/docs
- Management UI: http://localhost:8501
- Redis: internal (redis:6379)
- Qdrant: internal (qdrant:6333)

**How it works**:
- Backend: Mounts `../../backend/` → uvicorn --reload watches files
- Frontend: Mounts `../../frontend/src/` → Vite HMR detects changes
- Worker: Mounts `../../backend/` → auto-restarts on changes

**Pros**: Full stack isolation, matches production closely, no host dependencies
**Cons**: Requires VS Code Docker extension for full IDE integration, image rebuilds after dependency changes
**Reload speed**: Same as native dev (bind mounts + hot reload)

**See**: [infra/readme.md](infra/readme.md) for detailed setup instructions

---

### Testing

```bash
# Backend tests (recommended - fastest)
cd backend
pytest                                    # Run all tests
pytest tests/test_specific.py            # Run specific test file
pytest -v -s                              # Verbose output with prints
pytest --cov=src/voilib --cov-report=html # With coverage

# Linting
ruff check .                              # Check for issues
black --check .                           # Check formatting

# If using Docker dev workflow
cd infra/development
docker compose exec backend pytest
```

---

### Production Deployment

```bash
# First time setup
cd infra/production
cp .env.example .env
# Edit .env: set SECRET_KEY, ADMIN_PASSWORD, domain

# Update domain references in compose.yml
# Replace all instances of voilib.com with your domain

# Build and run
cd infra && make prod-build
make prod-run
```

**Production features**:
- Traefik reverse proxy with automatic HTTPS (Let's Encrypt)
- 3 replicated backend instances for load balancing
- No development dependencies in images
- Separate `data-production/` directory

**See**: [infra/readme.md](infra/readme.md) for complete production setup guide

---

### Management Scripts

```bash
# Native dev (recommended - after pip install -e .[dev])
cd backend
voilib-episodes --update                  # Fetch new episodes from feeds
voilib-episodes --transcribe-days 7       # Transcribe last 7 days
voilib-episodes --store                   # Index pending transcriptions

# If using Docker dev workflow (after make dev-run)
cd infra/development
docker compose exec worker voilib-episodes --update
docker compose exec worker voilib-episodes --transcribe-days 7
```

---

### Database Operations

```bash
# Native dev (recommended)
cd backend
make migration msg="add user preferences table"  # Create migration
make migrate                                      # Apply migrations

# If using Docker dev workflow (after make dev-run)
cd infra/development
docker compose exec backend alembic upgrade head

# Database files
# - Development: ./data/voilib.db
# - Production: ./data-production/voilib.db
```

---

### Environment Files

**Development** (`infra/development/.env`):
```bash
cp infra/development/.env.example infra/development/.env
```

**Production** (`infra/production/.env`):
```bash
cp infra/production/.env.example infra/production/.env
# IMPORTANT: Change SECRET_KEY and ADMIN_PASSWORD!
```

---

### Recommended Workflow for Claude Code Sessions

1. **Start infrastructure**: `docker compose up redis qdrant -d`
2. **Run backend locally**: `cd backend && make start`
3. **Run frontend locally**: `cd frontend && npm run dev`
4. **Make changes** - files reload instantly
5. **Run tests**: `cd backend && pytest`
6. **Commit** when tests pass

**Why native dev for Claude Code?**
- Full IDE intellisense (Python type hints, imports, definitions)
- Direct debugger attachment without Docker setup
- Simpler for AI to understand file paths and imports
- Same reload speed as Docker dev, better ergonomics

## Key Context Files

- [context/design-principles.md](context/design-principles.md) - Core design philosophy
- [context/style-guide.md](context/style-guide.md) - Code style conventions
- [backend/readme.md](backend/readme.md) - Backend architecture details
- [infra/readme.md](infra/readme.md) - Deployment and infrastructure
- [readme.md](readme.md) - Main project documentation

## Current Work

See [docs/plan.md](docs/plan.md) for active tasks and planning.
See [CHANGELOG.md](CHANGELOG.md) for recent changes and reasoning.

**Current Focus**: Renaming project from Voilib to Voogle (see GitHub issue #1)

## Critical Patterns

### Error Handling
- **Fail loud**: No swallowed exceptions, errors surface with full context
- **Validate at boundaries**: API handlers, message consumers, file readers
- **Trust internal code**: No redundant validation between internal modules

### Code Organization
- Settings centralized in `backend/src/voilib/settings.py` (loaded from env vars)
- Async workers handle long-running tasks (transcription, embeddings) via RQ
- Vector operations isolated in `backend/src/voilib/vector.py`
- Embedding logic in `backend/src/voilib/embedding.py`

### Data Flow
1. RSS feeds → Collection scripts → SQLite metadata
2. Audio files → Whisper transcription → CSV files (start|end|text)
3. Transcripts → Fragment into ~40 words → Sentence Transformers → Qdrant
4. User query → Calculate embedding → Cosine similarity search → Results

### Security
- Admin endpoints require JWT authentication
- Default admin: `voilib-admin` / `*audio*search*engine` (change in production!)
- All external input validated at API boundary

## Environment

### Required Services
- Redis (job queue broker)
- Qdrant (vector database)
- Sufficient disk space for audio files and transcriptions (`./data/`)

### ML Model Requirements
- Whisper model downloads on first transcription
- Sentence Transformer model downloads on first embedding calculation
- GPU acceleration optional but recommended for faster processing

### File Structure
```
voogle/
├── backend/                      # Python FastAPI backend
│   ├── src/voilib/              # Main application code (to be renamed to voogle)
│   ├── migrations/              # Alembic database migrations
│   ├── dockerfile               # Production Dockerfile
│   ├── requirements.txt         # Python dependencies
│   └── makefile                 # Dev commands (start, migrate, etc.)
├── frontend/                     # Svelte UI
│   ├── src/                     # Svelte components and routes
│   ├── public/                  # Static assets
│   ├── dockerfile.dev           # Development Dockerfile
│   └── dockerfile.prod          # Production Dockerfile
├── infra/                        # Infrastructure & deployment
│   ├── development/             # Dev environment
│   │   ├── compose.yml          # Dev stack with bind mounts for hot reload
│   │   └── .env.example         # Dev environment variables template
│   ├── production/              # Production environment
│   │   ├── compose.yml          # Prod stack with Traefik reverse proxy
│   │   ├── .env.example         # Prod environment variables template
│   │   └── traefik.prod.toml    # Traefik configuration
│   └── makefile                 # Infrastructure commands (dev-build, dev-run, etc.)
├── context/                      # Claude Code context
│   ├── design-principles.md     # Core design philosophy
│   └── style-guide.md           # Code style conventions
├── docs/                         # Project documentation
│   └── plan.md                  # Current task planning
├── data/                         # Development runtime data (git-ignored)
│   ├── voilib.db                # SQLite database
│   ├── media/                   # Audio files and transcriptions
│   └── qdrant/                  # Vector database storage
├── CLAUDE.md                     # This file - Claude Code context
└── CHANGELOG.md                  # Project changelog with reasoning
```

### Environment Variables
Set in Docker Compose or local environment:
- Database paths (SQLite, Qdrant)
- Redis connection settings
- Media storage location
- Admin credentials
- Model settings (embedding model, fragment size)
