# Task Planning

Active tasks and implementation plans for Voogle.

---

## Active: Issue #1 - Rename Voilib to Voogle

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
