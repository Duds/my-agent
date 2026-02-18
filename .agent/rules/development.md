# Development & Testing Rules

## Git Workflow

- **Branching**: Use feature branches (`feat/`, `fix/`, `docs/`).
- **Commits**: Follow Conventional Commits format (`type(scope): message`).
- **PBI Completion**: Commit and push to remote after completing each PBI. This ensures progress is saved and visible.
- **PRs**: Keep PRs small and focused.

## Backend Development (Python/FastAPI)

- Use **async/await** where appropriate (FastAPI supports both, prefer async for I/O).
- Implement structured error handling with `try/except` and `HTTPException`.
- Use **logging** or **loguru**; ensure logs are scannable and structured.
- Targeted Python version is **3.10+**.
- Adhere to **PEP 8** style guide.


## Frontend Development (Next.js)

- Use React functional components and hooks.
- Follow the App Router conventions for new work.

## Testing Standards

- **Coverage**: Aim for 80%+ test coverage.
- **Patterns**: Follow the AAA (Arrange, Act, Assert) pattern.
- **Tooling**: Use Jest/Vitest for unit/integration tests.
- **Data**: Seed unique business-specific data through scripts; avoid hardcoded placeholders.
- **Checklist**: 
  - Run tests before committing.
  - Do not build or commit until tests pass.

## Database & Migrations

- All schema changes must be done via migrations.
- Use parameterized queries or ORM/Query Builder to prevent SQL injection.
- For major schema or migration work, check [ARCHITECTURE.md](../../ARCHITECTURE.md) and [backlog/](../../backlog/) for dependencies and design constraints.
