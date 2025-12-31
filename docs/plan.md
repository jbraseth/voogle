# Task Planning

Active tasks and implementation plans for Voogle.

---

## Active: YouTube Playlist Ingestion Adapter (Milestone C)

**Goal**: Refactor `yt_playlist_tool.py` into a proper Voogle source adapter at `backend/src/voogle/sources/youtube_playlist.py` that provides three operations: scan (get metadata), sync_media (download audio), and emit_rss (generate local RSS feed for Voogle ingestion).

**Status**: Planning

**Branch**: `feat/<issue#>-youtube-playlist-adapter`

---

### Architecture Decision

The adapter will be placed in a new `sources/` directory, separate from `collection/`. This makes sense because:

1. **Different abstraction level**: `collection/` handles RSS/local ingestion into Voogle's database. `sources/` handles external platform integration (YouTube → local files + RSS)
2. **Decoupled workflow**: YouTube adapter produces files + RSS that the existing `collection/feed.py` can consume
3. **No database coupling**: The adapter just produces media files and RSS, not database models

**Data Flow**:
```
YouTube Playlist → scan() → PlannedEpisode list
                          ↓
                    sync_media() → downloads MP3 files to output_dir
                          ↓
                    emit_rss() → generates feed.xml
                          ↓
          Existing collection/feed.py → read_channel() + read_episodes() → database
```

---

### Data Types

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

class DownloadStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"  # file already exists

@dataclass
class PlannedEpisode:
    """Metadata about a YouTube video before downloading."""
    video_id: str
    title: str
    description: str
    duration_seconds: int | None
    upload_date: datetime | None
    playlist_title: str
    playlist_index: int | None
    expected_filename: str  # what the MP3 will be named

@dataclass
class DownloadResult:
    """Result of attempting to download a single video."""
    video_id: str
    status: DownloadStatus
    filepath: Path | None  # set if SUCCESS or SKIPPED
    error: str | None  # set if FAILED
```

---

### Module Interface

```python
# backend/src/voogle/sources/youtube_playlist.py

def scan(playlist_url: str) -> list[PlannedEpisode]:
    """Scan playlist and return metadata for all videos.

    Does NOT download anything. Uses yt-dlp extract_info with download=False.
    Progress: prints "Scanning: <playlist_title> (<count> videos)"

    Raises YouTubePlaylistError on failure (e.g., invalid URL, network error).
    """

def sync_media(
    episodes: list[PlannedEpisode],
    output_dir: Path,
    on_progress: Callable[[str, DownloadStatus, int, int], None] | None = None
) -> list[DownloadResult]:
    """Download audio files for episodes that don't exist yet.

    - Skips files that already exist in output_dir
    - Two-pass strategy: web client first, android fallback on 403/rate limit
    - Extracts audio to MP3 using FFmpeg postprocessor
    - Progress callback: (video_id, status, current, total)
    - Failed downloads don't stop the process; result list contains failures

    Returns list of DownloadResult (one per input episode).
    """

def emit_rss(
    episodes: list[PlannedEpisode],
    output_dir: Path,
    feed_path: Path,
    base_url: str = ""
) -> Path:
    """Generate RSS feed XML for successfully downloaded episodes.

    - Only includes episodes where MP3 file exists in output_dir
    - Uses base_url for enclosure URLs (e.g., "http://localhost:8080/local")
    - Returns path to generated feed.xml

    RSS structure matches what collection/feed.py expects.
    """
