from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

# Create the SQLAlchemy engine
# For PostgreSQL with psycopg2, the URL format is:
# postgresql://username:password@hostname:port/database_name

engine = create_engine(DATABASE_URL)

# Create a session factory using scoped_session for thread safety
Session = scoped_session(sessionmaker(bind=engine))

# Create base class for declarative models
Base = declarative_base()

def get_db_session():
    """Returns a thread-local database session."""
    return Session()

def close_db_session():
    """Removes the current session."""
    Session.remove()

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)