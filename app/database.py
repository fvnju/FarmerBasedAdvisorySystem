import os  # Import os to access environment variables
from dotenv import load_dotenv  # Import load_dotenv to read the .env file
from sqlalchemy import create_engine  # Import create_engine to connect to the database
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)  # Import sessionmaker and declarative_base

load_dotenv()  # Load the variables from the .env file

_database_url = os.getenv("DATABASE_URL")  # Retrieve the database connection string

if _database_url is None:
    raise Exception("No DATABASE_URL in env")

DATABASE_URL: str = _database_url  # Always a string after the check

engine = create_engine(DATABASE_URL)  # Create the database engine

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # Create session factory

Base = declarative_base()  # Create the base class for models


def get_db():  # Dependency function for FastAPI
    db = SessionLocal()  # Create a new session
    try:  # Try block
        yield db  # Yield session to route
    finally:  # Finally block
        db.close()  # Close the session
