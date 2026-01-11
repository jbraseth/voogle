# Session Browser + Documentation

## Metadata
```yaml
id: N2
wave: 5
priority: medium
dependencies: [N1]
branch: feat/session-browser
milestone: browser
```

## Objective
Browsable course/session UI and setup documentation

## File Targets
### Files to Create

- `frontend/src/lib/pages/Courses.svelte`:
  - Fetches `GET /bibleproject/courses` on mount
  - Displays grid of course cards (image, title, session count)
  - Click navigates to `/courses/{slug}`
- `frontend/src/lib/pages/CourseDetail.svelte`:
  - Fetches `GET /bibleproject/courses/{slug}`
  - Shows course info + list of sessions
  - Click session navigates to `/session/{course}/{id}`
- `frontend/src/lib/pages/SessionPlayer.svelte`:
  - Full-page BibleProjectPlayer for a session
  - Shows session title, description, PDF download link
- `docs/bibleproject-setup.md`:
  - Prerequisites (research data location)
  - Import command usage
  - Indexing after import
  - Troubleshooting

### Files to Modify

- `frontend/src/App.svelte` - Add routes: `/courses`, `/courses/:slug`, `/session/:course/:id`
- `backend/src/voogle/bibleproject/cli.py` - Add 'status' command showing import stats

## Acceptance Criteria
```bash
cd frontend && npm run build && test -f ../docs/bibleproject-setup.md
```

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): session-browser-+-documentation"
gh pr create --title "feat({id}): Session Browser + Documentation" --body "Browsable course/session UI and setup documentation"
gh pr merge --squash --delete-branch
```
