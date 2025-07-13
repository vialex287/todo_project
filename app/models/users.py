from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = 'Users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="user")
