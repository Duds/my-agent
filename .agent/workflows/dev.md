---
description: Standard development commands for the Between project
---

# Development Commands

## Starting Development

```bash
# Install dependencies
npm install

# Start Docker services (PostgreSQL, Redis)
npm run docker:up

# Start API server in development mode
npm run dev:api

# Start Next.js frontend
npm run dev:web

# Start all services concurrently
npm run dev
```

## Database

```bash
# Run migrations (ensure I002 is resolved in RAIDD.md)
npm run db:migrate

# Seed database
npm run db:seed
```

## Testing

// turbo
```bash
# Run all tests
npm run test

# Run API tests only
npm run test:api

# Run Frontend tests only
npm run test:web
```

## Code Quality

// turbo
```bash
# Lint code
npm run lint

# Type check
npm run typecheck
```

## Docker Management

```bash
# Start services
npm run docker:up

# Stop services
npm run docker:down

# View logs
docker-compose logs -f
```

## Critical Dependencies (Reference RAIDD.md)

Always check [RAIDD.md](file:///home/dale-rogers/Projects/active/personal/between/RAIDD.md) before starting major development tasks to ensure blocking issues (like I002) are addressed.
