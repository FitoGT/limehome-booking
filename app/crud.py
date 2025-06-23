from typing import Tuple
from datetime import timedelta, date

from sqlalchemy.orm import Session
from . import models, schemas


class UnableToBook(Exception):
    pass


class UnableToExtend(Exception):
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


def extend_booking(db: Session, booking_id: int, extra_nights: int) -> models.Booking:
    """
    Extend an existing booking by extra_nights if possible. Updates check_out_date.
    Throws UnableToExtend(reason) on conflict or not found.
    """
    can_extend, reason = can_extend_booking(db, booking_id, extra_nights)
    if not can_extend:
        raise UnableToExtend(reason)

    booking = db.query(models.Booking).get(booking_id)
    booking.number_of_nights += extra_nights
    booking.check_out_date = booking.check_in_date + \
        timedelta(days=booking.number_of_nights)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


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


def can_extend_booking(db: Session, booking_id: int, extra_nights: int) -> Tuple[bool, str]:
    """
    Determine whether an existing booking can be extended by extra_nights.
    Returns (True, 'OK') if possible, else (False, reason).
    """
    original = db.query(models.Booking).get(booking_id)
    if not original:
        return False, f"Booking id={booking_id} not found"

    current_end = original.check_out_date
    new_end = current_end + timedelta(days=extra_nights)

    conflict = db.query(models.Booking).filter(
        models.Booking.id != booking_id,
        models.Booking.check_in_date < new_end,
        models.Booking.check_out_date > current_end,
        models.Booking.unit_id == original.unit_id,
    ).first()

    if conflict:
        return False, 'Extension conflicts with another booking'

    return True, 'OK'
