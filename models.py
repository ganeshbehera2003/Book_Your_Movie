from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Boolean, Float
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timedelta
from db import Base

class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    shows = relationship("Show", back_populates="movie", cascade="all, delete")

class Theater(Base):
    __tablename__ = "theaters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    halls = relationship("Hall", back_populates="theater", cascade="all, delete")

class Hall(Base):
    __tablename__ = "halls"
    id: Mapped[int] = mapped_column(primary_key=True)
    theater_id: Mapped[int] = mapped_column(ForeignKey("theaters.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    theater = relationship("Theater", back_populates="halls")
    rows = relationship("HallRow", back_populates="hall", cascade="all, delete")
    seats = relationship("Seat", back_populates="hall", cascade="all, delete")
    shows = relationship("Show", back_populates="hall", cascade="all, delete")

class HallRow(Base):
    __tablename__ = "hall_rows"
    id: Mapped[int] = mapped_column(primary_key=True)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(10), nullable=False)
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False)

    hall = relationship("Hall", back_populates="rows")

class Seat(Base):
    __tablename__ = "seats"
    id: Mapped[int] = mapped_column(primary_key=True)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id", ondelete="CASCADE"))
    row_label: Mapped[str] = mapped_column(String(10), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_aisle: Mapped[bool] = mapped_column(Boolean, default=False)

    hall = relationship("Hall", back_populates="seats")

    __table_args__ = (
        UniqueConstraint("hall_id", "row_label", "number", name="uq_hall_row_seat"),
    )

class Show(Base):
    __tablename__ = "shows"
    id: Mapped[int] = mapped_column(primary_key=True)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id", ondelete="CASCADE"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    hall = relationship("Hall", back_populates="shows")
    movie = relationship("Movie", back_populates="shows")
    bookings = relationship("Booking", back_populates="show", cascade="all, delete")

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id", ondelete="CASCADE"))
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="CONFIRMED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    show = relationship("Show", back_populates="bookings")
    seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete")

class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"))
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id", ondelete="CASCADE"))
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id", ondelete="CASCADE"))

    booking = relationship("Booking", back_populates="seats")

    __table_args__ = (
        UniqueConstraint("show_id", "seat_id", name="uq_show_seat_once"),
    )