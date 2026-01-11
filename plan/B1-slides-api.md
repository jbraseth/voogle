# Slides API Endpoint

## Metadata
```yaml
id: B1
wave: 3
priority: critical
dependencies: [I2]
branch: feat/slides-api
milestone: media
```

## Objective
Backend API to serve slide data with resolved asset URLs for frontend consumption

## File Targets
### Files to Create

- `backend/src/voogle/routers/bibleproject.py`:
  - `GET /bibleproject/courses` → list of `{slug, title, session_count, image}`
  - `GET /bibleproject/courses/{slug}` → `{slug, title, description, sessions: [{id, title, duration}]}`
  - `GET /bibleproject/slides/{course_slug}/{session_id}` → `{session_id, total_slides, slides: [...]}`
  - Each slide includes `resolved_assets` dict mapping arc_ids to CDN URLs
  - Uses `assets.load_assets_manifest()` and `assets.resolve_slide_assets()`
- `backend/src/voogle/schemas/bibleproject.py` with Pydantic models: `CourseListItem`, `CourseDetail`, `SessionSlides`, `Slide`
- `tests/unit/bibleproject/test_slides_api.py`:
  - Use FastAPI TestClient (in-process, no deployment needed)
  - Use tmp_path fixtures with mock slide/asset JSON files
  - Test each endpoint returns expected schema
  - Test asset resolution works correctly

### Files to Modify

- `backend/src/voogle/app.py` - Register bibleproject router at `/bibleproject` prefix

## Acceptance Criteria
```bash
cd backend && pytest tests/unit/bibleproject/ -v && ruff check src/voogle/routers/bibleproject.py
```

## Notes
- Tests use TestClient, NOT a running deployment
- Mock data in fixtures, not real imported data

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): slides-api-endpoint"
gh pr create --title "feat({id}): Slides API Endpoint" --body "Backend API to serve slide data with resolved asset URLs for frontend consumption"
gh pr merge --squash --delete-branch
```
