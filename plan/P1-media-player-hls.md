# MediaPlayer with HLS Support

## Metadata
```yaml
id: P1
wave: 1
priority: critical
dependencies: []
branch: feat/media-player-hls
milestone: media
```

## Objective
Unified audio/video player component with HLS streaming for Mux URLs

## File Targets
### Files to Modify

- `frontend/package.json` - Add hls.js dependency

### Files to Create

- `frontend/src/lib/MediaPlayer.svelte`:
  - Props: `src` (string), `startTime` (number, default 0), `poster` (string, optional)
  - Exports: `currentTime` (reactive binding), `duration`, `paused`, `playing`
  - Events: `timeupdate`, `play`, `pause`, `ended`, `canplay`
  - Logic: If src contains '.m3u8', use `<video>` + hls.js; else use `<audio>`
  - Seek to startTime when canplay fires
  - Style: Full-width responsive, controls visible

### Files to Modify

- `frontend/src/lib/Player.svelte` - Refactor to use MediaPlayer internally, keep existing props/events for backward compat

## Acceptance Criteria
```bash
cd frontend && npm install && npm run build && grep -l 'hls.js' package.json
```

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): mediaplayer-with-hls-support"
gh pr create --title "feat({id}): MediaPlayer with HLS Support" --body "Unified audio/video player component with HLS streaming for Mux URLs"
gh pr merge --squash --delete-branch
```
