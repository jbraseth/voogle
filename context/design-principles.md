# Design Principles

## Error Handling

### Fail Loud
No swallowed exceptions. No silent fallbacks. Errors surface immediately with full context.

**Do:** Raise exceptions with descriptive messages, let errors propagate to proper handlers.
**Don't:** Catch exceptions just to log them, return `None` on failure, use bare `except:`.

### Validate at Boundaries
Validate external input rigorously. Trust internal code. Parse, don't validate—transform raw input into typed domain objects at entry points.

**Boundaries:** API handlers, message consumers, file readers, env var loading.
**Internal:** Function calls between modules don't re-validate.

## Code Style

### Simple Over Clever
Readable > compact. Build for current needs, not hypothetical futures. Three similar lines beats one clever abstraction.

**Do:** Inline simple logic, use explicit names, write boring code.
**Don't:** Create abstractions for single use cases, add "just in case" flexibility, optimize prematurely.

### Async All The Way
All I/O is async. No blocking calls in async contexts. Respect backpressure.

**Do:** Use `async/await` for network, file, and database operations.
**Don't:** Call sync libraries in async code, ignore queue/buffer limits.

## Architecture

### Single Source of Truth
No duplicated business logic. Config in env vars. Constants defined once.

- Config: `src/config/` reads env vars, exports typed settings
- Shared utilities: `src/shared/`
- Domain logic: Lives in one place, imported where needed

### Composition Over Inheritance
Prefer small, focused functions and classes. Inject dependencies explicitly.

**Do:** Pass dependencies as arguments, use protocols/interfaces.
**Don't:** Deep inheritance hierarchies, global state, hidden dependencies.

## Operations

### Observable by Default
Structured JSON logging. Metrics for key operations. Health endpoints.

Every log entry should answer: What happened? To what? Why does it matter?

### Secure by Default
Auth required unless explicitly marked public. Validate and sanitize all external input. Size limits on all inputs.

**Never:** Secrets in code, SQL string concatenation, unvalidated redirects.

## Testing

### Test Behavior, Not Implementation
Integration tests > unit tests for APIs. Mock external services, not internal code.

**Do:** Test public interfaces, use real dependencies when fast enough.
**Don't:** Test private methods, mock everything, write slow tests.

### Understand Before Fixing
When fixing test fixtures or adapting tests, read the actual data structures first. Don't guess field names or schemas from error messages.

**Do:** Read the NamedTuple/dataclass/schema definition before writing fixture data.
**Don't:** Reactively fix field names one error at a time.

### E2E Tests Monitor Console Errors
Browser console errors/warnings in E2E tests indicate real bugs. The `console_monitor` fixture exists to catch these.

**Do:** Run E2E tests with `--headed` during development to verify no console errors.
**Don't:** Bypass console monitoring during manual testing—if the browser shows errors, the test should fail.

---

## Pre-Commit Checklist

- [ ] Does this fail loudly when wrong?
- [ ] Is this the simplest solution that works?
- [ ] Am I validating at the right boundary?
- [ ] Are dependencies explicit (not hidden/global)?
- [ ] Can I observe this in production (logs/metrics)?
- [ ] Did I avoid adding unused flexibility?
