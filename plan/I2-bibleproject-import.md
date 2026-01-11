# Complete Import Pipeline

## Metadata
```yaml
id: I2
wave: 2
priority: critical
dependencies: [I1]
branch: feat/bibleproject-import
milestone: import
```

## Objective
Import all BibleProject research data into Voogle's expected structure

## File Targets
### Files to Create

- `backend/src/voogle/bibleproject/importer.py`:
  - `RESEARCH_DIR` = Path for source data location
  - `import_course(course_slug: str, source_dir: Path, target_dir: Path) -> ImportResult`
  - `import_all_courses(source_dir: Path) -> list[ImportResult]`
  - Steps: 1) Read metadata JSONs, 2) Generate adapter config, 3) Convert VTT→CSV, 4) Copy slides, 5) Copy assets.json
- `backend/src/voogle/bibleproject/cli.py` with click commands:
  - `voogle-bibleproject import --source PATH --target PATH`
  - `voogle-bibleproject list` (shows imported courses)
- `tests/component/bibleproject/__init__.py`
- `tests/component/bibleproject/test_importer.py` (use tmp_path fixture, mock research data structure)

### Files to Modify

- `backend/pyproject.toml` - Add entry point: `voogle-bibleproject = voogle.bibleproject.cli:main`

## Acceptance Criteria
```bash
cd backend && pip install -e . && voogle-bibleproject --help && pytest tests/component/bibleproject/ -v
```

## Git Protocol
```bash
git add -A
git commit -m "feat({id}): complete-import-pipeline"
gh pr create --title "feat({id}): Complete Import Pipeline" --body "Import all BibleProject research data into Voogle's expected structure"
gh pr merge --squash --delete-branch
```
