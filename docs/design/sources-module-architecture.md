# Source Adapters Module - Architecture Design

## Overview

This document defines the architecture for the "sources" module that generates RSS feeds from non-RSS sources (YouTube playlists, BibleProject Classroom, etc.), making RSS the universal ingestion boundary for Voogle.

**Status**: Planning Complete
**Milestone**: B - Make RSS the Ingestion Boundary
**Date**: 2025-12-31

---

## 1. Interface Contract

### LocalFeed Structure

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LocalFeed:
    """Represents a generated RSS feed file for local content."""
    path: Path          # Absolute path to generated RSS XML file
    source_id: str      # Adapter ID (e.g., "youtube", "bibleproject")
    channel_url: str    # Logical URL (e.g., "local://youtube/PLxxxxxx")

    def __post_init__(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Generated feed does not exist: {self.path}")
        if not self.path.suffix == ".xml":
            raise ValueError(f"Feed path must be XML file: {self.path}")
        if not self.channel_url.startswith("local://"):
            raise ValueError(f"Channel URL must use local:// scheme: {self.channel_url}")
```

### SourceAdapter Protocol

```python
from typing import Protocol, List
from pathlib import Path

class SourceAdapter(Protocol):
    """Protocol for adapters that generate RSS feeds from various sources."""

    @property
    def adapter_id(self) -> str:
        """Unique identifier for this adapter (e.g., 'youtube', 'bibleproject')."""
        ...

    @property
    def config_dir(self) -> Path:
        """Directory where this adapter reads its configuration."""
        ...

    def generate_feeds(self) -> List[LocalFeed]:
        """Generate RSS feed files from source configuration.

        Returns:
            List of LocalFeed objects pointing to generated XML files

        Raises:
            ValueError: If configuration is invalid
            IOError: If feed generation/writing fails
        """
        ...
```

---

## 2. Directory Structure

```
data/
├── local/                          # Source configurations
│   ├── youtube/                    # YouTube adapter configs
│   │   └── playlist-name.json      # Config: playlist ID, title, etc.
│   ├── bibleproject/               # BibleProject configs (future)
│   │   └── course-name.json
│   └── sources.json                # Existing local media config
│
├── generated-feeds/                # Generated RSS files (NEW)
│   ├── youtube/
│   │   └── playlist-name.xml       # Generated RSS feed
│   └── bibleproject/
│       └── course-name.xml
│
├── audio/                          # Downloaded/local audio files
│   ├── youtube/                    # YouTube audio downloads
│   │   └── {video_id}.mp3
│   └── local/                      # Existing local media
│
└── voogle.db                       # SQLite metadata
```

**Design Decisions:**
- `data/local/` holds human-editable JSON configs (source of truth)
- `data/generated-feeds/` holds machine-generated RSS XML (derived, gitignored)
- Clear separation enables safe regeneration and version control

---

## 3. YouTube Playlist Adapter

### Approach: yt-dlp Only (No API Key Required)

**Rationale:**
- No quota limits (YouTube API: 10,000 units/day)
- Rich metadata extraction (title, description, duration, thumbnail)
- Direct audio URL extraction
- Already proven in yt_playlist_tool

### Critical Limitation: URL Expiration

YouTube stream URLs expire in ~6 hours. Two strategies:

**Option A: Pre-Download Audio (Recommended for Voogle)**
```python
# Download audio to local storage
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'data/audio/youtube/%(id)s.%(ext)s',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
}
# RSS enclosure points to local file: /local/youtube/{video_id}.mp3
```

**Option B: Dynamic RSS (Fresh URLs on Request)**
```python
# Regenerate URLs when RSS is requested
# Requires caching with 3-hour TTL
# More complex, but no storage requirements
```

### Configuration Format

```json
{
  "playlist_id": "PLxxxxxxxxxxxxxxx",
  "title": "Playlist Name",
  "description": "Description",
  "language": "en"
}
```

### Implementation: Three-Phase Pipeline

Following the existing yt_playlist_tool pattern from C1-youtube-playlist-adapter.md:

```python
def scan(playlist_url: str) -> List[PlannedEpisode]:
    """Extract metadata without downloading."""

def sync_media(planned: List[PlannedEpisode], output_dir: Path) -> List[DownloadResult]:
    """Download missing audio files. Skips existing."""

def emit_rss(episodes: List[Episode], output_path: Path) -> Path:
    """Generate RSS feed file."""
