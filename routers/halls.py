from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from schemas import HallCreate, HallOut, HallRowIn
from models import Hall, HallRow, Seat
from deps import get_session
from utils.seating import aisle_positions

router = APIRouter()

@router.post("/", response_model=HallOut)
def create_hall(payload: HallCreate):
    with get_session() as db:
        hall = Hall(theater_id=payload.theater_id, name=payload.name)
        db.add(hall); db.flush()
        # create rows
        for row in payload.rows:
            if row.seat_count < 6:
                raise HTTPException(400, "row.seat_count must be >= 6")
            hr = HallRow(hall_id=hall.id, label=row.label, seat_count=row.seat_count)
            db.add(hr); db.flush()
            aisles = set(aisle_positions(row.seat_count))
            for num in range(1, row.seat_count+1):
                db.add(Seat(hall_id=hall.id, row_label=row.label, number=num, is_aisle=(num in aisles)))
        db.flush(); return hall

@router.get("/", response_model=list[HallOut])
def list_halls():
    with get_session() as db:
        return db.scalars(select(Hall)).all()

@router.get("/{hall_id}", response_model=HallOut)
def get_hall(hall_id:int):
    with get_session() as db:
        h = db.get(Hall, hall_id)
        if not h: raise HTTPException(404, "Not found")
        return h
