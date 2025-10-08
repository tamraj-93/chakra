from sqlalchemy import Column, String, Integer, DateTime, func
from app.models.database import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    title = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    service_type = Column(String, nullable=True)
    upload_date = Column(DateTime, default=func.now())
    file_size = Column(Integer)
    status = Column(String, default="pending")  # processed, pending, error