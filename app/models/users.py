from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.schemas.users import UserRoleEnum


class User(Base):
    __tablename__ = 'Users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    hashed_password = Column(String(100), nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER, nullable=False)
    is_active = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="user")
