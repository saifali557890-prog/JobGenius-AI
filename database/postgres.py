from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config
from utils.logger import get_logger

logger = get_logger("DatabaseManager")

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                pool_pre_ping=True,
                echo=False
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("Database engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Database Engine: {str(e)}")
            raise e

    def create_tables(self):
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables verified/created successfully.")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")

    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

db_manager = DatabaseManager()