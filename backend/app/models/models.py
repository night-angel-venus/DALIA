from sqlalchemy import Column, Integer, String, Enum, Date, DateTime, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base



# ENUM VALUES
class UserRoleEnum(str, enum.Enum):
    ADMIN = "Admin"
    USER = "User"

class ShiftTypeEnum(str, enum.Enum):
    FULL_DAY = "Full Day (8 Hours)"
    HALF_DAY = "Half Day (4 Hours)"


# ACTUAL MODELS
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), nullable=False)

    rel_dtr = relationship("DTR", back_populates="user", cascade="all, delete-orphan")



class DTR(Base):
    __tablename__ = "dtr"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=func.now())
    user_id = Column(Integer)
    shift_type = Column(Enum(ShiftTypeEnum), default=ShiftTypeEnum.FULL_DAY)
    time_in = Column(DateTime, default=func.now())
    estimated_time_out = Column(DateTime)
    time_out = Column(DateTime)

    rel_user = relationship("User", back_populates="rel_dtr")