```

### Error Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| Rate limit (HTTP 429) | DownloadError with "429" | Exponential backoff, raise RateLimitError |
| Private/deleted video | DownloadError | Skip video, log warning, continue |
| Age-restricted | DownloadError with "age" | Try authenticated cookies if configured |
| Geo-restricted | DownloadError with "geo" | Skip, document limitation |
| Network timeout | Timeout exception | Retry with backoff, then fail |

---

## 4. BibleProject Classroom Adapter

### Status: NOT RECOMMENDED (Legal/Technical Barriers)

**Findings:**
- No official RSS feeds for Classroom content
- Mux video platform with no public API
- Terms of Use prohibit redistribution
- No direct audio/video download links

**Recommendation:**
1. Contact BibleProject for explicit permission
2. Wait for their planned offline download feature
3. Use existing BibleProject Podcast RSS feed (different content)

**If Permission Granted:**
- Browser automation to extract Mux playback IDs
- Audio extraction from HLS streams
- RSS generation with proper attribution

**For Now:** Focus on YouTube adapter and other sources with existing RSS feeds.

---

## 5. RSS Generation Library

### Recommendation: feedgen

```python
from feedgen.feed import FeedGenerator

fg = FeedGenerator()
fg.load_extension('podcast')
fg.title('Playlist Title')
fg.description('Description')
fg.link(href='https://youtube.com/playlist?list=...')
fg.language('en')
fg.podcast.itunes_category('Education')

for episode in episodes:
    fe = fg.add_entry()
    fe.id(f"youtube:{episode.video_id}")
    fe.title(episode.title)
    fe.description(episode.description)
    fe.enclosure(episode.audio_url, type='audio/mpeg')
    fe.pubDate(episode.published_at)

fg.rss_file('output.xml')
```

**Why feedgen:**
- Native podcast extension with iTunes support
- Generates valid RSS 2.0 XML
- Well-maintained, BSD-licensed
- Already handles XML escaping

**Dependencies to Add:**
```
feedgen>=1.0.0
yt-dlp>=2024.1.0
```

---

## 6. Integration with Existing Collection Module

### Minimal Changes to crawler.py

```python
# New function
def update_local_channels():
    """Generate RSS feeds from local sources before updating."""
    from .generator import generate_all_feeds

    logger.info("Generating RSS feeds from local sources...")
    local_feeds = generate_all_feeds()

    for feed in local_feeds:
        logger.info(f"Generated: {feed.channel_url} -> {feed.path}")

# Modified update_channel to handle local:// URLs
async def get_or_create_channel(feed_url: str, language: str = None):
    if feed_url.startswith("local://"):
        # Parse local:// URL to find generated RSS file
        feed_path = _resolve_local_feed(feed_url)
        ch = read_local_rss_channel(feed_path, language)
    else:
        ch = feed.read_channel(feed_url, language)
    # ... existing logic
```

### CLI Integration

```bash
# Existing command now also processes local sources
voogle-episodes --update

# Internally:
# 1. generate_all_feeds() -> List[LocalFeed]
# 2. For each LocalFeed: get_or_create_channel(local_feed.channel_url)
# 3. For each HTTP feed: get_or_create_channel(http_feed_url)
```

---

## 7. Testing Strategy

### Test File Structure

```
tests/
├── unit/
│   └── sources/
│       └── test_rss_generation.py      # Pure RSS XML generation
├── component/
│   └── sources/
│       └── test_youtube_adapter.py     # Mocked yt-dlp
├── integration/
│   └── sources/
│       └── test_feed_parsing.py        # Generated feeds → collection module
└── fixtures/
    └── mock_responses/
        └── youtube_playlist.json       # Real yt-dlp response structure
```

### Mocking Strategy

- **Mock external services**: yt-dlp, HTTP requests
- **Use real structures**: Match actual yt-dlp response format
- **Don't mock internal code**: Test adapter logic with real dependencies

### Key Test Cases

```python
# Unit: RSS generation
def test_rss_xml_escaping():
    """XML special characters properly escaped."""

def test_rss_required_fields():
    """All required RSS 2.0 fields present."""

# Component: YouTube adapter
@patch("yt_dlp.YoutubeDL")
def test_scan_playlist_metadata(mock_ydl):
    """Extracts correct metadata from playlist."""

@patch("yt_dlp.YoutubeDL")
def test_sync_media_skips_existing(mock_ydl):
    """Doesn't re-download existing files."""

# Integration: Feed parsing
def test_generated_rss_parseable():
    """Generated RSS can be parsed by collection.read_channel()."""
```

### CI Requirements

- All tests run offline (no network calls)
- CI execution adds <15 seconds
- No new external service dependencies in CI

---

## 8. Error Handling Strategy

### Fail Loud Principle

```python
class YouTubeRateLimitError(Exception):
    """Raised when YouTube returns HTTP 429."""

class SourceUnavailableError(Exception):
    """Raised when source is down or format changed."""

class InvalidConfigError(Exception):
    """Raised when adapter configuration is malformed."""
