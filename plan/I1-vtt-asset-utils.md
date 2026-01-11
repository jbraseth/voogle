# VTT Converter + Asset Resolver

## Metadata
```yaml
id: I1
wave: 1
priority: critical
dependencies: []
branch: feat/vtt-asset-utils
milestone: foundation
```

## Objective
Create utility modules for VTT→CSV conversion and arc_id→URL resolution

## File Targets
### Files to Create

- `backend/src/voogle/bibleproject/__init__.py` - Package init
- `backend/src/voogle/bibleproject/vtt_converter.py`:
  - `parse_vtt_timestamp(ts: str) -> float` - Handles '00:01:23.456' → 83.456
  - `convert_vtt_to_csv(vtt_path: Path, csv_path: Path) -> int` - Returns cue count
  - Handle BOM prefix, multi-line cues, speaker tags like `<v ->text</v>`
- `backend/src/voogle/bibleproject/assets.py`:
  - `@dataclass AssetInfo(arc_id, asset_type, src, alt, caption, title)`
  - `load_assets_manifest(path: Path) -> dict[str, AssetInfo]`
  - `resolve_slide_assets(slide: dict, manifest: dict) -> dict` - Returns slide with resolved URLs
- `tests/unit/bibleproject/__init__.py`
- `tests/unit/bibleproject/test_vtt_converter.py`
- `tests/unit/bibleproject/test_assets.py`

## Acceptance Criteria
```bash
cd backend && pytest tests/unit/bibleproject/ -v && ruff check src/voogle/bibleproject/
```

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): vtt-converter-+-asset-resolver"
gh pr create --title "feat({id}): VTT Converter + Asset Resolver" --body "Create utility modules for VTT→CSV conversion and arc_id→URL resolution"
gh pr merge --squash --delete-branch
```
