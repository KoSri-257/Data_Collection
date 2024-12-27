import traceback, logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, SQLALCHEMY_POOL_SIZE, SQLALCHEMY_MAX_OVERFLOW, LOG_LEVEL

# Set up logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# engine to create DB & Base for ORM models
engine = create_engine(DATABASE_URL, pool_size=SQLALCHEMY_POOL_SIZE, max_overflow=SQLALCHEMY_MAX_OVERFLOW)
Base: DeclarativeMeta = declarative_base()

# Function to create all tables if not exist
def create_tables():
    try:
        logger.info("Checking if tables exist...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        if not existing_tables:
            logger.info("No tables found. Creating tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created successfully!")
        else:
            logger.info("Tables already exist!")
        
    except Exception as e:
        logger.exception(f"Error in creating tables: {e}")
        raise

# SessionLocal creates session instances
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"traceback: {traceback.format_exc()}")
        raise 
    finally:
        db.close()
        logger.info("Database session closed.") 
