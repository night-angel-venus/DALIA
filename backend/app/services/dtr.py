from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import DTR, ShiftTypeEnum, User


shift_hours = {
    ShiftTypeEnum.FULL_DAY: 8,
    ShiftTypeEnum.HALF_DAY: 4, 
}

def user_time_in(
    db: Session,
    user: User,
    shift_type: ShiftTypeEnum,
    timestamp: datetime
):

    dtr_date = timestamp.date()

    existing_dtr = db.query(DTR).filter(DTR.user_id == user.id, DTR.date == dtr_date).first()

    if existing_dtr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already timed in today"
        )

    hours = shift_hours[shift_type]

    dtr = DTR(
        date=dtr_date,
        user_id = user.id,
        shift_type = shift_type,
        time_in = timestamp,
        estimated_time_out = timestamp + timedelta(hours=hours)
    )

    db.add(dtr)
    return dtr


def user_time_out(
    db: Session,
    user: User,
    timestamp: datetime,
) -> DTR:

    dtr_date =timestamp.date()

    recent_dtr = db.query(DTR).filter(
        DTR.user_id == user.id,
        DTR.date == dtr_date
    ).first()

    if not recent_dtr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not timed in yet"
        )

    if recent_dtr.time_out is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already timed out"
        )

    recent_dtr.time_out = timestamp

    return recent_dtr