```

### Error Propagation

```python
def generate_all_feeds() -> List[LocalFeed]:
    """Run all adapters. Fail immediately if any adapter fails."""
    all_feeds = []

    for adapter in discover_adapters():
        try:
            feeds = adapter.generate_feeds()
            all_feeds.extend(feeds)
        except Exception as e:
            # FAIL LOUD: Don't continue if any adapter fails
            raise RuntimeError(
                f"Adapter {adapter.adapter_id} failed: {e}"
            ) from e

    return all_feeds
```

### Logging

```python
# Log all operations with context
logger.info(f"scanning playlist {playlist_id}")
logger.warning(f"skipping unavailable video {video_id}: {reason}")
logger.error(f"rate limited by YouTube, retrying in {delay}s")
```

---

## 9. PR-Sized Execution Chunks

### PR 1: Core Infrastructure (B1-a)
**Scope:** Interface definitions, directory structure, test fixtures
- [ ] `LocalFeed` dataclass in `backend/src/voogle/sources/__init__.py`
- [ ] `SourceAdapter` protocol in same file
- [ ] Create `data/generated-feeds/` directory
- [ ] Update `.gitignore` for generated feeds
- [ ] Add `feedgen>=1.0.0` to requirements.txt
- [ ] Unit tests for LocalFeed validation

**Estimated size:** ~150 LOC

### PR 2: YouTube Adapter Core (C1-a)
**Scope:** Scan and emit_rss functions, no downloading
- [ ] `backend/src/voogle/sources/youtube.py`
- [ ] `scan(playlist_url) -> List[PlannedEpisode]`
- [ ] `emit_rss(episodes, output_path) -> Path`
- [ ] Component tests with mocked yt-dlp
- [ ] Add `yt-dlp>=2024.1.0` to requirements.txt

**Estimated size:** ~300 LOC

### PR 3: YouTube Media Sync (C1-b)
**Scope:** Audio downloading with fallback strategy
- [ ] `sync_media(planned, output_dir) -> List[DownloadResult]`
- [ ] Two-pass download: web client → android fallback
- [ ] Progress reporting
- [ ] Component tests for download logic

**Estimated size:** ~250 LOC

### PR 4: Integration (B1-b)
**Scope:** Connect adapters to existing collection pipeline
- [ ] `backend/src/voogle/sources/generator.py`
- [ ] Modify `crawler.py` to handle `local://` URLs
- [ ] Integration tests: generated RSS → collection module
- [ ] CLI updates for `voogle-episodes`

**Estimated size:** ~200 LOC

### PR 5: Single-Item RSS Regression (B2)
**Scope:** Hardening existing feed parsing
- [ ] Test feed with exactly one `<item>`
- [ ] Test feed with multiple `<item>` elements
- [ ] Verify dict-vs-list handling in existing code

**Estimated size:** ~50 LOC

---

## 10. Dependencies Summary

### New Dependencies
```txt
# Add to backend/requirements.txt
feedgen>=1.0.0        # RSS/Podcast feed generation
yt-dlp>=2024.1.0      # YouTube metadata extraction
```

### Existing Dependencies Used
- `xmltodict` - RSS parsing (already present)
- `requests` - HTTP requests (already present)

---

## 11. Success Criteria

### Planning Phase Complete When:
- [x] Clear interface contract (LocalFeed, SourceAdapter)
- [x] Identified edge cases and failure modes
- [x] Dependency list evaluated (feedgen, yt-dlp)
- [x] Integration path with collection.py understood
- [x] PR-sized execution chunks identified and sequenced
- [x] Testing strategy defined

### Implementation Phase Complete When:
- [ ] All PRs merged and passing CI
- [ ] `ruff check .` passes
- [ ] `pytest tests/ --ignore=tests/e2e` passes
- [ ] E2E tests pass (no changes needed for backend-only feature)
- [ ] Can add YouTube playlist → episodes appear in search

---

## 12. Open Questions

1. **Audio storage location**: `data/audio/youtube/{video_id}.mp3` vs `data/media/youtube/...`?
   - Recommendation: Follow existing pattern in `storage.py`

2. **Feed regeneration frequency**: On every CLI run vs on-demand?
   - Recommendation: Every CLI run (simple, deterministic)

3. **BibleProject priority**: Defer until permission obtained?
   - Recommendation: Yes, focus on YouTube first

---

## Appendix: Expert Persona Concerns Addressed

### Data Engineer (Feed Reliability)
- URL expiration handled via local audio download
- Metadata mapping tested with real yt-dlp structures
- Error handling surfaces all failures immediately

### Platform Architect (Extensibility)
- Protocol-based interface allows new adapters without base class
- Directory structure supports multiple adapter types
- Integration via URL scheme (local://) is clean extension point

### Brutal Critic (Silent Failures)
- No try/except that swallows errors
- All adapter failures immediately propagate
- Clear logging at every step
- Test coverage for edge cases (empty playlists, private videos)
