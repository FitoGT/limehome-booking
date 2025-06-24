from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.orm import Session

from app.schemas.bookings_schemas import (
    BookingBase,
    BookingResponse,
    ExtendBookingRequest
)
from app.services.booking_service import BookingService
from app.services.exceptions import UnableToBook, UnableToExtend
from app.db.database import get_db

router = APIRouter(prefix="/api/v1/booking", tags=["Booking"])


@router.post(
    "",
    response_model=BookingResponse,
    summary="Create a new booking",
    description=(
        "Creates a booking for a guest in a given unit. "
        "Validates that there are no overlapping bookings for the same unit."
    ),
)
async def post_booking(
    booking: BookingBase,
    db: Session = Depends(get_db)
):
    try:
        return BookingService(db).create_booking(booking)
    except UnableToBook as err:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=str(err))


@router.patch(
    "/{booking_id}/extend",
    response_model=BookingResponse,
    summary="Extend an existing booking",
    description=(
        "Allows a guest to add extra nights to their current booking, "
        "after validating availability for the extension period."
    ),
)
async def patch_extend_booking(
    booking_id: int,
    request: ExtendBookingRequest,
    db: Session = Depends(get_db)
):
    try:
        return BookingService(db).extend_booking(booking_id, request.extra_nights)
    except UnableToExtend as err:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=str(err))
