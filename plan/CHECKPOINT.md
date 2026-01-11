# Wave 3 Checkpoint: Manual Verification

After `hive run --wave 1-3` completes, perform these manual verification steps before continuing to waves 4-5.

## Prerequisites

```bash
# Start infrastructure
docker compose up redis qdrant -d

# Start backend
cd backend && make start

# Start frontend
cd frontend && npm run dev
```

## 1. Import Test Data

```bash
cd backend

# Import one course for testing
voogle-bibleproject import \
  --source ~/projects/bibleproject-research/data \
  --courses abraham

# Verify import
voogle-bibleproject list
```

Expected: Shows "abraham" course with session count.

## 2. Test Slides API

```bash
# List courses
curl http://localhost:8080/bibleproject/courses | jq .

# Get course detail
curl http://localhost:8080/bibleproject/courses/abraham | jq .

# Get session slides
curl http://localhost:8080/bibleproject/slides/abraham/1 | jq .
```

Expected:
- Courses endpoint returns list with abraham
- Course detail shows sessions array
- Slides endpoint returns slides with `resolved_assets` containing CDN URLs (not arc_ids)

## 3. Test MediaPlayer (HLS Video)

Open browser to: `http://localhost:5173`

Create a test page or use browser console:
```javascript
// Test Mux HLS stream plays
// Use a known Mux playback ID from the imported data
```

Expected: Video loads and plays from Mux HLS stream.

## 4. Test Slide Components

Temporarily add a test route or use Storybook-style approach to render slides:

Verify each variant renders:
- [ ] TitleSlide - Shows course name, session, teacher
- [ ] MainPointSlide - Large centered text
- [ ] WordDefinitionSlide - Hebrew/Greek with transliteration
- [ ] ParagraphSlide - Title + content
- [ ] ScriptureSlide - Verse reference + text
- [ ] DiagramSlide - Image loads from CDN URL
- [ ] ImageSlide - Image loads from CDN URL

## 5. Test Sync Behavior

With SlidePanel + MediaPlayer together:
- [ ] Slides advance as video plays
- [ ] Clicking slide thumbnail seeks video
- [ ] currentTime binding works correctly

---

## If Issues Found

1. Note the specific issue
2. Create a bug fix branch: `fix/checkpoint-{issue}`
3. Fix and merge before continuing
4. Re-verify

## Continue Execution

Once all checks pass:

```bash
hive run --wave 4-5
```

Then run full E2E tests before considering the feature complete.
