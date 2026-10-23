import enum


class UserRoleEnum(str, enum.Enum):
    ADMIN = "Admin"
    USER = "User"


class ShiftTypeEnum(str, enum.Enum):
    FULL_DAY = "Full Day (8 Hours)"
    HALF_DAY = "Half Day (4 Hours)"