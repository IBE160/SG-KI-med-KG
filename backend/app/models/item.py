from sqlalchemy import Column, String, Integer, ForeignKey
from app.models.guid import GUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from .base import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(GUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    user_id = Column(GUID, ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="items")