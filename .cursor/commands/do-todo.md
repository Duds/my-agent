---
description: Identifies and helps work on the next TODO task
---

# Do TODO

## Purpose

Identifies and helps you work on the next TODO task marked with `[/]` in [TODO.md](./TODO.md).

## Usage

When invoked, this command will:

1. **Find the next task** - Locate the task marked with `[/]` in TODO.md
2. **Show task details** - Display the task description and any related links
3. **Provide context** - Show relevant sections from `RAIDD.md` or `docs/`

## Process

### Step 1: Identify Next Task

// turbo
```bash
grep -n "^-\s*\[/\]" TODO.md
```

### Step 2: Extract Task Details

- Parse the task description.
- Check [RAIDD.md](./RAIDD.md) for related Issues, Risks, or Decisions.

### Step 3: Open Relevant Context

Open the following files for reference:

- `TODO.md` - Main task list
- `RAIDD.md` - Central log of decisions, risks, issues, dependencies

### Step 4: Mark as Complete When Done

After completing the task:

1. Change `[/]` to `[x]` in [TODO.md](./TODO.md)
2. Move `[/]` marker to the next priority task
3. Update [RAIDD.md](./RAIDD.md) if any issue or dependency was resolved.
