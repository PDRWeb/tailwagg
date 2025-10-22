import os
import sys
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


def load_env_variables() -> dict:
    load_dotenv()  # loads from .env in project root if present

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    missing = [k for k, v in {"DB_PASSWORD": db_password, "DB_NAME": db_name}.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    return {
        "host": db_host,
        "port": db_port,
        "user": db_user,
        "password": db_password,
        "dbname": db_name,
    }


@contextmanager
def pg_connection(params: dict):
    # Retry connection a few times to allow container startup
    last_exc = None
    conn = None
    for _ in range(10):
        try:
            conn = psycopg2.connect(**params)
            break
        except Exception as exc:
            last_exc = exc
            import time
            time.sleep(2)
    if conn is None:
        # If we exhausted retries, raise last exception
        raise last_exc
    try:
        yield conn
    finally:
        conn.close()


def create_tables(conn) -> None:
    """Create tables by executing the schema.sql file."""
    # Resolve path to project root (two levels up from this file: services -> src -> project root)
    project_root = Path(__file__).resolve().parent.parent.parent
    schema_file = project_root / "data" / "schema" / "schema.sql"
    
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    
    # Read and execute the SQL file
    with open(schema_file, 'r') as f:
        sql_content = f.read()
    
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql_content)


def main() -> None:
    params = load_env_variables()
    with pg_connection(params) as conn:
        create_tables(conn)
    print("Schema created or already present.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
