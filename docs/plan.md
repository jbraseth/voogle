# Task Planning

Active tasks and implementation plans for Voogle.

---

## Active: PDF Ingestion Staging - Collect and Link (Issue #41)

**Goal**: Stage PDF ingestion capability by collecting PDFs from BibleProject Classroom and linking them to sessions. This first PR handles collection and linking only; extraction/chunking/embedding will be a follow-up PR.

**Status**: In Progress

**Branch**: `feat/41-pdf-ingestion-staging`

**Issue**: https://github.com/jbraseth/voogle/issues/41

**Milestone**: D - BibleProject Classroom Rich Series (D2)

---

### Problem Statement

BibleProject Classroom sessions often include "Teacher Notes" PDFs that contain valuable lesson summaries, diagrams, and discussion questions. Currently, even though the BibleProject adapter detects PDF URLs and includes them in RSS feeds, the PDFs are:

1. Not downloaded locally (the URL might 404 later)
2. Not visible in the UI (no API to list PDFs for a session)
3. Not searchable (no text extraction or embedding)

This PR addresses issues #1 and #2 - ensuring PDFs are collected, stored, and queryable. A follow-up PR (D2-follow-up) will add text extraction and embedding for searchability.

**User Story**: As a theology student, I want to see all PDFs associated with a BibleProject course so I can download them for offline study, even if the original URL changes.

---

### Architecture Decision: Resource Table vs Episode Extension

**Chosen Approach: Option A - New Resource Table**

After analyzing the codebase, Option A (new `Resource` table) is the best fit:

| Option | Pros | Cons |
|--------|------|------|
| A. New `Resource` table | Clean separation, extensible to videos/slides, no Episode field pollution | New table + migration |
| B. Extend Episode | Reuse existing model | Episode semantics are "playable media", PDFs aren't episodes |
| C. Separate PDF table | Simple | Not extensible to other resource types |

The `Resource` table design allows future expansion (video slides, diagrams, study guides) without schema changes.

---

### Data Model

```python
# backend/src/voogle/models/resource.py

class ResourceKind(enum.Enum):
    PDF = "pdf"
    # Future: SLIDE_DECK = "slide_deck", VIDEO = "video", etc.


class Resource(base.CoreModel):
    """A downloadable resource linked to a channel (course) or specific episode (session).

    Resources are non-audio artifacts like PDFs, slide decks, or supplemental materials.
    Unlike episodes, resources are not transcribed - they have their own extraction pipeline.

    Table: resources
    """

    ormar_config = ormar.OrmarConfig(
        tablename="resources",
        constraints=[ormar.UniqueColumns("guid")],
    )

    # Relationships - resource can be linked to channel, episode, or both
    channel: Optional[Channel] = ormar.ForeignKey(
        Channel,
        related_name="resources",
        ondelete=ormar.ReferentialAction.CASCADE,
    )
    episode: Optional[Episode] = ormar.ForeignKey(
        Episode,
        related_name="resources",
        ondelete=ormar.ReferentialAction.SET_NULL,
        nullable=True,
    )

    # Identity
    guid = ormar.Text()  # e.g., "bibleproject:htrtb:s1:pdf"
    kind = ormar.String(max_length=20, choices=list(ResourceKind))

    # Metadata
    title = ormar.String(max_length=250)
    description = ormar.Text(default="")

    # URLs - original and local
    original_url = ormar.Text()  # Where we fetched it from
    local_path = ormar.Text(default="")  # Relative path in media folder (empty if not downloaded)

    # File metadata
    file_size_bytes = ormar.Integer(default=0)
    mime_type = ormar.String(max_length=100, default="application/pdf")

    # Processing status (for future D2-follow-up)
    extracted = ormar.Boolean(default=False)  # Text extracted?
    embeddings = ormar.Boolean(default=False)  # Embeddings calculated?
```

**Key Design Decisions**:

1. **guid is unique**: Each resource has a stable identifier (same format as episode guids)
2. **original_url vs local_path**: Store both so we can re-fetch if local copy is missing
3. **Optional episode link**: Some resources are course-level, not session-specific
4. **CASCADE on channel delete**: If a course is removed, its resources go too
5. **SET_NULL on episode delete**: Resource remains if linked episode is removed
6. **extracted/embeddings flags**: Ready for D2-follow-up PR (initially always False)

---

### Implementation Plan

#### Step 1: Create Resource Model + Migration

**Files Created**:
- `backend/src/voogle/models/resource.py` - New Resource model
- `backend/migrations/versions/XXXX_add_resource_table.py` - Alembic migration

**Changes to Existing Files**:
- `backend/src/voogle/models/__init__.py` - Export Resource model
- `backend/src/voogle/db.py` - Register Resource in metadata

**Testing**: Run `make migrate` and verify table created

#### Step 2: Extend BibleProject Adapter to Collect PDFs

The BibleProject adapter already detects PDF URLs (see `bibleproject.py` line 469). We need to:

1. After generating RSS, download PDFs to local storage
2. Create Resource records linking PDFs to their sessions

**Changes to Existing Files**:
- `backend/src/voogle/sources/bibleproject.py` - Add `collect_resources()` method

**New Functions**:
```python
def collect_resources(self, feeds: list[LocalFeed]) -> list[Resource]:
    """Download PDFs and create Resource records for generated feeds.

    For each PDF artifact in the RSS feed:
    1. Parse the RSS to find PDF enclosures
    2. Download PDF to media folder (idempotent - skip if exists)
    3. Create or update Resource record in database

    Returns list of Resource objects created/updated.
    """
```

