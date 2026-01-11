# BibleProject Setup Guide

This guide explains how to set up and import BibleProject course content into Voogle.

## Prerequisites

1. **BibleProject Research Data**: You need the research data files at the expected path:
   ```
   data/bibleproject/
   ├── {course-slug}/
   │   ├── adapter_config.json    # Course metadata (title, description, image)
   │   ├── assets.json            # Asset manifest for CDN URLs
   │   └── slides/
   │       ├── {session-id}.json  # Slide data for each session
   │       └── ...
   └── ...
   ```

2. **Running Services**: Ensure the backend and database are running:
   ```bash
   # Native dev
   cd backend && make start

   # Or Docker dev
   ./infra/dev-up
   ```

## Import Commands

### Step 1: Import BibleProject Content

Run the import command to create Channel and Episode records from the research data:

```bash
voogle-bibleproject import
```

This command:
- Scans `data/bibleproject/` for course directories
- Creates a Channel record for each course (`channel_type='bibleproject'`)
- Creates Episode records for each session with proper `guid`, `title`, and `mux_playback_id`

### Step 2: Index for Search (Optional)

If you want episodes to be searchable, run the indexing command:

```bash
voogle-episodes --store
```

This indexes transcribed episodes into the Qdrant vector database for semantic search.

## Verification

### Check Courses API

Verify courses are available via the API:

```bash
curl http://localhost:8080/api/bibleproject/courses
```

Expected: JSON array of courses with `slug`, `title`, `session_count`, and `image`.

### Check Course Detail API

Verify a specific course and its sessions:

```bash
curl http://localhost:8080/api/bibleproject/courses/{course-slug}
```

Expected: JSON with `slug`, `title`, `description`, and `sessions` array.

### Check Frontend Routes

Navigate to these pages in your browser:
- `/courses` - Grid of all courses
- `/courses/{slug}` - Course detail with session list
- `/session/{course}/{id}` - Full-page player for a session

## Troubleshooting

### No Courses Showing

1. **Check data directory exists**:
   ```bash
   ls -la data/bibleproject/
   ```

2. **Check adapter_config.json exists** for each course:
   ```bash
   ls data/bibleproject/*/adapter_config.json
   ```

3. **Check import ran successfully**:
   ```bash
   voogle-bibleproject import --verbose
   ```

### Session Not Playing

1. **Check episode exists in database**:
   ```bash
   curl http://localhost:8080/api/bibleproject/episodes/{course}/{session}
   ```

2. **Check slides data exists**:
   ```bash
   ls data/bibleproject/{course}/slides/{session}.json
   ```

3. **Check mux_playback_id is set** on the episode:
   - The `mux_playback_id` field must be populated for video streaming
   - This is set during import from `adapter_config.json`

### Slides Not Rendering

1. **Check bp-web-components assets** are available at `/bp/`:
   - `/bp/bp-slides.js`
   - `/bp/bp-core.js`
   - `/bp/theme.css`
   - `/bp/bp.css`

2. **Check browser console** for JavaScript errors

### Search Not Working

1. **Ensure transcriptions exist** for episodes
2. **Run indexing command**:
   ```bash
   voogle-episodes --store
   ```
3. **Check Qdrant is running**:
   ```bash
   curl http://localhost:6333/collections
   ```

## Data Structure Reference

### adapter_config.json

```json
{
  "title": "Course Title",
  "description": "Course description...",
  "image": "https://cdn.example.com/course-image.jpg"
}
```

### slides/{session-id}.json

```json
{
  "title": "Session Title",
  "duration": 1234.5,
  "slides": [
    {
      "timestamp": 0,
      "variant": "title",
      "content": { ... },
      "animations": [ ... ]
    }
  ]
}
```

### Episode GUID Format

Episodes are identified by a GUID in the format:
```
bibleproject:{course-slug}:{session-id}
```

Example: `bibleproject:intro-to-bible:session-01`
