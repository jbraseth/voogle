# Changelog

All notable changes to Voogle will be documented in this file.

Format: **WHAT** changed, **WHY** it changed, and any **REASONING** behind decisions.

---

## [Unreleased]

### Added
- **Result Map Visualization with 2D Embedding Projection** (#32)
  - New `/media/query/visualize` endpoint returns 2D coordinates for search results
  - PCA projection in `backend/src/voogle/vector.py` for dimensionality reduction
  - Query embedding included as reference point in visualization
  - `VisualizationResponse` schema with points, labels, scores, and query_point
  - `search_with_vectors()` function returns results with embedding vectors
  - Frontend: `ResultMap.svelte` component with Plotly scatter plot
  - Lazy-loaded Plotly.js to minimize bundle impact
  - Click-to-scroll: clicking a point scrolls to and highlights the result card
  - Hover tooltips show fragment preview text
  - Toggle button to show/hide visualization on Query page
  - Score-based color gradient (green for high similarity)
  - 6 unit tests for projection edge cases (min results, identical embeddings, typical sizes)
  - 2 integration tests for endpoint validation

**WHY**: Users have no spatial understanding of how search results relate to each other semantically. A 2D visualization helps show which results are clustered together and how close they are to the query.

**REASONING**: PCA chosen over UMAP for speed (deterministic, ~10ms for 20 points) and no new dependencies (sklearn already available). Lazy-loaded Plotly minimizes frontend bundle impact. Query point shown as star to provide anchor for understanding relative distances.

- **Multi-provider embeddings with consistent metadata** (#25)
  - `EmbeddingsProvider.model_name` and `provider_name` properties for tracking
  - Qdrant payload now includes `embedding_model`, `embedding_provider`, `embedded_at`
  - CLI: `voogle-episodes --rebuild-embeddings --reindex-channel <id>` to regenerate embeddings with metadata
  - CLI: `voogle-episodes --provider local|openai` to override embedding provider
  - CLI: `voogle-episodes --check-metadata` to audit fragments missing metadata
  - `get_embeddings_provider_by_name()` factory for explicit provider creation (non-cached)
  - Tests for protocol properties and metadata storage

**WHY**: When debugging search quality, knowing which embedding model produced each fragment is critical. Previously it was impossible to tell if results came from local or OpenAI embeddings, or which model version was used.

**REASONING**: Metadata in payload (not collection) allows mixed models during migration. Protocol properties enable provider-agnostic metadata generation. CLI rebuild command allows per-channel migration without affecting other data. Non-cached factory for CLI overrides avoids state pollution.
- **Refresh episode URL capability** (#24)
  - New `backend/src/voogle/collection/url_health.py` module for URL validation and refresh
  - `check_url()`: HEAD request with timeout and comprehensive error handling
  - `check_episode_url()`, `check_channel_urls()`, `check_all_broken_urls()`: Batch URL checking
  - `find_episode_in_rss()`: Match episodes by GUID (preferred) or title (fallback)
  - `find_updated_url()`, `preview_channel_refresh()`, `apply_url_refresh()`: URL refresh workflow
  - Streamlit admin UI in Media page with 3 sections:
    - "Detect Broken URLs": Scan all episodes and show broken ones
    - "Preview URL Refresh": Show old/new URLs before applying
    - "Apply URL Refresh": Update URLs with confirmation
  - Rate limiting (0.5s delay between requests) to avoid CDN rate limits
  - Audit logging of URL changes (old URL, new URL) for rollback capability
  - Preserves transcription and embeddings status during URL refresh

**WHY**: Podcast hosts sometimes change CDNs or file locations, causing episode URLs to 404. Previously this required deleting the episode and losing transcription/embedding work. Now admins can detect and fix broken URLs while preserving all processing work.

**REASONING**: Safe by default - all changes require explicit admin action with preview. HEAD requests minimize bandwidth. GUID-first matching is stable; title fallback handles GUID changes. No automatic refresh to prevent unintended changes.

- **Configurable chunking strategy per channel** (#19)
  - New `ChunkingConfig` dataclass with `chunk_size_words`, `chunk_overlap_words`, `min_chunk_length_words`
  - YAML config file at `config/chunking.yaml` for per-channel settings
  - Sentence-level overlap support for context preservation across fragment boundaries
  - CLI: `voogle-episodes --reindex-channel <id> --experiment <name>` for A/B testing
  - CLI: `voogle-search "query" --compare default,experiment_name` for side-by-side results
  - Experiment collections isolated in Qdrant (no cross-contamination)
  - Validation fails loud on invalid config values

**WHY**: Different podcast content types benefit from different chunking strategies. Technical content needs larger chunks for context, while conversational content needs smaller chunks for precision. This enables experimentation without code changes.

**REASONING**: Config file over database for version control. Sentence-level overlap maintains natural speech boundaries. A/B testing uses separate collections to avoid mixing embeddings from different strategies.
- **YouTube playlist ingestion adapter** (#17)
  - New `backend/src/voogle/sources/youtube_playlist.py` module
  - `scan(playlist_url)`: Scan playlist and get metadata without downloading
  - `sync_media(episodes, output_dir)`: Download audio files with skip/retry logic
  - `emit_rss(episodes, output_dir, feed_path)`: Generate RSS feed for Voogle ingestion
  - Two-pass download strategy: web client first, android fallback for rate limits
  - Progress reporting and failure resilience (continues on individual failures)
  - Settings: `youtube_output_dir`, `youtube_audio_format`, `youtube_cookies_file`
  - Comprehensive unit test coverage (31 tests) (#27)
  - JSON fixture files for realistic yt-dlp data mocking
  - Tests for helper functions (`_make_filename`, `_parse_upload_date`)
  - Dry-run integration tests verifying full scan→emit_rss workflow

**WHY**: Enables indexing YouTube playlists in Voogle. The adapter produces files and RSS that the existing collection pipeline can consume, enabling semantic search over YouTube content.

**REASONING**: Placed in `sources/` directory (separate from `collection/`) because it represents a different abstraction level. The adapter doesn't touch the database directly - it produces files + RSS that existing `collection/feed.py` can ingest. Uses yt-dlp with no cookies by default (privacy-respecting).

### Fixed
- **Single-item RSS feeds now parse correctly** (#23)
  - Added `_normalize_items()` helper to handle xmltodict dict vs list edge case
  - When RSS has exactly one `<item>`, xmltodict returns a dict instead of list
  - New helper normalizes both cases to always return a list
  - Added 14 regression tests to prevent re-introduction
  - RSS fixture files (single, multi, empty) for deterministic testing

**WHY**: Podcasts with exactly one episode would fail to parse, breaking import for new or limited-episode feeds. This is a common edge case in RSS parsing.

**REASONING**: Test-driven fix locks in the behavior permanently. The `TestXmltodictBehavior` tests document the underlying library behavior we're protecting against.

- **Dev mode works natively and in Docker** (#15)
  - Vite proxy target now configurable via `VITE_BACKEND_TARGET` environment variable
  - Native dev defaults to `http://localhost:8080` (backend `make start` port)
  - Docker dev sets `VITE_BACKEND_TARGET=http://backend:80` in compose.yml
  - Dev mode continues to have no CORS restrictions (permissive for browser extensions)

**WHY**: The hardcoded `http://backend:80` proxy target only worked inside Docker. Native development (frontend `npm run dev` + backend `make start`) requires routing to `localhost:8080`.

- **Frontend local media playback** (#13)
  - Player now rewrites `/local/` URLs to use backend API origin (needed for dev where frontend/backend ports differ)
  - Fixed `scrollIntoView` timing bug using Svelte's `tick()` instead of arbitrary `setTimeout`
  - Added "LOCAL" badge to distinguish local episodes from podcast episodes in search results

**WHY**: In dev environment, frontend (port 5173) and backend (port 8080) run on different origins. Without URL rewriting, local media URLs failed to load.

### Added
- **Static route for local media files** (#11)
  - New `/local/<channel>/<file>` endpoint to serve audio files from the media folder
  - Path traversal protection prevents access to files outside media directory
  - Query results now include `media_url` field with the appropriate playback URL
  - Local channels return `/local/...` URLs, podcast channels return original URLs
  - Frontend updated to use `media_url` for playback (enables local channel audio)
  - Play button now visible for local channels (previously hidden)
  - Integration tests for file serving, 404 handling, and path security
  - E2E tests parametrized for both podcast and local channel playback
  - New fixtures: `local_channel_with_embeddings`, `mixed_channel_test_data`

**WHY**: Local episodes stored on disk need a stable URL for frontend playback. Without this route, the frontend couldn't play locally indexed audio files.

**REASONING**: URL rewriting happens at the presentation layer (in query results) rather than in the database, keeping the schema unchanged. The `/local/` route uses path resolution and prefix checking to prevent directory traversal attacks. The frontend now uses `media_url` consistently for all channel types, enabling unified playback.

### Changed
- **Upgraded Python from 3.9/3.10 to 3.12** (#7, #8)
  - Updated all Dockerfiles to use `python:3.12-slim-bookworm`
  - Migrated ormar models from `class Meta` to `ormar_config` pattern (ormar 0.20.x breaking change)
  - Migrated pydantic `BaseSettings` to `pydantic-settings` package (Pydantic v2 breaking change)
  - Upgraded all dependencies to latest compatible versions
  - Fixed deprecation warnings: FastAPI lifespan events, qdrant collection API

**WHY**: Python 3.12 brings performance improvements, better error messages, and security updates. Staying on 3.9/3.10 was becoming a liability as dependencies dropped support.

**REASONING**: This was a significant upgrade involving breaking changes in ormar (ORM) and pydantic (settings). The ormar 0.20 release changed the model configuration API entirely, and pydantic v2 moved BaseSettings to a separate package.

- **Optimized CI pipeline for fast feedback** (#9)
  - Lint runs natively on GitHub runner (~7 seconds) using ruff only
  - Test runs in Docker with full dependencies (~2 minutes)
  - Separate Build CI Image workflow - only triggers when dockerfile/requirements change
  - Removed Playwright from CI image (e2e tests run locally)
  - Type checking (pyright) is optional, not blocking in CI

**WHY**: Fast CI feedback is critical for developer productivity. Waiting 4+ minutes for lint results is unacceptable.

**REASONING**: Ruff doesn't need dependencies to run - it's pure syntax analysis. By running it natively instead of pulling an 8GB Docker image, lint drops from 3+ minutes to 7 seconds. Pyright needs all deps to resolve imports, so it remains optional for devs to run locally.

### Added
- **Baseline test infrastructure** (#6)
  - Unit tests for pure functions
  - Component tests for modules in isolation
  - Integration tests for API + database
  - E2E tests with Playwright (run locally)
  - Pytest configuration with warning filters for third-party deprecations
  - Test fixtures for database, models, and HTTP mocking

**WHY**: A solid test foundation enables confident refactoring and feature development. Tests document expected behavior and catch regressions early.

- Claude Code context files for AI-assisted development
  - `CLAUDE.md`: Comprehensive project overview, architecture, and critical patterns
  - `docs/plan.md`: Detailed task planning for the Voilib → Voogle rename
  - `context/design-principles.md`: Core design philosophy (fail loud, validate at boundaries, simple over clever)
  - `context/style-guide.md`: Code style conventions for Python, JavaScript/Svelte, SQL, and Git

**WHY**: To enable effective AI-assisted development with full project context. Claude Code can now understand the architecture, follow established patterns, and contribute to the codebase consistently.

**REASONING**: As a fork of an archived project, comprehensive documentation helps both human developers and AI assistants quickly understand the system, reducing onboarding time and maintaining code quality during the rename and future development.

---

## Project Origin

**Voogle** is a fork of [Voilib](https://github.com/unmonoqueteclea/voilib) by Pablo Álvarez de Sotomayor Posadillo.

**Fork Date**: December 2025

**WHY**: Voilib was archived by its original maintainer, but the core concept of semantic podcast search remains valuable. This fork aims to:
1. Continue development and maintenance
2. Rename the project to establish a distinct identity
3. Modernize dependencies and architecture as needed
4. Potentially extend functionality beyond the original scope

**Original License**: GNU GPLv3 (maintained in this fork)

**Acknowledgment**: Voogle builds upon the excellent foundation created by the Voilib project. The original architecture, design decisions, and implementation quality made this fork possible.

---

## Previous History

See git commit history for changes from the original Voilib project.
