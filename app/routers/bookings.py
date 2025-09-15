from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from deps import get_session
from models import Booking, BookingSeat, Show, Seat, HallRow, Movie
from schemas import BookingRequest, BookingOut, SuggestionOut
from utils.seating import find_contiguous_block
from utils.suggestions import suggest_alternatives

router = APIRouter()

@router.post("/", response_model=BookingOut)
def create_booking(payload: BookingRequest):
    with get_session() as db:
        show = db.get(Show, payload.show_id)
        if not show:
            raise HTTPException(400, "Show not found")
        movie = db.get(Movie, show.movie_id)
        if not movie:
            raise HTTPException(400, "Movie missing")
        
        # Validation: if both group_size and seats provided, they must match in length
        if payload.group_size and payload.seats:
            if len(payload.seats) != payload.group_size:
                raise HTTPException(400, "Length of seats[] must match group_size")

        # Mode 1: explicit seat IDs
        if payload.seats:
            seat_ids = list(dict.fromkeys(payload.seats))
        else:
            # Mode 2: auto-allocate contiguous seats of size group_size
            if not payload.group_size or payload.group_size < 1:
                raise HTTPException(400, "Provide seats[] or a valid group_size")
            # Build availability by row in the hall
            seats = db.query(Seat).filter(Seat.hall_id == show.hall_id).all()
            booked = set(
                [
                    sid
                    for (sid,) in db.query(BookingSeat.seat_id)
                    .filter(BookingSeat.show_id == show.id)
                    .all()
                ]
            )
            by_row = {}
            for s in seats:
                if s.id in booked:
                    continue
                by_row.setdefault(s.row_label, []).append(s)
            chosen = None
            for row_label, row_seats in sorted(by_row.items()):
                row_seats.sort(key=lambda x: x.number)
                avail_nums = [r.number for r in row_seats]
                block = find_contiguous_block(avail_nums, payload.group_size)
                if block:
                    map_id = {r.number: r.id for r in row_seats}
                    chosen = [map_id[n] for n in block]
                    break
            if not chosen:
                raise HTTPException(
                    409,
                    "Contiguous seats not available; call /bookings/suggest for alternatives",
                )
            seat_ids = chosen

        # Transaction: create booking + booking_seats with unique(show_id, seat_id)
        total_price = len(seat_ids) * movie.price
        booking = Booking(show_id=show.id, total_price=total_price)
        db.add(booking)
        db.flush()
        try:
            for sid in seat_ids:
                db.add(BookingSeat(booking_id=booking.id, show_id=show.id, seat_id=sid))
            db.flush()
        except IntegrityError:
            raise HTTPException(
                409,
                "Some seats were just booked by another request. Please retry or pick different seats.",
            )

        return BookingOut(
            id=booking.id,
            show_id=show.id,
            total_price=booking.total_price,
            status=booking.status,
            seat_ids=seat_ids,
        )


@router.get("/suggest", response_model=list[SuggestionOut])
def suggest(show_id: int, group_size: int):
    with get_session() as db:
        show = db.get(Show, show_id)
        if not show:
            raise HTTPException(404, "Show not found")
        return suggest_alternatives(
            db, show.movie_id, show.hall_id, group_size, show.start_time
        )
