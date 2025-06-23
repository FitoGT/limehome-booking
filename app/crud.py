from typing import Tuple
from datetime import timedelta, date

from sqlalchemy.orm import Session
from . import models, schemas


class UnableToBook(Exception):
    pass


def create_booking(db: Session, booking: schemas.BookingBase) -> models.Booking:
    ok, reason = is_booking_possible(db, booking)
    if not ok:
        raise UnableToBook(reason)

    db_booking = models.Booking(
        guest_name=booking.guest_name,
        unit_id=booking.unit_id,
        check_in_date=booking.check_in_date,
        number_of_nights=booking.number_of_nights,
        check_out_date=booking.check_in_date +
        timedelta(days=booking.number_of_nights),
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def is_booking_possible(db: Session, booking: schemas.BookingBase) -> Tuple[bool, str]:

    new_start = booking.check_in_date
    new_end = new_start + timedelta(days=booking.number_of_nights)

    guests = db.query(models.Booking).all()

    for guest in guests:
        guest_start = guest.check_in_date
        guest_end = guest_start + timedelta(days=guest.number_of_nights)

        if not (new_end <= guest_start or guest_end <= new_start):
            if guest.guest_name == booking.guest_name and guest.unit_id == booking.unit_id:
                return False, 'The given guest name cannot book the same unit multiple times'
            if guest.guest_name == booking.guest_name and guest.unit_id != booking.unit_id:
                return False, 'The same guest cannot be in multiple units at the same time'
            if guest.guest_name != booking.guest_name and guest.unit_id == booking.unit_id:
                return False, 'For the given check-in date, the unit is already occupied'

    return True, 'OK'