**Storage Path**: `data/media/{channel-slug}/resources/{filename}.pdf`

#### Step 3: Add PDF MIME Type to Local Router

**Changes to Existing Files**:
- `backend/src/voogle/routers/local.py` - Add `.pdf` to `_get_media_type()`

```python
def _get_media_type(suffix: str) -> str:
    media_types = {
        ".mp3": "audio/mpeg",
        ".pdf": "application/pdf",  # Add PDF support
        # ... existing types
    }
```

#### Step 4: Create Resources API Endpoint

**Files Created**:
- `backend/src/voogle/routers/resource.py` - New router
- `backend/src/voogle/schemas/resource.py` - Pydantic schemas

**API Endpoints**:
```
GET /media/resource?channel_id=<uuid>  # List resources for a channel
GET /media/resource?episode_id=<uuid>  # List resources for an episode
GET /media/resource/{resource_id}      # Get single resource
```

**Response Schema**:
```python
class ResourceOut(BaseModel):
    id: UUID
    kind: str
    title: str
    description: str
    original_url: str
    download_url: str | None  # /local/{channel}/{resources/filename.pdf}
    file_size_bytes: int
    extracted: bool
    embeddings: bool
```

#### Step 5: Add Tests

**Files Created**:
- `tests/unit/models/test_resource.py` - Model unit tests
- `tests/integration/test_resource_api.py` - API integration tests
- `tests/fixtures/resources/sample.pdf` - Test PDF fixture

**Test Coverage**:
1. Resource model creation and validation
2. Resource linking to channel/episode
3. API list/filter endpoints
4. PDF download and local storage
5. MIME type handling in local router

#### Step 6: Update CHANGELOG

**Changes to Existing Files**:
- `CHANGELOG.md` - Document new Resource model and API

---

### Files Summary

| Action | File |
|--------|------|
| Create | `backend/src/voogle/models/resource.py` |
| Create | `backend/migrations/versions/XXXX_add_resource_table.py` |
| Create | `backend/src/voogle/routers/resource.py` |
| Create | `backend/src/voogle/schemas/resource.py` |
| Create | `tests/unit/models/test_resource.py` |
| Create | `tests/integration/test_resource_api.py` |
| Create | `tests/fixtures/resources/sample.pdf` |
| Modify | `backend/src/voogle/models/__init__.py` |
| Modify | `backend/src/voogle/db.py` |
| Modify | `backend/src/voogle/sources/bibleproject.py` |
| Modify | `backend/src/voogle/routers/local.py` |
| Modify | `backend/src/voogle/main.py` (register router) |
| Modify | `CHANGELOG.md` |

---

### Success Criteria

- [ ] New `Resource` model with migration applied
- [ ] BibleProject adapter downloads PDFs to local storage
- [ ] Resource records created and linked to channels/episodes
- [ ] API endpoint returns resources with download URLs
- [ ] `/local/` endpoint serves PDF files correctly
- [ ] All existing tests pass (no regressions)
- [ ] New tests for Resource model and API
- [ ] CHANGELOG entry added

---

### Verification (REQUIRED before marking complete)

```bash
# 1. Lint (must pass)
cd backend && ruff check .

# 2. Unit + Integration tests (must pass)
pytest tests/ --ignore=tests/e2e -v

# 3. E2E tests (must pass) - requires frontend + backend running
pytest tests/e2e -v
```

---

### What This PR Does NOT Include (D2-follow-up scope)

- PDF text extraction (pdfplumber, PyPDF)
- PDF chunking strategy
- PDF embedding calculation
- PDF search results in query API
- UI for viewing/searching PDF content

These will be implemented in the D2-follow-up PR after this foundation is in place.

---

### Expert Persona Reviews

**Platform Architect (Staged Rollout)**:
- ✅ PR is self-contained and delivers value even without D2-follow-up
- ✅ Users can see and download PDFs immediately after this PR
- ✅ Resource table design is extensible for future resource types

**ML Engineer (Future Embedding)**:
- ✅ `extracted` and `embeddings` flags ready for D2-follow-up
- ✅ `guid` format consistent with episodes for vector payload
- ✅ No schema changes needed for embedding work

**Brutal Critic (Product Manager)**:
- "PDFs visible in UI, downloadable, associated with sessions" ✅
- "I can list PDFs for any course and download them" ✅
- "If source URL 404s, I still have local copy" ✅
- "Can't search PDF content yet" - Documented as D2-follow-up scope

---

## Previous: BibleProject Classroom Compound Episodes (Issue #31)

**Goal**: Extend the BibleProject Classroom scraper to detect compound sessions: pages that contain multiple Mux playback IDs (main video + slides video) plus PDF teacher notes. Generate RSS feeds that emit separate items for each artifact so Voogle can index them independently.

**Status**: Planning

**Branch**: `feat/31-bibleproject-compound-episodes`

**Issue**: https://github.com/jbraseth/voogle/issues/31

**Milestone**: D - BibleProject Classroom Rich Series

---

### Problem Statement

BibleProject Classroom session pages often contain multiple learning artifacts:
1. **Main video** - The primary lesson content (Mux playback ID)
2. **Slides video** - Optional presentation slides as video (separate Mux playback ID)
3. **Teacher notes PDF** - Optional downloadable PDF with lesson notes

Currently, if a scraper only extracts the main video, users searching for specific diagram content (found in slides) or lesson summaries (in PDFs) will get incomplete results. A theology student preparing a class presentation could miss key diagrams that were only in the slides video.

