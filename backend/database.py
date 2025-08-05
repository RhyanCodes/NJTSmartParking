# imports create_engine function from sqlalchemy library
from sqlalchemy import create_engine
# import declarative base_function 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Connection string for PostgreSQL database
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:FF7Cloud$@localhost/njtsmartparking"

#Create the SQLAlchemy Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for your models to inherit from 
Base = declarative_base()