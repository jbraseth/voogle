# Changelog

All notable changes to Voogle will be documented in this file.

Format: **WHAT** changed, **WHY** it changed, and any **REASONING** behind decisions.

---

## [Unreleased]

### Changed
- **Upgraded Python from 3.9/3.10 to 3.12** (#7)
  - Updated all Dockerfiles to use `python:3.12-slim-bookworm`
  - Migrated ormar models from `class Meta` to `ormar_config` pattern (ormar 0.20.x breaking change)
  - Migrated pydantic `BaseSettings` to `pydantic-settings` package (Pydantic v2 breaking change)
  - Upgraded all dependencies to latest compatible versions
  - Added `scripts/lint.sh` and `scripts/test.sh` for Docker-based CI
  - Simplified GitHub Actions workflow to use new CI scripts

**WHY**: Python 3.12 brings performance improvements, better error messages, and security updates. Staying on 3.9/3.10 was becoming a liability as dependencies dropped support.

**REASONING**: This was a significant upgrade involving breaking changes in ormar (ORM) and pydantic (settings). The ormar 0.20 release changed the model configuration API entirely, and pydantic v2 moved BaseSettings to a separate package.

### Added
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
