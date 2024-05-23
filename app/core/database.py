# Connection to the database
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mariadb  # for reqs file
import pymysql  # for reqs file
from sqlalchemy.sql import text

# Database configuration from environment variables
db_username = os.getenv("DB_USERNAME", "root")
db_password = os.getenv("DB_PASSWORD", "new_password")
db_url = os.getenv("DB_URL", "127.0.0.1:3306")
db_name = os.getenv("DB_NAME", "virtual_wallet3")


def create_database_if_not_exists():
    # Connect to the server without specifying a database
    temp_engine = create_engine(
        f"mariadb+pymysql://{db_username}:{db_password}@{db_url}/"
    )
    # Execute the raw SQL to create the database if it doesn't exist
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))


create_database_if_not_exists()

# Connection string for the actual database
connectionString = f"mariadb+pymysql://{db_username}:{db_password}@{db_url}/{db_name}"

# SQLAlchemy setup
engine = create_engine(connectionString, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
