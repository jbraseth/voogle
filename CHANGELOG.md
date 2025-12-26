# Changelog

All notable changes to Voogle will be documented in this file.

Format: **WHAT** changed, **WHY** it changed, and any **REASONING** behind decisions.

---

## [Unreleased]

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
