from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(f".env.{os.getenv('ENV', 'dev')}")
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL,pool_size=20)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db_singleton():
    db = SessionLocal()
    # print("Db start connectiion")
    try:
        return db
    finally:
        # print('Db session closed')
        db.close()

def get_db():
    db = SessionLocal()
    # print("Db start connectiion")
    # print(engine.pool.status())
    try:
        yield db
    finally:
        # print('Db session closed')
        db.close()        
