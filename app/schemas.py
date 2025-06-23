import datetime

from pydantic import BaseModel, Field


class BookingBase(BaseModel):
    guest_name: str
    unit_id: str
    check_in_date: datetime.date
    number_of_nights: int

    class Config:
        orm_mode = True


class ExtendBookingRequest(BaseModel):
    extra_nights: int = Field(..., gt=0,
                              description="Number of additional nights to extend the stay")

    class Config:
        schema_extra = {
            "example": {"extra_nights": 3}
        }
