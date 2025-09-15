from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from ..models import Seat, BookingSeat
from ..schemas import SeatOut
from ..deps import get_session

router = APIRouter()

@router.get("/hall/{hall_id}", response_model=list[SeatOut])
def list_hall_seats(hall_id:int):
    with get_session() as db:
        return db.scalars(select(Seat).where(Seat.hall_id==hall_id).order_by(Seat.row_label, Seat.number)).all()

@router.get("/availability/{show_id}")
def show_availability(show_id:int):
    with get_session() as db:
        all_seats = db.scalars(select(Seat)).all()
        booked = set([sid for (sid,) in db.query(BookingSeat.seat_id).filter(BookingSeat.show_id==show_id).all()])
        return {
            "booked": list(booked),
            "available": [s.id for s in all_seats if s.id not in booked]
        }
