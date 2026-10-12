from sqlalchemy import Column, Integer, String, Enum, Date, DateTime, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import UserRoleEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), nullable=False)

    rel_dtr = relationship("DTR", back_populates="rel_user", cascade="all, delete-orphan")