---

### Architecture Overview

This feature creates a new BibleProject adapter following the existing `SourceAdapter` protocol pattern from `backend/src/voogle/sources/`. The adapter will:

1. Parse session pages to extract all Mux playback IDs and PDF URLs
2. Generate RSS feeds with separate `<item>` entries for each artifact
3. Use clear naming conventions to distinguish artifact types

**Data Flow**:
```
Session Page HTML
    ↓
bibleproject.parse_session(html) → CompoundSession
    ↓
CompoundSession contains:
  - main_video: SessionArtifact (Mux ID, "main")
  - slides_video: SessionArtifact | None (Mux ID, "slides")
  - teacher_notes: SessionArtifact | None (PDF URL, "pdf")
    ↓
bibleproject.emit_rss(sessions) → RSS XML
    ↓
Each artifact becomes separate <item>:
  - "Session 1 - Main Video" with video/mp4 enclosure
  - "Session 1 - Slides" with video/mp4 enclosure
  - "Session 1 - Teacher Notes" with application/pdf enclosure
```

---

### Data Types

```python
# backend/src/voogle/sources/bibleproject.py

from dataclasses import dataclass
from enum import Enum


class ArtifactType(Enum):
    """Type of learning artifact in a session."""
    MAIN_VIDEO = "main"
    SLIDES_VIDEO = "slides"
    TEACHER_NOTES = "pdf"


@dataclass(frozen=True)
class SessionArtifact:
    """A single artifact within a compound session."""
    artifact_type: ArtifactType
    url: str  # Mux stream URL or PDF URL
    mux_playback_id: str | None  # Only for video artifacts
    title_suffix: str  # "Main Video", "Slides", "Teacher Notes"
    mime_type: str  # "video/mp4", "application/pdf"

    @property
    def is_video(self) -> bool:
        return self.artifact_type in (ArtifactType.MAIN_VIDEO, ArtifactType.SLIDES_VIDEO)


@dataclass
class CompoundSession:
    """A session page that may contain multiple artifacts."""
    session_id: str
    session_title: str
    session_url: str
    course_title: str
    description: str
    artifacts: list[SessionArtifact]

    @property
    def main_video(self) -> SessionArtifact | None:
        return next((a for a in self.artifacts if a.artifact_type == ArtifactType.MAIN_VIDEO), None)

    @property
    def slides_video(self) -> SessionArtifact | None:
        return next((a for a in self.artifacts if a.artifact_type == ArtifactType.SLIDES_VIDEO), None)

    @property
    def teacher_notes(self) -> SessionArtifact | None:
        return next((a for a in self.artifacts if a.artifact_type == ArtifactType.TEACHER_NOTES), None)
```

---

### Module Interface

```python
# backend/src/voogle/sources/bibleproject.py

import logging
from pathlib import Path

from voogle.sources import LocalFeed, SourceAdapter

logger = logging.getLogger(__name__)


def extract_mux_playback_ids(html: str) -> list[str]:
    """Extract all Mux playback IDs from session page HTML.

    Mux players are typically embedded with playback IDs in:
    - data-playback-id attributes
    - mux-player custom elements
    - JavaScript configuration objects

    Returns list of playback IDs in order of appearance.
    """


def extract_pdf_url(html: str) -> str | None:
    """Extract teacher notes PDF URL from session page HTML.

    Look for download links with:
    - .pdf extension in href
    - "teacher notes" or "download" in link text
    - PDF icon/indicator elements
    """


def parse_session(html: str, session_url: str) -> CompoundSession:
    """Parse a session page into a CompoundSession with all artifacts.

    Args:
        html: Raw HTML of the session page
        session_url: URL of the session page

    Returns:
        CompoundSession with all detected artifacts

    Raises:
        ValueError: If no main video found (required)
    """


def mux_stream_url(playback_id: str) -> str:
    """Convert Mux playback ID to HLS stream URL.

    Returns URL in format: https://stream.mux.com/{playback_id}.m3u8
    """


class BibleProjectAdapter(SourceAdapter):
    """Adapter for BibleProject Classroom content.

    Reads course configurations from data/local/bibleproject/
    Generates RSS feeds to data/generated-feeds/bibleproject/
    """

    def __init__(self, config_dir: Path, output_dir: Path) -> None:
        self._config_dir = config_dir
        self._output_dir = output_dir

    @property
    def adapter_id(self) -> str:
        return "bibleproject"

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def generate_feeds(self) -> list[LocalFeed]:
        """Generate RSS feeds from BibleProject course configs."""
```

---

### RSS Encoding Strategy

Each artifact becomes a separate RSS `<item>` with a clear title suffix:

```xml
<rss version="2.0">
  <channel>
    <title>BibleProject Classroom: How to Read the Bible</title>
    <link>https://classroom.bibleproject.com/courses/how-to-read</link>

    <!-- Session 1 has all three artifacts -->
    <item>
      <title>Session 1: Introduction - Main Video</title>
      <description>Primary lesson content for Session 1</description>
      <guid>bibleproject:htrtb:s1:main</guid>
      <enclosure url="https://stream.mux.com/abc123.m3u8" type="video/mp4" />
    </item>
    <item>
      <title>Session 1: Introduction - Slides</title>
      <description>Presentation slides for Session 1</description>
      <guid>bibleproject:htrtb:s1:slides</guid>
      <enclosure url="https://stream.mux.com/def456.m3u8" type="video/mp4" />
    </item>
    <item>
      <title>Session 1: Introduction - Teacher Notes</title>
      <description>Downloadable PDF notes for Session 1</description>
      <guid>bibleproject:htrtb:s1:pdf</guid>
      <enclosure url="https://classroom.bibleproject.com/downloads/s1-notes.pdf"
                 type="application/pdf" />
    </item>

    <!-- Session 2 only has main video -->
    <item>
      <title>Session 2: Reading Narrative - Main Video</title>
      <description>Primary lesson content for Session 2</description>
      <guid>bibleproject:htrtb:s2:main</guid>
      <enclosure url="https://stream.mux.com/ghi789.m3u8" type="video/mp4" />
    </item>
  </channel>
</rss>
```

