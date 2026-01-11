# Slide Panel + Variant Components

## Metadata
```yaml
id: P2
wave: 3
priority: critical
dependencies: [P1]
branch: feat/slide-panel
milestone: slides
```

## Objective
Frontend slide display system with components for each variant type, synchronized to video playback

## File Targets
### Files to Create

- `frontend/src/lib/slides/SlidePanel.svelte`:
  - Props: `slides` (array), `currentTime` (number from MediaPlayer)
  - Computed: `currentSlideIndex` based on timestamp <= currentTime
  - Shows current slide prominently, thumbnail strip below for navigation
  - Dispatches 'seek' event with timestamp when thumbnail clicked
- `frontend/src/lib/slides/SlideRenderer.svelte`:
  - Props: `slide` (object with variant, content, resolved_assets)
  - Switches on `slide.variant` to render appropriate component
  - Fallback for unknown variants
- `frontend/src/lib/slides/variants/TitleSlide.svelte` (className, sessionNumber, sessionName, teacherName)
- `frontend/src/lib/slides/variants/MainPointSlide.svelte` (content text, large centered)
- `frontend/src/lib/slides/variants/WordDefinitionSlide.svelte` (wordDefinitionData array with language, original, transliteration, definition)
- `frontend/src/lib/slides/variants/ParagraphSlide.svelte` (title, content)
- `frontend/src/lib/slides/variants/ScriptureSlide.svelte` (handles single-verse and multi-verse, verse reference + text)
- `frontend/src/lib/slides/variants/QuestionSlide.svelte` (question text)
- `frontend/src/lib/slides/variants/DiagramSlide.svelte` (uses resolved_assets.diagramArcId for src, shows caption)
- `frontend/src/lib/slides/variants/ImageSlide.svelte` (uses resolved_assets.imgArcId for src)
- `frontend/src/lib/slides/variants/TableSlide.svelte` (renders body HTML content)
- `frontend/src/lib/slides/variants/ThankYouSlide.svelte` (simple thank you message)
- `frontend/src/lib/slides/index.js` - Exports all components

## Acceptance Criteria
```bash
cd frontend && npm run build && ls src/lib/slides/variants/
```

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): slide-panel-variant-components"
gh pr create --title "feat({id}): Slide Panel + Variant Components" --body "Frontend slide display system with components for each variant type, synchronized to video playback"
gh pr merge --squash --delete-branch
```
