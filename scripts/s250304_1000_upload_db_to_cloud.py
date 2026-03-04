"""Upload local PostgreSQL database to cloud database.

Uses pg_dump to export the local DB and psql to import into the cloud.
Expects .env at project root with:
  - Local: DB_USERNAME, DB_URL, DB_NAME, DB_PASSWORD (optional)
  - Cloud: CLOUD_DB_USERNAME, CLOUD_DB_PASSWORD, CLOUD_DB_URL, CLOUD_DB_NAME

Usage:
  source venv/bin/activate
  python scripts/s250304_1000_upload_db_to_cloud.py \\
    [--schema-only] [--no-clean]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of scripts/)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


def _get_env(name: str, required: bool = True) -> str:
    """Get required or optional environment variable."""
    val = os.getenv(name)
    if required and not val:
        print(f"Error: {name} is not set in .env")
        sys.exit(1)
    return val or ""


def _build_local_url() -> str:
    """Build local PostgreSQL connection URL for pg_dump."""
    user = _get_env("DB_USERNAME")
    host = _get_env("DB_URL")
    name = _get_env("DB_NAME")
    passwd = _get_env("DB_PASSWORD", required=False)
    if passwd:
        return f"postgresql://{user}:{passwd}@{host}:5432/{name}"
    return f"postgresql://{user}@{host}:5432/{name}"


def _run(cmd: list[str], env_extra: dict | None = None) -> bool:
    """Run a command; return True on success."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    try:
        subprocess.run(cmd, check=True, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed (exit {e.returncode}): {' '.join(cmd)}")
        return False


def main() -> None:
    """Dump local DB and restore to cloud."""
    parser = argparse.ArgumentParser(
        description="Upload local database to cloud PostgreSQL"
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Transfer schema only, no data",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not add DROP before CREATE (faster if cloud is empty)",
    )
    args = parser.parse_args()

    user = _get_env("DB_USERNAME")
    host = _get_env("DB_URL")
    name = _get_env("DB_NAME")
    c_user = _get_env("CLOUD_DB_USERNAME")
    c_pass = _get_env("CLOUD_DB_PASSWORD")
    c_host = _get_env("CLOUD_DB_URL")
    c_name = _get_env("CLOUD_DB_NAME")

    dump_file = Path(__file__).resolve().parent / "dump_local_to_cloud.sql"

    pg_dump_cmd = [
        "pg_dump",
        "-h", host,
        "-U", user,
        "-d", name,
        "-f", str(dump_file),
        "--no-owner",
        "--no-acl",
    ]
    if args.schema_only:
        pg_dump_cmd.append("--schema-only")
    elif not args.no_clean:
        pg_dump_cmd.extend(["--clean", "--if-exists"])

    print("Dumping local database...")
    if not _run(pg_dump_cmd):
        sys.exit(1)
    print(f"  -> {dump_file}")

    psql_cmd = [
        "psql",
        "-h", c_host,
        "-U", c_user,
        "-d", c_name,
        "-f", str(dump_file),
    ]
    env_extra = {"PGPASSWORD": c_pass}

    print("Restoring to cloud database...")
    if not _run(psql_cmd, env_extra=env_extra):
        sys.exit(1)
    print("Done.")


if __name__ == "__main__":
    main()
