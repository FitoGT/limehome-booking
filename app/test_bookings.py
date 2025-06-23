import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

TEST_DATE = "2023-05-21"

GUEST_A_UNIT_1 = {
    'unit_id': '1',
    'guest_name': 'GuestA',
    'check_in_date': TEST_DATE,
    'number_of_nights': 5
}
GUEST_A_UNIT_2 = {
    'unit_id': '2',
    'guest_name': 'GuestA',
    'check_in_date': TEST_DATE,
    'number_of_nights': 5
}
GUEST_B_UNIT_1 = {
    'unit_id': '1',
    'guest_name': 'GuestB',
    'check_in_date': TEST_DATE,
    'number_of_nights': 5
}


@pytest.fixture()
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.freeze_time('2023-05-21')
def test_create_fresh_booking(test_db):
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    response.raise_for_status()
    assert response.status_code == 200, response.text


@pytest.mark.freeze_time('2023-05-21')
def test_same_guest_same_unit_booking(test_db):
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text
    response.raise_for_status()

    # Guests want to book same unit again
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 400, response.text
    assert response.json()[
        'detail'] == 'The given guest name cannot book the same unit multiple times'


@pytest.mark.freeze_time('2023-05-21')
def test_same_guest_different_unit_booking(test_db):
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text

    # Guest wants to book another unit
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_2
    )
    assert response.status_code == 400, response.text
    assert response.json()[
        'detail'] == 'The same guest cannot be in multiple units at the same time'


@pytest.mark.freeze_time('2023-05-21')
def test_different_guest_same_unit_booking(test_db):
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text

    # GuestB trying to book a unit that is already occuppied
    response = client.post(
        "/api/v1/booking",
        json=GUEST_B_UNIT_1
    )
    assert response.status_code == 400, response.text
    assert response.json()[
        'detail'] == 'For the given check-in date, the unit is already occupied'


@pytest.mark.freeze_time('2023-05-21')
def test_different_guest_same_unit_booking_different_date(test_db):
    # Create first booking
    # Create the payload inside the test in order to freeze_time wraps date.today();
    # module‐level date.today() executes at import and wont be frozen.
    guest_a = {
        'unit_id': '1',
        'guest_name': 'GuestA',
        'check_in_date': datetime.date.today().isoformat(),
        'number_of_nights': 5
    }
    response = client.post(
        "/api/v1/booking",
        json=guest_a
    )
    assert response.status_code == 200, response.text

    # GuestB trying to book a unit that is already occuppied
    response = client.post(
        "/api/v1/booking",
        json={
            'unit_id': '1',  # same unit
            'guest_name': 'GuestB',  # different guest
            # check_in date of GUEST A + 1, the unit is already booked on this date
            'check_in_date': (datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'),
            'number_of_nights': 5
        }
    )
    assert response.status_code == 400, response.text
    assert response.json()[
        'detail'] == 'For the given check-in date, the unit is already occupied'


@pytest.mark.freeze_time('2023-05-21')
def test_extend_booking_successful(test_db):
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text
    response = client.patch(
        "/api/v1/booking/1/extend",
        json={"extra_nights": 3}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["number_of_nights"] == 8
    assert data["check_out_date"] == "2023-05-29"


@pytest.mark.freeze_time('2023-05-21')
def test_extend_booking_not_found(test_db):
    response = client.patch(
        "/api/v1/booking/999/extend",
        json={"extra_nights": 1}
    )
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Booking id=999 not found"


@pytest.mark.freeze_time('2023-05-21')
def test_extend_booking_conflict(test_db):
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text
    booking_b = {
        "unit_id": "1",
        "guest_name": "GuestB",
        "check_in_date": "2023-05-26",
        "number_of_nights": 2
    }
    response = client.post(
        "/api/v1/booking",
        json=booking_b
    )
    assert response.status_code == 200, response.text
    response = client.patch(
        "/api/v1/booking/1/extend",
        json={"extra_nights": 2}
    )
    assert response.status_code == 400, response.text
    assert response.json()[
        "detail"] == "Extension conflicts with another booking"


@pytest.mark.freeze_time('2023-05-21')
def test_extend_booking_invalid_extra_nights(test_db):
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text
    response = client.patch(
        "/api/v1/booking/1/extend",
        json={"extra_nights": 0}
    )
    assert response.status_code == 422, response.text
    assert any(err["loc"][-1] ==
               "extra_nights" for err in response.json()["detail"])
