from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a SQLite database
DATABASE_URL = "sqlite:////data/image_model_server.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a base class for declarative class definitions
Base = declarative_base()


# Define the ImageModel table
class ImageModel(Base):
    __tablename__ = "image_models"
    id = Column(String, primary_key=True, index=True)
    image_name = Column(String, index=True)
    image_path = Column(String, index=True)
    detection_json = Column(Text)


# Create the table in the database
Base.metadata.create_all(bind=engine)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
