from sqlalchemy.orm import Session
from app.models.bookings import Booking
from datetime import date


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_booking(self, booking_id: int) -> Booking:
        return self.db.query(Booking).get(booking_id)

    def save_booking(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def find_overlaps(self, unit_id: str, start: date, end: date, exclude_id: int = None):
        q = self.db.query(Booking).filter(
            Booking.unit_id == unit_id,
            Booking.check_in_date < end,
            Booking.check_out_date > start,
        )
        if exclude_id:
            q = q.filter(Booking.id != exclude_id)
        return q.all()

    def find_guest_overlaps(self, guest_name: str, start: date, end: date, exclude_id: int = None):
        q = self.db.query(Booking).filter(
            Booking.guest_name == guest_name,
            Booking.check_in_date < end,
            Booking.check_out_date > start,
        )
        if exclude_id:
            q = q.filter(Booking.id != exclude_id)
        return q.all()