**GUID Format**: `bibleproject:{course_slug}:{session_id}:{artifact_type}`

**Title Format**: `{Session Title} - {Artifact Suffix}`
- Main Video: "Session 1: Introduction - Main Video"
- Slides: "Session 1: Introduction - Slides"
- Teacher Notes: "Session 1: Introduction - Teacher Notes"

---

### Mux Playback ID Detection

Mux video players can be identified by several patterns in the HTML:

```python
# Pattern 1: mux-player custom element
# <mux-player playback-id="abc123" ...></mux-player>
MUX_PLAYER_PATTERN = re.compile(r'<mux-player[^>]*playback-id=["\']([a-zA-Z0-9]+)["\']')

# Pattern 2: data attribute on container
# <div data-mux-playback-id="abc123">
DATA_ATTR_PATTERN = re.compile(r'data-(?:mux-)?playback-id=["\']([a-zA-Z0-9]+)["\']')

# Pattern 3: JavaScript config object
# Mux.Video({ playbackId: "abc123" })
# { "playbackId": "abc123" }
JS_CONFIG_PATTERN = re.compile(r'playback[_-]?[Ii]d["\']?\s*[:=]\s*["\']([a-zA-Z0-9]+)["\']')
```

**Detection Strategy**:
1. Parse HTML with regex patterns (fast, no browser needed)
2. Extract all matching playback IDs
3. First ID is typically main video, second is slides (if present)
4. Validate by checking Mux stream URL responds

---

### Test Fixtures Strategy

Create recorded HTML fixtures for session pages with various artifact combinations:

```
tests/fixtures/bibleproject/
├── session_main_only.html        # Only main video
├── session_main_slides.html      # Main + slides video
├── session_all_artifacts.html    # Main + slides + PDF
├── session_main_pdf.html         # Main + PDF (no slides)
└── course_metadata.json          # Course-level metadata
```

**Fixture Recording Process**:
1. Capture real session page HTML (with permission or from public pages)
2. Sanitize/anonymize if needed
3. Store minimal HTML that contains the detection patterns
4. Add inline comments marking the expected extraction points

**Test Coverage**:
```python
class TestExtractMuxPlaybackIds:
    @pytest.mark.description("Extract single Mux playback ID from main-only session")
    def test_main_only(self, main_only_html: str) -> None:
        ids = extract_mux_playback_ids(main_only_html)
        assert len(ids) == 1
        assert ids[0] == "expected_main_id"

    @pytest.mark.description("Extract both Mux playback IDs from main+slides session")
    def test_main_and_slides(self, main_slides_html: str) -> None:
        ids = extract_mux_playback_ids(main_slides_html)
        assert len(ids) == 2
        # Order matters: main first, slides second


class TestParseSession:
    @pytest.mark.description("Parse session with all artifacts")
    def test_all_artifacts(self, all_artifacts_html: str) -> None:
        session = parse_session(all_artifacts_html, "https://example.com/session/1")
        assert session.main_video is not None
        assert session.slides_video is not None
        assert session.teacher_notes is not None
        assert len(session.artifacts) == 3


class TestRssGeneration:
    @pytest.mark.description("Session with 3 artifacts produces 3 RSS items")
    def test_compound_session_rss(self) -> None:
        session = CompoundSession(
            session_id="s1",
            session_title="Introduction",
            # ... with all 3 artifacts
        )
        rss_xml = emit_rss([session], output_path)

        tree = ET.parse(output_path)
        items = tree.findall(".//item")
        assert len(items) == 3

        # Verify MIME types
        enclosures = [item.find("enclosure") for item in items]
        types = [e.get("type") for e in enclosures]
        assert "video/mp4" in types
        assert "application/pdf" in types
```

---

### Implementation Steps

#### Step 1: Create fixture HTML files
- [ ] Record or create minimal HTML fixtures for each artifact combination
- [ ] Document expected extraction results in fixture comments
- [ ] Add fixtures to `tests/fixtures/bibleproject/`

#### Step 2: Implement extraction functions
- [ ] `extract_mux_playback_ids(html)` with regex patterns
- [ ] `extract_pdf_url(html)` for teacher notes
- [ ] Unit tests for each extraction function

#### Step 3: Implement session parsing
- [ ] `parse_session(html, url)` combining extractions
- [ ] `CompoundSession` and `SessionArtifact` dataclasses
- [ ] Unit tests for session parsing

#### Step 4: Implement RSS generation
- [ ] `emit_rss(sessions, output_path)` with multi-item encoding
- [ ] Correct MIME types for each artifact type
- [ ] GUID generation for stable episode identifiers
- [ ] Unit tests for RSS structure

#### Step 5: Implement BibleProjectAdapter
- [ ] Follow `SourceAdapter` protocol from `sources/__init__.py`
- [ ] Config file format for courses
- [ ] Integration with existing generator

