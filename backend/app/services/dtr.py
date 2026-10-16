from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Import for Models to be worked on
from app.models import DTR, ShiftTypeEnum, User

# Essential Imports for time in and time out
from datetime import datetime, timedelta


# This dictionary contains keys that
# determine the values of each day, pointing them to the values of the enum declared in enums.py
shift_hours = {
    ShiftTypeEnum.FULL_DAY: 8,
    ShiftTypeEnum.HALF_DAY: 4, 
}

# Time in logic
def user_time_in(
    db: Session,
    user: User,
    shift_type: ShiftTypeEnum,
    timestamp: datetime
):

    # VARIABLES
    # These variables make are required to feed into the model for data creation

    # DTR DATE - takes in the date today
    dtr_date = timestamp.date()

    # EXISTING DTR - Queries a DTR record based on the User ID
    # the User ID is based on the user who is logged in (courtesy of Auth Access Token
    existing_dtr = db.query(DTR).filter(DTR.user_id == user.id, DTR.date == dtr_date).first()

    # Checks if there is already a DTR
    if existing_dtr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already timed in today"
        )

    # HOURS - Takes in the shift type based on the enum, and this is a parameter
    hours = shift_hours[shift_type]


    # This CREATES the python object by using the model

    # The variables declared earlier are being fed onto here
    # So they can fit the parameters of the model

    dtr = DTR(
        date=dtr_date,
        user_id = user.id,
        shift_type = shift_type,
        time_in = timestamp,
        estimated_time_out = timestamp + timedelta(hours=hours)
    )



    # This is what actually adds the DTR to the database
    db.add(dtr)

    # There is no db.commit since that should happen in main.py
    # and this is just a service that will be imported into main.py

    return dtr


# This function has similar logic to time in
def user_time_out(
    db: Session,
    user: User,
    timestamp: datetime,
) -> DTR:

    # This gets the current Date
    dtr_date = timestamp.date()


    # This retrieves the user's recent time in
    recent_dtr = db.query(DTR).filter(
        DTR.user_id == user.id,
        DTR.date == dtr_date
    ).first()


    # Error handlers
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

    # this sets the time_out column to the current timestamp
    recent_dtr.time_out = timestamp

    return recent_dtr