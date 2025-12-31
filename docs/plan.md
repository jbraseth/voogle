# Task Planning

Active tasks and implementation plans for Voogle.

---

## Active: Refresh Episode URL Capability (Issue #24)

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
