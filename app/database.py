from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db" #for psycopg2
# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://user:password@postgresserver/db" #for psycopg3

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} #-> second parameter used only for SQLite databases
# )
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # Every model we will use will modify this base model

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# #This is used to connect to the database in order to use it as raw SQL, above we do it by using SQL alchemy
# while True:
#     try:
#         conn = psycopg.connect(host=settings.DATABASE_HOSTNAME,dbname=settings.DATABASE_NAME,user=settings.DATABASE_USERAME,password=settings.DATABASE_PASSWORD,row_factory=psycopg.rows.dict_row)
#         cursor = conn.cursor()
#         print("Database connected successfully!")
#         break
#     except Exception as error:
#         print("Connection Failed!\nError: ", error)
#         time.sleep(10)
        
import os
var = os.getenv("MY_DB_URL")