#### Step 6: Add integration tests
- [ ] Test generated RSS is parseable by `collection/feed.py`
- [ ] Test full adapter workflow with fixture configs

---

### Files Created/Modified

**Created**:
- `backend/src/voogle/sources/bibleproject.py` - Main adapter module
- `tests/fixtures/bibleproject/session_main_only.html`
- `tests/fixtures/bibleproject/session_main_slides.html`
- `tests/fixtures/bibleproject/session_all_artifacts.html`
- `tests/fixtures/bibleproject/session_main_pdf.html`
- `tests/unit/sources/test_bibleproject.py`

**Modified**:
- `backend/src/voogle/sources/generator.py` - Register new adapter
- `CHANGELOG.md` - Document new feature

---

### Success Criteria

- [ ] Scraper correctly identifies all Mux playback IDs on a session page
- [ ] Sessions with only main video produce 1 RSS item
- [ ] Sessions with main + slides produce 2 RSS items
- [ ] Sessions with main + slides + PDF produce 3 RSS items
- [ ] RSS items have clear, distinguishable titles
- [ ] PDF enclosures have correct MIME type (application/pdf)
- [ ] Tests pass using recorded fixtures (no live scraping in CI)

---

### Verification (REQUIRED before marking complete)

Run these commands and confirm ALL pass:

```bash
# 1. Lint (must pass)
cd backend && ruff check .

# 2. Unit + Integration tests (must pass)
pytest tests/ --ignore=tests/e2e -v

# 3. E2E tests (must pass) - requires frontend + backend running
pytest tests/e2e -v
```

**Do NOT skip E2E tests.** If E2E tests fail or cannot run, that is a blocker.

---

### Expert Persona Reviews

**Scraping Engineer (Mux Detection)**:
- Multiple regex patterns cover common Mux embedding styles
- Order of playback IDs assumed (main first, slides second) - document assumption
- Consider fallback to DOM parsing if regex fails

**Data Modeler (RSS Encoding)**:
- GUID format ensures uniqueness across courses/sessions/artifacts
- Title suffix pattern is clear and searchable
- MIME types are standard (video/mp4, application/pdf)

**Brutal Critic (Missing Slides Scenario)**:
- ✅ Theology student now gets all artifacts indexed
- ✅ Clear titles distinguish main video from slides
- ✅ PDF enclosures enable full-text search of notes

---

### Open Questions

1. **Mux stream URL format**: Is `https://stream.mux.com/{id}.m3u8` the correct format?
   - Need to verify against actual BibleProject pages

2. **Playback ID ordering**: How to distinguish main video from slides when multiple IDs found?
   - Option A: Rely on DOM order (first = main)
   - Option B: Look for surrounding context (e.g., "slides" label)

3. **Authentication**: Do session pages require login?
   - If yes, adapter needs cookie/session handling

---

## Previous: Refresh Episode URL Capability (Issue #24)

**Goal**: Add capability to refresh episode URLs when enclosure URLs return 404, recovering without deleting the episode or losing transcription/embedding work.

**Status**: Planning

**Branch**: `feat/24-refresh-episode-urls`

**Issue**: https://github.com/jbraseth/voogle/issues/24

---

### Architecture Overview

This feature adds a new module `backend/src/voogle/collection/url_health.py` for URL validation and refresh logic, plus Streamlit admin controls for detecting and fixing broken URLs.

**Data Flow**:
```
Admin triggers "Detect Broken URLs"
    ↓
url_health.check_episode_url(episode) → HEAD request
    ↓
Returns URLHealthResult(status, error_code, error_message)
    ↓
Admin sees list of broken episodes with error details
    ↓
Admin clicks "Preview Refresh" for a channel
    ↓
url_health.find_updated_url(episode, channel) → re-fetch RSS, match by GUID
    ↓
Returns URLRefreshResult(old_url, new_url, validation_status)
    ↓
Admin confirms refresh
    ↓
url_health.apply_url_refresh(episode, new_url) → updates DB, logs change
```

---

### Data Types

```python
# backend/src/voogle/collection/url_health.py

from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class URLStatus(Enum):
    OK = "ok"                      # URL responds 200
    NOT_FOUND = "not_found"        # 404
    FORBIDDEN = "forbidden"        # 403
    SERVER_ERROR = "server_error"  # 5xx
    TIMEOUT = "timeout"            # Request timed out
    CONNECTION_ERROR = "connection_error"  # Host unreachable
    REDIRECT_LOOP = "redirect_loop"  # Too many redirects
    INVALID_URL = "invalid_url"    # Malformed URL

@dataclass
class URLHealthResult:
    """Result of checking a single episode URL."""
    episode_pk: int
    episode_title: str
    url: str
    status: URLStatus
    http_code: int | None          # Actual HTTP status code if available
    error_message: str | None      # Human-readable error
    checked_at: datetime

@dataclass
class URLRefreshResult:
    """Result of attempting to find an updated URL for an episode."""
    episode_pk: int
    episode_title: str
    old_url: str
    new_url: str | None            # None if no match found in RSS
    match_method: str | None       # "guid" or "title"
    new_url_valid: bool            # True if new URL responds 200
    error_message: str | None      # Why refresh failed (if applicable)
```

---

### Module Interface

