# -*- coding: utf-8 -*-

from config.settings import settings
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a base class for declarative models
Base = declarative_base()

# Get the database URL from the configuration settings
url = settings.DATABASE_URL

# Create a SQLAlchemy engine
engine = create_engine(url)

# Create a session maker
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """
    Initialize the database by creating all tables and resetting sequences.

    Returns:
        None
    """
    Base.metadata.create_all(bind=engine)
    reset_all_sequences()


def get_db():
    """
    Dependency to get a database session.

    Yields:
        db: Database session.

    Finally:
        Closes the database session.
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()


def reset_sequence(tabla_name):
    """
    Reset the sequence for a given table.

    Args:
        table_name (str): Name of the table.

    Returns:
        None
    """
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT max(id) FROM {tabla_name}"))
        max_id = result.fetchone()[0] or 1
        connection.execute(text(f"SELECT setval('{tabla_name}_id_seq', {max_id})"))


def reset_all_sequences():
    with engine.connect() as connection:
        tables = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        for table in tables:
            if table[0] != 'alembic_version':
                reset_sequence(table[0])