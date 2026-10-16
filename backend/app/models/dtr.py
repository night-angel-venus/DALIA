from sqlalchemy import Column, Integer, Enum, Date, DateTime, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import ShiftTypeEnum

# ACTUAL MODELS

class DTR(Base):
    __tablename__ = "dtr"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    shift_type = Column(Enum(ShiftTypeEnum), default=ShiftTypeEnum.FULL_DAY)
    time_in = Column(DateTime, default=func.now())
    estimated_time_out = Column(DateTime)
    time_out = Column(DateTime)

    rel_user = relationship("User", back_populates="rel_dtr")