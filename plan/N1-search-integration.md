# Search Integration

## Metadata
```yaml
id: N1
wave: 4
priority: high
dependencies: [B1, P2]
branch: feat/search-slides-integration
milestone: integration
```

## Objective
Connect BibleProject search results to slide-enabled video playback

## File Targets
### Files to Modify

- `backend/src/voogle/schemas/media.py`:
  - Add to QueryResponse: `source_type` (Optional[str]), `slides_url` (Optional[str])
- `backend/src/voogle/routers/media.py`:
  - In `query()` handler, detect if episode.channel is BibleProject source
  - If so, populate `source_type='bibleproject'` and `slides_url='/bibleproject/slides/{course}/{session}'`
  - Extract course_slug and session_id from episode metadata or channel info
- `frontend/src/lib/pages/Query.svelte`:
  - When rendering result, check `result.source_type` or `result.slides_url`
  - If bibleproject: render BibleProjectPlayer instead of Player

### Files to Create

- `frontend/src/lib/BibleProjectPlayer.svelte`:
  - Props: `episode`, `channel`, `startTime`, `mediaUrl`, `slidesUrl`
  - Composes: MediaPlayer (left/main) + SlidePanel (right/side)
  - Fetches slides from slidesUrl on mount
  - Binds currentTime from MediaPlayer to SlidePanel
  - Handles seek events from SlidePanel
- `tests/unit/bibleproject/test_query_response.py`:
  - Test QueryResponse schema includes new fields
  - Test source_type detection logic (mock channel data)
  - Use TestClient, no deployment needed

## Acceptance Criteria
```bash
cd backend && pytest tests/unit/bibleproject/test_query_response.py -v && ruff check src/voogle/routers/media.py
cd frontend && npm run build
```

## Notes
- Backend tests use TestClient with mocked Episode/Channel
- Frontend just needs to build (visual verification at checkpoint)

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): search-integration"
gh pr create --title "feat({id}): Search Integration" --body "Connect BibleProject search results to slide-enabled video playback"
gh pr merge --squash --delete-branch
```
