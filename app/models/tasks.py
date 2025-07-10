from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from app.core.database import Base
from app.schemas.tasks import TaskEnum

class Task(Base):
    __tablename__ = 'Task'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(256))
    status = Column(Enum(TaskEnum), default=TaskEnum.IN_PROGRESS, nullable=False)
    deadline = Column(DateTime, default=(datetime.now(timezone.utc) + timedelta(days=1)))
    is_complited = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("User.id"))
    user = relationship("User", back_populates="tasks")

    async def update_status(self):
        if self.is_complited:
            self.status = TaskEnum.DONE
        elif self.deadline < datetime.now(timezone.utc):
            self.status = TaskEnum.EXPIRED
        else:
            self.status = TaskEnum.IN_PROGRESS
