import os
import argparse
from sqlalchemy import create_engine, MetaData, Table, select, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# Heuristic order: parents first, junctions last
PREFERRED_ORDER = [
    "EMPLOYEE",
    "CUSTOMER",
    "GENERATOR",
    "PROJECT",
    "PROJECTS",
    "TASK",
    "TASKS",
    "SERVICE_RECORD",
    "SERVICE_EMPLOYEE_INT",
    "PASSWORD_RECOVERY",
]


def ordered_tables(src_engine: Engine) -> list[str]:
    insp = inspect(src_engine)
    tables = insp.get_table_names()
    # Normalize to uppercase for matching quoted identifiers
    upper = {t.upper(): t for t in tables}
    ordered = []
    for name in PREFERRED_ORDER:
        if name in upper:
            ordered.append(upper[name])
    # Append any remaining tables not in preferred order
    for t in tables:
        if t not in ordered:
            ordered.append(t)
    return ordered


def copy_table(src_engine: Engine, dst_engine: Engine, table_name: str) -> tuple[int, int]:
    src_meta = MetaData()
    dst_meta = MetaData()
    src_table = Table(table_name, src_meta, autoload_with=src_engine)
    dst_table = Table(table_name, dst_meta, autoload_with=dst_engine)

    with src_engine.connect() as sconn:
        rows = sconn.execute(select(src_table)).fetchall()

    inserted = 0
    if not rows:
        return 0, 0

    # Convert Row objects to dicts
    payload = [dict(r._mapping) for r in rows]

    with dst_engine.begin() as dconn:
        try:
            dconn.execute(dst_table.insert(), payload)
            inserted = len(payload)
        except Exception as e:
            # Best-effort: try inserting one-by-one to skip conflicts
            inserted = 0
            for r in payload:
                try:
                    dconn.execute(dst_table.insert().values(**r))
                    inserted += 1
                except Exception:
                    # skip conflicting row
                    pass
    return len(rows), inserted


def ensure_dest_schema(pg_url: str):
    """Create destination schema using app models."""
    # Use app's models metadata to create all tables in the destination
    os.environ["DATABASE_URL"] = pg_url
    from base import api  # imports app bound via ApplicationConfig
    from models import db

    with api.app_context():
        db.create_all()


def main():
    parser = argparse.ArgumentParser(description="Migrate data from local SQLite to Postgres")
    parser.add_argument("--pg", required=True, help="Destination Postgres DATABASE_URL")
    parser.add_argument("--sqlite", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "db.sqlite")), help="Source SQLite path (default: ../instance/db.sqlite)")
    args = parser.parse_args()

    sqlite_url = f"sqlite:///{args.sqlite}"
    pg_url = args.pg

    if not os.path.exists(args.sqlite):
        raise SystemExit(f"SQLite file not found: {args.sqlite}")

    print(f"Source: {sqlite_url}")
    print(f"Destination: {pg_url}")

    # Create destination schema
    ensure_dest_schema(pg_url)

    src_engine = create_engine(sqlite_url, future=True)
    dst_engine = create_engine(pg_url, future=True)

    tables = ordered_tables(src_engine)
    print("Tables (copy order):", tables)

    total_read = 0
    total_inserted = 0

    for t in tables:
        try:
            read, ins = copy_table(src_engine, dst_engine, t)
            total_read += read
            total_inserted += ins
            print(f"- {t}: read {read}, inserted {ins}")
        except Exception as e:
            print(f"! Skipped {t}: {e}")

    print("Done.")
    print(f"Total rows read: {total_read}")
    print(f"Total rows inserted: {total_inserted}")


if __name__ == "__main__":
    main()
