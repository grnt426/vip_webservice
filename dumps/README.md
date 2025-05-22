# Item Database Dumps

This directory contains SQLite dumps of the items table. These dumps are used to preserve the items data between container restarts, preventing unnecessary API calls to the Guild Wars 2 API.

## Usage

1. To create a new dump of the items table:
   ```bash
   python scripts/dump_items.py
   ```
   This will create `items.sql` in this directory.

2. The dump will be automatically loaded when the container starts up via `scripts/load_items.py`.

## Why?

The items table contains static data from the Guild Wars 2 API. Since this data rarely changes, we don't need to fetch it from the API every time the container restarts. This helps us:

1. Reduce unnecessary API calls
2. Stay within API rate limits during development
3. Speed up container initialization

The dump file is ignored by git (see .gitignore) since it's considered build/runtime data rather than source code. 