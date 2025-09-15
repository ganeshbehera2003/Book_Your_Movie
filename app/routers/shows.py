from fastapi import APIRouter, HTTPException
from sqlalchemy import select, and_, or_
from schemas import ShowCreate, ShowOut
from models import Seat, Show, Hall, Movie, BookingSeat
from deps import get_session

router = APIRouter()

@router.post("/", response_model=ShowOut)
def create_show(payload: ShowCreate):
    with get_session() as db:
        if not db.get(Hall, payload.hall_id):
            raise HTTPException(400, "Hall not found")
        if not db.get(Movie, payload.movie_id):
            raise HTTPException(400, "Movie not found")
        if payload.end_time <= payload.start_time:
            raise HTTPException(400, "end_time must be after start_time")
        # Overlapping show check
        overlapping = db.scalar(
            select(Show).where(
                Show.hall_id == payload.hall_id,
                or_(
                    and_(
                        Show.start_time <= payload.start_time,
                        Show.end_time > payload.start_time,
                    ),
                    and_(
                        Show.start_time < payload.end_time,
                        Show.end_time >= payload.end_time,
                    ),
                    and_(
                        Show.start_time >= payload.start_time,
                        Show.end_time <= payload.end_time,
                    ),
                ),
            )
        )
        if overlapping:
            raise HTTPException(
                400, "Another show is already scheduled in this hall during this time"
            )

        s = Show(**payload.model_dump())
        db.add(s)
        db.flush()
        return s


@router.get("/", response_model=list[ShowOut])
def list_shows():
    with get_session() as db:
        return db.scalars(select(Show)).all()


@router.get("/{show_id}", response_model=ShowOut)
def get_show(show_id: int):
    with get_session() as db:
        s = db.get(Show, show_id)
        if not s:
            raise HTTPException(404, "Not found")
        return s


@router.get("/{show_id}/seats")
def get_seat_layout(show_id: int):
    with get_session() as db:
        show = db.get(Show, show_id)
        if not show:
            raise HTTPException(404, "Show not found")

        seats = db.query(Seat).filter(Seat.hall_id == show.hall_id).all()
        booked_seat_ids = set(
            sid
            for (sid,) in db.query(BookingSeat.seat_id)
            .filter(BookingSeat.show_id == show_id)
            .all()
        )

        by_row = {}
        for seat in seats:
            by_row.setdefault(seat.row_label, []).append(
                {
                    "seat_id": seat.id,
                    "number": seat.number,
                    "is_aisle": seat.is_aisle,
                    "booked": seat.id in booked_seat_ids,
                }
            )

        # Sort seats by number within each row
        layout = [
            {"row_label": row_label, "seats": sorted(seats, key=lambda x: x["number"])}
            for row_label, seats in sorted(by_row.items())
        ]

        return {"hall_id": show.hall_id, "rows": layout}
