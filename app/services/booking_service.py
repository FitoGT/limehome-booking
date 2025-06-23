from typing import Tuple
from datetime import timedelta
from sqlalchemy.orm import Session

from app.models.bookings import Booking
from app.schemas.bookings_schemas import BookingBase
from app.repositories.booking_repository import BookingRepository
from app.services.exceptions import UnableToBook, UnableToExtend


class BookingService:
    def __init__(self, db: Session):
        self.repo = BookingRepository(db)

    def create_booking(self, booking_data: BookingBase) -> Booking:
        start = booking_data.check_in_date
        end = start + timedelta(days=booking_data.number_of_nights)

        unit_conflicts = self.repo.find_overlaps(
            booking_data.unit_id, start, end)
        for existing in unit_conflicts:
            if existing.guest_name == booking_data.guest_name:
                raise UnableToBook(
                    'The given guest name cannot book the same unit multiple times')
            else:
                raise UnableToBook(
                    'For the given check-in date, the unit is already occupied')

        guest_conflicts = self.repo.find_guest_overlaps(
            booking_data.guest_name, start, end)
        for existing in guest_conflicts:
            if existing.unit_id != booking_data.unit_id:
                raise UnableToBook(
                    'The same guest cannot be in multiple units at the same time')

        booking = Booking(
            guest_name=booking_data.guest_name,
            unit_id=booking_data.unit_id,
            check_in_date=start,
            number_of_nights=booking_data.number_of_nights,
            check_out_date=end,
        )
        return self.repo.save_booking(booking)

    def extend_booking(self, booking_id: int, extra_nights: int) -> Booking:
        original = self.repo.get_booking(booking_id)
        if not original:
            raise UnableToExtend(f"Booking id={booking_id} not found")

        current_end = original.check_out_date
        new_end = current_end + timedelta(days=extra_nights)

        conflicts = self.repo.find_overlaps(original.unit_id,
                                            current_end, new_end, exclude_id=booking_id)
        if conflicts:
            raise UnableToExtend('Extension conflicts with another booking')

        original.number_of_nights += extra_nights
        original.check_out_date = new_end
        return self.repo.save_booking(original)