```python
# backend/src/voogle/collection/url_health.py

import logging
from typing import AsyncIterator
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

from voogle import models
from voogle.collection import feed

logger = logging.getLogger(__name__)

# Constants
HEAD_TIMEOUT = 10  # seconds
GET_TIMEOUT = 30   # seconds for full feed fetch
BATCH_DELAY = 0.5  # seconds between requests to avoid rate limiting


def check_url(url: str, timeout: int = HEAD_TIMEOUT) -> URLHealthResult:
    """Check if a URL is accessible via HEAD request.

    Returns URLHealthResult with status and error details.
    Does not raise exceptions - all errors captured in result.
    """


async def check_episode_url(episode: models.Episode) -> URLHealthResult:
    """Check the health of an episode's media URL."""


async def check_channel_urls(
    channel: models.Channel,
    on_progress: Callable[[int, int], None] | None = None
) -> list[URLHealthResult]:
    """Check all episode URLs for a channel with rate limiting.

    Args:
        channel: Channel to check
        on_progress: Callback(checked_count, total_count) for progress

    Returns list of URLHealthResult for all episodes.
    """


async def check_all_broken_urls(
    on_progress: Callable[[int, int], None] | None = None
) -> list[URLHealthResult]:
    """Check all episode URLs across all channels.

    Returns only episodes with non-OK status.
    """


def find_episode_in_rss(
    episode: models.Episode,
    rss_items: list[dict]
) -> dict | None:
    """Match an episode to an RSS item by GUID (preferred) or title (fallback).

    Returns the matching RSS item dict or None if not found.
    """


async def find_updated_url(
    episode: models.Episode,
    channel: models.Channel
) -> URLRefreshResult:
    """Re-fetch channel RSS and find updated URL for episode.

    Strategy:
    1. Fetch current RSS feed for channel
    2. Match episode by GUID (preferred) or title (fallback)
    3. Compare enclosure URL to stored URL
    4. If different, validate new URL responds 200
    5. Return result with old URL, new URL, and validation status
    """


async def preview_channel_refresh(
    channel: models.Channel,
    broken_only: bool = True
) -> list[URLRefreshResult]:
    """Preview URL refreshes for a channel without applying changes.

    Args:
        channel: Channel to check
        broken_only: If True, only check episodes with broken URLs

    Returns list of URLRefreshResult showing potential changes.
    """


async def apply_url_refresh(
    episode: models.Episode,
    new_url: str
) -> None:
    """Apply a URL refresh to an episode.

    - Validates new URL responds 200 before updating
    - Logs old URL for audit trail
    - Updates episode.url in database
    - Preserves transcription and embeddings status

    Raises ValueError if new URL is not accessible.
    """


async def refresh_broken_urls(
    channel: models.Channel,
    dry_run: bool = True
) -> list[URLRefreshResult]:
    """Refresh all broken URLs for a channel from its RSS feed.

    Args:
        channel: Channel to refresh
        dry_run: If True, preview only (don't apply changes)

    Returns list of URLRefreshResult for all broken episodes.
    """
```

---

### Implementation Steps

#### Step 1: Create url_health.py module

Create `backend/src/voogle/collection/url_health.py` with:
- Data classes (URLStatus, URLHealthResult, URLRefreshResult)
- `check_url()` - basic HEAD request with timeout and error handling
- `check_episode_url()` - wrapper for Episode model

**Key implementation detail for check_url()**:
```python
def check_url(url: str, timeout: int = HEAD_TIMEOUT) -> tuple[URLStatus, int | None, str | None]:
    """Check URL health via HEAD request."""
    try:
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Voogle/1.0 (URL Health Check)"}
        )
        response.raise_for_status()
        return URLStatus.OK, response.status_code, None

    except Timeout:
        return URLStatus.TIMEOUT, None, "Request timed out"
    except ConnectionError:
        return URLStatus.CONNECTION_ERROR, None, "Host unreachable"
    except requests.HTTPError as e:
        code = e.response.status_code
        if code == 404:
            return URLStatus.NOT_FOUND, code, "URL not found"
        elif code == 403:
            return URLStatus.FORBIDDEN, code, "Access forbidden"
        elif 500 <= code < 600:
            return URLStatus.SERVER_ERROR, code, f"Server error ({code})"
        else:
            return URLStatus.SERVER_ERROR, code, f"HTTP error ({code})"
    except RequestException as e:
        return URLStatus.INVALID_URL, None, str(e)
```

#### Step 2: Implement batch URL checking

Add `check_channel_urls()` and `check_all_broken_urls()` with:
- Rate limiting (0.5s delay between requests)
- Progress callback for UI updates
- Parallel checking within channel, sequential between channels

#### Step 3: Implement RSS re-parsing for URL refresh

Add `find_episode_in_rss()` with episode matching logic:
```python
def find_episode_in_rss(
    episode: models.Episode,
    rss_items: list[dict]
) -> dict | None:
    """Match episode to RSS item by GUID (preferred) or title (fallback)."""
    episode_guid = str(episode.guid)
    episode_title = str(episode.title).lower().strip()

    # First pass: match by GUID
    for item in rss_items:
        item_guid = feed._episode_guid(item.get("guid", ""))
        if item_guid == episode_guid:
            return item

    # Second pass: match by title (fallback)
    for item in rss_items:
        item_title = (item.get("title") or "").lower().strip()
        if item_title == episode_title:
            logger.warning(f"Episode {episode.pk} matched by title, not GUID")
            return item

    return None
```

#### Step 4: Implement URL refresh functions

Add `find_updated_url()`, `preview_channel_refresh()`, and `apply_url_refresh()`:
- `find_updated_url()` - fetch RSS, match, compare URLs, validate new URL
- `preview_channel_refresh()` - batch preview without DB changes
- `apply_url_refresh()` - validate and persist URL change

