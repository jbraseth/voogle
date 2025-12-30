# Changelog

All notable changes to Voogle will be documented in this file.

Format: **WHAT** changed, **WHY** it changed, and any **REASONING** behind decisions.

---

## [Unreleased]

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
