from datetime import datetime

from sqlalchemy import Column, Integer, TIMESTAMP

from src.database import Base


class Coil(Base):
    __tablename__ = "coil_coils"

    id: int = Column(Integer, primary_key=True, index=True)
    length = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    deleted_at = Column(TIMESTAMP)