```

---

### Implementation Steps

#### Step 1: Create sources directory structure
```
backend/src/voogle/sources/
├── __init__.py           # empty or minimal exports
└── youtube_playlist.py   # main adapter module
```

#### Step 2: Implement PlannedEpisode and DownloadResult dataclasses
- Simple dataclasses, no validation logic
- Matches existing yt_playlist_tool patterns

#### Step 3: Implement scan() function
Extract from existing `list_playlists()` and scan loop in `download_playlists()`:
- Use yt-dlp `extract_flat=False` to get full metadata
- Map entries to PlannedEpisode
- Handle missing playlist_index gracefully
- Log progress to stdout (not JSONL - keep it simple)

#### Step 4: Implement sync_media() function
Extract from existing `download_playlists()`:
- Check if file exists before downloading (skip logic)
- Pass 1: web client
- Pass 2: android fallback for failures
- Use FFmpegExtractAudio postprocessor for MP3
- Progress reporting via callback
- Collect results without stopping on failure

#### Step 5: Implement emit_rss() function
New code - generate standard RSS 2.0 XML:
- Use xml.etree.ElementTree (stdlib, no new deps)
- Include: title, description, pubDate, enclosure URL
- Match format expected by collection/feed.py

#### Step 6: Add configuration to settings.py
Add optional settings:
```python
# YouTube Playlist Adapter
youtube_output_dir: str = "youtube"  # relative to data_dir
youtube_audio_format: str = "mp3"
youtube_cookies_file: str | None = None
```

#### Step 7: Update CHANGELOG.md
Add entry for new YouTube playlist adapter.

---

### Key Design Decisions

1. **No database models**: This adapter produces files + RSS. The existing collection pipeline handles database ingestion.

2. **No JSONL logging**: The existing tool has complex JSONL logging. For simplicity, we use stdout with clear progress messages. If structured logging is needed later, it can be added.

3. **No cookies by default**: Cookies only used if explicitly configured via `youtube_cookies_file` setting.

4. **Format selector preserved**: Keep the existing format selector logic:
   ```
   18/ba[ext=m4a][protocol!=m3u8]/best[ext=mp4][vcodec!=none][acodec!=none][height<=360]/bestaudio[protocol!=m3u8]
   ```

5. **Two-pass download**: Web client first, android fallback. This is the proven strategy from the existing tool.

6. **Progress visibility**: Clear stdout output showing which video is being processed, success/failure/skip status.

7. **Error handling**: Failed downloads logged but don't crash. User can see which videos failed and retry.

---

### Files Modified/Created

**Created**:
- `backend/src/voogle/sources/__init__.py`
- `backend/src/voogle/sources/youtube_playlist.py`

**Modified**:
- `backend/src/voogle/settings.py` (optional config additions)
- `CHANGELOG.md`

**Not Modified**:
- `collection/` modules (no changes to existing RSS ingestion)
- Tests will be added in a follow-up PR

---

### Testing Strategy

**Unit tests** (Phase 2 - not in this PR):
- `test_planned_episode_creation`
- `test_download_result_states`

**Integration tests** (Phase 2):
- Mock yt-dlp to test scan/sync_media behavior
- Test emit_rss generates valid XML

**Manual verification** (this PR):
```bash
cd backend && ruff check .                 # lint passes
pytest tests/ --ignore=tests/e2e -v        # existing tests pass
pytest tests/e2e -v                        # e2e tests pass (no new failures)
```

---

### Brutal Critic Review (500-video playlist scenario)

**Addressed concerns**:
1. ✅ **Progress visibility**: `on_progress` callback shows current video number
2. ✅ **Failure resilience**: One failed download doesn't stop the batch
3. ✅ **Resume capability**: `sync_media` skips existing files automatically
4. ✅ **Clear error reporting**: DownloadResult contains error message for failures

**Not addressed (out of scope for this PR)**:
- Checkpoint/resume across process restarts (would require state persistence)
- Concurrent downloads (yt-dlp handles fragment concurrency, not parallel videos)

---

### Dependencies

**New dependency needed**:
- `yt-dlp>=2024.0.0` - must be added to `backend/requirements.txt`

This is the only new dependency. FFmpeg is expected to be available on the system (typical for audio processing environments).

---

## Archived: Issue #1 - Rename Voilib to Voogle

**Goal**: Rename all references of "voilib" to "voogle" throughout the application to reflect the fork's new identity.

**Status**: In Progress (Branch: `refactor/1-rename-voilib-to-voogle`)

### Strategy

This is a comprehensive rename across four main categories:
1. Package names and Python module references
2. UI/branding text visible to users
3. Configuration files and infrastructure
4. Documentation

The rename will be executed systematically to minimize breakage, testing at each step.

---

### Task 1: Update Package Names and References

**Files to modify**:

#### Backend (Python)
- [ ] `backend/pyproject.toml` - Change project name from `voilib` to `voogle`
- [ ] `backend/setup.cfg` - Update package name and entry points
- [ ] `backend/src/voilib/` - Rename directory to `backend/src/voogle/`
- [ ] All Python imports - Change `from voilib.` to `from voogle.`
  - [ ] `backend/src/voilib/__init__.py`
  - [ ] `backend/src/voilib/main.py`
  - [ ] `backend/src/voilib/settings.py`
  - [ ] `backend/src/voilib/auth.py`
  - [ ] `backend/src/voilib/db.py`
  - [ ] `backend/src/voilib/embedding.py`
  - [ ] `backend/src/voilib/storage.py`
  - [ ] `backend/src/voilib/tasks.py`
  - [ ] `backend/src/voilib/transcription.py`
  - [ ] `backend/src/voilib/utils.py`
  - [ ] `backend/src/voilib/vector.py`
  - [ ] `backend/src/voilib/worker.py`
  - [ ] All files in `backend/src/voilib/cli/`
  - [ ] All files in `backend/src/voilib/collection/`
  - [ ] All files in `backend/src/voilib/management/`
  - [ ] All files in `backend/src/voilib/models/`
  - [ ] All files in `backend/src/voilib/routers/`
  - [ ] All files in `backend/src/voilib/schemas/`
  - [ ] All test files in `backend/src/voilib/tests/`
- [ ] `backend/requirements.txt` - Update if any self-references
- [ ] `backend/alembic.ini` - Update script location if needed
- [ ] `backend/migrations/` - Update any hardcoded references

#### Frontend
- [ ] `frontend/package.json` - Change name from `voilib-ui` to `voogle-ui`
- [ ] Search all `.svelte` and `.js` files for "voilib" references
- [ ] Update API endpoint references if needed

**Testing after this step**:
```bash
# Verify imports work
cd backend && python -c "import voogle"
# Run tests
cd backend && pytest
# Start services
cd infra && make dev-run
```

---

### Task 2: Update UI/Branding Text

**Files to modify**:

- [ ] `frontend/index.html` - Update `<title>` and meta tags
- [ ] `frontend/src/App.svelte` - Update application title/branding
- [ ] `frontend/public/` - Replace any logo/favicon files with Voogle branding
- [ ] `backend/src/voogle/management/` - Update Streamlit management UI pages
  - [ ] Update page titles and headers
  - [ ] Update any "Voilib" text in descriptions/help text
- [ ] Search for user-visible "Voilib" strings:
  ```bash
  grep -r "Voilib" frontend/src/
  grep -r "Voilib" backend/src/voogle/management/
  ```

**User-facing locations**:
- Page titles and headers
- Error messages
- Help text and tooltips
- Footer/copyright notices
- Management UI welcome screens

**Testing after this step**:
- Manually verify all UI pages display "Voogle" correctly
- Check browser tab titles
- Review management interface

---

### Task 3: Update Configuration Files

**Files to modify**:

#### Backend Dockerfiles
- [ ] `backend/dockerfile`
  - [ ] Update labels/comments
  - [ ] Update any hardcoded "voilib" references
  - [ ] Update working directory if it references voilib

#### Frontend Dockerfiles
- [ ] `frontend/dockerfile.dev`
  - [ ] Update labels/comments
  - [ ] Update any build args or env references
- [ ] `frontend/dockerfile.prod`
  - [ ] Update labels/comments
  - [ ] Update any build args or env references

#### Infrastructure - Development
- [ ] `infra/development/compose.yml`
  - [ ] Change `name: voilib` → `name: voogle`
  - [ ] Update image names: `voilib-backend:latest` → `voogle-backend:latest`
  - [ ] Update image names: `voilib-ui:latest` → `voogle-ui:latest`
  - [ ] Update commands: `src.voilib.main` → `src.voogle.main`
  - [ ] Update commands: `src/voilib/management` → `src/voogle/management`
  - [ ] Update commands: `src/voilib/worker.py` → `src/voogle/worker.py`
  - [ ] Update env var names in ports: `VOILIB_*` → `VOOGLE_*`
- [ ] `infra/development/.env.example`
  - [ ] Update any voilib references (probably none)

#### Infrastructure - Production
- [ ] `infra/production/compose.yml`
  - [ ] Change `name: voilib-backend` → `name: voogle-backend`
  - [ ] Update image names: `voilib-backend:latest` → `voogle-backend:latest`
  - [ ] Update image names: `voilib-ui:latest` → `voogle-ui:latest`
  - [ ] Update commands: `src.voilib.main` → `src.voogle.main`
  - [ ] Update commands: `src/voilib/management` → `src/voogle/management`
  - [ ] Update commands: `src/voilib/worker.py` → `src/voogle/worker.py`
  - [ ] Update Traefik labels: `Host(\`voilib.com\`)` → document to replace with user's domain
  - [ ] Update data volume: `data-production/` (keep as is, document in migration guide)
- [ ] `infra/production/.env.example`
  - [ ] Update any voilib references
- [ ] `infra/production/traefik.prod.toml`
  - [ ] Update any voilib.com references (document as example domain)

#### Infrastructure - Makefile
- [ ] `infra/makefile`
  - [ ] Update help text: "Voilib Infrastructure" → "Voogle Infrastructure"
  - [ ] Commands themselves are generic, no changes needed

#### Environment Variables
- `VOILIB_MANAGEMENT_PORT` → `VOOGLE_MANAGEMENT_PORT`
- `VOILIB_FRONTEND_PORT` → `VOOGLE_FRONTEND_PORT`
- `VOILIB_API_PORT` → `VOOGLE_API_PORT`

#### Database Files
- [ ] Default database filename: `voilib.db` → `voogle.db` (in settings)
- [ ] Document in migration guide: Users can rename or keep existing `voilib.db`

#### Data Directories
- [ ] Development: `./data/` (keep as is, generic)
- [ ] Production: `./data-production/` (keep as is, generic)
- [ ] Document: Users don't need to change data directory names

**Testing after this step**:
```bash
# Test development setup
cd infra/development
cp .env.example .env
cd infra && make dev-build
make dev-run
# Verify services start and hot reload works
Ctrl+C

# Test production config validation
cd infra/production
cp .env.example .env
docker compose config

# Clean up
docker compose down
```

---

### Task 4: Update Documentation

**Files to modify**:

- [ ] `readme.md` - Main project README
  - [ ] Title and description
  - [ ] All command examples (docker commands, paths)
  - [ ] Default credentials username: `voilib-admin` → `voogle-admin`
  - [ ] All URLs and references
- [ ] `backend/readme.md` - Backend documentation
  - [ ] Title and references
  - [ ] Example commands (`voilib-management` → `voogle-management`, etc.)
  - [ ] Module paths in code examples
- [ ] `frontend/readme.md` - Frontend documentation
- [ ] `infra/readme.md` - Infrastructure documentation
  - [ ] Deployment examples
  - [ ] Service names
  - [ ] First-run tasks
- [ ] `CHANGELOG.md` - Add comprehensive entry for the rename
- [ ] `CLAUDE.md` - Update this file (already reflects Voogle)
- [ ] `context/style-guide.md` - Update any voilib-specific examples
- [ ] `.github/` - Update any workflow files or issue templates

**Testing after this step**:
- Read through all documentation to verify consistency
- Try following quick-start instructions with new names
- Verify all links work

---

### Task 5: GitHub & Repository Metadata

**Actions needed**:

- [ ] Update repository description
- [ ] Update repository topics/tags
- [ ] Consider repository name change (if desired)
- [ ] Update any GitHub Actions workflows
- [ ] Close issue #1 with summary of changes

---

## Migration Guide for Users

Migrating from Voilib to Voogle:

1. **Update environment variables**: `VOILIB_*` → `VOOGLE_*`
2. **Rebuild Docker images**
3. **Rename database file**: `voilib.db` → `voogle.db`
4. **Update admin username**: `voilib-admin` → `voogle-admin`
5. **Update Python imports** if using as a library

---

## Post-Rename Tasks

After the rename is complete:

- [ ] Run full test suite
- [ ] Test fresh installation following README
- [ ] Test upgrade path from Voilib
- [ ] Update any external references (blog posts, etc.)
- [ ] Create release/tag documenting the rename

---

## Notes

- **Branch strategy**: All work in `refactor/1-rename-voilib-to-voogle`
- **Commit style**: Use `#1:` prefix for all commits
- **Testing strategy**: Test after each major task category
- **Rollback plan**: Branch allows easy revert if issues found

**Search patterns to find all references**:
```bash
# Case-insensitive search for voilib
grep -ri "voilib" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=data
# Find file/directory names containing voilib
find . -iname "*voilib*" -not -path "*/node_modules/*" -not -path "*/.git/*"
```
