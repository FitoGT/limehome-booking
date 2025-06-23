from app.db.database import Base, engine
import app.models.bookings


def init_db():
    Base.metadata.create_all(bind=engine)
