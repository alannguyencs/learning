---
name: db-cloud-migration
description: Generate a cloud migration script from implementation plans. Use when
  user says "db cloud migration", "generate migration script", "migration script",
  "deploy migrations", or "cloud deploy".
---

# Cloud Migration Script Generator

Generate a Python migration script that deploys database changes from implementation plans to DEV and PROD cloud servers.

## Step 1: Identify the Plan Files

1. Read `docs/checklist.md` and find the `## DB Cloud Migration` section.
2. Collect all **unchecked** items (`- [ ]`) from that section — these are the plan file paths that still need migration scripts generated.
3. If there are no unchecked items, inform the user that all migrations are up to date and stop.
4. For each unchecked plan file path:
   a. Read the plan file and extract the **Database Schema** section.
   b. From the Database Schema section, identify all SQL migration files referenced (e.g., `scripts/sql/150_create_email_notification_settings.sql`).
   c. Collect a deduplicated, sorted list of migration version numbers and filenames.
5. If a plan has no Database Schema changes (all "None"), skip it and inform the user.

## Step 2: Verify SQL Files Exist

For each migration file referenced in the plans:

1. Use Glob to verify the file exists in `scripts/sql/`.
2. Read the file to confirm it contains valid SQL.
3. If a referenced file does not exist, warn the user and ask whether to proceed without it.

## Step 3: Generate the Migration Script

Create a Python script at `scripts/s{yymmdd}_cloud_migration.py` (using today's date) following the reference pattern from `scripts/s260305_run_cloud_migrations.py`.

The generated script MUST include:

### 3a. Environment Support (DEV and PROD)

```python
# --target dev   -> reads DEV_DB_USERNAME, DEV_DB_NAME, DEV_DB_URL, DEV_DB_PASSWORD
# --target prod  -> reads PROD_DB_USERNAME, PROD_DB_NAME, PROD_DB_URL, PROD_DB_PASSWORD
```

- Default target is `dev` (safest default).
- PROD requires explicit `--target prod`.
- The `get_engine(target)` function builds the connection URL from `{TARGET}_DB_*` env vars.

### 3b. Core Arguments

| Argument | Description |
|----------|-------------|
| `--target {dev,prod}` | Which server to run against (default: `dev`) |
| `--dry-run` | Print what would be applied without executing |
| `--from N` | Only run migrations with version >= N |
| `--only N,M,...` | Run only specific migration numbers |
| `--backfill-to N` | Mark migrations 1..N as applied without running |

### 3c. Safety Features

- **PROD confirmation**: When `--target prod` is used WITHOUT `--dry-run`, prompt `"You are about to run migrations on PRODUCTION. Type 'yes' to confirm: "` before proceeding.
- **Tracking table**: `schema_migrations` table to track applied versions (same as reference).
- **Transaction per migration**: Each migration runs in its own transaction.
- **Fail-fast**: Stop on first failure (do not continue to next migration).

### 3d. Script Structure

Follow this structure (matching the reference script):

```python
#!/usr/bin/env python
"""Run SQL migrations against DEV or PROD cloud database.

Generated from implementation plans:
  - {plan_file_1}
  - {plan_file_2}

Migrations included: {comma-separated list of version numbers}

Usage (from project root):
    source venv/bin/activate

    # DEV (default target)
    python scripts/s{yymmdd}_cloud_migration.py --dry-run
    python scripts/s{yymmdd}_cloud_migration.py
    python scripts/s{yymmdd}_cloud_migration.py --only {versions}

    # PROD
    python scripts/s{yymmdd}_cloud_migration.py --target prod --dry-run
    python scripts/s{yymmdd}_cloud_migration.py --target prod
"""
```

Include these functions (adapted from reference):
- `_build_url(username, db_name, db_url, password)` — build PostgreSQL URL
- `get_engine(target)` — create engine from `{TARGET}_DB_*` env vars
- `ensure_tracking_table(engine)` — create `schema_migrations` if missing
- `get_applied_versions(engine)` — return set of applied versions
- `discover_migrations()` — scan `scripts/sql/` for migration files
- `run_migration(engine, version, filename, filepath, dry_run)` — execute one migration
- `backfill(engine, up_to)` — mark range as applied without executing
- `main()` — argparse entry point with all arguments

### 3e. Scoped Migration List

Unlike the reference script which runs ALL pending migrations, the generated script should have a `INCLUDED_VERSIONS` set that limits which migrations it will consider:

```python
# Migrations from the implementation plans
INCLUDED_VERSIONS = {150, 151, ...}  # populated from Step 1
```

The `discover_migrations()` function should filter to only these versions by default. Add a `--all` flag to override and run all pending migrations (matching reference behavior).

## Step 4: Verify the Script

1. Read back the generated script to verify completeness.
2. Run a syntax check:

```bash
source venv/bin/activate && python -m py_compile scripts/s{yymmdd}_cloud_migration.py
```

3. Fix any syntax errors.

## Step 5: Run Pre-commit

```bash
source venv/bin/activate && pre-commit run --all-files
```

Fix any issues reported.

## Step 6: Update Checklist

For each plan file that was successfully processed (had migrations included in the generated script), mark its entry as checked in `docs/checklist.md` under `## DB Cloud Migration`:

- Change `- [ ] docs/plan/{plan_file}.md` to `- [x] docs/plan/{plan_file}.md`

Plans that were skipped (no Database Schema changes) should also be marked as checked since they have no migrations to generate.

## Step 7: Present Summary

- **Plans processed**: list of plan files and the migrations extracted from each
- **Migrations included**: sorted list of version numbers with filenames
- **Script generated**: path to the generated file
- **Usage examples**:
  ```
  # Dry run on DEV
  python scripts/s{yymmdd}_cloud_migration.py --dry-run

  # Actual run on DEV
  python scripts/s{yymmdd}_cloud_migration.py

  # Dry run on PROD
  python scripts/s{yymmdd}_cloud_migration.py --target prod --dry-run

  # Actual run on PROD (will prompt for confirmation)
  python scripts/s{yymmdd}_cloud_migration.py --target prod
  ```
- **Pre-commit result**: passed / issues fixed
- **Reminder**: Ensure `PROD_DB_*` env vars are set in `.env` before running against PROD
