"""Allow running `python -m scripts query "..."` as a shorthand for the CLI."""

from scripts.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
