import logging

import databases
import sqlalchemy
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Table,
    Time,
)
from sqlalchemy.orm.session import Session

from .config import config

logger: logging.Logger = logging.getLogger(__name__)
metadata = sqlalchemy.MetaData()


user_table = Table(
    "User",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("age", SmallInteger, nullable=False),
    Column("contact_number", Integer, nullable=False),
    Column("emergency_contact_number", Integer, nullable=False),
    Column("address", String, nullable=False),
    Column("date_of_birth", Date, nullable=False),
    Column("joining_date", Date, nullable=False),
    Column("instructor", Boolean, default=False),
)


course_table = Table(
    "Course",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("slot", SmallInteger, nullable=False),
    Column("timing", Time(timezone=True), nullable=False),
)


course_user_table = Table(
    "CourseUser",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("booked_slot", Integer),
    Column(
        "user_id",
        ForeignKey("User.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    Column(
        "course_id",
        ForeignKey("Course.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
)


booking_table = Table(
    "Booking",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("booking_date", Date, nullable=False),
    Column(
        "course_user_id",
        ForeignKey("CourseUser.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
)


engine: sqlalchemy.Engine = sqlalchemy.create_engine(
    url=config.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    pool_size=20,
    max_overflow=5,
    pool_pre_ping=True,
)

metadata.create_all(engine, checkfirst=True)
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)


def get_db_session():
    logger.info("generating session")
    with Session(engine) as db:
        db.begin()
        yield db
        db.close()