**Key: apply_url_refresh() audit logging**:
```python
async def apply_url_refresh(episode: models.Episode, new_url: str) -> None:
    """Apply URL refresh with validation and audit logging."""
    old_url = episode.url

    # Validate new URL is accessible
    status, code, error = check_url(new_url)
    if status != URLStatus.OK:
        raise ValueError(f"New URL not accessible: {error}")

    # Log for audit trail
    logger.info(
        f"Refreshing episode URL",
        extra={
            "episode_pk": episode.pk,
            "episode_title": episode.title,
            "old_url": old_url,
            "new_url": new_url,
        }
    )

    # Update database (preserves transcription/embeddings)
    await episode.update(url=new_url)
```

#### Step 5: Add Streamlit admin controls

Create new section in `backend/src/voogle/management/pages/3_🔈-Media.py`:

```python
async def url_health_section() -> None:
    st.header("🔗 URL Health")
    st.markdown("""Detect and fix broken episode media URLs.
    This helps recover episodes when podcast hosts change their CDN or file locations.""")

    # Metrics
    col1, col2 = st.columns(2)
    total_episodes = await models.Episode.objects.count()
    col1.metric("Total Episodes", total_episodes)

    # Last check status
    if last_check := utils.get_event("event_url_check_start"):
        last_time = datetime.fromtimestamp(float(last_check["time"]), tz=timezone.utc)
        col2.markdown(f"**Last check**: `{last_time.strftime('%c')}`")

    # Detect broken URLs button
    st.subheader("1. Detect Broken URLs")
    if st.button("🔍 Scan All Episode URLs", use_container_width=True):
        with st.spinner("⌛ Checking URLs... This may take several minutes."):
            broken = await url_health.check_all_broken_urls()

        if not broken:
            st.success("✓ All episode URLs are accessible!")
        else:
            st.warning(f"Found {len(broken)} broken URLs")
            for result in broken:
                with st.expander(f"❌ {result.episode_title}"):
                    st.code(result.url)
                    st.error(f"Status: {result.status.value} - {result.error_message}")

    st.divider()

    # Preview refresh section
    st.subheader("2. Preview URL Refresh")
    channels = await models.Channel.objects.all()
    channel_options = {ch.title: ch for ch in channels}

    selected_channel = st.selectbox(
        "Select channel to preview",
        options=list(channel_options.keys())
    )

    if st.button("👁️ Preview Changes", use_container_width=True):
        channel = channel_options[selected_channel]
        with st.spinner("⌛ Fetching RSS and comparing URLs..."):
            results = await url_health.preview_channel_refresh(channel, broken_only=True)

        if not results:
            st.success("✓ No URL changes found")
        else:
            st.info(f"Found {len(results)} potential URL updates")
            for result in results:
                with st.expander(f"📝 {result.episode_title}"):
                    st.markdown(f"**Old URL**: `{result.old_url}`")
                    st.markdown(f"**New URL**: `{result.new_url}`")
                    st.markdown(f"**Match method**: {result.match_method}")
                    if result.new_url_valid:
                        st.success("✓ New URL is accessible")
                    else:
                        st.error(f"❌ New URL not accessible: {result.error_message}")

    st.divider()

    # Apply refresh section
    st.subheader("3. Apply URL Refresh")
    st.warning("⚠️ This will update episode URLs in the database. Preview first!")

    if st.button("🔄 Apply Refresh for Selected Channel", use_container_width=True):
        channel = channel_options[selected_channel]
        with st.spinner("⌛ Applying URL refreshes..."):
            results = await url_health.refresh_broken_urls(channel, dry_run=False)

        applied = [r for r in results if r.new_url and r.new_url_valid]
        failed = [r for r in results if r.error_message]

        if applied:
            st.success(f"✓ Updated {len(applied)} episode URLs")
        if failed:
            st.error(f"❌ Failed to update {len(failed)} episodes")
            for result in failed:
                st.error(f"- {result.episode_title}: {result.error_message}")
```

#### Step 6: Add event logging for URL health checks

Add to `utils.py`:
- `"event_url_check_start"` - when URL scan begins
- `"event_url_check_end"` - when URL scan completes with summary

#### Step 7: Add tests

Create `tests/unit/collection/test_url_health.py`:
```python
pytestmark = pytest.mark.unit

class TestCheckUrl:
    @pytest.mark.description("check_url returns OK for accessible URLs")
    def test_accessible_url(self) -> None:
        with patch("requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            status, code, error = check_url("https://example.com/file.mp3")

            assert status == URLStatus.OK
            assert code == 200
            assert error is None

    @pytest.mark.description("check_url returns NOT_FOUND for 404")
    def test_not_found_url(self) -> None:
        with patch("requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_head.return_value = mock_response
            mock_head.side_effect = requests.HTTPError(response=mock_response)

            status, code, error = check_url("https://example.com/missing.mp3")

            assert status == URLStatus.NOT_FOUND
            assert code == 404

    @pytest.mark.description("check_url handles timeout")
    def test_timeout(self) -> None:
        with patch("requests.head") as mock_head:
            mock_head.side_effect = Timeout()

            status, code, error = check_url("https://slow.example.com/file.mp3")

            assert status == URLStatus.TIMEOUT
            assert code is None

class TestFindEpisodeInRss:
    @pytest.mark.description("find_episode_in_rss matches by GUID")
    def test_match_by_guid(self) -> None:
        episode = MagicMock()
        episode.guid = "unique-guid-123"
        episode.title = "Episode Title"

        rss_items = [
            {"guid": "other-guid", "title": "Other Episode"},
            {"guid": "unique-guid-123", "title": "Episode Title", "enclosure": {"@url": "new-url"}},
        ]

        result = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert result["guid"] == "unique-guid-123"

    @pytest.mark.description("find_episode_in_rss falls back to title match")
    def test_fallback_to_title(self) -> None:
        episode = MagicMock()
        episode.guid = "old-guid"
        episode.title = "Episode Title"

        rss_items = [
            {"guid": "new-guid", "title": "Episode Title", "enclosure": {"@url": "new-url"}},
        ]

        result = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert result["title"] == "Episode Title"
```

