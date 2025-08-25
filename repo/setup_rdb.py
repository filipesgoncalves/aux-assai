# repo/setup_rdb.py
"""
Setup script for initializing the relational database schema and tables
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Base, DEFAULT_SCHEMA
from app.database import engine, SETTINGS


def setup_database():
    """Set up the database schema and tables."""
    print("Setting up database schema and tables...")

    try:
        # Create schema if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {DEFAULT_SCHEMA}'))
            conn.commit()

        # Create all tables
        Base.metadata.create_all(engine)
        print("Database setup completed successfully.")

        # Give feedback about what was created
        print("\nCreated schema:", DEFAULT_SCHEMA)
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"- {table.name}")

    except Exception as e:
        print("Error setting up database:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    # Print environment for debugging
    print("Environment settings:")
    print(f"PGDATABASE: {SETTINGS.dbname}")
    print(f"PGHOST: {SETTINGS.host}")
    print(f"PGPORT: {SETTINGS.port}")
    print(f"PGUSER: {SETTINGS.user}")
    print(f"PGSCHEMA: {SETTINGS.schema}")
    
    setup_database()
