# Style Guide

Code conventions for Voogle.

---

## Python (Backend)

### Formatting
- **Formatter:** Black (default settings)
- **Linting:** Pylint
- **Imports:** Standard library, third-party, local (separated by blank lines)

### Naming
```python
# Variables and functions: snake_case
user_count = 0
def get_episodes():

# Classes: PascalCase
class ChannelOut:

# Constants: SCREAMING_SNAKE_CASE
MAX_PAGE_SIZE = 100
```

### Type Hints
```python
# Use type hints for function signatures
def score_query(query: str, k: int = 6) -> list[QueryResponse]:
    ...

# Use Optional from typing or | None
from typing import Optional
def find_channel(channel_id: Optional[uuid.UUID] = None):
    ...
```

### Async Patterns
```python
# FastAPI routes are async
@router.get("/channel")
async def channels():
    return await paginate(qs)

# Use Ormar ORM for async database access
channel = await media.Channel.objects.get(id=channel_id)
```

### Error Handling
```python
# Log with context
logger.error("operation_failed", error=str(e), context={"id": item_id})

# Let FastAPI handle HTTP exceptions
raise fastapi.HTTPException(status_code=404, detail="Not found")
```

---

## JavaScript/Svelte (Frontend)

### Formatting
- **Build:** Vite
- **Styling:** Tailwind CSS + DaisyUI

### Naming
```javascript
// Variables and functions: camelCase
const userCount = 0;
function getEpisodes() {}

// Components: PascalCase files
// CardQueryResult.svelte, PageHeader.svelte
```

### Component Structure
```svelte
<script>
  // Imports first
  import Component from './lib/Component.svelte'

  // Props (export let)
  export let data;

  // Local state
  let isLoading = false;

  // Reactive statements
  $: derivedValue = data.length;

  // Functions
  function handleClick() {
    // ...
  }
</script>

<div class="flex flex-col">
  <Component {data} on:click={handleClick} />
</div>
```

### Routing
```javascript
// Uses page.js for client-side routing
import router from "page"

router('/path', (ctx, next) => {
  // handle route
  next();
});
router.start();
```

---

## SQL

### Formatting
```sql
-- Keywords uppercase
SELECT id, title
FROM episodes
WHERE transcribed = true
ORDER BY created_at DESC;

-- Table names: snake_case, plural
CREATE TABLE episodes (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL
);
```

---

## Git

### Commit Messages
```
#<issue>: <short summary>

Examples:
#12: add episode search endpoint
#42: fix null values in transcription
```

### Branch Names
```
<type>/<issue#>-<short-description>

Examples:
feat/12-add-search-endpoint
fix/42-transcription-null-check
refactor/1-rename-voilib-to-voogle
```

### Branch Types
- `feat` - New functionality
- `fix` - Bug fixes
- `refactor` - Code restructuring without behavior change
- `chore` - Maintenance tasks, dependencies
- `doc` - Documentation updates
- `test` - Adding or updating tests

---

## Testing

### Type Hints
Always use type hints for test function parameters:
```python
def test_crud_episodes(channel: models.media.Channel, auth_client: TestClient) -> None:
    ...
```

### Imports
All imports at module top-level:
```python
from unittest.mock import patch
from voogle import models

def test_something():
    ...
```

### Test Documentation
Use description markers for all tests:
```python
@pytest.mark.description("Full CRUD operations for channels: list, filter, get, delete, and create")
async def test_crud_channels(channel: models.media.Channel, auth_client: TestClient) -> None:
    ...
```

### Fixtures
Name fixtures explicitly to avoid linter warnings:
```python
@pytest.fixture(name="channel")
async def fixture_channel(aiolib) -> models.media.Channel:  # type: ignore
    # Create test data
    ch = await models.Channel.objects.create(...)
    return ch
```

Handle unused fixture parameters with side effects:
```python
def test_crud_episodes(channel: models.media.Channel, auth_client: TestClient) -> None:
    _unused = channel  # Creates episodes in DB
    response = auth_client.get("/media/episode").json()
    ...
```

### Mocking
Patch where the function is called, not where it's defined:
```python
async def test_something(channel: models.media.Channel) -> None:
    with patch("voogle.collection.crawler.get_or_create_channel") as mock:
        mock.return_value = (True, channel)
        ...
```

Prefer real database objects with mocked network calls:
```python
async def test_create_channel(auth_client: TestClient) -> None:
    with patch("voogle.collection.crawler.get_or_create_channel") as mock:
        new_channel = await models.Channel.objects.create(...)
        mock.return_value = (True, new_channel)
        ...
```

### Test Markers
```python
# Module-level marker
pytestmark = pytest.mark.integration

# Test-level markers
@pytest.mark.component
@pytest.mark.description("Verifies storage path generation")
async def test_episodes(channel: models.media.Channel) -> None:
    ...
```