Create `tests/integration/test_url_health.py`:
```python
pytestmark = pytest.mark.integration

@pytest.mark.description("URL refresh preserves episode transcription status")
async def test_refresh_preserves_transcription(
    channel: models.Channel,
    auth_client: TestClient
) -> None:
    """Refreshing URL should not affect transcription/embeddings flags."""
    # Get episode with transcription
    episode = await models.Episode.objects.filter(
        channel=channel, transcribed=True
    ).first()

    old_transcribed = episode.transcribed
    old_embeddings = episode.embeddings

    # Mock RSS with new URL
    with patch("voogle.collection.feed._read_channel_feed") as mock_feed:
        mock_feed.return_value = {
            "rss": {
                "channel": {
                    "item": [
                        {
                            "guid": episode.guid,
                            "title": episode.title,
                            "enclosure": {"@url": "https://new-cdn.example.com/episode.mp3"}
                        }
                    ]
                }
            }
        }

        with patch("voogle.collection.url_health.check_url") as mock_check:
            mock_check.return_value = (URLStatus.OK, 200, None)

            await url_health.apply_url_refresh(
                episode,
                "https://new-cdn.example.com/episode.mp3"
            )

    # Reload and verify
    await episode.load()
    assert episode.url == "https://new-cdn.example.com/episode.mp3"
    assert episode.transcribed == old_transcribed
    assert episode.embeddings == old_embeddings
```

#### Step 8: Update CHANGELOG.md

Add entry documenting the new feature.

---

### Key Design Decisions

1. **HEAD requests for validation**: Use HEAD instead of GET to minimize bandwidth and server load when just checking URL accessibility.

2. **Rate limiting**: 0.5 second delay between URL checks to avoid triggering rate limits on podcast CDNs.

3. **GUID-first matching**: Match episodes by GUID (stable identifier) first, fall back to title only if GUID doesn't match. Log title-based matches as warnings.

4. **Preview before apply**: All URL changes require explicit admin confirmation. Preview shows what will change before any database modifications.

5. **Audit logging**: Log old and new URLs for every refresh to enable rollback if needed.

6. **Preserve transcription state**: URL refresh updates only the `url` field, preserving `transcribed` and `embeddings` status.

7. **No auto-refresh**: All URL changes require explicit admin action. No automatic background refresh.

---

### Files Modified/Created

**Created**:
- `backend/src/voogle/collection/url_health.py` - URL validation and refresh logic

**Modified**:
- `backend/src/voogle/management/pages/3_🔈-Media.py` - Add URL health section
- `CHANGELOG.md` - Document new feature

**Tests Added**:
- `tests/unit/collection/test_url_health.py` - Unit tests for URL checking/matching
- `tests/integration/test_url_health.py` - Integration tests for refresh flow

---

### Edge Cases

1. **GUID changed in RSS**: Fall back to title matching, log warning
2. **Episode removed from RSS**: Cannot refresh, show clear error message
3. **New URL also 404s**: Reject update, show error in preview
4. **Rate limiting on HEAD requests**: 0.5s delay, exponential backoff on 429
5. **Timeout during batch check**: Mark as TIMEOUT status, don't fail entire batch
6. **Redirect chains**: Follow redirects (allow_redirects=True), detect loops

---

### Success Criteria

- [ ] Admin can detect broken episode URLs in bulk
- [ ] Admin can preview URL changes before applying
- [ ] Admin can refresh URLs for a specific channel
- [ ] URL changes are validated before persisting (new URL must return 200)
- [ ] Episode transcriptions and embeddings are preserved during URL update
- [ ] Clear audit trail of URL changes (old URL, new URL, timestamp in logs)
- [ ] No automatic URL changes - all require explicit admin action

---

### Verification (REQUIRED before marking complete)

Run these commands and confirm ALL pass:

```bash
# 1. Lint (must pass)
cd backend && ruff check .

# 2. Unit + Integration tests (must pass)
pytest tests/ --ignore=tests/e2e -v

# 3. E2E tests (must pass) - requires frontend + backend running
pytest tests/e2e -v
```

---

### Brutal Critic Review (Meeting 404 scenario)

**Addressed concerns**:
1. ✅ **Detection visibility**: Admin sees clear list of broken URLs with status codes
2. ✅ **Safe by default**: Preview before apply, no automatic changes
3. ✅ **Audit trail**: All URL changes logged with old/new values
4. ✅ **Preserve work**: Transcriptions and embeddings untouched by URL refresh
5. ✅ **Clear errors**: Human-readable error messages for all failure modes

**Not addressed (out of scope)**:
- Automatic monitoring/alerting for broken URLs (would require scheduled job)
- Bulk refresh across all channels (can add if needed)
- URL validation during initial episode ingestion (separate concern)

---

## Previous: YouTube Playlist Ingestion Adapter (Milestone C)

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
