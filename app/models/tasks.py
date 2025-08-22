from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from app.core.database import Base
from app.schemas.tasks import TaskEnum

class Task(Base):
    __tablename__ = 'Tasks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(256))
    status = Column(Enum(TaskEnum), default=TaskEnum.IN_PROGRESS, nullable=False, index=True)
    deadline = Column(DateTime, default=(datetime.now(timezone.utc) + timedelta(days=1)), index=True)
    is_completed = Column(Boolean, default=False, index=True)

    user_id = Column(Integer, ForeignKey("Users.id"))
    user = relationship("User", back_populates="tasks")

    async def update_status(self):
        if self.is_completed:
            self.status = TaskEnum.DONE
        elif self.deadline < datetime.now(timezone.utc):
            self.status = TaskEnum.EXPIRED
        else:
            self.status = TaskEnum.IN_PROGRESS

    def __repr__(self):
        return f"<Task id={self.id} title={self.title} status={self.status}>"

