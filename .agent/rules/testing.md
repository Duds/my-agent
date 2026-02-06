# Testing Strategy

## Philosophy
We follow the **Testing Pyramid**:
1.  **Unit Tests (Pytest/Jest)**: Fast, isolated tests for individual functions and classes. (70%)
2.  **Integration Tests**: Testing interactions between components (e.g., Router -> ModelAdapter). (20%)
3.  **E2E Tests**: Full system flows (User -> frontend -> core -> LLM -> response). (10%)

## Python (Core)
*   **Framework**: `pytest`
*   **Async Support**: `pytest-asyncio`
*   **HTTP Testing**: `httpx` (using `TestClient` from FastAPI)
*   **Mocking**: Use `unittest.mock` or `pytest-mock` to mock external LLM calls. **NEVER** let unit tests call real paid APIs or local heavy models.

### Example: Unit Test
```python
import pytest
from core.router import ModelRouter, Intent

@pytest.mark.asyncio
async def test_router_intent_detection():
    # Mock adapters...
    router = ModelRouter(...)
    result = await router.route_request("Calculate 2+2")
    assert result["intent"] == Intent.SPEED
```

## Frontend (Next.js)
*   **Framework**: Jest + React Testing Library (implied, yet to be fully set up).
*   **Linting**: `npm run lint`

## Rules
1.  **New Features = New Tests**: Do not merge code without coverage.
2.  **Fixes = Regression Tests**: If you fix a bug, write a test that reproduces it first.
3.  **Fast**: Unit tests must run in <5 seconds total.
