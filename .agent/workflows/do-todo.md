# Do TODO

## Purpose

Identifies and helps you work on the next TODO task marked with `[/]` in [TODO.md](./TODO.md).

## Usage

When invoked, this command will:

1. **Find the next task** - Locate the task marked with `[/]` in TODO.md
2. **Show task details** - Display the task description and any related links
3. **Provide context** - Show relevant sections from `docs/` or `backlog/`

## Process

### Step 1: Identify Next Task

// turbo
```bash
grep -n "^-\s*\[/\]" TODO.md
```

### Step 2: Extract Task Details

- Parse the task description.
- Check backlog/ and docs/ for related PBIs, design decisions, or dependencies.

### Step 3: Open Relevant Context

Open the following files for reference:

- `TODO.md` - Main task list
- `backlog/` - Product backlog items; `docs/` - Design decisions and documentation

### Step 4: Mark as Complete When Done

After completing the task:

1. Change `[/]` to `[x]` in [TODO.md](./TODO.md)
2. Move `[/]` marker to the next priority task
3. Update backlog or docs if any issue or dependency was resolved.
