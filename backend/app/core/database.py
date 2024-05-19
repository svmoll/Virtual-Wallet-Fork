# Connection to the database
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql
from sqlalchemy.sql import text


# Database configuration
db_username = "root"
db_password = "new_password"
db_url = "127.0.0.1:3306"
db_name = "virtual_wallet"


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

Base = declarative_base()
